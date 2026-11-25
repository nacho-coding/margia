"""Comprobación manual de persistencia/reset en la pila margia-validacion.

No se ejecuta dentro de pytest ni contra la demo de presentación.
"""
import json
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.creatividad.servicio import actual as creatividad_actual
from app.main import app
from app.modelos.ab import VERSION_AB
from app.modelos.mmm import VERSION
from app.modelos.search import VERSION as VERSION_SEARCH
from app.modelos.search_servicio import search_actual
from app.persistencia.db import SessionLocal
from app.persistencia.tablas import Decision, Modelo, NegocioDiario, Snapshot

if os.environ.get("MARGIA_VALIDACION") != "1":
    raise RuntimeError("Solo se ejecuta con MARGIA_VALIDACION=1 en la pila aislada de QA.")

client = TestClient(app)
expected = Path("/app/evaluacion/operacion.json")
action = sys.argv[1]
with SessionLocal.begin() as db:
    snapshot = db.scalar(select(Snapshot))
    modelo = db.scalar(select(Modelo).where(Modelo.snapshot_id == snapshot.id, Modelo.version == VERSION))
    search = db.scalar(select(Modelo).where(Modelo.snapshot_id == snapshot.id, Modelo.version == VERSION_SEARCH))
    creativo = creatividad_actual(db, snapshot)
    creativo_reproducible = {k: v for k, v in creativo.resultado.items() if k != "segundos_ajuste"}
    modelo_reproducible = {k: v for k, v in modelo.resultado.items() if k != "segundos_ajuste"}
    if action == "preparar":
        db.add(Decision(id="qa-persistencia", snapshot_id=snapshot.id,
                        ejecucion_id="fixture-operacion-sin-ejecucion", estado="archivado",
                        motivo="Fixture explícita para verificar persistencia, no decisión de negocio.",
                        evidencia={"tipo": "Fixture de prueba operativa"}))
        simulacion = client.post("/api/v1/busqueda/simular", json={"recorte_pct": 50, "cuota_plataforma": 6000}).json()
        geo = client.post("/api/v1/experimentos/disenar", json={"nombre": "Fixture operativa geo de persistencia"}).json()
        uri = "/api/v1/experimentos/"+geo["id"]
        assert client.post(uri+"/ejecutar", json={}).status_code == 200
        evaluado = client.post(uri+"/evaluar", json={})
        assert evaluado.status_code == 200 and evaluado.json()["protocolo"]["evaluacion"]["compatible"]
        aceptado = client.post(uri+"/aceptar", json={})
        assert aceptado.status_code == 200, aceptado.text
        geo = {**aceptado.json(), "reutilizada": False}
        vigente = search_actual(db, snapshot)
        pretest = client.post("/api/v1/creativos/evaluar", json={"objetivo": "Fixture operativa creativa de persistencia"})
        assert pretest.status_code == 200, pretest.text
        pretest = {**pretest.json(), "reutilizada": True}
        seleccion = client.post("/api/v1/creativos/selecciones", json={"pretest_id": pretest["id"], "variante_id": pretest["variantes"][0]["id"]})
        assert seleccion.status_code == 200, seleccion.text
        seleccion = {**seleccion.json(), "reutilizada": True}
        ab = client.post("/api/v1/creativos/pruebas/disenar", json={"pretest_id": pretest["id"],
            "control": pretest["variantes"][0]["id"], "tratamientos": [v["id"] for v in pretest["variantes"][1:]],
            "nombre": "Fixture operativa A/B de persistencia"})
        assert ab.status_code == 200, ab.text
        ab_uri = "/api/v1/creativos/pruebas/"+ab.json()["id"]
        assert client.post(ab_uri+"/ejecutar", json={}).status_code == 200
        assert client.post(ab_uri+"/evaluar", json={}).status_code == 200
        ab = client.post(ab_uri+"/aceptar", json={})
        assert ab.status_code == 200, ab.text
        ab = {**ab.json(), "reutilizada": False}
        modelo_ab = db.get(Modelo, ab["protocolo"]["actualizacion"]["modelo"])
        expected.write_text(json.dumps({"checksum": snapshot.checksum,
                                        "conteos": snapshot.manifiesto["conteos"],
                                        "modelo": modelo_reproducible,
                                        "modelo_creado": modelo.creado.isoformat(),
                                        "search": search.resultado,
                                        "simulacion": simulacion, "geo": geo,
                                        "search_vigente": vigente.resultado,
                                        "search_vigente_creado": vigente.creado.isoformat(),
                                        "creatividad": creativo_reproducible, "creatividad_creado": creativo.creado.isoformat(),
                                        "pretest": pretest, "seleccion_creativa": seleccion, "ab_creativo": ab,
                                        "modelo_ab": modelo_ab.resultado, "modelo_ab_creado": modelo_ab.creado.isoformat()}), encoding="utf-8")
        print("Fixtures de persistencia, MMM, geo, Search, creatividad y A/B preparadas en PostgreSQL de validación.")
    elif action == "verificar":
        assert db.get(Decision, "qa-persistencia") is not None
        assert snapshot.checksum == json.loads(expected.read_text())["checksum"]
        assert db.scalar(select(func.count()).select_from(NegocioDiario)) == 17520
        assert modelo_reproducible == json.loads(expected.read_text())["modelo"]
        assert modelo.creado.isoformat() == json.loads(expected.read_text())["modelo_creado"]
        assert search.resultado == json.loads(expected.read_text())["search"]
        guardada = json.loads(expected.read_text())["simulacion"]
        assert client.get("/api/v1/busqueda/simulaciones/"+guardada["id"]).json()["resultado"] == guardada["resultado"]
        geo = json.loads(expected.read_text())["geo"]
        assert client.get("/api/v1/experimentos/"+geo["id"]).json() == geo
        vigente = search_actual(db, snapshot)
        assert vigente.resultado == json.loads(expected.read_text())["search_vigente"]
        assert vigente.creado.isoformat() == json.loads(expected.read_text())["search_vigente_creado"]
        datos = json.loads(expected.read_text())
        assert creativo_reproducible == datos["creatividad"]
        assert creativo.creado.isoformat() == datos["creatividad_creado"]
        assert client.get("/api/v1/creativos/evaluaciones/"+datos["pretest"]["id"]).json() == datos["pretest"]
        assert client.get("/api/v1/creativos/selecciones/"+datos["seleccion_creativa"]["id"]).json() == datos["seleccion_creativa"]
        assert client.get("/api/v1/creativos/pruebas/"+datos["ab_creativo"]["id"]).json() == datos["ab_creativo"]
        modelo_ab = db.get(Modelo, datos["ab_creativo"]["protocolo"]["actualizacion"]["modelo"])
        assert modelo_ab.resultado == datos["modelo_ab"]
        assert modelo_ab.creado.isoformat() == datos["modelo_ab_creado"]
        print("Reinicio: hechos, MMM, geo, Search, pretest, selección, protocolo/observaciones A/B y aprendizaje conservados sin reentrenar ni reejecutar.")
    elif action == "reset":
        before = snapshot.checksum
        assert client.post("/api/v1/demo/reset", json={"confirmacion": "NO"}).status_code == 422
        result = client.post("/api/v1/demo/reset", json={"confirmacion": "RESTABLECER DEMO"})
        assert result.status_code == 200, result.text
        assert result.json()["checksum"] == before
        assert client.get("/api/v1/decisiones").json()["filas"] == []
        assert client.get("/api/v1/contexto").json()["manifiesto"]["conteos"] == snapshot.manifiesto["conteos"]
        with SessionLocal() as despues:
            nuevo = despues.scalar(select(Modelo).where(Modelo.version == VERSION))
            assert {k: v for k, v in nuevo.resultado.items() if k != "segundos_ajuste"} == modelo_reproducible
            assert nuevo.creado != modelo.creado
            search_nuevo = despues.scalar(select(Modelo).where(Modelo.version == VERSION_SEARCH))
            assert search_nuevo.resultado == search.resultado
        guardada = json.loads(expected.read_text())["simulacion"]
        assert client.get("/api/v1/busqueda/simulaciones/"+guardada["id"]).status_code == 404
        geo = json.loads(expected.read_text())["geo"]
        assert client.get("/api/v1/experimentos/"+geo["id"]).status_code == 404
        assert client.get("/api/v1/busqueda/evidencia").json()["modelo"]["id"] == search.id
        assert len(client.get("/api/v1/experimentos").json()["filas"]) == 12
        datos = json.loads(expected.read_text())
        assert client.get("/api/v1/creativos/evaluaciones/"+datos["pretest"]["id"]).status_code == 404
        assert client.get("/api/v1/creativos/selecciones/"+datos["seleccion_creativa"]["id"]).status_code == 404
        assert client.get("/api/v1/creativos/historial").json()["filas"] == []
        assert client.get("/api/v1/creativos/pruebas/"+datos["ab_creativo"]["id"]).status_code == 404
        assert client.get("/api/v1/creativos/pruebas").json()["filas"] == []
        with SessionLocal() as despues:
            actual_creativo = creatividad_actual(despues, snapshot)
            assert {k: v for k, v in actual_creativo.resultado.items() if k != "segundos_ajuste"} == creativo_reproducible
            assert actual_creativo.creado != creativo.creado
            assert despues.scalar(select(func.count()).select_from(Modelo).where(Modelo.version == VERSION_AB)) == 0
        assert client.get("/api/v1/modelos/mmm").status_code == 200
        print(json.dumps({"reinicio": "correcto", "reset": result.json()}, ensure_ascii=False))
    else:
        raise ValueError("Acción no válida.")
