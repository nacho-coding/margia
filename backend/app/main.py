import csv
import io
import math
import time
from collections.abc import Iterator

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import case, delete, func, insert, select, text
from sqlalchemy.exc import SQLAlchemyError

from app.api.consultas import (
    Db,
    FiltroAPI,
    canales,
    contexto,
    fiabilidad,
    kpis,
    snapshot_actual,
)
from app.api.contratos import (
    ConfirmacionReset,
    Contexto,
    CurvasModelo,
    EvidenciaSearch,
    Fiabilidad,
    InventarioModelos,
    KPIs,
    MedicionModelo,
    ParametrosSearch,
    RadarSearch,
    Salud,
    SimulacionSearchRespuesta,
    TablaDatos,
)
from app.datos.generador import generar
from app.datos.historia_search import asegurar_historia
from app.dominio.economia import cociente
from app.modelos.search_servicio import (
    asegurar_search,
    evidencia,
    guardar_simulacion,
    oportunidades,
)
from app.modelos.servicio import asegurar_modelo, ficha, medicion, modelo_actual
from app.persistencia.db import Base
from app.persistencia.tablas import (
    AsignacionExperimento,
    Campana,
    Canal,
    Creativo,
    Decision,
    Experimento,
    NegocioDiario,
    ObservacionExperimento,
    SimulacionSearch,
    Snapshot,
)
from app.persistencia.tablas import (
    BusquedaDiaria as B,
)
from app.persistencia.tablas import (
    CreatividadDiaria as C,
)
from app.persistencia.tablas import (
    GrupoBusqueda as G,
)

app = FastAPI(title="MARGIA · API de la demo sintética", version="0.1.0",
              description="Datos 100 % sintéticos. Sin activación de publicidad real.",
              docs_url="/api/documentacion", openapi_url="/api/openapi.json", redoc_url=None)


@app.exception_handler(SQLAlchemyError)
async def base_no_disponible(_request: Request, _exc: SQLAlchemyError):
    return JSONResponse(status_code=503, content={"detail": "La base de datos no está disponible. Comprueba los contenedores y reintenta.", "codigo": "base_no_disponible"})


@app.exception_handler(RequestValidationError)
async def validacion_es(_request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": "Parámetros no válidos. Revisa los campos indicados.",
                                                  "campos": [".".join(map(str, e["loc"])) for e in exc.errors()]})


@app.get("/api/v1/health", response_model=Salud)
def salud(db: Db):
    db.execute(text("SELECT 1"))
    snapshot = snapshot_actual(db)
    return Salud(estado="listo", base_datos="PostgreSQL", snapshot=snapshot.id)


@app.get("/api/v1/contexto", response_model=Contexto)
def obtener_contexto(db: Db):
    return contexto(db)


@app.get("/api/v1/kpis", response_model=KPIs)
def obtener_kpis(db: Db, filtro: FiltroAPI):
    return kpis(db, filtro)


@app.get("/api/v1/medios", response_model=TablaDatos)
def obtener_medios(db: Db, filtro: FiltroAPI):
    filas = canales(db, filtro)
    return TablaDatos(periodo=filtro.periodo(), filas=filas, total=len(filas), pagina=1, paginas=1,
                      evidencia="Atribución sintética de plataforma", cobertura="Completa en el periodo seleccionado",
                      advertencias=["Las conversiones atribuidas se solapan entre plataformas: no son pedidos únicos.",
                                    "El MMM nacional se consulta por separado: las asociaciones modeladas no identifican causalidad."])


@app.get("/api/v1/modelos", response_model=InventarioModelos)
def obtener_modelos(db: Db):
    return {"filas": [ficha(modelo_actual(db, snapshot_actual(db)))]}


@app.get("/api/v1/modelos/mmm", response_model=MedicionModelo)
def obtener_medicion_modelada(db: Db, filtro: FiltroAPI):
    return medicion(db, filtro)


@app.get("/api/v1/modelos/{modelo_id}/curvas", response_model=CurvasModelo)
def obtener_curvas(db: Db, modelo_id: str, canal: str | None = Query(None, max_length=30)):
    modelo = modelo_actual(db, snapshot_actual(db))
    if modelo.id != modelo_id:
        raise HTTPException(404, "El modelo no pertenece al snapshot activo.")
    curvas = modelo.resultado["curvas"]
    if canal:
        curvas = [c for c in curvas if c["id"] == canal]
        if not curvas:
            raise HTTPException(422, "El canal no tiene curva de demanda. SEM marca se evalúa en One Search.")
    return {"modelo": modelo.id, "curvas": curvas}


@app.get("/api/v1/busqueda", response_model=TablaDatos)
def obtener_busqueda(db: Db, filtro: FiltroAPI, pagina: int = Query(1, ge=1),
                     intencion: str | None = Query(None, max_length=40),
                     orden: str = Query("gasto", pattern="^(gasto|nombre|seo|sem)$")):
    condiciones = filtro.condiciones(B)
    if intencion:
        if intencion not in ("Marca pura", "Marca + producto", "Genérica"):
            raise HTTPException(422, "Intención de búsqueda no válida.")
        condiciones.append(G.intencion == intencion)
    gasto = func.sum(B.gasto_cent)
    seo = func.sum(case((B.fuente == "SEO", B.clics), else_=0))
    sem = func.sum(case((B.fuente == "SEM", B.clics), else_=0))
    orden_sql = {"gasto": gasto.desc(), "nombre": G.nombre, "seo": seo.desc(), "sem": sem.desc()}[orden]
    consulta = select(G.id, G.nombre, G.intencion, G.elegible, seo, sem, gasto,
                      func.avg(B.posicion), func.avg(B.competencia), func.sum(B.conversiones),
                      func.sum(B.impresiones)).join(B, B.grupo_id == G.id).where(*condiciones).group_by(G.id)
    total = db.scalar(select(func.count()).select_from(consulta.subquery()))
    paginas = max(1, math.ceil(total/10))
    pagina = min(pagina, paginas)
    filas = db.execute(consulta.order_by(orden_sql, G.id).offset((pagina-1)*10).limit(10)).all()
    return TablaDatos(periodo=filtro.periodo(), filas=[dict(id=f[0], nombre=f[1], intencion=f[2], elegible=f[3],
                    clics_seo=f[4], clics_sem=f[5], inversion=float(f[6])/100, posicion=float(f[7]) if f[7] else None,
                    competencia=float(f[8]), conversiones_atribuidas=f[9], impresiones=f[10],
                    cpc=cociente(float(f[6])/100, f[5])) for f in filas],
                    total=total, pagina=pagina, paginas=paginas, evidencia="Observado sintético",
                    cobertura="Últimos 28 días del snapshot; las fechas anteriores no están observadas en búsqueda.",
                    advertencias=["La posición SEO no identifica recuperación de pedidos.",
                                  "La evidencia experimental estima cambio total de pedidos por euro; no recuperación SEO por consulta."])


@app.get("/api/v1/busqueda/evidencia", response_model=EvidenciaSearch)
def obtener_evidencia_search(db: Db, filtro: FiltroAPI):
    return evidencia(db, filtro)


@app.post("/api/v1/busqueda/simular", response_model=SimulacionSearchRespuesta)
def simular_busqueda(entrada: ParametrosSearch, db: Db, filtro: FiltroAPI):
    return guardar_simulacion(db, filtro, entrada)


@app.get("/api/v1/busqueda/simulaciones/{simulacion_id}", response_model=SimulacionSearchRespuesta)
def obtener_simulacion_search(simulacion_id: str, db: Db):
    fila = db.get(SimulacionSearch, simulacion_id)
    if not fila:
        raise HTTPException(404, "La evaluación guardada no existe.")
    return dict(id=fila.id, reutilizada=True, resultado=fila.resultado)


@app.get("/api/v1/busqueda/historicos/{experimento_id}")
def obtener_historico_search(experimento_id: str, db: Db):
    e = db.get(Experimento, experimento_id)
    if not e or e.snapshot_id != snapshot_actual(db).id or e.tipo != "historico_search":
        raise HTTPException(404, "El histórico no pertenece al snapshot activo.")
    asignaciones = db.scalars(select(AsignacionExperimento).where(AsignacionExperimento.experimento_id == e.id)
                             .order_by(AsignacionExperimento.par_id, AsignacionExperimento.brazo)).all()
    observaciones = db.scalars(select(ObservacionExperimento).where(ObservacionExperimento.experimento_id == e.id)
                               .order_by(ObservacionExperimento.mercado_id, ObservacionExperimento.periodo)).all()
    return dict(id=e.id, origen=e.origen, protocolo=e.protocolo,
        asignaciones=[dict(mercado=a.mercado_id, par=a.par_id, brazo=a.brazo, probabilidad=a.probabilidad) for a in asignaciones],
        observaciones=[dict(mercado=o.mercado_id, periodo=o.periodo, pedidos=o.pedidos,
                           gasto=o.gasto_cent/100, presupuesto=o.presupuesto_cent/100) for o in observaciones])


@app.get("/api/v1/oportunidades", response_model=RadarSearch)
def obtener_oportunidades(db: Db, filtro: FiltroAPI):
    return oportunidades(db, filtro, ParametrosSearch())


@app.get("/api/v1/creativos", response_model=TablaDatos)
def obtener_creativos(db: Db, filtro: FiltroAPI, pagina: int = Query(1, ge=1),
                      canal: str | None = Query(None, max_length=30),
                      categoria: str | None = Query(None, max_length=30)):
    condiciones = filtro.condiciones(C)
    if canal:
        if db.get(Canal, canal) is None:
            raise HTTPException(422, "Canal no válido.")
        condiciones.append(Campana.canal_id == canal)
    if categoria:
        if categoria not in ("moda", "hogar", "belleza"):
            raise HTTPException(422, "Categoría no válida.")
        condiciones.append(Campana.categoria == categoria)
    consulta = select(Creativo.id, Creativo.nombre, Creativo.asset, Creativo.atributos,
                      Canal.nombre, Creativo.formato, func.sum(C.impresiones), func.sum(C.clics),
                      func.sum(C.conversiones), func.sum(C.gasto_cent), Creativo.licencia,
                      Campana.categoria, func.avg(C.frecuencia))\
        .join(Campana, Creativo.campana_id == Campana.id).join(Canal, Campana.canal_id == Canal.id)\
        .join(C, C.creativo_id == Creativo.id).where(*condiciones).group_by(Creativo.id, Canal.id, Campana.categoria)
    total = db.scalar(select(func.count()).select_from(consulta.subquery()))
    paginas = max(1, math.ceil(total/12))
    pagina = min(pagina, paginas)
    filas = db.execute(consulta.order_by(Creativo.id).offset((pagina-1)*12).limit(12)).all()
    return TablaDatos(periodo=filtro.periodo(), filas=[dict(id=f[0], nombre=f[1], asset=f[2], atributos=f[3],
                    canal=f[4], formato=f[5], impresiones=f[6], clics=f[7], conversiones=f[8],
                    inversion=float(f[9])/100, ctr=cociente(f[7], f[6]), cvr=cociente(f[8], f[7]),
                    licencia=f[10], categoria=f[11], frecuencia=float(f[12])) for f in filas],
                    total=total, pagina=pagina, paginas=paginas, evidencia="Observado sintético",
                    cobertura="Últimos 28 días; muestra parcial de mercados por activo. El gasto es una vista parcial de medios.",
                    advertencias=["Composiciones originales reutilizadas explícitamente en 80 registros.",
                                  "Métricas descriptivas; pretest, A/B y efecto en escenarios pendientes del Día 4."])


@app.get("/api/v1/fiabilidad", response_model=Fiabilidad)
def obtener_fiabilidad(db: Db):
    return fiabilidad(db)


@app.get("/api/v1/decisiones")
def obtener_decisiones(db: Db):
    filas = db.scalars(select(Decision).order_by(Decision.creado.desc()).limit(25)).all()
    return {"filas": [dict(id=f.id, estado=f.estado, motivo=f.motivo, fecha=f.creado.isoformat(),
                          snapshot=f.snapshot_id) for f in filas], "evidencia": "Decisiones simuladas registradas"}


@app.get("/api/v1/demo/manifiesto")
def manifiesto(db: Db):
    return snapshot_actual(db).manifiesto


@app.post("/api/v1/demo/reset")
def reset_demo(confirmacion: ConfirmacionReset, db: Db):
    inicio = time.perf_counter()
    # Generar primero. Cualquier error conserva la base; borrado y recarga son atómicos.
    mundo = generar()
    db.execute(text("SELECT pg_advisory_xact_lock(260725)"))
    for tabla in reversed(Base.metadata.sorted_tables):
        db.execute(delete(tabla))
    m = mundo.manifiesto
    db.execute(insert(Snapshot), [dict(id=m["id"], corte=m["corte"], semilla=m["semilla"],
                                      version=m["version"], checksum=m["checksum"], manifiesto=m, estado="valido")])
    for nombre, filas in mundo.tablas.items():
        for i in range(0, len(filas), 2000):
            db.execute(insert(Base.metadata.tables[nombre]), filas[i:i+2000])
    snapshot = db.get(Snapshot, m["id"])
    asegurar_modelo(db, snapshot)
    asegurar_historia(db, snapshot)
    asegurar_search(db, snapshot)
    db.commit()
    return {"estado": "restablecido", "snapshot": m["id"], "checksum": m["checksum"],
            "segundos": round(time.perf_counter()-inicio, 3)}


@app.get("/api/v1/exportar/negocio.csv")
def exportar_negocio(db: Db, filtro: FiltroAPI):
    filas = db.execute(select(NegocioDiario.fecha, NegocioDiario.mercado_id, NegocioDiario.pedidos,
                              NegocioDiario.ventas_cent, NegocioDiario.coste_cent, NegocioDiario.margen_cent)
                       .where(*filtro.condiciones(NegocioDiario)).order_by(NegocioDiario.fecha, NegocioDiario.mercado_id)).all()

    def contenido() -> Iterator[str]:
        salida = io.StringIO()
        escritor = csv.writer(salida, delimiter=";")
        escritor.writerow(["fecha", "mercado", "pedidos_unicos", "ventas_netas_eur", "coste_directo_eur", "margen_bruto_eur", "snapshot", "evidencia"])
        yield "\ufeff" + salida.getvalue()
        for fila in filas:
            salida.seek(0)
            salida.truncate(0)
            escritor.writerow([fila[0].strftime("%d/%m/%Y"), fila[1], fila[2],
                               *[f"{v/100:.2f}".replace(".", ",") for v in fila[3:]],
                               filtro.snapshot.id, "Observado sintético"])
            yield salida.getvalue()

    return StreamingResponse(contenido(), media_type="text/csv; charset=utf-8",
                             headers={"Content-Disposition": 'attachment; filename="margia-negocio-sintetico.csv"'})
