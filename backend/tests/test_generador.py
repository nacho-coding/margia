from collections import defaultdict

import numpy as np
import pytest

from app.datos.generador import checksum_logico, generar, repartir


def test_reproduccion_exacta_y_semillas(mundo):
    repetido = generar()
    assert mundo.manifiesto == repetido.manifiesto
    assert checksum_logico(mundo.tablas) == mundo.manifiesto["checksum"]
    assert mundo.verdad_evaluacion["captura"]["max_error_masa"] < 1e-12
    assert mundo.verdad_evaluacion["captura"]["min_probabilidad"] >= 0
    assert mundo.verdad_evaluacion["coeficientes_demanda"][0] == 0
    assert "recuperacion" not in mundo.manifiesto
    reordenado = dict(mundo.tablas)
    reordenado["mercado"] = list(reversed(reordenado["mercado"]))
    assert checksum_logico(reordenado) == mundo.manifiesto["checksum"]


def test_integridad_y_fk(mundo):
    t = mundo.tablas
    assert len(t["mercado"]) == 24
    assert len(t["canal"]) == 8
    assert len(t["campana"]) == 120
    assert len(t["creativo"]) == 80
    assert len({c["asset"] for c in t["creativo"]}) == 12
    assert len(t["negocio_diario"]) == 730*24
    mercados = {m["id"] for m in t["mercado"]}
    canales = {c["id"] for c in t["canal"]}
    campanas = {c["id"] for c in t["campana"]}
    for nombre in ("negocio_diario", "medios_diarios", "busqueda_diaria", "creatividad_diaria", "campana_diaria"):
        filas = t[nombre]
        assert all(f["mercado_id"] in mercados for f in filas)
        assert all(mundo.manifiesto["inicio"] <= f["fecha"].isoformat() <= mundo.manifiesto["corte"] for f in filas)
    assert all(f["canal_id"] in canales for f in t["medios_diarios"])
    assert all(f["campana_id"] in campanas for f in t["creativo"])
    categorias = {f["id"]: f["categoria"] for f in t["campana"]}
    assert all(f["atributos"]["categoria"] == categorias[f["campana_id"]] for f in t["creativo"])
    for f in t["negocio_diario"]:
        assert f["margen_cent"] == f["ventas_cent"]-f["coste_cent"]
        assert min(f["pedidos"], f["ventas_cent"], f["coste_cent"]) >= 0
    for nombre in ("medios_diarios", "busqueda_diaria", "creatividad_diaria"):
        for f in t[nombre]:
            if f["clics"] is not None:
                assert 0 <= f["clics"] <= f["impresiones"]
            assert f["gasto_cent"] >= 0


def test_reconciliacion_inversion_vistas_parciales(mundo):
    t = mundo.tablas
    medios = {(f["fecha"], f["mercado_id"], f["canal_id"]): f["gasto_cent"] for f in t["medios_diarios"]}
    assert sum(medios.values()) == 960_000_000
    assert mundo.manifiesto["gasto_bloque_365_eur"] == [4800000, 4800000]
    canales_campana = {f["id"]: f["canal_id"] for f in t["campana"]}
    campanas = defaultdict(int)
    for f in t["campana_diaria"]:
        campanas[f["fecha"], f["mercado_id"], canales_campana[f["campana_id"]]] += f["gasto_cent"]
    assert all(v == medios[k] for k, v in campanas.items())
    elegibles = {f["id"]: f["elegible"] for f in t["grupo_busqueda"]}
    busqueda = defaultdict(int)
    for f in t["busqueda_diaria"]:
        if f["fuente"] == "SEO":
            assert f["gasto_cent"] == 0 and f["conversiones"] is None
        else:
            canal = "sem_marca" if elegibles[f["grupo_id"]] else "sem_generico"
            busqueda[f["fecha"], f["mercado_id"], canal] += f["gasto_cent"]
    assert all(v == medios[k] for k, v in busqueda.items())
    canal_creativo = {f["id"]: canales_campana[f["campana_id"]] for f in t["creativo"]}
    creatividad = defaultdict(int)
    for f in t["creatividad_diaria"]:
        creatividad[f["fecha"], f["mercado_id"], canal_creativo[f["creativo_id"]]] += f["gasto_cent"]
    assert all(v <= medios[k] for k, v in creatividad.items())


def test_reparto_mayor_resto():
    assert repartir(101, np.ones(3)).tolist() == [34, 34, 33]
    assert repartir(0, np.ones(3)).tolist() == [0, 0, 0]
    with pytest.raises(ValueError):
        repartir(10, np.zeros(3))
