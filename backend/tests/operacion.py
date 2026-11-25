"""Comprobación manual de persistencia/reset en la pila margia-validacion.

No se ejecuta dentro de pytest ni contra la demo de presentación.
"""
import json
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.main import app
from app.modelos.mmm import VERSION
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
    modelo_reproducible = {k: v for k, v in modelo.resultado.items() if k != "segundos_ajuste"}
    if action == "preparar":
        db.add(Decision(id="qa-persistencia", snapshot_id=snapshot.id,
                        ejecucion_id="fixture-operacion-sin-ejecucion", estado="archivado",
                        motivo="Fixture explícita para verificar persistencia, no decisión de negocio.",
                        evidencia={"tipo": "Fixture de prueba operativa"}))
        expected.write_text(json.dumps({"checksum": snapshot.checksum,
                                        "conteos": snapshot.manifiesto["conteos"],
                                        "modelo": modelo_reproducible,
                                        "modelo_creado": modelo.creado.isoformat()}), encoding="utf-8")
        print("Fixture de persistencia y MMM preparados en PostgreSQL de validación.")
    elif action == "verificar":
        assert db.get(Decision, "qa-persistencia") is not None
        assert snapshot.checksum == json.loads(expected.read_text())["checksum"]
        assert db.scalar(select(func.count()).select_from(NegocioDiario)) == 17520
        assert modelo_reproducible == json.loads(expected.read_text())["modelo"]
        assert modelo.creado.isoformat() == json.loads(expected.read_text())["modelo_creado"]
        print("Reinicio: decisión, checksum, negocio y artefacto MMM conservados sin reentrenar.")
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
        assert client.get("/api/v1/modelos/mmm").status_code == 200
        print(json.dumps({"reinicio": "correcto", "reset": result.json()}, ensure_ascii=False))
    else:
        raise ValueError("Acción no válida.")
