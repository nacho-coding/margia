from fastapi import APIRouter

from app.api.consultas import Db
from app.api.creatividad_contratos import (
    EvaluacionCreativa,
    ParametrosPretest,
    SeleccionarCreativo,
    SeleccionRespuesta,
)
from app.creatividad.servicio import catalogo, consultar, evaluar, historial, seleccion, seleccionar

router = APIRouter(prefix="/api/v1/creativos", tags=["Creatividad sintética"])


@router.get("/pretest")
def obtener_contexto(db: Db):
    return catalogo(db)


@router.post("/evaluar", response_model=EvaluacionCreativa)
def evaluar_pretest(entrada: ParametrosPretest, db: Db):
    return evaluar(db, entrada)


@router.get("/evaluaciones/{pretest_id}", response_model=EvaluacionCreativa)
def obtener_pretest(pretest_id: str, db: Db):
    return consultar(db, pretest_id)


@router.post("/selecciones", response_model=SeleccionRespuesta)
def guardar_seleccion(entrada: SeleccionarCreativo, db: Db):
    return seleccionar(db, entrada)


@router.get("/selecciones/{seleccion_id}", response_model=SeleccionRespuesta)
def obtener_seleccion(seleccion_id: str, db: Db):
    return seleccion(db, seleccion_id)


@router.get("/historial")
def obtener_historial(db: Db):
    return historial(db)
