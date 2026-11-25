"""Predicción de CTR con conteos observados. No accede al mundo ni a su verdad."""
import hashlib
import json

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, logit

VERSION = "creatividad-1.0.0"
REPLICAS = 200
RIDGE = 10.0
CATEGORICAS = ("canal", "paquete", "audiencia")


def paquete(fila):
    return " | ".join(fila[k] for k in ("categoria", "tono", "cta"))


def particionar(filas):
    """Componentes conectados: una composición o campaña no cruza la frontera."""
    padres = {}

    def raiz(k):
        padres.setdefault(k, k)
        if padres[k] != k:
            padres[k] = raiz(padres[k])
        return padres[k]

    for f in filas:
        a, b = raiz("asset:"+f["asset"]), raiz("campana:"+f["campana"])
        padres[max(a, b)] = min(a, b)
    grupos = {f["id"]: raiz("asset:"+f["asset"]) for f in filas}
    por_canal = {}
    for f in filas:
        por_canal.setdefault(f["canal"], set()).add(grupos[f["id"]])
    reservados = set()
    for canal, ids in sorted(por_canal.items()):
        if len(ids) < 3:
            raise ValueError(f"Faltan tres grupos independientes de composición/campaña en {canal}.")
        reservados.add(sorted(ids)[-1])
    fechas = sorted({f["fecha"] for f in filas})
    if len(fechas) < 28:
        raise ValueError("Creatividad requiere al menos 28 días observados para validar.")
    frontera = fechas[-7]
    train = [dict(f, grupo=grupos[f["id"]]) for f in filas if f["fecha"] < frontera and grupos[f["id"]] not in reservados]
    holdout = [dict(f, grupo=grupos[f["id"]]) for f in filas if f["fecha"] >= frontera and grupos[f["id"]] in reservados]
    if not train or not holdout:
        raise ValueError("No se puede separar train y holdout por fecha y grupo.")
    if {f["campana"] for f in train} & {f["campana"] for f in holdout}:
        raise ValueError("Hay campañas compartidas entre train y holdout.")
    return train, holdout, len(filas)-len(train)-len(holdout)


def esquema(train):
    datos = [dict(f, paquete=paquete(f)) for f in train]
    frecuencias = np.array([f["frecuencia"] for f in datos])
    return dict(niveles={k: sorted({f[k] for f in datos}) for k in CATEGORICAS},
        frecuencia_media=float(frecuencias.mean()), frecuencia_escala=max(float(frecuencias.std()), .01),
        frecuencia_min=float(frecuencias.min()), frecuencia_max=float(frecuencias.max()))


def matriz(filas, schema):
    columnas = [np.ones(len(filas))]
    datos = [dict(f, paquete=paquete(f)) for f in filas]
    for k in CATEGORICAS:
        columnas.extend(np.array([f[k] == nivel for f in datos], dtype=float) for nivel in schema["niveles"][k][1:])
    columnas.append(np.array([(f["frecuencia"]-schema["frecuencia_media"])/schema["frecuencia_escala"] for f in datos]))
    return np.column_stack(columnas)


def ajustar_binomial(x, y, n, pesos=None):
    w = np.ones(len(y)) if pesos is None else np.asarray(pesos)
    if np.sum(n*w) <= 0:
        raise ValueError("No hay exposición positiva para ajustar CTR.")
    penalizacion = np.full(x.shape[1], RIDGE)
    penalizacion[0] = 0

    def objetivo(beta):
        eta = x@beta
        valor = np.sum(w*(n*np.logaddexp(0, eta)-y*eta))+.5*np.sum(penalizacion*beta**2)
        gradiente = x.T@(w*(n*expit(eta)-y))+penalizacion*beta
        escala = float(np.sum(n*w))
        return valor/escala, gradiente/escala

    inicial = np.zeros(x.shape[1])
    inicial[0] = logit(np.clip(np.sum(y*w)/np.sum(n*w), 1e-6, 1-1e-6))
    resultado = minimize(objetivo, inicial, jac=True, method="L-BFGS-B", bounds=[(-20, 20)]*x.shape[1],
                         options=dict(maxiter=250, ftol=1e-13, gtol=1e-8))
    if not resultado.success or not np.all(np.isfinite(resultado.x)):
        raise ValueError("El modelo binomial no ha convergido; no utilizar puntuaciones.")
    return resultado.x


def metricas(y, n, p):
    p = np.clip(p, 1e-12, 1-1e-12)
    if np.sum(n) <= 0:
        raise ValueError("No hay denominador para evaluar CTR.")
    return dict(log_loss=float(np.sum(-y*np.log(p)-(n-y)*np.log1p(-p))/n.sum()),
        mae_tasa=float(np.sum(n*np.abs(y/n-p))/n.sum()),
        observado=float(y.sum()/n.sum()), predicho=float(np.sum(n*p)/n.sum()),
        impresiones=int(n.sum()), clics=int(y.sum()))


def entrenar_creatividad(filas, semilla):
    if not filas or any(not 0 <= f["conversiones"] <= f["clics"] <= f["impresiones"] or f["impresiones"] <= 0
                        or not np.isfinite(f["frecuencia"]) or f["frecuencia"] < 0 for f in filas):
        raise ValueError("Conteos o frecuencia creativa no válidos.")
    claves = [(f["id"], f["fecha"], f["mercado"]) for f in filas]
    if len(set(claves)) != len(claves):
        raise ValueError("Observaciones creativas duplicadas.")
    train, holdout, excluidas = particionar(filas)
    schema = esquema(train)
    xt, xh = matriz(train, schema), matriz(holdout, schema)
    yt, nt = (np.array([f[k] for f in train], dtype=float) for k in ("clics", "impresiones"))
    yh, nh = (np.array([f[k] for f in holdout], dtype=float) for k in ("clics", "impresiones"))
    beta = ajustar_binomial(xt, yt, nt)
    referencias = {}
    for canal in schema["niveles"]["canal"]:
        lote = [f for f in train if f["canal"] == canal]
        n, y = sum(f["impresiones"] for f in lote), sum(f["clics"] for f in lote)
        referencias[canal] = dict(ctr=(y+.5)/(n+1), impresiones=n, clics=y,
            conversiones=sum(f["conversiones"] for f in lote), cvr=sum(f["conversiones"] for f in lote)/y if y else None)
    pred = expit(xh@beta)
    diagnostico = metricas(yh, nh, pred)
    naive = metricas(yh, nh, np.array([referencias[f["canal"]]["ctr"] for f in holdout]))
    motivos = []
    if diagnostico["log_loss"] >= naive["log_loss"]:
        motivos.append("No mejora la referencia por canal en el holdout: utilizar la referencia, sin priorización predictiva.")
    grupos = sorted({f["grupo"] for f in train})
    if len(grupos) < 8:
        motivos.append("Menos de ocho grupos de composición/campaña en entrenamiento.")
    rng = np.random.default_rng(np.random.SeedSequence([semilla, 4101]))
    indices = {g: i for i, g in enumerate(grupos)}
    por_canal = {c: sorted({f["grupo"] for f in train if f["canal"] == c}) for c in referencias}
    replicas = []
    for _ in range(REPLICAS):
        seleccion = [g for c in sorted(por_canal) for g in rng.choice(por_canal[c], len(por_canal[c]), replace=True)]
        repeticiones = np.bincount([indices[g] for g in seleccion], minlength=len(grupos))
        pesos = np.array([repeticiones[indices[f["grupo"]]] for f in train])
        replicas.append(ajustar_binomial(xt, yt, nt, pesos).tolist())
    proyeccion = expit(matriz(holdout, schema)@np.asarray(replicas).T)
    inferior, superior = np.quantile(proyeccion, [.05, .95], axis=1)
    diagnostico["cobertura_tasas_observadas"] = float(np.mean((yh/nh >= inferior) & (yh/nh <= superior)))
    checksum = hashlib.sha256(json.dumps(filas, sort_keys=True).encode()).hexdigest()
    return dict(version=VERSION, semilla=semilla, checksum_datos=checksum,
        estado="bloqueado" if motivos else "limitado", motivos=motivos, schema=schema,
        parametros=beta.tolist(), draws=replicas, replicas=REPLICAS, referencias=referencias,
        train=metricas(yt, nt, expit(xt@beta)), holdout=diagnostico, naive=naive,
        particiones=dict(train_inicio=min(f["fecha"] for f in train), train_fin=max(f["fecha"] for f in train),
            holdout_inicio=min(f["fecha"] for f in holdout), holdout_fin=max(f["fecha"] for f in holdout),
            filas_train=len(train), filas_holdout=len(holdout), filas_excluidas=excluidas,
            grupos_train=grupos, grupos_holdout=sorted({f["grupo"] for f in holdout}),
            campanas_train=sorted({f["campana"] for f in train}), campanas_holdout=sorted({f["campana"] for f in holdout})),
        soporte=[dict(canal=c, categoria=k, tono=t, cta=a, audiencia=u)
                 for c, k, t, a, u in sorted({(f["canal"], f["categoria"], f["tono"], f["cta"], f["audiencia"]) for f in train})],
        metodo="Regresión logística binomial regularizada: clics con denominador impresiones. Ridge fija 10; atributos categoría/tono/CTA tratados como paquete. Bootstrap de composiciones/campañas completas, estratificado por canal.",
        advertencias=["28 días de muestra parcial, pocos grupos y asignación observacional: no identifica causalidad.",
            "Categoría, tono y CTA están ligados; no se estiman efectos independientes de esos atributos.",
            "Las composiciones nuevas no tienen efecto diferencial identificado; su puntuación es referencia del contexto.",
            "Bandas p05–p95 de parámetros por grupos, no intervalos predictivos de nuevos clics ni IC causales; cobertura no garantizada.",
            "CVR se muestra como referencia observada, conversiones por clic; no es una predicción ni pedidos propios.",
            "Multiplicador económico conservado en 1 hasta contar con evidencia compatible."])


def predecir_contexto(modelo, contexto):
    schema = modelo["schema"]
    clave = dict(contexto, paquete=paquete(contexto))
    if any(clave[k] not in schema["niveles"][k] for k in CATEGORICAS):
        raise ValueError("El contexto incluye un paquete o audiencia no observados en entrenamiento.")
    x = matriz([contexto], schema)
    p = float(expit(x@np.asarray(modelo["parametros"]))[0])
    draws = expit(x@np.asarray(modelo["draws"]).T)[0]
    motivos = list(modelo["motivos"])
    if not schema["frecuencia_min"] <= contexto["frecuencia"] <= schema["frecuencia_max"]:
        motivos.append("Frecuencia fuera del rango de entrenamiento: hipótesis de transporte.")
    soporte = {k: contexto[k] for k in ("canal", "categoria", "tono", "cta", "audiencia")}
    if soporte not in modelo["soporte"]:
        motivos.append("Combinación de canal y paquete no observada en train; hipótesis aditiva.")
    if modelo["estado"] == "bloqueado":
        p = modelo["referencias"][contexto["canal"]]["ctr"]
        # No presentar bandas del predictor rechazado como incertidumbre del naive.
        return dict(ctr=p, p05=None, p95=None, motivos=motivos, fuente="Referencia por canal; predictor bloqueado")
    return dict(ctr=p, p05=float(np.quantile(draws, .05)), p95=float(np.quantile(draws, .95)),
                motivos=motivos, fuente="Estimación del contexto observado; sin efecto de composición identificado")
