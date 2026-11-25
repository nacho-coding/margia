from fastapi import APIRouter

from app.api.consultas import Db
from app.api.geo_contratos import CatalogoGeo, DetalleGeo, DisenoGeo
from app.experimentos.servicio import accion, catalogo, crear, detalle

router = APIRouter(prefix="/api/v1/experimentos", tags=["Experimentos sintéticos"])


@router.get("", response_model=CatalogoGeo)
def listar(db: Db):
    return catalogo(db)


@router.post("/disenar", response_model=DetalleGeo)
def disenar(entrada: DisenoGeo, db: Db):
    return crear(db, entrada)


@router.get("/{experimento_id}", response_model=DetalleGeo)
def consultar(experimento_id: str, db: Db):
    return detalle(db, experimento_id)


@router.post("/{experimento_id}/ejecutar", response_model=DetalleGeo)
def ejecutar(experimento_id: str, db: Db):
    return accion(db, experimento_id, "ejecutar")


@router.post("/{experimento_id}/evaluar", response_model=DetalleGeo)
def evaluar(experimento_id: str, db: Db):
    return accion(db, experimento_id, "evaluar")


@router.post("/{experimento_id}/aceptar", response_model=DetalleGeo)
def aceptar(experimento_id: str, db: Db):
    return accion(db, experimento_id, "aceptar")
