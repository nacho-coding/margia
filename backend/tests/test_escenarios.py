import ast
import copy
import math
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.consultas import snapshot_actual
from app.api.escenarios_contratos import ParametrosEscenario
from app.dominio.economia import comparar_plan
from app.escenarios import servicio
from app.escenarios.motor import MotorEscenarios, soportes
from app.escenarios.proyeccion import proyectar_base
from app.main import app
from app.modelos.mmm import CONTROLES
from app.modelos.servicio import modelo_actual
from app.persistencia.db import engine, get_db
from app.persistencia.tablas import Ejecucion, NegocioDiario


@pytest.fixture
def fixture_motor():
    """Modelo habilitado EXPLÍCITO para probar el algoritmo, no el diagnóstico real."""
    canales = ["crm", "display", "meta", "sem_generico", "tiktok", "tv", "youtube"]
    inicio = date(2024, 11, 3)
    semanas = [dict(inicio=(inicio+timedelta(weeks=i)).isoformat(),
        fin=(inicio+timedelta(weeks=i, days=6)).isoformat(),
        pedidos=1000+5*i+80*math.sin(i*2*math.pi/52),
        gasto={c: 1000. for c in [*canales, "sem_marca"]}) for i in range(104)]
    beta = np.array([0.]*len(CONTROLES)+[10. if c != "meta" else 600. for c in canales])
    betas = np.repeat(beta[None, :], 80, axis=0)
    betas[:, len(CONTROLES)+2] += np.linspace(-20, 20, 80)
    mmm = dict(estado="limitado", optimizable=True, motivos=[], train_fin=semanas[83]["fin"],
        parametros=dict(canales=canales, persistencia=.3, k=1., escala_gasto=[1000.]*7,
            coeficientes=beta.tolist(), bootstrap_coeficientes=betas.tolist()),
        curvas=[dict(id=c, nombre=c, color="#176B57", minimo=500., maximo=1500.) for c in canales])
    search = dict(estado="limitado", motivos=[], soporte=[.25, .5, .75], tasas=[-.002]*3, replicas=400,
        draws=np.repeat(np.linspace(-.004, 0, 400)[:, None], 3, axis=1).tolist())
    pedidos = sum(s["pedidos"] for s in semanas[-4:])
    ref = dict(pedidos=pedidos, ventas=pedidos*100, margen=pedidos*40, inversion=32000.)
    _, lim = soportes(semanas, mmm)
    e = ParametrosEscenario(presupuesto_total=32000.,
        limites=[{k: s[k] for k in ("canal", "minimo", "maximo")} for s in lim]).model_dump()
    return semanas, mmm, search, ref, e


def test_comparador_comun_costes_y_limites_fisicos():
    r = comparar_plan(1000, 50000, 10000, -10, 3000, 1000, ventas=100000,
        creatividad=200, experimento=100, plataforma=500, plataforma_comun=True, otros=50)
    assert r["delta"] == 1150
    assert r["costes_incrementales"] == 350
    assert r["alternativa"]["ventas"]-r["alternativa"]["coste_directo"] == r["alternativa"]["margen"]
    assert comparar_plan(100, 5000, 1000, 0, 0, plataforma=600)["delta"] == -600
    with pytest.raises(ValueError):
        comparar_plan(10, 100, 100, -11, 0)
    with pytest.raises(ValueError):
        comparar_plan(10, 100, 100, 0, 0, ventas=90)


def test_base_estacional_y_errores_sin_holdout(fixture_motor):
    semanas, mmm, *_ = fixture_motor
    base = proyectar_base(semanas, 84)
    esperada = sum(s["pedidos"] for s in semanas[52:56])*sum(s["pedidos"] for s in semanas[-4:])/sum(s["pedidos"] for s in semanas[48:52])
    assert base["pedidos"] == pytest.approx(esperada)
    assert base["fin_errores"] == mmm["train_fin"] and base["semanas_errores"] == 28
    assert base["validacion"]["bloques"] == 5
    alteradas = copy.deepcopy(semanas)
    for s in alteradas[84:]:
        s["pedidos"] *= 1.2
    cambiada = proyectar_base(alteradas, 84)
    assert cambiada["errores_centrados"] == base["errores_centrados"]
    assert cambiada["pedidos"] != base["pedidos"]
    assert cambiada["validacion"]["filas"][0]["predicho"] == base["validacion"]["filas"][0]["predicho"]
    assert cambiada["validacion"]["filas"][0]["observado"] != base["validacion"]["filas"][0]["observado"]


def test_draws_pareados_nulo_semilla_y_costes_una_vez(fixture_motor):
    semanas, mmm, search, ref, e = fixture_motor
    e.update(recorte_pct=0)
    motor = MotorEscenarios(semanas, mmm, search, ref, e)
    r = motor.ejecutar()
    for p in (r["base"], r["ahorro"], r["reinversion"]):
        assert p["delta"] == 0 and p["bandas"]["delta"]["p05"] == 0
        assert all(d["delta"] == 0 for d in p["draws"])
    assert r == MotorEscenarios(semanas, mmm, search, ref, e).ejecutar()
    distinta = MotorEscenarios(semanas, mmm, search, ref, {**e, "semilla": e["semilla"]+1}).ejecutar()
    assert distinta["traza_draws"]["checksum"] != r["traza_draws"]["checksum"]
    e.update(recorte_pct=50, coste_produccion=200, coste_experimento=100, cuota_plataforma=500,
        plataforma_comun=True, otros_costes=50)
    creativo = dict(canal="meta", seleccion="fixture-explicita", ctr=.99)
    c = MotorEscenarios(semanas, mmm, search, ref, e, creativo).ejecutar()
    assert c["ahorro"]["coste_incremental"] == 150 and c["reinversion"]["coste_incremental"] == 350
    for p in (c["base"], c["ahorro"], c["reinversion"]):
        assert sum(d["importe"] for d in p["desglose"][:-1]) == pytest.approx(p["delta"])
        assert len(p["draws"]) == 200
        for b, d in zip(c["base"]["draws"], p["draws"], strict=True):
            assert b["alternativa"]["pedidos"] == d["base"]["pedidos"]
            a = d["alternativa"]
            assert a["contribucion"] == pytest.approx(a["margen"]-sum(a[k] for k in ("inversion", "creatividad", "experimento", "plataforma", "otros")))
            assert d["delta"] == pytest.approx(a["contribucion"]-d["base"]["contribucion"])
    assert c["reinversion"]["multiplicador_demanda"] == 1
    sin_ctr = MotorEscenarios(semanas, mmm, search, ref, e, {**creativo, "ctr": .001}).ejecutar()
    assert sin_ctr["reinversion"]["delta"] == c["reinversion"]["delta"]


def test_adstock_inicial_formula_cerrada_y_sem_fuera_de_demanda(fixture_motor):
    semanas, mmm, search, ref, e = fixture_motor
    motor = MotorEscenarios(semanas, mmm, search, ref, e)
    r = motor.evaluar("Fixture de respuesta", .5, .5, "meta")
    inicial = (1-.3**104)/(1-.3)
    nuevo_equilibrio = 1.25/(1-.3)
    stocks = [nuevo_equilibrio+(inicial-nuevo_equilibrio)*.3**(t+1) for t in range(4)]
    esperado = 600*sum(a/(a+1)-inicial/(inicial+1) for a in stocks)
    assert r["delta_demanda"] == pytest.approx(esperado, abs=1e-7)
    assert motor.stock_inicial[2] == pytest.approx(inicial)
    ahorro = motor.evaluar("Solo captura", .75)
    assert ahorro["delta_demanda"] == 0
    assert ahorro["delta_captura"] == pytest.approx(3000*-.002)
    malo = copy.deepcopy(mmm)
    malo["parametros"]["canales"][0] = "sem_marca"
    with pytest.raises(ValueError, match="captura SEM"):
        MotorEscenarios(semanas, malo, search, ref, e)


def test_optimizacion_factible_soporte_y_mejor_en_rejilla(fixture_motor):
    semanas, mmm, search, ref, e = fixture_motor
    r = MotorEscenarios(semanas, mmm, search, ref, e).ejecutar()
    opt = r["optimizacion"]
    mejor = opt["mejor"]
    assert opt["demanda_habilitada"] and mejor["canal"] == "meta"
    assert mejor["factible"] and mejor["elegible"]
    assert sum(mejor["presupuestos"].values()) <= e["presupuesto_total"]+1e-6
    assert mejor["bandas"]["delta"]["media"] == max(a["media_delta"] for a in opt["auditoria"] if a["elegible"])
    for limite in e["limites"]:
        assert limite["minimo"] <= mejor["presupuestos"][limite["canal"]] <= limite["maximo"]
    fuera = MotorEscenarios(semanas, mmm, search, ref, e).evaluar("Fuera de soporte", .75, 1., "meta")
    assert not fuera["factible"] and fuera["restricciones"]
    imposible = MotorEscenarios(semanas, mmm, search, ref, {**e, "presupuesto_total": 0}).ejecutar()
    assert imposible["optimizacion"]["mejor"] is None and imposible["optimizacion"]["estado"] == "sin_candidato"
    assert not imposible["base"]["factible"]


def test_bloqueo_mmm_no_se_relaja_y_riesgo_puede_imponer_mantener(fixture_motor):
    semanas, mmm, search, ref, e = fixture_motor
    mmm.update(estado="bloqueado", optimizable=False, motivos=["Fixture explícita de sensibilidad"])
    r = MotorEscenarios(semanas, mmm, search, ref, e).ejecutar()
    assert not r["reinversion"]["elegible"] and r["reinversion"]["motivos"]
    assert not r["optimizacion"]["demanda_habilitada"]
    assert all(a["canal"] is None for a in r["optimizacion"]["auditoria"])
    search["draws"] = [[t]*3 for t in [-.04, .04]*200]
    search["tasas"] = [0.]*3
    r = MotorEscenarios(semanas, mmm, search, ref, e).ejecutar()
    assert r["ahorro"]["bandas"]["delta"]["media"] > 0
    assert r["ahorro"]["bandas"]["delta"]["probabilidad_perdida"] > .1
    assert r["optimizacion"]["mejor"]["recorte_pct"] == 0
    e["riesgo_max_pct"] = 100
    assert MotorEscenarios(semanas, mmm, search, ref, e).ejecutar()["optimizacion"]["mejor"]["recorte_pct"] > 0
    search["draws"], search["tasas"] = [[-.05]*3]*400, [-.05]*3
    negativo = MotorEscenarios(semanas, mmm, search, ref, e).ejecutar()
    assert negativo["ahorro"]["delta"] < 0 and negativo["optimizacion"]["mejor"]["recorte_pct"] == 0


def test_canal_sin_cambios_fuera_soporte_no_bloquea_captura(fixture_motor):
    semanas, mmm, search, ref, e = fixture_motor
    mmm["curvas"][1].update(minimo=500., maximo=500.)
    mmm.update(estado="bloqueado", optimizable=False, motivos=["Fixture de sensibilidad"])
    _, soporte = soportes(semanas, mmm)
    assert soporte[1]["actual_fuera_soporte"]
    e["limites"] = [{k: s[k] for k in ("canal", "minimo", "maximo")} for s in soporte]
    motor = MotorEscenarios(semanas, mmm, search, ref, e)
    r = motor.ejecutar()
    assert r["base"]["factible"] and r["ahorro"]["factible"]
    assert r["optimizacion"]["mejor"] and not r["optimizacion"]["demanda_habilitada"]
    cambiado = motor.evaluar("Cambio fuera de soporte", .5, .5, "display")
    assert not cambiado["factible"] and not cambiado["elegible"]
    assert any("soporte observado" in m for m in cambiado["restricciones"])


def test_orquestador_sin_mundo_ni_verdad():
    for f in Path("app/escenarios").glob("*.py"):
        fuente = f.read_text()
        arbol = ast.parse(fuente)
        assert all(not (n.module or "").startswith("app.datos") for n in ast.walk(arbol) if isinstance(n, ast.ImportFrom))
        assert "verdad_sintetica" not in fuente and "demanda_proxy" not in fuente


@pytest.fixture
def escenarios_client():
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


def test_api_comparacion_guardada_checksum_reuso_y_search_comun(escenarios_client):
    c, db = escenarios_client
    n = db.scalar(select(func.count()).select_from(Ejecucion))
    catalogo = c.get("/api/v1/escenarios")
    assert catalogo.status_code == 200, catalogo.text
    assert db.scalar(select(func.count()).select_from(Ejecucion)) == n
    assert catalogo.json()["modelos"]["mmm"]["estado"] == "bloqueado"
    pedidos = db.scalar(select(func.sum(NegocioDiario.pedidos)))
    entrada = dict(nombre="Fixture explícita de comparación", recorte_pct=50, cuota_plataforma=100)
    respuesta = c.post("/api/v1/escenarios/ejecutar", json=entrada)
    assert respuesta.status_code == 200, respuesta.text
    a = respuesta.json()
    assert not a["reutilizada"] and a["revision"] == 1 and a["resultado"]["replicas"] == 200
    assert a["resultado"]["inicio"] == "2026-11-01" and a["resultado"]["fin"] == "2026-11-28"
    assert "draws" not in a["resultado"]["base"] and "indices_search" not in a["resultado"]["traza_draws"]
    r = c.post("/api/v1/escenarios/ejecutar", json=entrada).json()
    assert r["id"] == a["id"] and r["reutilizada"] and r["resultado"] == a["resultado"]
    completa = c.post("/api/v1/escenarios/ejecutar", json=a["entradas"]).json()
    assert completa["id"] == a["id"] and completa["reutilizada"]
    assert c.get("/api/v1/escenarios/ejecuciones/"+a["id"]).json() == a
    assert db.scalar(select(func.count()).select_from(Ejecucion)) == n+1
    source = c.post("/api/v1/busqueda/simular", json=dict(recorte_pct=50, cuota_plataforma=100)).json()
    search = source["resultado"]
    assert a["resultado"]["ahorro"]["delta"] == pytest.approx(search["delta"], abs=.001)
    assert not a["resultado"]["optimizacion"]["demanda_habilitada"]
    origen = c.get("/api/v1/escenarios?simulacion="+source["id"]).json()
    assert origen["defecto"]["cuota_plataforma"] == 100
    assert origen["origen_search"]["id"] == source["id"]
    derivada = c.post("/api/v1/escenarios/ejecutar", json={**entrada, "simulacion_search_id": source["id"]}).json()
    assert derivada["modelos"]["search_origen"] == source["resultado"]["modelo"]
    assert derivada["resultado"]["origen_search"]["id"] == source["id"]
    assert db.scalar(select(func.sum(NegocioDiario.pedidos))) == pedidos
    assert snapshot_actual(db).checksum == "6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d"


def test_api_seleccion_aprendizaje_y_ejecuciones_anteriores_inmutables(escenarios_client):
    c, db = escenarios_client
    p = c.post("/api/v1/creativos/evaluar", json=dict(objetivo="Fixture de selección en escenario", frecuencia=4.312345)).json()
    s = c.post("/api/v1/creativos/selecciones", json=dict(pretest_id=p["id"], variante_id=p["variantes"][1]["id"])).json()
    entrada = dict(nombre="Fixture con creatividad", seleccion_creativa_id=s["id"], coste_produccion=200)
    contexto = c.get("/api/v1/escenarios?seleccion="+s["id"]).json()
    assert contexto["defecto"]["seleccion_creativa_id"] == s["id"]
    assert c.post("/api/v1/escenarios/ejecutar", json={**entrada, "canal_reinversion": "display"}).status_code == 422
    primera = c.post("/api/v1/escenarios/ejecutar", json=entrada)
    assert primera.status_code == 200, primera.text
    a = primera.json()
    conservado = copy.deepcopy(db.get(Ejecucion, a["id"]).resultado)
    ab = c.post("/api/v1/creativos/pruebas/disenar", json=dict(pretest_id=p["id"], control=p["variantes"][0]["id"],
        tratamientos=[p["variantes"][1]["id"]], nombre="Fixture A/B para versión del escenario")).json()
    uri = "/api/v1/creativos/pruebas/"+ab["id"]
    for paso in ("ejecutar", "evaluar", "aceptar"):
        respuesta = c.post(uri+"/"+paso, json={})
        assert respuesta.status_code == 200, respuesta.text
    b = c.post("/api/v1/escenarios/ejecutar", json=entrada).json()
    assert b["id"] != a["id"] and b["escenario"] == a["escenario"]
    assert b["modelos"]["creativo_ab"] and a["modelos"]["creativo_ab"] is None
    assert b["resultado"]["reinversion"]["delta"] == a["resultado"]["reinversion"]["delta"]
    assert b["resultado"]["reinversion"]["metricas"]["creatividad"] == 200
    assert b["resultado"]["reinversion"]["multiplicador_demanda"] == 1
    assert db.get(Ejecucion, a["id"]).resultado == conservado
    assert c.get("/api/v1/escenarios/ejecuciones/"+a["id"]).json() == a
    assert modelo_actual(db, snapshot_actual(db)).resultado["estado"] == "bloqueado"


def test_api_validacion_inviabilidad_y_bloqueo_critico(escenarios_client, monkeypatch):
    c, db = escenarios_client
    assert c.post("/api/v1/escenarios/ejecutar", json={"mercado": "m01"}).status_code == 422
    assert c.post("/api/v1/escenarios/ejecutar", json={"optimizable": True}).status_code == 422
    assert c.post("/api/v1/escenarios/ejecutar", json={"canal_reinversion": "sem_marca"}).status_code == 422
    assert c.post("/api/v1/escenarios/ejecutar", json={"coste_produccion": 100}).status_code == 422
    assert c.get("/api/v1/escenarios?simulacion=ajena").status_code == 404
    assert c.post("/api/v1/escenarios/ejecutar", json={"limites": [{"canal": "meta", "minimo": 100, "maximo": 0}]}).status_code == 422
    imposible = c.post("/api/v1/escenarios/ejecutar", json={"presupuesto_total": 0})
    assert imposible.status_code == 200, imposible.text
    a = imposible.json()
    assert a["resultado"]["optimizacion"]["mejor"] is None
    n = db.scalar(select(func.count()).select_from(Ejecucion))
    monkeypatch.setattr(servicio, "fiabilidad", lambda _: SimpleNamespace(estado="bloqueado"))
    assert c.post("/api/v1/escenarios/ejecutar", json={"nombre": "Fixture bloqueada"}).status_code == 409
    assert db.scalar(select(func.count()).select_from(Ejecucion)) == n
    assert c.get("/api/v1/escenarios/ejecuciones/"+a["id"]).status_code == 200
