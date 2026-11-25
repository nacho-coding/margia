import json
import time
from pathlib import Path

from sqlalchemy import insert, select, text

from app.datos.generador import CORTE, SEMILLA, VERSION, generar
from app.persistencia.db import Base, SessionLocal
from app.persistencia.tablas import Snapshot


def inicializar() -> dict:
    inicio = time.perf_counter()
    snapshot_id = f"aurel-{CORTE.isoformat()}-{SEMILLA}-{VERSION}"
    with SessionLocal.begin() as db:
        # Una única inicialización, incluso con dos procesos simultáneos.
        db.execute(text("SELECT pg_advisory_xact_lock(260725)"))
        existente = db.scalar(select(Snapshot).where(Snapshot.id == snapshot_id))
        if existente:
            return {"accion": "conservado", "snapshot": existente.id,
                    "checksum": existente.checksum}
        mundo = generar()
        db.add(Snapshot(id=snapshot_id, corte=CORTE, semilla=SEMILLA,
                        version=VERSION, checksum=mundo.manifiesto["checksum"],
                        manifiesto=mundo.manifiesto, estado="valido"))
        db.flush()
        for nombre, filas in mundo.tablas.items():
            tabla = Base.metadata.tables[nombre]
            for inicio_lote in range(0, len(filas), 2000):
                db.execute(insert(tabla), filas[inicio_lote:inicio_lote+2000])
    # Fixture de verdad fuera de tablas/modelos/API. Solo el evaluador puede leerla.
    destino = Path("/app/evaluacion")
    destino.mkdir(exist_ok=True)
    (destino / "verdad_sintetica.json").write_text(json.dumps(mundo.verdad_evaluacion), encoding="utf-8")
    return {"accion": "generado", "snapshot": snapshot_id,
            "checksum": mundo.manifiesto["checksum"],
            "filas": sum(mundo.manifiesto["conteos"].values()),
            "segundos": round(time.perf_counter()-inicio, 3)}


if __name__ == "__main__":
    print(json.dumps(inicializar(), ensure_ascii=False))
