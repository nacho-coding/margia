"""Estimación por pares observados. Sin leer el mecanismo ni la verdad del mundo."""
import hashlib
import json

import numpy as np
from scipy.stats import t

VERSION = "search-1.0.0"
REPLICAS = 400


def ajustar_search(filas: list[dict], semilla: int) -> dict:
    if not filas:
        raise ValueError("Faltan observaciones experimentales de marca.")
    pares = sorted({f["par"] for f in filas})
    cortes = sorted({f["recorte"] for f in filas if f["recorte"] > 0})
    if len(pares) < 8 or len(cortes) < 2:
        raise ValueError("Evidencia insuficiente: al menos ocho pares y dos intensidades.")
    deltas = np.zeros((len(pares), len(cortes)))
    ahorros = np.zeros_like(deltas)
    placebos = {p: [] for p in pares}
    unidades = {}
    for f in filas:
        if f["pre_t"] <= 0 or f["pre_c"] <= 0 or f["post_t"] < 0 or f["post_c"] < 0:
            raise ValueError("Preperiodo insuficiente o pedidos no válidos.")
        key = (f["experimento"], f["par"])
        if key in unidades:
            raise ValueError("Duplicado de unidad experimental.")
        unidades[key] = True
        delta = f["post_t"] - f["pre_t"]*f["post_c"]/f["pre_c"]
        if f["recorte"] == 0:
            placebos[f["par"]].append(delta)
            continue
        if f["ahorro"] <= 0:
            raise ValueError("No hay contraste de inversión positivo.")
        i, j = pares.index(f["par"]), cortes.index(f["recorte"])
        deltas[i, j] += delta
        ahorros[i, j] += f["ahorro"]
    if np.any(ahorros <= 0) or any(not v for v in placebos.values()):
        raise ValueError("Cobertura incompleta de intensidades o placebos por par.")
    tasas = deltas.sum(axis=0)/ahorros.sum(axis=0)
    rng = np.random.default_rng(np.random.SeedSequence([semilla, 3101]))
    indices = rng.integers(0, len(pares), size=(REPLICAS, len(pares)))
    draws = deltas[indices].sum(axis=1)/ahorros[indices].sum(axis=1)
    placebo = np.array([np.mean(placebos[p]) for p in pares])
    sem = float(placebo.std(ddof=1)/np.sqrt(len(pares)))
    margen = float(t.ppf(.975, len(pares)-1)*sem)
    placebo_ic = [float(placebo.mean()-margen), float(placebo.mean()+margen)]
    motivos = [] if placebo_ic[0] <= 0 <= placebo_ic[1] else ["El placebo no es compatible con cero; revisar equilibrio y pretrends."]
    estratos = []
    for estrato in sorted({f["estrato"] for f in filas}):
        ids = sorted({f["par"] for f in filas if f["estrato"] == estrato})
        idx = [pares.index(p) for p in ids]
        estratos.append(dict(id=estrato, pares=len(ids), pooling="Nacional: muestra por estrato insuficiente para recomendar",
            tasas=(deltas[idx].sum(axis=0)/ahorros[idx].sum(axis=0)).tolist()))
    checksum = hashlib.sha256(json.dumps(filas, sort_keys=True).encode()).hexdigest()
    return dict(version=VERSION, semilla=semilla, checksum_datos=checksum,
        estado="bloqueado" if motivos else "limitado", motivos=motivos,
        unidad="Cambio de pedidos propios por euro ahorrado", recuperacion=None,
        metodo="Diferencia post por par, normalizada por ratio pre; ratio de sumas de pedidos y ahorro. Bootstrap por par completo, conservando intensidades y mercados repetidos.",
        pares=len(pares), experimentos=len({f["experimento"] for f in filas}), replicas=REPLICAS,
        soporte=cortes, tasas=tasas.tolist(), draws=draws.tolist(), estratos=estratos,
        placebo=dict(efecto=float(placebo.mean()), ic95=placebo_ic, pares=len(pares)),
        intervalos=[dict(recorte=c, tasa=float(tasas[j]), p05=float(np.quantile(draws[:, j], .05)),
                        p95=float(np.quantile(draws[:, j], .95))) for j, c in enumerate(cortes)],
        advertencias=["Históricos sintéticos de arranque, no experimentos nuevos ejecutados por el usuario.",
            "El tratamiento afecta SEM marca completo: no identifica efectos por consulta ni separa SEO de directo.",
            "No se identifica recuperación ni pedidos pagados afectados; se estima directamente el cambio total de pedidos por euro.",
            "Pooling nacional; aplicar a un mercado es una hipótesis de transferencia, sin recomendación automática.",
            f"Bandas bootstrap por {len(pares)} pares; pocos conglomerados, sin garantía nominal ni incertidumbre completa de transporte.",
            "Supone ausencia de spillover, comparabilidad temporal y estabilidad del efecto por euro en el horizonte de 28 días."])


def respuesta_recorte(modelo: dict, recorte: float):
    if not np.isfinite(recorte) or not 0 <= recorte <= 1:
        raise ValueError("El recorte debe estar entre 0 y 1.")
    if recorte == 0:
        return 0.0, np.zeros(modelo["replicas"])
    # Interpolación entre intervenciones observadas. Fuera del soporte se usa el
    # extremo más próximo solo como hipótesis, nunca se habilita recomendación.
    tasa = float(np.interp(recorte, modelo["soporte"], modelo["tasas"]))
    draws = np.array([np.interp(recorte, modelo["soporte"], d) for d in modelo["draws"]])
    return tasa, draws
