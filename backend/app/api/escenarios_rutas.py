from fastapi import APIRouter, Query

from app.api.consultas import Db
from app.api.escenarios_contratos import EjecucionEscenarioRespuesta, ParametrosEscenario
from app.escenarios.servicio import catalogo, detalle, ejecutar

router = APIRouter(prefix="/api/v1/escenarios", tags=["Escenarios sintéticos"])


@router.get("")
def listar(db: Db, seleccion: str | None = Query(None, min_length=1, max_length=60),
           simulacion: str | None = Query(None, min_length=1, max_length=60)):
    return catalogo(db, seleccion, simulacion)


@router.post("/ejecutar", response_model=EjecucionEscenarioRespuesta)
def ejecutar_comparacion(entrada: ParametrosEscenario, db: Db):
    return ejecutar(db, entrada)


@router.get("/ejecuciones/{ejecucion_id}", response_model=EjecucionEscenarioRespuesta)
def consultar_ejecucion(ejecucion_id: str, db: Db):
    return detalle(db, ejecucion_id)
