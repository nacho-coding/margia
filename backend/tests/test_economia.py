import math

import pytest

from app.dominio.economia import cociente, contribucion, evaluar_recorte


def test_fixture_economica_contractual():
    positivo = evaluar_recorte(60000, .5, 3000, .92, 50, 6000)
    assert positivo.ahorro == 30000
    assert positivo.pedidos_perdidos == pytest.approx(240)
    assert positivo.perdida_margen == pytest.approx(12000)
    assert positivo.delta == pytest.approx(12000)
    assert positivo.recuperacion_equilibrio == pytest.approx(.84)
    assert evaluar_recorte(60000, .5, 3000, .70, 50, 6000).delta == pytest.approx(-21000)


def test_cero_recorte_y_coste_de_contratacion():
    assert evaluar_recorte(60000, 0, 0, .92, 50).delta == 0
    assert evaluar_recorte(60000, 0, 0, .92, 50, 6000).delta == -6000


@pytest.mark.parametrize("recuperacion, esperado", [(0, -4000), (1, 1000)])
def test_extremos(recuperacion, esperado):
    r = evaluar_recorte(1000, 1, 100, recuperacion, 50)
    assert r.delta == esperado
    assert r.delta == pytest.approx(r.ahorro-r.perdida_margen-r.costes)


@pytest.mark.parametrize("parametros", [(-1, .5, 10, .9, 20), (100, 1.01, 10, .9, 20),
                                        (100, .5, 10, 1.1, 20), (100, 0, 10, .9, 20),
                                        (math.nan, .5, 10, .9, 20)])
def test_rechaza_entradas_invalidas(parametros):
    with pytest.raises(ValueError):
        evaluar_recorte(*parametros)


def test_contribucion_no_duplica_ahorro_y_costes():
    base = contribucion(10000, 2000, plataforma=100)
    alternativa = contribucion(9500, 1000, plataforma=100, experimento=50)
    assert alternativa-base == 450
    assert cociente(10, 0) is None
    assert evaluar_recorte(0, 0, 0, 1, 0).recuperacion_equilibrio is None
