"""Diseño y estimación geo: solo observaciones, nunca verdad ni futuro del generador."""
import numpy as np
from scipy.stats import norm, t

VERSION = "geo-1.0.1"
VERSION_SEARCH_GEO = "search-geo-1.0.0"


def intervalo_pares(diferencias):
    d = np.asarray(diferencias, dtype=float)
    if len(d) < 2 or not np.all(np.isfinite(d)):
        raise ValueError("Se necesitan al menos dos pares completos y finitos.")
    total = float(d.sum())
    se = float(np.sqrt(len(d))*d.std(ddof=1))
    ancho = float(t.ppf(.975, len(d)-1)*se)
    return dict(efecto=total, se=se, ic95=[total-ancho, total+ancho])


def disenar_geo(series: dict, semilla: int, dias: int, recorte: float):
    ids = sorted(series)
    if len(ids) < 8 or len(ids) % 2:
        raise ValueError("Selecciona un número par de mercados, entre 8 y 24.")
    x = np.array([series[mid]["pedidos"] for mid in ids], dtype=float)
    if x.ndim != 2 or x.shape[1] < 28 or np.any(x <= 0):
        raise ValueError("Falta un preperiodo completo de al menos 28 días con pedidos positivos.")
    mitad = x.shape[1]//2
    primero, ultimo = x[:, :mitad].sum(axis=1), x[:, mitad:].sum(axis=1)
    features = np.column_stack((np.log(x.sum(axis=1)), ultimo/primero-1, x.std(axis=1)/x.mean(axis=1)))
    features = (features-features.mean(axis=0))/np.maximum(features.std(axis=0), 1e-8)
    pendientes = list(range(len(ids)))
    rng = np.random.default_rng(np.random.SeedSequence([semilla, 3201]))
    asignaciones, diferencias, escalas, ruido = [], [], [], []
    while pendientes:
        a = pendientes.pop(0)
        b = min(pendientes, key=lambda j: (float(np.linalg.norm(features[a]-features[j])), ids[j]))
        pendientes.remove(b)
        tratado, control = (a, b) if rng.integers(0, 2) else (b, a)
        par = f"geo-par-{len(diferencias)+1:02}"
        for i, brazo in ((tratado, "tratamiento"), (control, "control")):
            asignaciones.append(dict(mercado=ids[i], par=par, brazo=brazo, probabilidad=.5,
                pre_pedidos=int(x[i].sum()), primera_mitad=int(primero[i]), segunda_mitad=int(ultimo[i]),
                tendencia=float(ultimo[i]/primero[i]-1), variabilidad=float(x[i].std()/x[i].mean())))
        ratio = primero[tratado]/primero[control]
        diferencia = ultimo[tratado]-ratio*ultimo[control]
        diferencias.append(float(diferencia))
        escalas.append(float(ultimo[tratado]))
        ruido.append(float(ultimo[tratado]+ratio**2*ultimo[control]))
    placebo = intervalo_pares(diferencias)
    # Variación entre pares, con suelo Poisson para no prometer potencia infinita.
    se_pre = max(placebo["se"], float(np.sqrt(sum(ruido))))
    se_post = se_pre*np.sqrt(dias/(x.shape[1]-mitad))
    critico = float(t.ppf(.975, len(diferencias)-1)+norm.ppf(.8))
    mde = critico*se_post
    pedidos_t = sum(a["pre_pedidos"] for a in asignaciones if a["brazo"] == "tratamiento")*dias/x.shape[1]
    presupuesto_t = sum(sum(series[a["mercado"]]["gasto"][-28:])/100*dias/28
                        for a in asignaciones if a["brazo"] == "tratamiento")
    ahorro = presupuesto_t*recorte
    max_tendencia = max(abs(asignaciones[i]["tendencia"]-asignaciones[i+1]["tendencia"])
                        for i in range(0, len(asignaciones), 2))
    return dict(version=VERSION, asignaciones=asignaciones, pares=len(diferencias),
        placebo=placebo, max_diferencia_tendencia=max_tendencia,
        mde_pedidos=float(mde), mde_relativo=float(mde/pedidos_t),
        se_pedidos_previsto=float(se_post), se_tasa_prevista=float(se_post/ahorro) if ahorro > 0 else None,
        pedidos_tratados_previstos=float(pedidos_t), presupuesto_tratado=presupuesto_t,
        ahorro_tratado=ahorro, alfa=.05, potencia_objetivo=.8,
        metodo="Parejas por volumen, tendencia y variabilidad del preperiodo; distancia euclídea estandarizada, emparejamiento voraz determinista. Aleatorización 0,5 dentro de par.")


def estimar_geo(asignaciones: list[dict], observaciones: list[dict], pre_dias: int, post_dias: int):
    obs = {(o["mercado"], o["periodo"]): o for o in observaciones}
    if len(obs) != len(observaciones) or len(obs) != len(asignaciones)*2:
        raise ValueError("Observaciones duplicadas o incompletas: hacen falta pre y post por mercado.")
    pares, diferencias, ahorros = [], [], []
    total_cf = 0.0
    for par in sorted({a["par"] for a in asignaciones}):
        miembros = [a for a in asignaciones if a["par"] == par]
        if len(miembros) != 2 or {a["brazo"] for a in miembros} != {"tratamiento", "control"}:
            raise ValueError("Cada par requiere un control y un tratamiento.")
        mt = next(a["mercado"] for a in miembros if a["brazo"] == "tratamiento")
        mc = next(a["mercado"] for a in miembros if a["brazo"] == "control")
        pt, pc = obs[(mt, "pre")]["pedidos"], obs[(mc, "pre")]["pedidos"]
        yt, yc = obs[(mt, "post")]["pedidos"], obs[(mc, "post")]["pedidos"]
        if min(pt, pc) <= 0 or min(yt, yc) < 0:
            raise ValueError("Los pedidos pre deben ser positivos y los post no negativos.")
        cf = pt*yc/pc
        delta = yt-cf
        ahorro = (obs[(mt, "post")]["presupuesto_cent"]-obs[(mt, "post")]["gasto_cent"])/100
        diferencias.append(delta)
        ahorros.append(ahorro)
        total_cf += cf
        pares.append(dict(par=par, tratamiento=mt, control=mc, pre_tratamiento=pt,
            pre_control=pc, post_tratamiento=yt, post_control=yc,
            contrafactual_estimado=cf, delta_pedidos=delta, ahorro=ahorro,
            pre_tratamiento_equivalente=pt*post_dias/pre_dias,
            pre_control_equivalente=pc*post_dias/pre_dias))
    resultado = intervalo_pares(diferencias)
    ahorro = float(sum(ahorros))
    tasa = resultado["efecto"]/ahorro if ahorro > 0 else None
    # Error del ratio de sumas por linealización, conservando el par como unidad.
    residuos = np.array(diferencias)-(tasa or 0)*np.array(ahorros)
    se_tasa = float(np.sqrt(len(pares)/(len(pares)-1)*np.sum(residuos**2))/ahorro) if ahorro > 0 else None
    ancho = float(t.ppf(.975, len(pares)-1)*(se_tasa or 0))
    return dict(**resultado, pares=pares, numero_pares=len(pares), ahorro=ahorro,
        tasa=tasa, se_tasa=se_tasa, tasa_ic95=[tasa-ancho, tasa+ancho] if tasa is not None else None,
        contrafactual_tratado=total_cf, efecto_relativo=resultado["efecto"]/total_cf if total_cf else None,
        metodo="Diferencia de pedidos post por par normalizada por ratio pre. IC t de la suma de diferencias, df = pares − 1. Tasa por euro: ratio de sumas con error linealizado por par.",
        advertencias=["Contrafactual estimado desde control; no es la verdad latente del simulador.",
            "IC aproximado: pocos pares, heterogeneidad y supuestos de tendencias paralelas y ausencia de spillover.",
            "La prueba usa pedidos propios; no separa recuperación SEO/directo ni efectos por consulta."])
