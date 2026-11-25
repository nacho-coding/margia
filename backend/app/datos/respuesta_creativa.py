"""Mecanismo compartido de respuesta creativa del mundo; ajeno al estimador."""
CVR = .035


def promocion(fecha):
    return fecha.month == 11 and fecha.day >= 20 or fecha.month == 6 and fecha.day <= 12


def ctr_base(indice_categoria, en_promocion):
    return .012 + .002*(indice_categoria % 3-1) + .0015*en_promocion
