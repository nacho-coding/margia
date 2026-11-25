"""Nueva rama sintética condicionada al snapshot; únicamente el mundo conoce captura."""
import numpy as np

from app.datos.captura import estructura_mercados, factor_pedidos


def ejecutar_mundo_geo(series, asignaciones, dias, recorte, semilla, semilla_mundo, mercados_mundo, escala_cent):
    _, recuperacion = estructura_mercados(np.random.default_rng(np.random.SeedSequence(semilla_mundo).spawn(5)[0]))
    obs = []
    ruido_comun = np.random.default_rng(np.random.SeedSequence([semilla, 3202])).normal(0, .015, dias)
    for a in asignaciones:
        mid = a["mercado"]
        i = mercados_mundo.index(mid)
        rng = np.random.default_rng(np.random.SeedSequence([semilla, 3203, i]))
        s = series[mid]
        obs.append(dict(mercado=mid, periodo="pre", pedidos=sum(s["pedidos"]),
                        gasto_cent=sum(s["gasto"]), presupuesto_cent=sum(s["gasto"])))
        pedidos, gasto, presupuesto = 0, 0, 0
        for d in range(dias):
            j = -28+d % 28
            base = s["gasto"][j]
            invertido = round(base*(1-recorte)) if a["brazo"] == "tratamiento" else base
            ratio = factor_pedidos(invertido, escala_cent, recuperacion[i])/factor_pedidos(base, escala_cent, recuperacion[i])
            media = s["pedidos"][j]*ratio*np.exp(ruido_comun[d]+rng.normal(0, .01))
            pedidos += int(rng.poisson(media))
            gasto += invertido
            presupuesto += base
        obs.append(dict(mercado=mid, periodo="post", pedidos=pedidos,
                        gasto_cent=gasto, presupuesto_cent=presupuesto))
    return obs
