import copy
import csv
import importlib
import io
import os
from types import SimpleNamespace

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.escenarios import decisiones, servicio
from app.main import app
from app.persistencia.db import engine, get_db
from app.persistencia.tablas import Decision, Ejecucion, EventoEscenario, NegocioDiario


@pytest.fixture
def gestion_client():
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


def crear(c, **parametros):
    r = c.post("/api/v1/escenarios", json={"nombre": "Fixture explícita de borrador", **parametros})
    assert r.status_code == 200, r.text
    return r.json()


def ejecutar(c, s):
    r = c.post(f"/api/v1/escenarios/{s['id']}/ejecutar", json={"revision": s["revision"]})
    assert r.status_code == 200, r.text
    return r.json()


def uri(e):
    return f"/api/v1/escenarios/ejecuciones/{e['id']}"


def test_borrador_guardar_no_ejecuta_lecturas_no_crean_resultados(gestion_client, monkeypatch):
    c, db = gestion_client
    n = db.scalar(select(func.count()).select_from(Ejecucion))
    def no_calcular(_):
        raise AssertionError("Guardar o leer no debe ejecutar el motor.")
    monkeypatch.setattr(servicio.MotorEscenarios, "ejecutar", no_calcular)
    s = crear(c)
    assert s["editable"] and s["estado"] == "borrador" and s["revision"] == 1
    assert s["ejecuciones"] == [] and len(s["revisiones"]) == 1
    assert s["eventos"][0]["tipo"] == "creado"
    assert c.get("/api/v1/escenarios/"+s["id"]).json() == s
    catalogo = c.get("/api/v1/escenarios").json()
    assert s["id"] in {f["id"] for f in catalogo["escenarios"]}
    assert db.scalar(select(func.count()).select_from(Ejecucion)) == n


def test_revisiones_concurrencia_reuso_ejecucion_y_resultado_congelado(gestion_client):
    c, db = gestion_client
    s = crear(c)
    e = ejecutar(c, s)
    matriz = copy.deepcopy(db.get(Ejecucion, e["id"]).resultado)
    assert ejecutar(c, s)["id"] == e["id"] and ejecutar(c, s)["reutilizada"]
    cambio = {**s["parametros"], "nombre": "Fixture revisada", "cuota_plataforma": 650.}
    ruta = "/api/v1/escenarios/"+s["id"]
    r = c.patch(ruta, json=dict(revision=1, parametros=cambio))
    assert r.status_code == 200, r.text
    s2 = r.json()
    assert s2["revision"] == 2 and len(s2["revisiones"]) == 2
    assert s2["revisiones"][-1]["parametros"] == s["parametros"]
    assert c.patch(ruta, json=dict(revision=1, parametros=cambio)).status_code == 409
    assert c.post(ruta+"/ejecutar", json=dict(revision=1)).status_code == 409
    assert c.patch(ruta, json=dict(revision=2, parametros=cambio)).json()["revision"] == 2
    e2 = ejecutar(c, s2)
    assert e2["id"] != e["id"] and e2["revision"] == 2
    assert e2["resultado"]["ahorro"]["delta"] == pytest.approx(e["resultado"]["ahorro"]["delta"]-650.)
    assert c.get(uri(e)).json() == e
    assert db.get(Ejecucion, e["id"]).resultado == matriz
    ctx = c.get(uri(e)+"/decision").json()
    assert all(not p["aprobable"] for p in ctx["planes"])
    assert any("revisión posterior" in m for m in ctx["planes"][0]["motivos"])


def test_duplicar_archivar_con_motivo_preserva_historia_y_decision(gestion_client):
    c, db = gestion_client
    s = crear(c)
    e = ejecutar(c, s)
    body = dict(plan="base", estado="aprobado", motivo="Conservar la estrategia actual con sus límites.")
    d = c.post(uri(e)+"/decision", json=body)
    assert d.status_code == 200, d.text
    ruta = "/api/v1/escenarios/"+s["id"]
    assert c.post(ruta+"/archivar", json=dict(revision=1, motivo="corto")).status_code == 422
    archivado = c.post(ruta+"/archivar", json=dict(revision=1, motivo="Cierre explícito del borrador de prueba."))
    assert archivado.status_code == 200 and archivado.json()["estado"] == "archivado"
    n = db.scalar(select(func.count()).select_from(EventoEscenario))
    assert c.post(ruta+"/archivar", json=dict(revision=1, motivo="Cierre explícito del borrador de prueba.")).status_code == 200
    assert c.post(ruta+"/archivar", json=dict(revision=1, motivo="Intento de sustituir el motivo del archivo.")).status_code == 409
    assert db.scalar(select(func.count()).select_from(EventoEscenario)) == n
    assert c.post(ruta+"/ejecutar", json=dict(revision=1)).status_code == 409
    assert c.patch(ruta, json=dict(revision=1, parametros=s["parametros"])).status_code == 409
    copia = c.post(ruta+"/duplicar", json=dict(nombre="Copia explícita archivada"))
    assert copia.status_code == 200, copia.text
    s2 = copia.json()
    assert s2["id"] != s["id"] and s2["revision"] == 1 and s2["estado"] == "borrador"
    assert not s2["ejecuciones"] and s2["parametros"]["nombre"] == "Copia explícita archivada"
    assert c.get(uri(e)).json() == e
    assert c.get("/api/v1/decisiones/"+d.json()["id"]).json() == d.json()


def test_configuracion_d43_solo_lectura_y_duplicacion_editable(gestion_client):
    c, _ = gestion_client
    e = c.post("/api/v1/escenarios/ejecutar", json={"nombre": "Fixture histórica D4.3"}).json()
    ruta = "/api/v1/escenarios/"+e["escenario"]
    s = c.get(ruta).json()
    assert not s["editable"] and s["estado"] == "evaluado" and len(s["revisiones"]) == 1
    assert c.patch(ruta, json=dict(revision=1, parametros=s["parametros"])).status_code == 409
    assert c.post(ruta+"/duplicar", json=dict(nombre="Copia para edición")).json()["editable"]


def test_decision_terminal_motivo_reuso_conflicto_historial_y_evidencia(gestion_client):
    c, db = gestion_client
    s = crear(c)
    e = ejecutar(c, s)
    antes = db.scalar(select(func.sum(NegocioDiario.pedidos)))
    base = dict(plan="base", estado="aprobado", motivo="Mantener hasta contar con evidencia de reparto defendible.")
    assert c.post(uri(e)+"/decision", json={**base, "motivo": "  "}).status_code == 422
    assert c.post(uri(e)+"/decision", json={**base, "estado": "archivado"}).status_code == 422
    n = db.scalar(select(func.count()).select_from(Decision))
    respuesta = c.post(uri(e)+"/decision", json=base)
    assert respuesta.status_code == 200, respuesta.text
    d = respuesta.json()
    assert c.post(uri(e)+"/decision", json=base).json() == d
    assert c.post(uri(e)+"/decision", json={**base, "estado": "rechazado"}).status_code == 409
    assert db.scalar(select(func.count()).select_from(Decision)) == n+1
    assert d["evidencia"]["metricas"] == e["resultado"]["base"]["metricas"]
    assert d["evidencia"]["guardrails"]["aprobable"] and not d["evidencia"]["activa_publicidad"]
    assert c.get(uri(e)+"/decision").json()["decision"] == d
    assert c.get("/api/v1/decisiones/"+d["id"]).json() == d
    assert d["id"] in {f["id"] for f in c.get("/api/v1/decisiones").json()["filas"]}
    assert db.scalar(select(func.sum(NegocioDiario.pedidos))) == antes
    assert c.get(uri(e)).json() == e


def test_mmm_bloqueado_impide_b_permite_mantener_y_rechazar(gestion_client):
    c, _ = gestion_client
    e = ejecutar(c, crear(c))
    planes = {p["id"]: p for p in c.get(uri(e)+"/decision").json()["planes"]}
    assert planes["base"]["aprobable"] and not planes["reinversion"]["aprobable"]
    body = dict(plan="reinversion", estado="aprobado", motivo="Fixture explícita de intento directo de aprobación.")
    bloqueada = c.post(uri(e)+"/decision", json=body)
    assert bloqueada.status_code == 409 and "MMM" in bloqueada.text
    rechazada = c.post(uri(e)+"/decision", json={**body, "estado": "rechazado"})
    assert rechazada.status_code == 200
    assert not rechazada.json()["evidencia"]["guardrails"]["aprobable"]


def test_datos_criticos_bloquean_api_y_rechazo_sigue_disponible(gestion_client, monkeypatch):
    c, _ = gestion_client
    e = ejecutar(c, crear(c))
    monkeypatch.setattr(decisiones, "fiabilidad", lambda _: SimpleNamespace(estado="bloqueado"))
    def no_cargar(_):
        raise AssertionError("Un bloqueo crítico debe impedir la aprobación incluso sin modelos disponibles.")
    monkeypatch.setattr(decisiones, "cargar", no_cargar)
    body = dict(plan="base", estado="aprobado", motivo="Fixture de datos críticos incompletos para aprobación.")
    assert c.post(uri(e)+"/decision", json=body).status_code == 409
    assert c.get(uri(e)).status_code == 200
    assert c.post(uri(e)+"/decision", json={**body, "estado": "rechazado"}).status_code == 200


def test_version_search_obsoleta_solo_bloquea_planes_dependientes(gestion_client, monkeypatch):
    c, _ = gestion_client
    e = ejecutar(c, crear(c, riesgo_max_pct=100))
    original = decisiones.cargar
    def version_posterior(db):
        snapshot, mmm, actual, semanas, referencia = original(db)
        return snapshot, mmm, SimpleNamespace(id="fixture-explicita-version-posterior", resultado=actual.resultado), semanas, referencia
    monkeypatch.setattr(decisiones, "cargar", version_posterior)
    filas = {p["id"]: p for p in c.get(uri(e)+"/decision").json()["planes"]}
    assert filas["base"]["aprobable"]
    assert not filas["ahorro"]["aprobable"] and any("ha cambiado" in m for m in filas["ahorro"]["motivos"])
    body = dict(plan="ahorro", estado="aprobado", motivo="Fixture de intento con versión de Search obsoleta.")
    assert c.post(uri(e)+"/decision", json=body).status_code == 409


def test_presupuesto_inviable_no_se_aprueba_y_se_puede_registrar_abstencion(gestion_client):
    c, _ = gestion_client
    e = ejecutar(c, crear(c, presupuesto_total=0))
    planes = c.get(uri(e)+"/decision").json()["planes"]
    assert all(not p["aprobable"] for p in planes)
    body = dict(plan="optimizacion", estado="aprobado", motivo="Fixture de rejilla sin candidato y presupuesto inviable.")
    assert c.post(uri(e)+"/decision", json=body).status_code == 409
    rechazo = c.post(uri(e)+"/decision", json={**body, "estado": "rechazado"})
    assert rechazo.status_code == 200 and rechazo.json()["evidencia"]["metricas"] is None


def test_archivado_bloquea_nueva_aprobacion_sin_borrar_resultados(gestion_client):
    c, _ = gestion_client
    s = crear(c)
    e = ejecutar(c, s)
    c.post(f"/api/v1/escenarios/{s['id']}/archivar", json=dict(revision=1, motivo="Archivo del escenario sin decisión previa."))
    body = dict(plan="base", estado="aprobado", motivo="Fixture de aprobación sobre escenario archivado.")
    assert c.post(uri(e)+"/decision", json=body).status_code == 409
    assert c.get(uri(e)).json() == e


def test_exportacion_fiel_sin_recalcular_escape_y_decision(gestion_client, monkeypatch):
    c, _ = gestion_client
    nombre = '=HYPERLINK("https://ejemplo.invalid") | <script>ejemplo</script>'
    e = ejecutar(c, crear(c, nombre=nombre))
    motivo = "@SUM(1+1) | <img src=x onerror=ejemplo>\n# Motivo de prueba"
    d = c.post(uri(e)+"/decision", json=dict(plan="base", estado="aprobado", motivo=motivo)).json()
    def no_calcular(_):
        raise AssertionError("Exportar nunca debe ejecutar el motor.")
    monkeypatch.setattr(servicio.MotorEscenarios, "ejecutar", no_calcular)
    r = c.get(uri(e)+"/exportar?formato=csv")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/csv")
    assert ".csv" in r.headers["content-disposition"] and r.headers["cache-control"] == "no-store"
    filas = list(csv.DictReader(io.StringIO(r.text.lstrip("\ufeff")), delimiter=";"))
    assert next(f for f in filas if f["magnitud"] == "nombre")["valor"] == "'"+nombre
    assert next(f for f in filas if f["seccion"] == "decision" and f["magnitud"] == "motivo")["valor"] == "'"+motivo
    for plan in ("base", "ahorro", "reinversion"):
        valores = {f["magnitud"]: float(f["valor"].replace(",", ".")) for f in filas if f["seccion"] == "economia" and f["plan"] == plan}
        assert valores["contribucion"] == e["resultado"][plan]["metricas"]["contribucion"]
        assert valores["delta"] == e["resultado"][plan]["delta"]
        assert valores["margen"]-sum(valores[k] for k in ("inversion", "creatividad", "experimento", "plataforma", "otros")) == pytest.approx(valores["contribucion"])
    md = c.get(uri(e)+"/exportar?formato=md")
    assert md.status_code == 200 and e["id"] in md.text and d["id"] in md.text
    assert "<script>" not in md.text and "<img" not in md.text
    assert "\\|" in md.text and "&lt;script&gt;" in md.text and "# MARGIA" in md.text
    assert c.get(uri(e)).json() == e


def test_identificadores_inputs_exportaciones_y_motivo_largo(gestion_client):
    c, _ = gestion_client
    assert c.get("/api/v1/escenarios/inexistente").status_code == 404
    assert c.get("/api/v1/decisiones/inexistente").status_code == 404
    assert c.get("/api/v1/escenarios/ejecuciones/inexistente/exportar").status_code == 404
    assert c.post("/api/v1/escenarios", json={"mercado": "m01"}).status_code == 422
    assert c.post("/api/v1/escenarios", json={"editable": True}).status_code == 422
    s = crear(c)
    e = ejecutar(c, s)
    assert c.get(uri(e)+"/exportar?formato=html").status_code == 422
    assert c.post(uri(e)+"/decision", json=dict(plan="base", estado="aprobado", motivo="x"*1000)).status_code == 200


def test_plan_adverso_no_se_aprueba_aunque_se_tolere_todo_el_riesgo(gestion_client):
    c, _ = gestion_client
    e = ejecutar(c, crear(c, cuota_plataforma=1000000, riesgo_max_pct=100))
    assert e["resultado"]["ahorro"]["bandas"]["delta"]["media"] < 0
    r = c.post(uri(e)+"/decision", json=dict(plan="ahorro", estado="aprobado", motivo="Fixture de plan adverso sin límite de probabilidad de pérdida."))
    assert r.status_code == 409 and "no mejora la contribución" in r.text


def test_fuentes_observadas_cambiadas_bloquean_y_conservan_ejecucion(gestion_client, monkeypatch):
    c, _ = gestion_client
    e = ejecutar(c, crear(c))
    original = decisiones.cargar
    def observaciones_revisadas(db):
        snapshot, mmm, search, semanas, ref = original(db)
        return snapshot, mmm, search, semanas, {**ref, "margen": ref["margen"]+100}
    monkeypatch.setattr(decisiones, "cargar", observaciones_revisadas)
    r = c.post(uri(e)+"/decision", json=dict(plan="base", estado="aprobado", motivo="Fixture de revisión de observaciones con snapshot conservado."))
    assert r.status_code == 409 and "fuentes observadas" in r.text
    assert c.get(uri(e)).json() == e


@pytest.mark.skipif(os.environ.get("MARGIA_VALIDACION") != "1", reason="DDL transaccional solo autorizado en QA aislada.")
def test_migracion_aditiva_recupera_revision_d43_sin_alterar_ejecucion(gestion_client):
    """DDL transaccional aislado y revertido por la fixture; no toca la pila principal."""
    c, db = gestion_client
    r = c.post("/api/v1/escenarios/ejecutar", json={"nombre": "Fixture explícita anterior a 0006"})
    assert r.status_code == 200, r.text
    e = r.json()
    antes = copy.deepcopy(db.get(Ejecucion, e["id"]).resultado)
    migracion = importlib.import_module("migrations.versions.0006_borradores")
    with Operations.context(MigrationContext.configure(db.connection())):
        migracion.downgrade()
        # La configuración y su resultado existen en el esquema 0005.
        assert db.scalar(text("SELECT count(*) FROM ejecucion WHERE id=:id"), {"id": e["id"]}) == 1
        migracion.upgrade()
    s = c.get("/api/v1/escenarios/"+e["escenario"]).json()
    assert not s["editable"] and s["revisiones"][0]["parametros"] == e["entradas"]
    assert s["revisiones"][0]["revision"] == 1
    assert db.get(Ejecucion, e["id"]).resultado == antes
    assert c.get(uri(e)).json() == e


@pytest.mark.parametrize("plan", ["ahorro", "optimizacion"])
def test_aprobar_search_respaldado_con_mmm_bloqueado(gestion_client, plan):
    c, _ = gestion_client
    e = ejecutar(c, crear(c, riesgo_max_pct=100))
    assert e["modelos"]["mmm"]["estado"] == "bloqueado"
    r = c.post(uri(e)+"/decision", json=dict(plan=plan, estado="aprobado",
        motivo="Decisión sintética condicionada al transporte de Search; se conserva el bloqueo del reparto MMM."))
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["evidencia"]["guardrails"]["aprobable"]
    assert d["evidencia"]["presupuestos"] == decisiones.plan_guardado(SimpleNamespace(resultado=e["resultado"]), plan)["presupuestos"]
