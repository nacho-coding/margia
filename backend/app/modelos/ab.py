"""Estimador de conteos aleatorizados. Sin mundo, imágenes ni parámetros verdaderos."""
import hashlib
import json
import math

import numpy as np
from scipy.stats import norm

VERSION_AB = "creatividad-ab-1.0.0"
ALFA = .05
REPLICAS_AB = 200


def wilson(y, n, alfa=ALFA):
    if n <= 0:
        return None
    if not 0 <= y <= n:
        raise ValueError("Conteos binomiales no válidos.")
    z = float(norm.ppf(1-alfa/2))
    p = y/n
    centro = (p+z*z/(2*n))/(1+z*z/n)
    radio = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return [max(0., centro-radio), min(1., centro+radio)]


def diferencia(y_t, n_t, y_c, n_c, comparaciones=1):
    if n_t <= 0 or n_c <= 0 or comparaciones < 1:
        raise ValueError("Faltan denominadores positivos o contrastes predefinidos.")
    pt, pc = y_t/n_t, y_c/n_c
    lt, ut = wilson(y_t, n_t, ALFA/comparaciones)
    lc, uc = wilson(y_c, n_c, ALFA/comparaciones)
    delta = pt-pc
    ic = [max(-1., delta-math.sqrt((pt-lt)**2+(uc-pc)**2)),
          min(1., delta+math.sqrt((ut-pt)**2+(pc-lc)**2))]
    return dict(diferencia=delta, ic95_familiar=ic,
        cambio_relativo=delta/pc if pc else None,
        lectura="Mejora de CTR frente al control" if ic[0] > 0 else
            "Empeora el CTR frente al control" if ic[1] < 0 else "Diferencia no concluyente")


def plan_ab(p_referencia, n, numero_brazos, presupuesto_cent, produccion_cent):
    if not 0 < p_referencia < 1 or n <= 0 or numero_brazos not in (2, 3) or presupuesto_cent < 0 or produccion_cent < 0:
        raise ValueError("Referencia o tamaño de diseño no válidos.")
    k = numero_brazos-1
    mde = (norm.ppf(1-ALFA/(2*k))+norm.ppf(.8))*math.sqrt(2*p_referencia*(1-p_referencia)/n)
    return dict(kpi="CTR: clics por impresión", unidad="Oportunidad sintética independiente, una impresión",
        asignacion="Aleatoria completa y equilibrada dentro de cada fecha",
        brazos=numero_brazos, impresiones_por_brazo=n, impresiones_totales=n*numero_brazos,
        probabilidad=1/numero_brazos, comparaciones=k, alfa_familiar=ALFA,
        ctr_referencia=p_referencia, mde_absoluto=float(mde), mde_relativo=float(mde/p_referencia), potencia_objetivo=.8,
        coste_medios=presupuesto_cent*numero_brazos/100, coste_produccion=produccion_cent/100,
        coste_total=(presupuesto_cent*numero_brazos+produccion_cent)/100,
        advertencias=["MDE normal aproximado al nulo, no garantía de potencia real.",
            "Contrastes preespecificados frente al control; Bonferroni si hay dos comparaciones.",
            "No se modelan usuarios repetidos ni spillover. El IC presupone oportunidades independientes y tasas aproximadamente estables.",
            "CVR es secundario y condicionado a hacer clic; no identifica un efecto causal de conversión entre audiencias seleccionadas.",
            "Los costes se imputan una vez. Más CTR no demuestra más pedidos propios ni beneficio."])


def huella_observaciones(observaciones):
    return hashlib.sha256(json.dumps(sorted(observaciones, key=lambda o: (o["fecha"], o["brazo"])), sort_keys=True).encode()).hexdigest()


def estimar_ab(observaciones, brazos, control, n_previsto, dias, presupuesto_cent, produccion_cent, semilla):
    if control not in brazos or len(set(brazos)) != len(brazos) or len(brazos) not in (2, 3):
        raise ValueError("Brazos no válidos.")
    claves = [(o["fecha"], o["brazo"]) for o in observaciones]
    if len(set(claves)) != len(claves) or any(o["brazo"] not in brazos or not 0 <= o["conversiones"] <= o["clics"] <= o["impresiones"]
        or o["impresiones"] < 0 or o["gasto_cent"] < 0 for o in observaciones):
        raise ValueError("Observaciones duplicadas o conteos no válidos.")
    motivos, filas, draws = [], [], []
    rng = np.random.default_rng(np.random.SeedSequence([semilla, 4205]))
    fechas = {o["fecha"] for o in observaciones}
    if len(fechas) != dias or len(observaciones) != dias*len(brazos):
        motivos.append("Cobertura incompleta de fechas o brazos.")
    for b in brazos:
        lote = [o for o in observaciones if o["brazo"] == b]
        n, y, c, gasto = (sum(o[k] for o in lote) for k in ("impresiones", "clics", "conversiones", "gasto_cent"))
        if n != n_previsto or gasto != presupuesto_cent:
            motivos.append("Exposición o presupuesto distintos del protocolo congelado.")
        if y < 30 or n-y < 30:
            motivos.append("Conteos insuficientes para guardar un modelo experimental de CTR: al menos 30 clics y 30 no clics por brazo.")
        filas.append(dict(id=b, impresiones=n, clics=y, conversiones=c, gasto=gasto/100,
            ctr=y/n if n else None, ic95_ctr=wilson(y, n), cvr=c/y if y else None, ic95_cvr=wilson(c, y)))
        draws.append(rng.beta(y+.5, n-y+.5, size=REPLICAS_AB).tolist())
    ref = next(f for f in filas if f["id"] == control)
    contrastes = []
    for f in filas:
        if f["id"] == control or not f["impresiones"] or not ref["impresiones"]:
            continue
        r = diferencia(f["clics"], f["impresiones"], ref["clics"], ref["impresiones"], len(brazos)-1)
        contrastes.append(dict(variante=f["id"], control=control, **r))
    # Comprobar equilibrio por bloque además de los totales.
    for fecha in fechas:
        bloque = [o for o in observaciones if o["fecha"] == fecha]
        if len({o["impresiones"] for o in bloque}) > 1 or len({o["gasto_cent"] for o in bloque}) > 1:
            motivos.append("Exposición o coste no comparables dentro de la fecha.")
    motivos = sorted(set(motivos))
    checksum = huella_observaciones(observaciones)
    return dict(version=VERSION_AB, control=control, filas=filas, contrastes=contrastes, compatible=not motivos, motivos=motivos,
        metodo="Diferencia de proporciones con IC Newcombe-Wilson sin corrección de continuidad; Bonferroni por contrastes frente al control.",
        confianza_familiar=.95, comparaciones=len(brazos)-1, checksum_observaciones=checksum,
        coste_medios=sum(f["gasto"] for f in filas), coste_produccion=produccion_cent/100,
        coste_total=sum(f["gasto"] for f in filas)+produccion_cent/100,
        replicas=REPLICAS_AB, draws_ctr=draws,
        incertidumbre_modelo="200 draws Beta con prior Jeffreys (0,5; 0,5), condicionados a conteos; no son los IC frecuentistas ni nuevos clics.",
        multiplicador_demanda=1., efecto_economico_identificado=False,
        recomendacion="Puede guardar aprendizaje de CTR, incluso si es nulo o adverso" if not motivos else "Abstención: conservar aprendizaje anterior")
