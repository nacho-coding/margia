from dataclasses import dataclass
from math import isfinite


def cociente(numerador: float, denominador: float) -> float | None:
    return numerador / denominador if denominador > 0 else None


def contribucion(margen: float, inversion: float, *, creatividad: float = 0,
                 experimento: float = 0, plataforma: float = 0, otros: float = 0) -> float:
    costes = (inversion, creatividad, experimento, plataforma, otros)
    if not isfinite(margen) or any(not isfinite(c) or c < 0 for c in costes):
        raise ValueError("Los importes deben ser finitos y los costes no negativos.")
    return margen - sum(costes)


@dataclass(frozen=True)
class ResultadoRecorte:
    ahorro: float
    pedidos_perdidos: float
    perdida_margen: float
    costes: float
    delta: float
    recuperacion_equilibrio: float | None


def evaluar_recorte(gasto: float, recorte: float, pedidos_afectados: float,
                    recuperacion: float, margen_pedido: float,
                    costes: float = 0) -> ResultadoRecorte:
    """L son pedidos contrafactuales afectados POR el recorte, nunca clics atribuidos.

    Función aritmética; no estima L ni recuperación a partir de correlaciones.
    Los estimadores futuros deberán aportar esas cantidades y su evidencia.
    """
    valores = (gasto, recorte, pedidos_afectados, recuperacion, margen_pedido, costes)
    if any(not isfinite(v) or v < 0 for v in valores):
        raise ValueError("Los parámetros deben ser finitos y no negativos.")
    if not 0 <= recorte <= 1 or not 0 <= recuperacion <= 1:
        raise ValueError("Recorte y recuperación deben estar entre 0 y 1.")
    if recorte == 0 and pedidos_afectados != 0:
        raise ValueError("Sin recorte no puede haber pedidos afectados.")
    ahorro = gasto * recorte
    perdidos = pedidos_afectados * (1 - recuperacion)
    perdida = perdidos * margen_pedido
    base = pedidos_afectados * margen_pedido
    equilibrio = 1 - (ahorro - costes) / base if base > 0 else None
    return ResultadoRecorte(ahorro, perdidos, perdida, costes,
                            ahorro - perdida - costes, equilibrio)


def comparar_plan(pedidos: float, margen: float, inversion: float, delta_pedidos: float,
                  ahorro: float, reinversion: float = 0, *, ventas: float | None = None,
                  creatividad: float = 0, experimento: float = 0, plataforma: float = 0,
                  plataforma_comun: bool = False, otros: float = 0) -> dict:
    """Única valoración de base y alternativa, con captura/demanda ya expresadas en pedidos."""
    valores = (pedidos, margen, inversion, ahorro, reinversion, creatividad, experimento, plataforma, otros)
    if any(not isfinite(v) or v < 0 for v in valores) or not isfinite(delta_pedidos):
        raise ValueError("La evaluación económica requiere importes finitos y no negativos.")
    if ahorro > inversion+1e-6 or pedidos+delta_pedidos < 0 or (pedidos == 0 and margen != 0):
        raise ValueError("El cambio no respeta los límites físicos o de inversión.")
    if ventas is not None and (not isfinite(ventas) or ventas < margen or (pedidos == 0 and ventas != 0)):
        raise ValueError("Ventas y margen deben reconciliarse con los pedidos de referencia.")
    margen_pedido = cociente(margen, pedidos)
    cambio_margen = delta_pedidos*(margen_pedido or 0)
    cuota_base = plataforma if plataforma_comun else 0
    base = dict(pedidos=pedidos, margen=margen, inversion=inversion, plataforma=cuota_base,
                creatividad=0, experimento=0, otros=0,
                contribucion=contribucion(margen, inversion, plataforma=cuota_base))
    alternativa = dict(pedidos=pedidos+delta_pedidos, margen=margen+cambio_margen,
        inversion=inversion-ahorro+reinversion, creatividad=creatividad, plataforma=plataforma,
        experimento=experimento, otros=otros,
        contribucion=contribucion(margen+cambio_margen, inversion-ahorro+reinversion,
                                 creatividad=creatividad, plataforma=plataforma, experimento=experimento, otros=otros))
    if ventas is not None:
        cambio_ventas = delta_pedidos*(cociente(ventas, pedidos) or 0)
        base.update(ventas=ventas, coste_directo=ventas-margen)
        alternativa.update(ventas=ventas+cambio_ventas, coste_directo=ventas+cambio_ventas-margen-cambio_margen)
    costes_incrementales = plataforma-cuota_base+experimento+creatividad+otros
    delta = alternativa["contribucion"]-base["contribucion"]
    return dict(base=base, alternativa=alternativa, ahorro=ahorro, reinversion=reinversion,
        delta_pedidos=delta_pedidos, cambio_margen=cambio_margen, costes_incrementales=costes_incrementales,
        delta=delta, margen_pedido=margen_pedido)


def waterfall(terminos: list[tuple[str, float]], delta: float) -> list[dict]:
    desglose, acumulado = [], 0.0
    for nombre, importe in terminos:
        siguiente = acumulado+importe
        desglose.append(dict(nombre=nombre, importe=importe, offset=min(acumulado, siguiente),
                              altura=abs(importe), favorable=importe >= 0))
        acumulado = siguiente
    desglose.append(dict(nombre="Contribución incremental neta", importe=delta,
                          offset=min(0, delta), altura=abs(delta), favorable=delta >= 0))
    return desglose


def comparar_captura(pedidos: float, margen: float, inversion: float, gasto_marca: float,
                     recorte: float, delta_pedidos: float, plataforma: float = 0,
                     experimento: float = 0, plataforma_comun: bool = False) -> dict:
    """Contrato histórico Search; delega toda la valoración al comparador común."""
    if not isfinite(gasto_marca) or gasto_marca < 0 or not isfinite(recorte) or not 0 <= recorte <= 1 or gasto_marca > inversion+1e-6:
        raise ValueError("El cambio no respeta los límites físicos o de inversión.")
    r = comparar_plan(pedidos, margen, inversion, delta_pedidos, gasto_marca*recorte,
        plataforma=plataforma, experimento=experimento, plataforma_comun=plataforma_comun)
    claves = ("pedidos", "margen", "inversion", "plataforma", "experimento", "contribucion")
    return dict(base={k: r["base"][k] for k in claves}, alternativa={k: r["alternativa"][k] for k in claves},
        **{k: r[k] for k in ("ahorro", "delta_pedidos", "cambio_margen", "costes_incrementales", "delta", "margen_pedido")},
        perdida_maxima_pedidos=cociente(r["ahorro"]-r["costes_incrementales"], r["margen_pedido"] or 0),
        desglose=waterfall([("Ahorro de medios", r["ahorro"]), ("Cambio de margen", r["cambio_margen"]),
            ("Costes incrementales", -r["costes_incrementales"])], r["delta"]))
