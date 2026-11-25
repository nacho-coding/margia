from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.ab_contratos import AccionAB, DetalleAB, DisenoAB
from app.api.consultas import Db
from app.creatividad.experimentos import (
    accion,
    aprendizaje,
    asignaciones_csv,
    catalogo,
    crear,
    detalle,
    modelo_guardado,
)

router = APIRouter(prefix="/api/v1/creativos", tags=["A/B creativo sintético"])


@router.get("/pruebas")
def listar_pruebas(db: Db):
    return catalogo(db)


@router.post("/pruebas/disenar", response_model=DetalleAB)
def disenar(entrada: DisenoAB, db: Db):
    return crear(db, entrada)


@router.get("/pruebas/{prueba_id}", response_model=DetalleAB)
def obtener(prueba_id: str, db: Db):
    return detalle(db, prueba_id)


@router.post("/pruebas/{prueba_id}/{paso}", response_model=DetalleAB)
def ejecutar_accion(prueba_id: str, paso: str, entrada: AccionAB, db: Db):
    return accion(db, prueba_id, paso)


@router.get("/pruebas/{prueba_id}/asignaciones.csv")
def exportar(prueba_id: str, db: Db):
    return StreamingResponse(asignaciones_csv(db, prueba_id), media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{prueba_id}-asignaciones.csv"'})


@router.get("/aprendizaje/{pretest_id}")
def obtener_aprendizaje(pretest_id: str, db: Db):
    return aprendizaje(db, pretest_id)


@router.get("/aprendizaje/modelos/{modelo_id}")
def obtener_modelo(modelo_id: str, db: Db):
    return modelo_guardado(db, modelo_id)
