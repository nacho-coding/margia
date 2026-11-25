"""MMM nacional de pedidos; asociación predictiva, no identificación causal.

No importa el generador ni lee su verdad. Selección rolling antes del holdout;
escalas, soportes, residuos y bootstrap se aprenden exclusivamente en train.
"""
import hashlib
import itertools
import json
from dataclasses import asdict, dataclass
from datetime import date

import numpy as np
from scipy.optimize import lsq_linear

VERSION = "mmm-1.0.1"
CONTROLES = ["intercepto", "tendencia", "seno_anual", "coseno_anual",
             "seno_semestral", "coseno_semestral", "promocion"]


@dataclass(frozen=True)
class Configuracion:
    holdout: int = 20
    validacion: int = 12
    lambdas: tuple[float, ...] = (0.0, 0.3, 0.6)
    semisaturaciones: tuple[float, ...] = (0.5, 1.5)
    penalizaciones: tuple[float, ...] = (0.01, 1.0)
    replicas: int = 80
    bloque: int = 4
    max_correlacion: float = 0.98
    max_condicion: float = 100_000.0
    min_variacion: float = 0.02
    max_sensibilidad: float = 1.0


def adstock(gasto: np.ndarray, persistencia: float) -> np.ndarray:
    x = np.asarray(gasto, dtype=float)
    if not 0 <= persistencia <= 0.9 or x.ndim not in (1, 2) or not np.isfinite(x).all() or np.any(x < 0):
        raise ValueError("Adstock requiere gasto finito no negativo y persistencia entre 0 y 0,9.")
    resultado = np.zeros_like(x)
    stock = np.zeros_like(x[0]) if len(x) else 0.0
    for i, valor in enumerate(x):
        stock = valor + persistencia * stock
        resultado[i] = stock
    return resultado


def hill(stock: np.ndarray, k: float) -> np.ndarray:
    x = np.asarray(stock, dtype=float)
    if k <= 0 or not np.isfinite(k) or not np.isfinite(x).all() or np.any(x < 0):
        raise ValueError("Hill requiere stock no negativo y semisaturación positiva.")
    # Pendiente s=1 fijada para reducir grados de libertad.
    return x / (x + k)


def metricas(observado: np.ndarray, predicho: np.ndarray) -> dict:
    y, p = np.asarray(observado), np.asarray(predicho)
    error = p - y
    denominador = float(np.abs(y).sum())
    return dict(mae=float(np.abs(error).mean()),
                wape=float(np.abs(error).sum()/denominador) if denominador else None,
                sesgo=float(error.sum()/denominador) if denominador else None)


def _diseno(fechas, gasto, promocion, fin_train, persistencia, k):
    escala = np.mean(gasto[:fin_train], axis=0)
    if np.any(escala <= 0):
        raise ValueError("No hay gasto de entrenamiento suficiente en todos los canales.")
    stock = adstock(gasto / escala, persistencia)
    t = np.arange(len(fechas), dtype=float)
    tendencia = (t - (fin_train-1)/2) / fin_train
    dias = np.array([(date.fromisoformat(f)-date(2000, 1, 1)).days for f in fechas])
    fase = 2*np.pi*dias/365.25
    controles = np.column_stack([np.ones(len(t)), tendencia, np.sin(fase), np.cos(fase),
                                 np.sin(2*fase), np.cos(2*fase), promocion])
    return np.column_stack([controles, hill(stock, k)]), escala, stock


def _ajustar(x, y, penalizacion):
    escala_y = float(np.mean(y))
    if escala_y <= 0:
        raise ValueError("No hay pedidos suficientes para ajustar el modelo.")
    # Intercepto sin penalizar; controles suavemente regularizados; medios positivos.
    pesos = np.array([0.0] + [0.05]*(len(CONTROLES)-1) + [1.0]*(x.shape[1]-len(CONTROLES)))
    matriz = np.vstack([x, np.diag(np.sqrt(penalizacion*pesos))])
    objetivo = np.r_[y/escala_y, np.zeros(x.shape[1])]
    inferior = np.r_[0.0, np.full(len(CONTROLES)-1, -np.inf),
                     np.zeros(x.shape[1]-len(CONTROLES))]
    fit = lsq_linear(matriz, objetivo, bounds=(inferior, np.inf), method="bvls", tol=1e-10)
    if not fit.success:
        raise ValueError("El ajuste restringido no ha convergido.")
    return fit.x * escala_y


def _bloques(residuos, longitud, bloque, rng):
    # Bootstrap circular de residuos centrados; conserva dependencia local temporal.
    inicios = rng.integers(0, len(residuos), size=int(np.ceil(longitud/bloque)))
    indices = (inicios[:, None]+np.arange(bloque)) % len(residuos)
    return residuos[indices.ravel()[:longitud]]


def politica(diagnostico: dict, config: Configuracion) -> list[str]:
    motivos = []
    if diagnostico["holdout"]["wape"] is None or diagnostico["holdout"]["wape"] >= diagnostico["naive"]["wape"]:
        motivos.append("El MMM no mejora la referencia estacional en holdout.")
    if diagnostico["correlacion_maxima"] >= config.max_correlacion:
        motivos.append("Colinealidad de medios por encima del umbral.")
    if diagnostico["condicion"] is None or diagnostico["condicion"] > config.max_condicion:
        motivos.append("Matriz de diseño inestable.")
    if diagnostico["variacion_minima"] < config.min_variacion:
        motivos.append("Variación de inversión insuficiente en algún canal.")
    if diagnostico["sensibilidad"] > config.max_sensibilidad:
        motivos.append("Las contribuciones son sensibles a configuraciones con validación similar.")
    if diagnostico["prediccion_no_positiva"]:
        motivos.append("Predicción o baseline no positivos; no interpretar las curvas.")
    return motivos


def entrenar(semanas: list[dict], canales: list[dict], semilla: int,
             config: Configuracion = Configuracion()) -> dict:
    """Ajuste determinista; las semanas deben ser completas, nacionales y ordenadas."""
    if len(semanas) < 100 or config.holdout not in range(16, 21) or config.replicas < 20:
        raise ValueError("MMM requiere al menos 100 semanas, 16–20 de holdout y 20 réplicas.")
    if any(c["id"] == "sem_marca" or c["tipo"] != "demanda" for c in canales):
        raise ValueError("SEM marca es captura y queda excluida de los efectos de demanda.")
    fechas = [s["fin"] for s in semanas]
    if any((date.fromisoformat(b)-date.fromisoformat(a)).days != 7 for a, b in itertools.pairwise(fechas)):
        raise ValueError("Las semanas de modelado deben ser consecutivas y completas.")
    gasto = np.array([[s["gasto"][c["id"]] for c in canales] for s in semanas], dtype=float)
    y = np.array([s["pedidos"] for s in semanas], dtype=float)
    promo = np.array([s["promocion"] for s in semanas], dtype=float)
    if not np.isfinite(gasto).all() or not np.isfinite(y).all() or np.any(gasto < 0) or np.any(y < 0):
        raise ValueError("Observaciones no válidas para el MMM.")
    n_train = len(y)-config.holdout
    folds = [n_train-2*config.validacion, n_train-config.validacion]
    if min(folds) < 52:
        raise ValueError("No hay preperiodo anual suficiente para validación rolling.")
    candidatos = []
    for persistencia, k, penalizacion in itertools.product(config.lambdas, config.semisaturaciones, config.penalizaciones):
        errores = []
        for fin in folds:
            x, _, _ = _diseno(fechas, gasto, promo, fin, persistencia, k)
            beta = _ajustar(x[:fin], y[:fin], penalizacion)
            errores.append(metricas(y[fin:fin+config.validacion], x[fin:fin+config.validacion] @ beta)["wape"])
        candidatos.append(dict(persistencia=persistencia, k=k, penalizacion=penalizacion,
                               wape=float(np.mean(errores)), folds=errores))
    elegido = min(candidatos, key=lambda c: c["wape"])
    persistencia, k, penalizacion = (elegido[n] for n in ("persistencia", "k", "penalizacion"))
    x, escala, stock = _diseno(fechas, gasto, promo, n_train, persistencia, k)
    beta = _ajustar(x[:n_train], y[:n_train], penalizacion)
    pred = x @ beta
    baseline = x[:, :len(CONTROLES)] @ beta[:len(CONTROLES)]
    componentes = x[:, len(CONTROLES):] * beta[len(CONTROLES):]
    residuos = y[:n_train]-pred[:n_train]
    centrados = residuos-residuos.mean()
    rng = np.random.default_rng(np.random.SeedSequence([semilla, 202]))
    refits = np.array([_ajustar(x[:n_train], pred[:n_train]+_bloques(centrados, n_train, config.bloque, rng), penalizacion)
                       for _ in range(config.replicas)])
    # Reajustar una señal ya regularizada vuelve a contraer sus coeficientes.
    # Centrar los errores de refit evita confundir esa segunda contracción con
    # incertidumbre alrededor del ajuste. Respetar el soporte no negativo.
    betas = beta + refits-refits.mean(axis=0)
    betas[:, len(CONTROLES):] = np.maximum(betas[:, len(CONTROLES):], 0)
    draws_media = betas @ x.T
    draws_predictivos = draws_media + np.array([_bloques(centrados, len(y), config.bloque, rng)
                                                for _ in range(config.replicas)])
    inferior, superior = np.quantile(draws_predictivos, [.05, .95], axis=0)
    naive = y[np.arange(n_train, len(y))-52]
    correlaciones = np.corrcoef(x[:n_train, len(CONTROLES):], rowvar=False)
    corr = float(np.max(np.abs(correlaciones-np.eye(len(canales)))))
    normalizado = x[:n_train, 1:]
    desviaciones = normalizado.std(axis=0)
    condicion = float(np.linalg.cond((normalizado-normalizado.mean(axis=0))/np.maximum(desviaciones, 1e-12)))
    # Sensibilidad de masa por canal entre modelos casi empatados en rolling.
    masas = []
    for candidato in candidatos:
        if candidato["wape"] <= elegido["wape"]*1.10 + 1e-12:
            matriz, _, _ = _diseno(fechas, gasto, promo, n_train, candidato["persistencia"], candidato["k"])
            coef = _ajustar(matriz[:n_train], y[:n_train], candidato["penalizacion"])
            masas.append(np.sum(matriz[:n_train, len(CONTROLES):]*coef[len(CONTROLES):], axis=0))
    masas = np.array(masas)
    sensibilidad = float(np.max(np.ptp(masas, axis=0)/np.maximum(np.mean(masas, axis=0), y[:n_train].sum()*.01)))
    diagnostico = dict(train=metricas(y[:n_train], pred[:n_train]),
                       holdout=metricas(y[n_train:], pred[n_train:]), naive=metricas(y[n_train:], naive),
                       autocorrelacion_lag1=float(np.corrcoef(residuos[:-1], residuos[1:])[0, 1]) if np.std(residuos) > 1e-10 else None,
                       correlacion_maxima=corr if np.isfinite(corr) else 1.0,
                       condicion=condicion if np.isfinite(condicion) else None,
                       variacion_minima=float(np.min(gasto[:n_train].std(axis=0)/escala)),
                       sensibilidad=sensibilidad,
                       cobertura_banda_holdout=float(np.mean((y[n_train:] >= inferior[n_train:]) & (y[n_train:] <= superior[n_train:]))),
                       prediccion_no_positiva=bool(np.any(pred <= 0) or np.any(baseline <= 0)),
                       umbrales=asdict(config), candidatos=candidatos)
    motivos = politica(diagnostico, config)
    serie = []
    for i, s in enumerate(semanas):
        serie.append(dict(inicio=s["inicio"], fin=s["fin"], observado=float(y[i]),
                          predicho=float(pred[i]), baseline=float(baseline[i]),
                          efectos=float(componentes[i].sum()), residual=float(y[i]-pred[i]),
                          componentes={c["id"]: float(componentes[i, j]) for j, c in enumerate(canales)},
                          p05=float(inferior[i]), p95=float(superior[i]),
                          ancho_banda=float(superior[i]-inferior[i]),
                          naive=float(y[i-52]) if i >= 52 else None,
                          particion="holdout" if i >= n_train else "train",
                          margen_por_pedido=s["margen"]/y[i] if y[i] else None,
                          gasto=s["gasto"]))
    curvas = []
    for j, canal in enumerate(canales):
        minimo, maximo = float(gasto[:n_train, j].min()), float(gasto[:n_train, j].max())
        referencia = float(gasto[-1, j])
        previo = float(stock[-2, j])
        puntos = []
        for euros in sorted(set(np.linspace(0, maximo*1.3, 31).tolist()+[minimo, maximo, referencia])):
            a = euros/escala[j] + persistencia*previo
            h = float(hill(a, k))
            valor = float(beta[len(CONTROLES)+j]*h)
            p05, p95 = np.quantile(betas[:, len(CONTROLES)+j]*h, [.05, .95])
            puntos.append(dict(inversion=float(euros), pedidos=valor, p05=float(p05), p95=float(p95),
                               ancho_banda=float(p95-p05), marginal=float(beta[len(CONTROLES)+j]*k/(a+k)**2/escala[j]),
                               extrapolado=bool(euros < minimo or euros > maximo)))
        curvas.append(dict(**canal, minimo=minimo, maximo=maximo, referencia=referencia,
                           stock_previo_normalizado=previo, horizonte_dias=7, puntos=puntos))
    payload = dict(version=VERSION, semilla=semilla, configuracion=asdict(config),
                   checksum_datos=hashlib.sha256(json.dumps(semanas, sort_keys=True).encode()).hexdigest())
    identidad = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return dict(id=f"mmm-{identidad[:20]}", **payload, estado="bloqueado" if motivos else "limitado",
                optimizable=False, motivos=motivos,
                ambito="Nacional · todos los mercados", objetivo="Pedidos propios por semana", unidad="pedidos",
                semanas=len(y), train_inicio=semanas[0]["inicio"], train_fin=semanas[n_train-1]["fin"],
                holdout_inicio=semanas[n_train]["inicio"], holdout_fin=semanas[-1]["fin"],
                folds=[dict(train_fin=semanas[f-1]["fin"], validacion_inicio=semanas[f]["inicio"],
                            validacion_fin=semanas[f+config.validacion-1]["fin"]) for f in folds],
                diagnostico=diagnostico, parametros=dict(**elegido, pendiente_hill=1,
                    controles=CONTROLES, canales=[c["id"] for c in canales], escala_gasto=escala.tolist(),
                    coeficientes=beta.tolist(), bootstrap_coeficientes=betas.tolist()),
                incertidumbre=f"Banda de escenarios predictivos p05–p95: {config.replicas} refits de residuos en bloques de {config.bloque} semanas. Errores de refit centrados en el ajuste para corregir la segunda contracción de ridge, con coeficientes de medios truncados a cero; se añade ruido residual de train. Condicional a la forma elegida, sin garantía de cobertura ni interpretación causal.",
                advertencias=["Modelo observacional nacional: las contribuciones son asociaciones condicionadas a controles, no efectos causales identificados.",
                              "SEM marca se excluye como generador de demanda; su captura corresponde a One Search.",
                              "La banda de las curvas usa refits centrados y truncados, con forma fija; no es un IC calibrado ni cubre selección, endogeneidad o cambios estructurales.",
                              "La optimización permanece deshabilitada hasta calibrar la evidencia y conectar el orquestador.",
                              "Stock inicial cero y agregación semanal; no reproduce el mecanismo diario ni todas sus interacciones."],
                serie=serie, curvas=curvas)
