"""Borradores revisables; nunca modifica las ejecuciones guardadas."""
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select, text

from app.api.consultas import snapshot_actual
from app.api.escenarios_contratos import ParametrosEscenario
from app.persistencia.tablas import Ejecucion, Escenario, EventoEscenario, RevisionEscenario


def bloquear(db):
    db.execute(text("SELECT pg_advisory_xact_lock(260725)"))


def obtener(db, sid):
    s = db.get(Escenario, sid)
    if not s:
        raise HTTPException(404, "No existe este escenario.")
    return s


def comprobar_revision(s, revision):
    if s.revision != revision:
        raise HTTPException(409, "El borrador tiene otra revisión. Recarga sus datos antes de guardar o ejecutar.")


def modificable(db, s):
    if s.snapshot_id != snapshot_actual(db).id:
        raise HTTPException(409, "El escenario pertenece a otro snapshot. Conserva su histórico y prepara uno nuevo.")
    if s.estado == "archivado":
        raise HTTPException(409, "El escenario está archivado. Duplícalo para continuar con un borrador nuevo.")


def evento(db, s, tipo, motivo, revision_numero=None):
    db.add(EventoEscenario(id="evt-"+uuid4().hex, escenario_id=s.id, revision=revision_numero or s.revision,
        tipo=tipo, motivo=motivo))


def revision(db, s):
    db.add(RevisionEscenario(escenario_id=s.id, revision=s.revision, parametros=s.parametros))


def resumir(s):
    return dict(id=s.id, snapshot=s.snapshot_id, nombre=s.nombre, revision=s.revision, estado=s.estado,
        editable=s.editable, creado=s.creado.isoformat())


def consultar(db, sid):
    s = obtener(db, sid)
    revisiones = db.scalars(select(RevisionEscenario).where(RevisionEscenario.escenario_id == sid)
        .order_by(RevisionEscenario.revision.desc())).all()
    eventos = db.scalars(select(EventoEscenario).where(EventoEscenario.escenario_id == sid)
        .order_by(EventoEscenario.creado, EventoEscenario.id)).all()
    ejecuciones = db.scalars(select(Ejecucion).where(Ejecucion.escenario_id == sid)
        .order_by(Ejecucion.creado.desc(), Ejecucion.id)).all()
    return dict(**resumir(s), parametros=s.parametros,
        revisiones=[dict(revision=r.revision, parametros=r.parametros, creado=r.creado.isoformat()) for r in revisiones],
        eventos=[dict(tipo=e.tipo, revision=e.revision, motivo=e.motivo, creado=e.creado.isoformat()) for e in eventos],
        ejecuciones=[dict(id=e.id, revision=e.revision, creado=e.creado.isoformat(),
            nombre=e.entradas["nombre"]) for e in ejecuciones])


def validar(db, entrada):
    from app.escenarios.servicio import cargar, normalizar, origen_search, recurso_elegido
    snapshot, mmm, _, semanas, referencia = cargar(db)
    origen_search(db, entrada.simulacion_search_id, snapshot.id)
    creatividad = recurso_elegido(db, entrada.seleccion_creativa_id)
    return snapshot, normalizar(entrada, semanas, mmm.resultado, referencia, creatividad)


def crear(db, entrada, origen=None):
    bloquear(db)
    snapshot, parametros = validar(db, entrada)
    s = Escenario(id="borr-"+uuid4().hex, snapshot_id=snapshot.id, nombre=parametros["nombre"],
        revision=1, estado="borrador", editable=True, parametros=parametros)
    db.add(s)
    db.flush()
    revision(db, s)
    evento(db, s, "duplicado" if origen else "creado",
        f"Borrador duplicado del escenario {origen}." if origen else "Nuevo borrador guardado sin ejecutar cálculos.")
    db.commit()
    return consultar(db, s.id)


def editar(db, sid, entrada):
    bloquear(db)
    s = obtener(db, sid)
    comprobar_revision(s, entrada.revision)
    modificable(db, s)
    if not s.editable:
        raise HTTPException(409, "Esta configuración histórica es de solo lectura. Duplícala para editarla.")
    _, parametros = validar(db, entrada.parametros)
    if parametros != s.parametros:
        s.revision += 1
        s.nombre, s.parametros = parametros["nombre"], parametros
        revision(db, s)
        evento(db, s, "editado", "Parámetros revisados; las ejecuciones anteriores se conservan.")
    db.commit()
    return consultar(db, sid)


def duplicar(db, sid, entrada):
    bloquear(db)
    s = obtener(db, sid)
    if s.snapshot_id != snapshot_actual(db).id:
        raise HTTPException(409, "Prepara un escenario nuevo con el snapshot activo.")
    return crear(db, ParametrosEscenario(**{**s.parametros, "nombre": entrada.nombre}), sid)


def archivar(db, sid, entrada):
    bloquear(db)
    s = obtener(db, sid)
    comprobar_revision(s, entrada.revision)
    if s.estado == "archivado":
        anterior = db.scalar(select(EventoEscenario).where(EventoEscenario.escenario_id == sid,
            EventoEscenario.tipo == "archivado"))
        if not anterior or anterior.motivo != entrada.motivo:
            raise HTTPException(409, "El escenario ya está archivado y conserva su motivo original.")
    else:
        s.estado = "archivado"
        evento(db, s, "archivado", entrada.motivo)
    db.commit()
    return consultar(db, sid)


def ejecutar_borrador(db, sid, entrada):
    from app.escenarios.servicio import ejecutar
    bloquear(db)
    s = obtener(db, sid)
    comprobar_revision(s, entrada.revision)
    modificable(db, s)
    return ejecutar(db, ParametrosEscenario(**s.parametros), s)
