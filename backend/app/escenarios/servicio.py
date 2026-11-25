"""Carga única de hechos, recursos y modelos; persistencia de comparaciones."""
import time
from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy import select, text

from app.api.consultas import Filtro, fiabilidad, snapshot_actual, totales
from app.api.escenarios_contratos import ParametrosEscenario
from app.creatividad.experimentos import aprendizaje
from app.creatividad.servicio import consultar, seleccion
from app.escenarios.motor import VERSION_ESCENARIOS, MotorEscenarios, huella, soportes
from app.escenarios.proyeccion import proyectar_base
from app.modelos.search_servicio import search_actual
from app.modelos.servicio import modelo_actual, semanas_observadas
from app.persistencia.tablas import (
    Canal,
    Ejecucion,
    Escenario,
    PretestCreativo,
    SeleccionCreativa,
    SimulacionSearch,
)


def cargar(db):
    snapshot = snapshot_actual(db)
    mmm, search = modelo_actual(db, snapshot), search_actual(db, snapshot)
    try:
        semanas, _ = semanas_observadas(db, snapshot)
    except ValueError as error:
        raise HTTPException(503, str(error)) from error
    filtro = Filtro(snapshot, 28, None, snapshot.corte-timedelta(days=27), snapshot.corte)
    referencia = totales(db, filtro)
    if referencia["pedidos"] <= 0:
        raise HTTPException(503, "Faltan pedidos propios para valorar la proyección.")
    referencia["periodo"] = dict(inicio=filtro.inicio.isoformat(), fin=filtro.fin.isoformat(), dias=28, mercado=None)
    return snapshot, mmm, search, semanas, referencia


def recurso_elegido(db, sid):
    if not sid:
        return None
    s = seleccion(db, sid)
    p = consultar(db, s["pretest_id"])
    v = next(v for v in p["variantes"] if v["id"] == s["variante_id"])
    ab = aprendizaje(db, p["id"])["modelo"]
    tasa = next((r for r in ab["estimaciones"] if r["id"] == s["variante_id"]), None) if ab else None
    return dict(seleccion=sid, pretest=p["id"], variante=v, canal=p["entradas"]["canal"],
        contexto={k: p["entradas"][k] for k in ("canal", "categoria", "audiencia", "frecuencia")},
        modelo_historico=p["modelo"], modelo_ab=ab["id"] if ab else None,
        ctr=tasa["ctr_modelo"] if tasa else v["ctr_referencia"],
        referencia_ctr="Aprendizaje A/B de CTR del contexto exacto" if tasa else "Referencia del pretest histórico",
        multiplicador_demanda=1., efecto_economico_identificado=False)


def normalizar(entrada, semanas, mmm, referencia, creatividad):
    e = entrada.model_dump()
    _, soporte = soportes(semanas, mmm)
    ids = {s["canal"] for s in soporte}
    if e["canal_reinversion"] not in ids:
        raise HTTPException(422, "El destino debe ser un canal de demanda; SEM marca solo interviene en captura.")
    if creatividad and e["canal_reinversion"] != creatividad["canal"]:
        raise HTTPException(422, "El canal de reinversión debe coincidir con el de la propuesta seleccionada.")
    if e["presupuesto_total"] is None:
        e["presupuesto_total"] = referencia["inversion"]
    if e["limites"] is None:
        e["limites"] = [{k: s[k] for k in ("canal", "minimo", "maximo")} for s in soporte]
    if {limite["canal"] for limite in e["limites"]} != ids:
        raise HTTPException(422, "Define un límite para cada uno de los siete canales de demanda.")
    por_id = {s["canal"]: s for s in soporte}
    for limite in e["limites"]:
        s = por_id[limite["canal"]]
        if limite["minimo"] < s["minimo"]-1e-6 or limite["maximo"] > s["maximo"]+1e-6:
            raise HTTPException(422, "Los límites deben respetar el soporte permitido o conservar la asignación actual; los cambios se validan por semana.")
    e["limites"] = sorted(e["limites"], key=lambda limite: limite["canal"])
    return e


def resumen_modelo(m):
    return dict(id=m.id, version=m.version, estado=m.resultado["estado"], motivos=m.resultado["motivos"],
        optimizable=m.resultado.get("optimizable"))


def origen_search(db, sid, snapshot_id):
    if not sid:
        return None
    s = db.get(SimulacionSearch, sid)
    if not s or s.snapshot_id != snapshot_id:
        raise HTTPException(404, "La simulación Search de partida no pertenece al snapshot activo.")
    return dict(id=s.id, modelo=s.modelo_id, entradas=s.entradas, periodo=s.resultado["periodo"])


def catalogo(db, seleccion_id=None, simulacion_id=None):
    snapshot, mmm, search, semanas, referencia = cargar(db)
    _, limites = soportes(semanas, mmm.resultado)
    seleccionadas = db.scalars(select(SeleccionCreativa).join(PretestCreativo)
        .where(PretestCreativo.snapshot_id == snapshot.id)
        .order_by(SeleccionCreativa.creado.desc(), SeleccionCreativa.id).limit(50)).all()
    if seleccion_id and seleccion_id not in {s.id for s in seleccionadas}:
        seleccion(db, seleccion_id)
        seleccionadas.insert(0, db.get(SeleccionCreativa, seleccion_id))
    elecciones = []
    for s in seleccionadas:
        p = consultar(db, s.pretest_id)
        v = next(v for v in p["variantes"] if v["id"] == s.variante_id)
        elecciones.append(dict(id=s.id, nombre=v["nombre"], canal=p["entradas"]["canal"], variante=v, pretest=p["id"]))
    ejecuciones = db.scalars(select(Ejecucion).where(Ejecucion.snapshot_id == snapshot.id)
        .order_by(Ejecucion.creado.desc(), Ejecucion.id).limit(30)).all()
    defecto = ParametrosEscenario(semilla=snapshot.semilla+5100,
        presupuesto_total=referencia["inversion"], recorte_max_pct=search.resultado["soporte"][-1]*100,
        limites=[{k: limite[k] for k in ("canal", "minimo", "maximo")} for limite in limites]).model_dump()
    origen = origen_search(db, simulacion_id, snapshot.id)
    if origen:
        defecto.update({k: origen["entradas"][k] for k in ("recorte_pct", "cuota_plataforma", "coste_experimento", "plataforma_comun")})
        defecto["simulacion_search_id"] = simulacion_id
    if seleccion_id:
        elegida = next(s for s in elecciones if s["id"] == seleccion_id)
        defecto.update(seleccion_creativa_id=seleccion_id, canal_reinversion=elegida["canal"])
    fin_train = next(i+1 for i, s in enumerate(semanas) if s["fin"] == mmm.resultado["train_fin"])
    base = proyectar_base(semanas, fin_train)
    return dict(snapshot=snapshot.id, corte=snapshot.corte.isoformat(),
        inicio=(snapshot.corte+timedelta(days=1)).isoformat(), fin=(snapshot.corte+timedelta(days=28)).isoformat(),
        defecto=defecto, referencia=referencia, proyeccion={k: v for k, v in base.items() if k != "errores_centrados"},
        canales=limites, selecciones=elecciones, origen_search=origen, modelos=dict(mmm=resumen_modelo(mmm), search=resumen_modelo(search)),
        filas=[dict(id=e.id, escenario=e.escenario_id, nombre=e.entradas["nombre"], creado=e.creado.isoformat(),
            recomendacion=e.resultado["optimizacion"]["recomendacion"]) for e in ejecuciones])


def publico(valor):
    if isinstance(valor, dict):
        return {k: publico(v) for k, v in valor.items() if k not in ("draws", "indices_mmm", "indices_search", "indices_proceso")}
    if isinstance(valor, list):
        return [publico(v) for v in valor]
    return valor


def detalle(db, eid, reutilizada=False):
    e = db.get(Ejecucion, eid)
    if not e or e.snapshot_id != snapshot_actual(db).id:
        raise HTTPException(404, "La ejecución no pertenece al snapshot activo.")
    return dict(id=e.id, escenario=e.escenario_id, snapshot=e.snapshot_id, revision=e.revision,
        version=e.version, semilla=e.semilla, creado=e.creado.isoformat(), entradas=e.entradas,
        modelos=e.modelos, resultado=publico(e.resultado), reutilizada=reutilizada)


def ejecutar(db, entrada):
    db.execute(text("SELECT pg_advisory_xact_lock(260725)"))
    if fiabilidad(db).estado == "bloqueado":
        raise HTTPException(409, "La integridad de los datos impide ejecutar una comparación nueva; consulta el historial.")
    snapshot, mmm, search, semanas, referencia = cargar(db)
    origen = origen_search(db, entrada.simulacion_search_id, snapshot.id)
    creatividad = recurso_elegido(db, entrada.seleccion_creativa_id)
    e = normalizar(entrada, semanas, mmm.resultado, referencia, creatividad)
    modelos = dict(mmm=resumen_modelo(mmm), search=resumen_modelo(search),
        creativo_historico=creatividad["modelo_historico"] if creatividad else None,
        creativo_ab=creatividad["modelo_ab"] if creatividad else None, search_origen=origen["modelo"] if origen else None)
    checksum = huella(dict(semanas=semanas, referencia=referencia, creatividad=creatividad))
    sid = "esc-"+huella(dict(snapshot=snapshot.id, entradas=e))[:24]
    eid = "ejec-"+huella(dict(escenario=sid, version=VERSION_ESCENARIOS, modelos=modelos, checksum=checksum))[:24]
    if db.get(Ejecucion, eid):
        return detalle(db, eid, True)
    inicio = time.perf_counter()
    try:
        resultado = MotorEscenarios(semanas, mmm.resultado, search.resultado, referencia, e, creatividad).ejecutar()
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
    resultado.update(inicio=(snapshot.corte+timedelta(days=1)).isoformat(),
        fin=(snapshot.corte+timedelta(days=28)).isoformat(), segundos=round(time.perf_counter()-inicio, 4), origen_search=origen)
    resultado["canales"] = [dict(id=c.id, nombre=c.nombre, color=c.color) for c in db.scalars(select(Canal).order_by(Canal.id))]
    escenario = db.get(Escenario, sid)
    if not escenario:
        escenario = Escenario(id=sid, snapshot_id=snapshot.id, nombre=e["nombre"], revision=1,
            estado="evaluado", parametros=e)
        db.add(escenario)
        db.flush()
    db.add(Ejecucion(id=eid, escenario_id=sid, snapshot_id=snapshot.id, revision=escenario.revision,
        version=VERSION_ESCENARIOS, semilla=e["semilla"], entradas=e, modelos=modelos, checksum_fuentes=checksum,
        resultado=resultado))
    db.commit()
    return detalle(db, eid)
