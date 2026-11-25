import copy
from datetime import date

import numpy as np
import pytest
from fastapi.testclient import TestClient
from scipy.stats import binomtest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.consultas import snapshot_actual
from app.creatividad.experimentos import contexto_pretest
from app.datos.mundo_ab import decodificar, ejecutar_mundo_ab
from app.main import app
from app.modelos.ab import VERSION_AB, diferencia, estimar_ab, plan_ab, wilson
from app.persistencia.db import engine, get_db
from app.persistencia.tablas import Experimento, Modelo, NegocioDiario


@pytest.fixture
def ab_client():
    with engine.connect() as conexion:
        transaccion = conexion.begin()
        with Session(bind=conexion, join_transaction_mode="create_savepoint") as db:
            def override():
                yield db
            app.dependency_overrides[get_db] = override
            try:
                yield TestClient(app), db
            finally:
                app.dependency_overrides.pop(get_db, None)
        transaccion.rollback()


@pytest.mark.parametrize("y,n", [(0, 100), (100, 100), (1, 500), (250, 50000)])
def test_wilson_coincide_con_implementacion_primaria(y, n):
    ci = binomtest(y, n).proportion_ci(method="wilson")
    assert wilson(y, n) == pytest.approx([ci.low, ci.high])


def test_ic_nulo_adverso_positivo_y_multiplicidad():
    nulo = diferencia(0, 1000, 0, 1000)
    assert nulo["ic95_familiar"][0] < 0 < nulo["ic95_familiar"][1]
    assert nulo["cambio_relativo"] is None
    assert diferencia(500, 100000, 1000, 100000)["ic95_familiar"][1] < 0
    a = diferencia(1500, 100000, 1000, 100000)
    b = diferencia(1500, 100000, 1000, 100000, 2)
    assert 0 < b["ic95_familiar"][0] < a["ic95_familiar"][0]
    assert b["ic95_familiar"][1] > a["ic95_familiar"][1]
    with pytest.raises(ValueError):
        diferencia(0, 0, 1, 10)


def test_plan_mde_y_costes_comparables_una_vez():
    a = plan_ab(.01, 50000, 2, 50000, 25000)
    b = plan_ab(.01, 50000, 3, 50000, 25000)
    assert a["coste_total"] == 1250 and b["coste_total"] == 1750
    assert b["mde_absoluto"] > a["mde_absoluto"]
    assert plan_ab(.01, 100000, 2, 50000, 25000)["mde_absoluto"] < a["mde_absoluto"]
    assert a["probabilidad"] == .5 and b["comparaciones"] == 2


def generar_fixture(efectos, n=50000):
    variantes = [dict(id=f"v{i}", asset=f"/fixture-{i}.svg") for i in range(len(efectos))]
    contexto = dict(canal="meta", categoria="hogar", audiencia="Cohorte 01", frecuencia=2.5)
    return ejecutar_mundo_ab(contexto, variantes, "2026-11-01", 14, n, 50000, 264928, 260725,
        efectos_fixture=efectos)


def test_mundo_aleatoriza_unidades_y_preserva_semilla():
    a, o = generar_fixture([0, 0, 0])
    assert (a, o) == generar_fixture([0, 0, 0])
    assert len(a) == 14 and len(o) == 42
    for asignacion in a:
        x = decodificar(asignacion)
        assert len(set(x.tolist())) == 3
        assert len(set(np.bincount(x).tolist())) == 1
        assert date.fromisoformat(asignacion["fecha"]) > date(2026, 10, 31)
    assert {b: sum(f["impresiones"] for f in o if f["brazo"] == b) for b in ("v0", "v1", "v2")} == dict(v0=50000, v1=50000, v2=50000)
    assert all(0 <= f["conversiones"] <= f["clics"] <= f["impresiones"] for f in o)
    alterada = copy.deepcopy(a[0])
    alterada["sha256"] = "x"
    with pytest.raises(ValueError):
        decodificar(alterada)


def test_estimador_conserva_adverso_y_se_abstiene_con_conteos_escasos():
    _, obs = generar_fixture([0, -.7])
    r = estimar_ab(obs, ["v0", "v1"], "v0", 50000, 14, 50000, 25000, 264928)
    assert r["compatible"] and r["contrastes"][0]["ic95_familiar"][1] < 0
    assert r["coste_total"] == 1250 and r["multiplicador_demanda"] == 1
    assert r["efecto_economico_identificado"] is False
    assert len(r["draws_ctr"]) == 2 and len(r["draws_ctr"][0]) == 200
    _, pocos = generar_fixture([0, 0], n=500)
    insuf = estimar_ab(pocos, ["v0", "v1"], "v0", 500, 14, 50000, 0, 264928)
    assert not insuf["compatible"] and insuf["motivos"]
    with pytest.raises(ValueError):
        estimar_ab(obs+obs[:1], ["v0", "v1"], "v0", 50000, 14, 50000, 0, 264928)


def protocolo(c, nombre="Fixture explícita de A/B", n=50000, tres=True):
    p = c.post("/api/v1/creativos/evaluar", json={"objetivo": "Fixture de contexto para A/B", "frecuencia": 4.123456}).json()
    return p, dict(pretest_id=p["id"], control=p["variantes"][0]["id"],
        tratamientos=[v["id"] for v in p["variantes"][1:3 if tres else 2]],
        nombre=nombre, impresiones_por_brazo=n)


def completar(c, entrada, aceptar=False):
    diseno = c.post("/api/v1/creativos/pruebas/disenar", json=entrada)
    assert diseno.status_code == 200, diseno.text
    uri = "/api/v1/creativos/pruebas/"+diseno.json()["id"]
    assert c.post(uri+"/ejecutar", json={}).status_code == 200
    evaluacion = c.post(uri+"/evaluar", json={})
    assert evaluacion.status_code == 200, evaluacion.text
    if aceptar:
        aceptado = c.post(uri+"/aceptar", json={})
        assert aceptado.status_code == 200, aceptado.text
        return uri, aceptado.json()
    return uri, evaluacion.json()


def test_api_ciclo_futuro_inmutable_aprendizaje_y_contexto(ab_client):
    c, db = ab_client
    p, entrada = protocolo(c)
    antes = db.scalar(select(func.sum(NegocioDiario.pedidos)))
    inicial = c.post("/api/v1/creativos/pruebas/disenar", json=entrada).json()
    uri = "/api/v1/creativos/pruebas/"+inicial["id"]
    assert inicial["estado"] == "disenado" and not inicial["observaciones"] and not inicial["asignaciones"]
    assert c.get(uri+"/asignaciones.csv").status_code == 409
    assert c.post(uri+"/evaluar", json={}).status_code == 409
    assert c.post(uri+"/aceptar", json={}).status_code == 409
    assert c.post("/api/v1/creativos/pruebas/disenar", json=entrada).json()["id"] == inicial["id"]
    assert c.post(uri+"/ejecutar", json={"ganador": 1}).status_code == 422
    ejecucion = c.post(uri+"/ejecutar", json={}).json()
    repetida = c.post(uri+"/ejecutar", json={}).json()
    assert ejecucion["observaciones"] == repetida["observaciones"] and repetida["reutilizada"]
    assert len(ejecucion["observaciones"]) == 42 and len(ejecucion["asignaciones"]) == 14
    assert all("datos" not in a for a in ejecucion["asignaciones"])
    assert c.get(uri+"/asignaciones.csv").text.count("\n") == 150001
    assert c.get("/api/v1/experimentos/"+inicial["id"]).status_code == 404
    assert all(e["id"] != inicial["id"] for e in c.get("/api/v1/experimentos").json()["filas"])
    evaluado = c.post(uri+"/evaluar", json={}).json()
    assert evaluado["protocolo"]["evaluacion"]["compatible"]
    aceptado = c.post(uri+"/aceptar", json={}).json()
    mid = aceptado["protocolo"]["actualizacion"]["modelo"]
    aprendido = c.get("/api/v1/creativos/aprendizaje/"+p["id"]).json()["modelo"]
    assert aprendido["id"] == mid and aprendido["contexto"] == contexto_pretest(p)
    assert aprendido["multiplicador_demanda"] == 1 and len(aprendido["estimaciones"]) == 3
    assert "draws_ctr" not in aprendido
    assert c.post(uri+"/aceptar", json={}).json()["reutilizada"]
    assert c.get("/api/v1/creativos/aprendizaje/modelos/"+mid).status_code == 200
    otra = c.post("/api/v1/creativos/evaluar", json={"frecuencia": 4.234567}).json()
    assert c.get("/api/v1/creativos/aprendizaje/"+otra["id"]).json()["modelo"] is None
    assert c.get("/api/v1/creativos/evaluaciones/"+p["id"]).json()["variantes"] == p["variantes"]
    assert db.scalar(select(func.sum(NegocioDiario.pedidos))) == antes
    assert snapshot_actual(db).checksum == "6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d"


def test_no_acumular_copias_obsoletas_ni_reescribir_versiones(ab_client):
    c, db = ab_client
    p, entrada = protocolo(c, "Fixture rama primera")
    _, obsoleta = completar(c, {**entrada, "nombre": "Fixture rama obsoleta", "semilla": 42})
    _, primera = completar(c, entrada, aceptar=True)
    mid = primera["protocolo"]["actualizacion"]["modelo"]
    conservado = copy.deepcopy(db.get(Modelo, mid).resultado)
    _, copia = completar(c, {**entrada, "nombre": "Fixture copia exacta"}, aceptar=True)
    assert copia["protocolo"]["actualizacion"]["modelo"] == mid
    assert copia["reutilizada"]
    assert db.scalar(select(func.count()).select_from(Modelo).where(Modelo.version == VERSION_AB,
        Modelo.resultado["clave_contexto"].as_string() == db.get(Modelo, mid).resultado["clave_contexto"])) == 1
    uri = "/api/v1/creativos/pruebas/"+obsoleta["id"]
    assert c.post(uri+"/aceptar", json={}).status_code == 409
    _, segunda = completar(c, {**entrada, "nombre": "Fixture nueva versión", "semilla": 50}, aceptar=True)
    siguiente = segunda["protocolo"]["actualizacion"]["modelo"]
    assert siguiente != mid
    assert db.get(Modelo, siguiente).resultado["modelo_anterior"] == mid
    assert db.get(Modelo, mid).resultado == conservado
    assert c.get("/api/v1/creativos/aprendizaje/"+p["id"]).json()["modelo"]["id"] == siguiente


def test_api_guardrails_y_datos_alterados(ab_client):
    c, db = ab_client
    _, entrada = protocolo(c, n=500, tres=False)
    assert c.post("/api/v1/creativos/pruebas/disenar", json={**entrada, "tratamientos": [entrada["control"]]}).status_code == 422
    assert c.post("/api/v1/creativos/pruebas/disenar", json={**entrada, "tratamientos": ["ajena"]}).status_code == 422
    assert c.post("/api/v1/creativos/pruebas/disenar", json={**entrada, "efecto": 1}).status_code == 422
    uri, evaluado = completar(c, entrada)
    assert not evaluado["protocolo"]["evaluacion"]["compatible"]
    assert c.post(uri+"/aceptar", json={}).status_code == 409
    registro = db.get(Experimento, evaluado["id"])
    datos = copy.deepcopy(registro.protocolo)
    datos["asignaciones"][0]["sha256"] = "alterada"
    registro.estado, registro.protocolo = "simulado", datos
    db.commit()
    assert c.post(uri+"/evaluar", json={}).status_code == 409
    _, entrada_sana = protocolo(c, "Fixture de integridad tras evaluar", n=50000, tres=False)
    uri_sana, sana = completar(c, entrada_sana)
    registro_sano = db.get(Experimento, sana["id"])
    cambiadas = copy.deepcopy(registro_sano.protocolo)
    cambiadas["observaciones"][0]["clics"] += 1
    registro_sano.protocolo = cambiadas
    db.commit()
    assert c.post(uri_sana+"/aceptar", json={}).status_code == 409
