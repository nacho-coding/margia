import ast
import copy
from datetime import date
from pathlib import Path

import numpy as np
import pytest
from sqlalchemy import func, select

from app.api.consultas import snapshot_actual
from app.modelos.mmm import VERSION, Configuracion, adstock, entrenar, hill, metricas, politica
from app.modelos.servicio import asegurar_modelo, semanas_observadas
from app.persistencia.tablas import Modelo, NegocioDiario


@pytest.fixture(scope="module")
def observaciones():
    from app.persistencia.db import SessionLocal
    with SessionLocal() as db:
        return semanas_observadas(db, snapshot_actual(db))


@pytest.fixture(scope="module")
def ajuste(observaciones):
    semanas, canales = observaciones
    return entrenar(semanas, canales, 260725)


def test_adstock_hill_limites_y_derivada():
    assert adstock(np.array([10., 0., 0.]), .5).tolist() == [10, 5, 2.5]
    assert adstock(np.ones(500), .9)[-1] == pytest.approx(10)
    x = np.linspace(0, 20, 100)
    assert np.all((hill(x, 2) >= 0) & (hill(x, 2) <= 1))
    assert np.all(np.diff(hill(x, 2)) >= 0)
    assert (hill(3.0001, 2)-hill(2.9999, 2))/.0002 == pytest.approx(2/25)
    for gasto, persistencia in [(np.array([-1]), .5), (np.array([np.nan]), .5), (np.ones(2), 1)]:
        with pytest.raises(ValueError):
            adstock(gasto, persistencia)
    with pytest.raises(ValueError):
        hill(x, 0)
    assert metricas(np.zeros(3), np.ones(3))["wape"] is None


def test_semanas_nacionales_completas_sin_multiplicar_pedidos(observaciones, db):
    semanas, canales = observaciones
    assert len(semanas) == 104
    assert len(canales) == 7
    assert all(c["id"] != "sem_marca" for c in canales)
    total = db.scalar(select(func.sum(NegocioDiario.pedidos)).where(
        NegocioDiario.snapshot_id == snapshot_actual(db).id,
        NegocioDiario.fecha >= date.fromisoformat(semanas[0]["inicio"])))
    assert sum(s["pedidos"] for s in semanas) == total
    assert semanas[-1]["fin"] == snapshot_actual(db).corte.isoformat()


def test_reconciliacion_bandas_curvas_y_reproducibilidad(ajuste, observaciones):
    assert ajuste == entrenar(*observaciones, 260725)
    assert ajuste["train_fin"] < ajuste["holdout_inicio"]
    assert sum(s["particion"] == "holdout" for s in ajuste["serie"]) == 20
    for fold in ajuste["folds"]:
        assert fold["train_fin"] < fold["validacion_inicio"] <= fold["validacion_fin"] < ajuste["holdout_inicio"]
    for s in ajuste["serie"]:
        assert s["baseline"]+sum(s["componentes"].values()) == pytest.approx(s["predicho"])
        assert s["predicho"]+s["residual"] == pytest.approx(s["observado"])
        assert "sem_marca" not in s["componentes"]
        assert s["p95"] > s["p05"]
    for curva in ajuste["curvas"]:
        assert any(p["extrapolado"] for p in curva["puntos"])
        assert any(not p["extrapolado"] for p in curva["puntos"])
        assert all(p["p05"] <= p["p95"] and p["marginal"] >= 0 for p in curva["puntos"])
        assert np.all(np.diff([p["pedidos"] for p in curva["puntos"]]) >= -1e-9)
    assert ajuste["estado"] in ("limitado", "bloqueado")
    assert ajuste["optimizable"] is False


def test_holdout_no_interviene_en_seleccion_escalado_refit_ni_bootstrap(ajuste, observaciones):
    semanas, canales = copy.deepcopy(observaciones)
    for s in semanas[-20:]:
        s["pedidos"] *= 10
        s["gasto"] = {c: v*100 for c, v in s["gasto"].items()}
    alterado = entrenar(semanas, canales, 260725)
    assert alterado["parametros"] == ajuste["parametros"]
    assert alterado["diagnostico"]["candidatos"] == ajuste["diagnostico"]["candidatos"]
    assert alterado["serie"][:-20] == ajuste["serie"][:-20]
    assert alterado["diagnostico"]["holdout"] != ajuste["diagnostico"]["holdout"]
    assert [c["maximo"] for c in alterado["curvas"]] == [c["maximo"] for c in ajuste["curvas"]]


def test_abstencion_si_peor_que_naive_o_inestable(ajuste):
    diag = copy.deepcopy(ajuste["diagnostico"])
    diag["holdout"]["wape"] = diag["naive"]["wape"]+1
    diag["correlacion_maxima"] = 1
    diag["condicion"] = None
    diag["variacion_minima"] = 0
    diag["sensibilidad"] = 2
    diag["prediccion_no_positiva"] = True
    assert len(politica(diag, Configuracion())) == 6


def test_rechaza_sem_marca_y_huecos(observaciones):
    semanas, canales = copy.deepcopy(observaciones)
    with pytest.raises(ValueError, match="SEM marca"):
        entrenar(semanas, canales+[dict(id="sem_marca", tipo="captura")], 1)
    semanas.pop(20)
    with pytest.raises(ValueError, match="consecutivas"):
        entrenar(semanas, canales, 1)


def test_estimador_sin_importaciones_de_generador_o_verdad():
    for fichero in Path("app/modelos").glob("*.py"):
        fuente = fichero.read_text()
        arbol = ast.parse(fuente)
        assert all(not (n.module or "").startswith("app.datos") for n in ast.walk(arbol) if isinstance(n, ast.ImportFrom))
        assert "verdad_sintetica" not in fuente
        assert "demanda_proxy" not in fuente


def test_modelo_persistido_consultas_y_no_desagregacion(client, db):
    snapshot = snapshot_actual(db)
    primero = asegurar_modelo(db, snapshot)
    assert primero.id == asegurar_modelo(db, snapshot).id
    assert db.scalar(select(func.count()).select_from(Modelo).where(Modelo.version == VERSION)) == 1
    respuesta = client.get("/api/v1/modelos/mmm?dias=28")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["aplicable"] and len(datos["serie"]) == 4
    assert datos["modelo"]["snapshot"] == snapshot.id
    assert datos["modelo"]["checksum_snapshot"] == snapshot.checksum
    assert len(client.get("/api/v1/modelos/mmm?dias=365").json()["serie"]) == 52
    for fila in datos["resumen"]:
        assert fila["saldo_modelado"] == pytest.approx(fila["margen_asignado"]-fila["inversion"])
    local = client.get("/api/v1/modelos/mmm?mercado=m01").json()
    assert not local["aplicable"] and not local["serie"] and not local["curvas"] and not local["resumen"]
    assert local["modelo"]["id"] == datos["modelo"]["id"]
    assert client.get("/api/v1/modelos").json()["filas"][0]["id"] == datos["modelo"]["id"]
    ruta = f"/api/v1/modelos/{datos['modelo']['id']}/curvas"
    assert len(client.get(ruta+"?canal=meta").json()["curvas"]) == 1
    assert client.get(ruta+"?canal=sem_marca").status_code == 422
    assert client.get("/api/v1/modelos/inexistente/curvas").status_code == 404
    assert VERSION in client.get("/api/v1/fiabilidad").json()["diagnostico_modelos"]
