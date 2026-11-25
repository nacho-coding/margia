import copy
import inspect

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.api.consultas import snapshot_actual
from app.api.geo_contratos import DisenoGeo
from app.experimentos.servicio import cargar_series
from app.main import app
from app.modelos import geo
from app.modelos.geo import disenar_geo, estimar_geo
from app.modelos.informacion import valor_informacion
from app.modelos.search import VERSION
from app.persistencia.db import engine, get_db
from app.persistencia.tablas import (
    AsignacionExperimento,
    Experimento,
    Modelo,
    NegocioDiario,
    ObservacionExperimento,
    SimulacionSearch,
)


@pytest.fixture
def geo_client():
    # Cada POST puede confirmar, pero el conjunto se revierte: no cambia la demo.
    with engine.connect() as conexion:
        transaccion = conexion.begin()
        with Session(bind=conexion, join_transaction_mode="create_savepoint") as session:
            # Baseline de la fixture dentro de la transacción; todo vuelve al salir.
            geos = select(Experimento.id).where(Experimento.tipo == "geo_search")
            modelos_geo = select(Modelo.id).where(Modelo.version == "search-geo-1.0.0")
            session.execute(delete(SimulacionSearch).where(SimulacionSearch.modelo_id.in_(modelos_geo)))
            session.execute(delete(Modelo).where(Modelo.id.in_(modelos_geo)))
            session.execute(delete(ObservacionExperimento).where(ObservacionExperimento.experimento_id.in_(geos)))
            session.execute(delete(AsignacionExperimento).where(AsignacionExperimento.experimento_id.in_(geos)))
            session.execute(delete(Experimento).where(Experimento.id.in_(geos)))
            def override():
                yield session
            app.dependency_overrides[get_db] = override
            try:
                yield TestClient(app), session
            finally:
                app.dependency_overrides.pop(get_db, None)
        transaccion.rollback()


def fixture_observaciones(tasa=0):
    asignaciones, obs = [], []
    for i in range(12):
        for brazo in ("control", "tratamiento"):
            mid = f"{i}-{brazo}"
            asignaciones.append(dict(mercado=mid, par=f"par{i}", brazo=brazo))
            for periodo in ("pre", "post"):
                ahorro = 1000 if brazo == "tratamiento" and periodo == "post" else 0
                obs.append(dict(mercado=mid, periodo=periodo, pedidos=2000+tasa*ahorro,
                    presupuesto_cent=200000, gasto_cent=200000-ahorro*100))
    return asignaciones, obs


@pytest.mark.parametrize("tasa", [0, -.1, .02])
def test_estimador_nulo_adverso_y_positivo_por_pares(tasa):
    asignaciones, obs = fixture_observaciones(tasa)
    r = estimar_geo(asignaciones, obs, 56, 28)
    assert r["efecto"] == pytest.approx(12000*tasa)
    assert r["tasa"] == pytest.approx(tasa)
    assert r["numero_pares"] == 12
    assert r["ic95"][0] <= r["efecto"] <= r["ic95"][1]
    assert "mundo_geo" not in inspect.getsource(geo)
    assert "captura" not in inspect.getsource(geo)
    with pytest.raises(ValueError):
        estimar_geo(asignaciones, obs+obs[:1], 56, 28)
    with pytest.raises(ValueError):
        estimar_geo(asignaciones, obs[1:], 56, 28)


def test_intervalo_no_degenerado_y_efecto_sin_futuro():
    a, obs = fixture_observaciones(-.02)
    for i, o in enumerate(obs):
        if o["periodo"] == "post":
            o["pedidos"] += (i % 11)**2
    r = estimar_geo(a, obs, 56, 28)
    assert r["ic95"][0] < r["ic95"][1]
    assert r["se_tasa"] > 0
    alteradas = copy.deepcopy(obs)
    for o in alteradas:
        o["verdad_latente"] = 999999  # No accede a contrafactuales de generación.
    assert estimar_geo(a, alteradas, 56, 28) == r


@pytest.mark.parametrize("entrada", [{"mercados": ["m01"]*8}, {"mercados": [f"m{i:02}" for i in range(9)]},
    {"dias": 1}, {"pre_dias": 14}, {"coste": -1}, {"semilla": -1}, {"recorte_pct": 101},
    {"cuota_plataforma": float("nan")}, {"kpi": "clics"}])
def test_validacion_geo(entrada):
    with pytest.raises(ValidationError):
        DisenoGeo(**entrada)


def test_diseno_reproducible_y_solo_preperiodo(db):
    snapshot = snapshot_actual(db)
    ids = [f"m{i:02}" for i in range(1, 25)]
    series = cargar_series(db, snapshot, ids, 56)
    plan = disenar_geo(series, 260776, 28, .5)
    assert plan == disenar_geo(series, 260776, 28, .5)
    otro = disenar_geo(series, 1, 28, .5)
    assert plan["asignaciones"] != otro["asignaciones"]
    assert plan["pares"] == 12 and plan["mde_pedidos"] > 0
    assert sum(a["brazo"] == "tratamiento" for a in plan["asignaciones"]) == 12
    assert all(a["probabilidad"] == .5 for a in plan["asignaciones"])
    assert all("post" not in a for a in plan["asignaciones"])


def test_valor_informacion_fixture_y_ruido():
    u = [[0, 0], [80000, -60000]]
    perfecto = valor_informacion(u, [1, -1], 0)
    assert perfecto["ev_sin_informacion"] == 10000
    assert perfecto["evpi"] == 30000
    assert perfecto["evsi"] == perfecto["evpi"]
    r = valor_informacion(u, [1, -1], .8)
    peor = valor_informacion(u, [1, -1], 10)
    assert 0 <= peor["evsi"] < r["evsi"] < r["evpi"]
    assert r["evsi"]-40000 < 0  # Una prueba cara destruye valor.
    assert r == valor_informacion(u, [1, -1], .8)
    assert valor_informacion([[0, 0], [80, 60]], [1, -1], 1)["evpi"] == 0
    # Igual señal no permite distinguir estados aunque el ruido sea cero.
    assert valor_informacion(u, [1, 1], 0)["evsi"] == 0
    rara = valor_informacion([[0]*400, [80000]*399+[-60000]], [1]*399+[-1], 0)
    assert rara["evpi"] == pytest.approx(150)
    assert rara["evsi"] == pytest.approx(150)


def test_api_ciclo_geo_reproducibilidad_versiones_y_economia(geo_client):
    client, db = geo_client
    catalogo = client.get("/api/v1/experimentos").json()
    anterior = client.get("/api/v1/busqueda/evidencia").json()["modelo"]
    conteo = db.scalar(select(func.sum(NegocioDiario.pedidos)))
    entrada = dict(nombre="Prueba geo automatizada", semilla=260776, coste=100000)
    creado = client.post("/api/v1/experimentos/disenar", json=entrada)
    assert creado.status_code == 200, creado.text
    d = creado.json()
    assert d["estado"] == "disenado" and not d["observaciones"]
    assert d["inicio_post"] > catalogo["corte"]
    assert len(d["asignaciones"]) == 24
    assert d["protocolo"]["plan"]["potencia_insuficiente"] == (abs(d["protocolo"]["plan"]["efecto_previo_pedidos"]) < d["protocolo"]["plan"]["mde_pedidos"])
    info = d["protocolo"]["informacion"]
    assert 0 <= info["evsi"] <= info["evpi"]
    assert info["estados"] == 400
    assert info["valor_neto"] < 0 and "no compensa" in info["recomendacion"]
    assert info["costes_totales"] == pytest.approx(100000+info["coste_oportunidad_prueba"])
    assert client.post("/api/v1/experimentos/disenar", json=entrada).json()["reutilizada"]
    uri = "/api/v1/experimentos/"+d["id"]
    assert client.post(uri+"/evaluar", json={}).status_code == 409
    simulado = client.post(uri+"/ejecutar", json={}).json()
    assert simulado["estado"] == "simulado" and len(simulado["observaciones"]) == 48
    assert client.post(uri+"/ejecutar", json={}).json()["observaciones"] == simulado["observaciones"]
    evaluado = client.post(uri+"/evaluar", json={}).json()
    assert evaluado["estado"] == "evaluado"
    r = evaluado["protocolo"]["evaluacion"]
    assert r["ic95"][0] < r["ic95"][1]
    assert r["compatible"], r["motivos"]
    guardada = client.post("/api/v1/busqueda/simular", json={}).json()
    aceptado = client.post(uri+"/aceptar", json={})
    assert aceptado.status_code == 200, aceptado.text
    nuevo = client.get("/api/v1/busqueda/evidencia").json()["modelo"]
    assert nuevo["id"] != anterior["id"]
    assert nuevo["modelo_anterior"] == anterior["id"]
    assert nuevo["soporte"] == [.5] and nuevo["experimentos"] == 1
    assert client.post(uri+"/aceptar", json={}).json()["reutilizada"]
    assert db.get(Modelo, anterior["id"]) is not None
    assert client.get("/api/v1/busqueda/simulaciones/"+guardada["id"]).json()["resultado"] == guardada["resultado"]
    assert client.post("/api/v1/busqueda/simular", json={"recorte_pct": 25}).json()["resultado"]["extrapolado"]
    assert db.scalar(select(func.sum(NegocioDiario.pedidos))) == conteo
    assert db.scalar(select(Modelo).where(Modelo.version == VERSION)) is not None
    # Una prueba diseñada con evidencia antigua no sobrescribe la nueva versión.
    assert client.get(uri).json()["estado"] == "aceptado"


@pytest.mark.parametrize("entrada,motivo", [({"recorte_pct": 0}, "Tratamiento nulo"),
    ({"dias": 14}, "Horizonte incompatible"), ({"mercados": [f"m{i:02}" for i in range(1, 9)]}, "Cobertura insuficiente")])
def test_abstencion_y_protocolo_inmutable(geo_client, entrada, motivo):
    client, _ = geo_client
    d = client.post("/api/v1/experimentos/disenar", json=entrada).json()
    uri = "/api/v1/experimentos/"+d["id"]
    assert client.post(uri+"/aceptar", json={}).status_code == 409
    client.post(uri+"/ejecutar", json={})
    evaluado = client.post(uri+"/evaluar", json={}).json()
    assert any(motivo in m for m in evaluado["protocolo"]["evaluacion"]["motivos"])
    assert client.post(uri+"/aceptar", json={}).status_code == 409
    cat = client.get("/api/v1/experimentos").json()
    hist = next(e["id"] for e in cat["filas"] if e["tipo"] == "historico_search")
    assert client.post(f"/api/v1/experimentos/{hist}/ejecutar", json={}).status_code == 409
    assert client.post("/api/v1/experimentos/disenar", json={"mercados": [f"m{i:02}" for i in range(91, 99)]}).status_code == 422
    assert client.get("/api/v1/experimentos/inventado").status_code == 404


def test_guardrail_adverso_impide_actualizar(geo_client):
    client, db = geo_client
    d = client.post("/api/v1/experimentos/disenar", json={"nombre": "Prueba de pérdida adversa"}).json()
    uri = "/api/v1/experimentos/"+d["id"]
    client.post(uri+"/ejecutar", json={})
    for a in d["asignaciones"]:
        if a["brazo"] == "tratamiento":
            db.get(ObservacionExperimento, (d["id"], a["mercado"], "post")).pedidos = 0
    db.commit()
    r = client.post(uri+"/evaluar", json={}).json()["protocolo"]["evaluacion"]
    assert r["efecto"] < 0 and not r["compatible"]
    assert any("límite de pérdida" in m for m in r["motivos"])
    assert client.post(uri+"/aceptar", json={}).status_code == 409


def test_evidencia_antigua_no_sobrescribe_y_faltantes_bloquean(geo_client):
    client, db = geo_client
    pruebas = []
    for nombre in ("Primera rama", "Segunda rama"):
        d = client.post("/api/v1/experimentos/disenar", json={"nombre": nombre}).json()
        uri = "/api/v1/experimentos/"+d["id"]
        client.post(uri+"/ejecutar", json={})
        client.post(uri+"/evaluar", json={})
        pruebas.append((d, uri))
    assert client.post(pruebas[0][1]+"/aceptar", json={}).status_code == 200
    assert client.post(pruebas[1][1]+"/aceptar", json={}).status_code == 409
    sano = client.get("/api/v1/fiabilidad").json()
    assert any(f["id"] == "evidencia_geo" for f in sano["fuentes"])
    d = pruebas[0][0]
    db.delete(db.get(ObservacionExperimento, (d["id"], d["asignaciones"][0]["mercado"], "post")))
    db.commit()
    assert client.get("/api/v1/fiabilidad").json()["estado"] == "bloqueado"
    assert client.post("/api/v1/busqueda/simular", json={}).json()["resultado"]["estado"] == "bloqueado"


def test_repetir_rama_identica_no_duplica_evidencia(geo_client):
    client, db = geo_client
    modelos = []
    for nombre in ("Primera observación", "Misma observación con otro nombre"):
        d = client.post("/api/v1/experimentos/disenar", json={"nombre": nombre}).json()
        uri = "/api/v1/experimentos/"+d["id"]
        client.post(uri+"/ejecutar", json={})
        client.post(uri+"/evaluar", json={})
        a = client.post(uri+"/aceptar", json={})
        assert a.status_code == 200, a.text
        modelos.append(a.json()["protocolo"]["actualizacion"]["modelo"])
    assert modelos[0] == modelos[1]
    assert db.scalar(select(func.count()).select_from(Modelo).where(Modelo.version == "search-geo-1.0.0")) == 1
