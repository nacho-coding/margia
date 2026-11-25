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
