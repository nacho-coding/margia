"""Mecanismo del mundo sintético; nunca se importa desde estimadores."""


def estructura_mercados(rng):
    tamanos = rng.uniform(.65, 1.4, 24)
    tamanos /= tamanos.mean()
    return tamanos, rng.uniform(.50, .95, 24)


def probabilidades_captura(gasto, escala, recuperacion):
    paid = .43 * (gasto / (gasto + escala))
    organic = (.33 + recuperacion*.20) * (1-paid)
    direct = .19*(1-paid)
    return paid, organic, direct, 1-paid-organic-direct


def factor_pedidos(gasto, escala, recuperacion):
    paid, organic, direct, _ = probabilidades_captura(gasto, escala, recuperacion)
    return .70 + .30*(paid+organic+direct)
