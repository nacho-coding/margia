from typing import Literal

from fastapi import APIRouter, Query

from app.api.consultas import Db
from app.api.escenarios_contratos import (
    ArchivarEscenario,
    DuplicarEscenario,
    EditarBorrador,
    EjecucionEscenarioRespuesta,
    ParametrosEscenario,
    RegistrarDecision,
    RevisionEsperada,
)
from app.escenarios import decisiones, gestion
from app.escenarios.exportacion import exportar
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


@router.get("/ejecuciones/{ejecucion_id}/decision")
def consultar_decision(ejecucion_id: str, db: Db):
    return decisiones.contexto(db, ejecucion_id)


@router.post("/ejecuciones/{ejecucion_id}/decision")
def registrar_decision(ejecucion_id: str, entrada: RegistrarDecision, db: Db):
    return decisiones.registrar(db, ejecucion_id, entrada)


@router.get("/ejecuciones/{ejecucion_id}/exportar")
def exportar_ejecucion(ejecucion_id: str, db: Db, formato: Literal["csv", "md"] = "csv"):
    return exportar(db, ejecucion_id, formato)


@router.post("")
def crear_borrador(entrada: ParametrosEscenario, db: Db):
    return gestion.crear(db, entrada)


@router.get("/{escenario_id}")
def consultar_borrador(escenario_id: str, db: Db):
    return gestion.consultar(db, escenario_id)


@router.patch("/{escenario_id}")
def editar_borrador(escenario_id: str, entrada: EditarBorrador, db: Db):
    return gestion.editar(db, escenario_id, entrada)


@router.post("/{escenario_id}/duplicar")
def duplicar_borrador(escenario_id: str, entrada: DuplicarEscenario, db: Db):
    return gestion.duplicar(db, escenario_id, entrada)


@router.post("/{escenario_id}/archivar")
def archivar_borrador(escenario_id: str, entrada: ArchivarEscenario, db: Db):
    return gestion.archivar(db, escenario_id, entrada)


@router.post("/{escenario_id}/ejecutar", response_model=EjecucionEscenarioRespuesta)
def ejecutar_revision(escenario_id: str, entrada: RevisionEsperada, db: Db):
    return gestion.ejecutar_borrador(db, escenario_id, entrada)
