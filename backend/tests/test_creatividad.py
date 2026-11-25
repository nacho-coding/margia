import copy

import numpy as np
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from scipy.special import expit
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.consultas import snapshot_actual
from app.api.creatividad_contratos import ParametrosPretest
from app.creatividad.servicio import actual, asegurar_creatividad, observaciones
from app.main import app
from app.modelos.creatividad import (
    VERSION,
    ajustar_binomial,
    entrenar_creatividad,
    particionar,
    predecir_contexto,
)
from app.persistencia.db import engine, get_db
from app.persistencia.tablas import Modelo, NegocioDiario, PretestCreativo


@pytest.fixture
def creativo_client():
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


def test_binomial_pondera_exposiciones_y_no_promedia_tasas():
    beta = ajustar_binomial(np.ones((2, 1)), np.array([100., 9.]), np.array([10000., 10.]))
    assert expit(beta[0]) == pytest.approx(109/10010, rel=1e-5)
    assert expit(beta[0]) != pytest.approx((.01+.9)/2)
    with pytest.raises(ValueError):
        ajustar_binomial(np.ones((2, 1)), np.zeros(2), np.zeros(2))


def test_particiones_sin_fuga_y_holdout_no_cambia_parametros(db):
    s = snapshot_actual(db)
    filas = observaciones(db, s)
    train, holdout, descartadas = particionar(filas)
    assert max(f["fecha"] for f in train) < min(f["fecha"] for f in holdout)
    for campo in ("grupo", "asset", "campana", "id"):
        assert not {f[campo] for f in train} & {f[campo] for f in holdout}
    assert len(train)+len(holdout)+descartadas == len(filas) == 2240
    assert max(f["fecha"] for f in filas) <= s.corte.isoformat()
    referencia = actual(db, s).resultado
    modificadas = copy.deepcopy(filas)
    ids_holdout = {f["id"] for f in holdout}
    for f in modificadas:
        if f["id"] in ids_holdout and f["fecha"] >= min(h["fecha"] for h in holdout):
            f["clics"] = round(f["impresiones"]*referencia["referencias"][f["canal"]]["ctr"])
            f["conversiones"] = 0
    modelo = entrenar_creatividad(modificadas, s.semilla)
    assert modelo["parametros"] == referencia["parametros"]
    assert modelo["draws"] == referencia["draws"]
    assert modelo["holdout"] != referencia["holdout"]
    assert modelo["estado"] == "bloqueado"
    contexto = dict(canal="meta", categoria="hogar", tono="Editorial", cta="Descubre la colección", audiencia="Cohorte 01", frecuencia=2.5)
    punto = predecir_contexto(modelo, contexto)
    assert punto["ctr"] == modelo["referencias"]["meta"]["ctr"]
    assert punto["p05"] is None and punto["p95"] is None


def test_modelo_reproducible_soporte_y_band_bounded(db):
    s = snapshot_actual(db)
    guardado = actual(db, s)
    filas = observaciones(db, s)
    nuevo = entrenar_creatividad(filas, s.semilla)
    assert nuevo["parametros"] == guardado.resultado["parametros"]
    assert nuevo["draws"] == guardado.resultado["draws"]
    assert len(nuevo["draws"]) == 200
    assert asegurar_creatividad(db, s).id == guardado.id
    assert db.scalar(select(func.count()).select_from(Modelo).where(Modelo.version == VERSION)) == 1
    contexto = dict(canal="meta", categoria="hogar", tono="Editorial", cta="Descubre la colección", audiencia="Cohorte 01", frecuencia=2.5)
    p = predecir_contexto(nuevo, contexto)
    assert 0 <= p["p05"] < p["p95"] <= 1
    assert nuevo["holdout"]["log_loss"] < nuevo["naive"]["log_loss"]
    fuera = predecir_contexto(nuevo, {**contexto, "frecuencia": 9})
    assert any("Frecuencia" in m for m in fuera["motivos"])
    with pytest.raises(ValueError):
        predecir_contexto(nuevo, {**contexto, "cta": "CTA no observado"})
    with pytest.raises(ValueError):
        entrenar_creatividad(filas+filas[:1], s.semilla)
    mal = copy.deepcopy(filas)
    mal[0]["clics"] = mal[0]["impresiones"]+1
    with pytest.raises(ValueError):
        entrenar_creatividad(mal, s.semilla)


@pytest.mark.parametrize("entrada", [{"canal": "sem_marca"}, {"impresiones": 0}, {"impresiones": 1000001},
    {"frecuencia": float("nan")}, {"frecuencia": 0}, {"objetivo": ""}, {"ganador": "v1"}])
def test_pretest_valida_inputs(entrada):
    with pytest.raises(ValidationError):
        ParametrosPretest(**entrada)


def test_api_pretest_tres_variantes_honestas_y_seleccion_guardada(creativo_client):
    c, db = creativo_client
    catalogo = c.get("/api/v1/creativos/pretest").json()
    assert catalogo["modelo"]["version"] == VERSION
    assert "draws" not in catalogo["modelo"] and "parametros" not in catalogo["modelo"]
    conteo = db.scalar(select(func.sum(NegocioDiario.pedidos)))
    r = c.post("/api/v1/creativos/evaluar", json={})
    assert r.status_code == 200, r.text
    a = r.json()
    b = c.post("/api/v1/creativos/evaluar", json={}).json()
    assert a["id"] == b["id"] and b["reutilizada"]
    assert a["ganador"] is None and len(a["variantes"]) == 3
    assert len({v["asset"] for v in a["variantes"]}) == 3
    assert len({v["ctr_referencia"] for v in a["variantes"]}) == 1
    assert all(v["multiplicador_demanda"] == 1 and not v["efecto_diferencial_identificado"] for v in a["variantes"])
    assert a["referencia"]["clics_esperados"] == pytest.approx(10000*a["referencia"]["ctr"])
    assert "Plantilla determinista" in a["brief"]["metodo"]
    assert a["referencia"]["cvr_observado"] == pytest.approx(a["referencia"]["cvr_conversiones"]/a["referencia"]["cvr_clics"])
    mas = c.post("/api/v1/creativos/evaluar", json={"impresiones": 20000}).json()
    assert mas["id"] != a["id"]
    assert mas["referencia"]["clics_esperados"] == pytest.approx(2*a["referencia"]["clics_esperados"])
    consulta = c.get("/api/v1/creativos/evaluaciones/"+a["id"]).json()
    assert {k: v for k, v in consulta.items() if k != "reutilizada"} == {k: v for k, v in a.items() if k != "reutilizada"}
    datos = dict(pretest_id=a["id"], variante_id=a["variantes"][1]["id"])
    s = c.post("/api/v1/creativos/selecciones", json=datos)
    assert s.status_code == 200, s.text
    s = s.json()
    assert c.post("/api/v1/creativos/selecciones", json=datos).json()["id"] == s["id"]
    assert c.get("/api/v1/creativos/selecciones/"+s["id"]).json()["multiplicador_demanda"] == 1
    assert db.scalar(select(func.sum(NegocioDiario.pedidos))) == conteo
    assert db.get(PretestCreativo, a["id"]).modelo_id == a["modelo"]
    assert c.get("/api/v1/creativos/historial").json()["filas"]
    assert c.post("/api/v1/creativos/selecciones", json={**datos, "variante_id": "ajena"}).status_code == 422
    assert c.post("/api/v1/creativos/evaluar", json={"audiencia": "Cohorte 02"}).status_code == 422
    assert c.get("/api/v1/creativos/evaluaciones/inexistente").status_code == 404
    assert c.get("/api/v1/creativos/selecciones/inexistente").status_code == 404


def test_biblioteca_filtra_y_ordena_sin_sumar_medios(client):
    datos = client.get("/api/v1/creativos?canal=meta&categoria=hogar&audiencia=Cohorte%2001&orden=ctr").json()
    assert datos["filas"]
    assert all(f["categoria"] == "hogar" and f["atributos"]["audiencia"] == "Cohorte 01" for f in datos["filas"])
    assert [f["ctr"] for f in datos["filas"]] == sorted((f["ctr"] for f in datos["filas"]), reverse=True)
    assert client.get("/api/v1/creativos?objetivo=Captación").json()["total"] == 0
    assert client.get("/api/v1/creativos?formato=desconocido").status_code == 422
    assert client.get("/api/v1/creativos?orden=sql").status_code == 422


@pytest.mark.parametrize("canal,relacion", [("meta", "4:5"), ("tiktok", "9:16"), ("display", "1.91:1"), ("youtube", "16:9")])
def test_pretest_adapta_plataforma_sin_cambiar_evidencia(creativo_client, canal, relacion):
    c, db = creativo_client
    catalogo = c.get("/api/v1/creativos/pretest").json()
    audiencia = next(p for p in catalogo["canales"] if p["id"] == canal)["audiencias"][0]
    resultado = c.post("/api/v1/creativos/evaluar", json={"canal": canal, "audiencia": audiencia}).json()
    assert len(resultado["variantes"]) == 3
    for v in resultado["variantes"]:
        assert v["plataforma"]["id"] == canal and v["plataforma"]["relacion"] == relacion
        assert v["asset"].endswith(".webp") and v["version_recurso"] == "fotografia-2.0.0"
        assert v["ancho"] > 1000 and v["alto"] > v["ancho"] and v["bytes"] < 300000
        assert v["texto"]["cta"] == v["cta"] and "Imagen sintética" in v["alt"]
        assert not v["efecto_diferencial_identificado"] and v["multiplicador_demanda"] == 1
    assert len({v["ctr_referencia"] for v in resultado["variantes"]}) == 1
    biblioteca = c.get(f"/api/v1/creativos?canal={canal}").json()["filas"]
    assert biblioteca and all(f["asset"].endswith(".svg") for f in biblioteca)
    assert all(f["vista_previa"]["plataforma"]["id"] == canal and f["vista_previa"]["recreacion"] for f in biblioteca)
    assert all(f["vista_previa"]["asset_observado"] == f["asset"] for f in biblioteca)
    assert actual(db, snapshot_actual(db)).version == VERSION


def test_evaluaciones_anteriores_conservan_el_recurso_original(creativo_client):
    c, db = creativo_client
    actual_json = c.post("/api/v1/creativos/evaluar", json={}).json()
    anterior = {k: v for k, v in actual_json.items() if k not in ("id", "reutilizada")}
    anterior["variantes"] = [dict(id=f"hogar-{vid}", categoria="hogar", nombre="Composición original",
        composicion="Fixture explícita de evaluación de la versión anterior", asset=f"/assets/creatividad/pretest-hogar-{vid}.svg",
        tono="Editorial", cta="Descubre la colección", version_recurso="variantes-1.0.0", licencia="Original MARGIA · CC BY 4.0")
        for vid in ("espacio", "marco", "detalle")]
    pid = "pretest-version-anterior-qa"
    db.add(PretestCreativo(id=pid, snapshot_id=actual_json["snapshot"], modelo_id=actual_json["modelo"],
        entradas=actual_json["entradas"], resultado=anterior))
    db.commit()
    consulta = c.get("/api/v1/creativos/evaluaciones/"+pid).json()
    assert consulta == dict(id=pid, **anterior, reutilizada=True)
    assert c.post("/api/v1/creativos/evaluar", json={}).json()["id"] == actual_json["id"] != pid
    seleccion = c.post("/api/v1/creativos/selecciones", json={"pretest_id": pid, "variante_id": "hogar-marco"})
    assert seleccion.status_code == 200 and seleccion.json()["pretest_id"] == pid
