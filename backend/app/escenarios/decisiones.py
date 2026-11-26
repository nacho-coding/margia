"""Decisiones terminales sobre planes guardados y guardrails revalidados."""
from fastapi import HTTPException
from sqlalchemy import select

from app.api.consultas import fiabilidad, snapshot_actual
from app.escenarios.gestion import bloquear, evento
from app.escenarios.motor import VERSION_ESCENARIOS, huella
from app.escenarios.servicio import cargar, recurso_elegido
from app.persistencia.tablas import Decision, Ejecucion, Escenario

PLANES = (("base", "Mantener la estrategia actual"), ("ahorro", "A · conservar ahorro"),
          ("reinversion", "B · reinvertir"), ("optimizacion", "Candidato de la búsqueda"))


def ejecucion(db, eid):
    e = db.get(Ejecucion, eid)
    if not e:
        raise HTTPException(404, "No existe esta ejecución guardada.")
    return e


def plan_guardado(e, plan):
    return e.resultado["optimizacion"]["mejor"] if plan == "optimizacion" else e.resultado[plan]


def serializar(d):
    return dict(id=d.id, ejecucion=d.ejecucion_id, snapshot=d.snapshot_id, estado=d.estado,
        motivo=d.motivo, creado=d.creado.isoformat(), evidencia=d.evidencia)


def consultar(db, did):
    d = db.get(Decision, did)
    if not d:
        raise HTTPException(404, "No existe esta decisión registrada.")
    return serializar(d)


def planes_bloqueados(e, motivos):
    return [dict(id=k, nombre=n, aprobable=False, motivos=sorted(set(motivos+
        (plan_guardado(e, k)["restricciones"]+plan_guardado(e, k)["motivos"] if plan_guardado(e, k) else
         ["La búsqueda no encontró un candidato elegible."])))) for k, n in PLANES]


def guardrails(db, e):
    """Solo consulta fuentes actuales: no reejecuta ni sustituye resultados."""
    snapshot = snapshot_actual(db)
    s = db.get(Escenario, e.escenario_id)
    comunes = []
    if e.snapshot_id != snapshot.id:
        comunes.append("La ejecución pertenece a otro snapshot. Ejecuta con el contexto activo.")
    critico = snapshot.estado == "bloqueado" or fiabilidad(db).estado == "bloqueado"
    if critico:
        comunes.append("La integridad de los datos bloquea nuevas aprobaciones.")
    if s.estado == "archivado":
        comunes.append("El escenario está archivado. Duplícalo para continuar.")
    if s.revision != e.revision:
        comunes.append("El borrador tiene una revisión posterior. Ejecuta sus parámetros actuales.")
    if e.version != VERSION_ESCENARIOS:
        comunes.append("Ha cambiado la versión del motor; prepara una ejecución nueva.")
    if critico or e.snapshot_id != snapshot.id:
        return planes_bloqueados(e, comunes)
    try:
        _, mmm, search, semanas, referencia = cargar(db)
    except HTTPException as error:
        return planes_bloqueados(e, comunes+[f"No se puede revalidar la evidencia vigente: {error.detail}"])
    if e.snapshot_id == snapshot.id:
        congelada = e.resultado["reinversion"]["creatividad"]
        if huella(dict(semanas=semanas, referencia=referencia, creatividad=congelada)) != e.checksum_fuentes:
            comunes.append("Las fuentes observadas de la ejecución han cambiado. Prepara otra comparación.")
        if mmm.resultado["train_fin"] != e.resultado["proyeccion"]["fin_errores"]:
            comunes.append("Ha cambiado la calibración temporal de la base. Prepara otra comparación.")
    filas = []
    for key, nombre in PLANES:
        p = plan_guardado(e, key)
        motivos = list(comunes)
        if p is None:
            motivos.append("La búsqueda no encontró un candidato elegible.")
        else:
            motivos += p["restricciones"]+p["motivos"]
            if not p["factible"] or not p["elegible"]:
                motivos.append("El plan guardado no cumple los límites o la evidencia requerida.")
            if p["bandas"]["delta"]["probabilidad_perdida"] > e.entradas["riesgo_max_pct"]/100+1e-12:
                motivos.append("La probabilidad de pérdida supera el límite fijado.")
            media = p["bandas"]["delta"]["media"]
            if key != "base" and (media < -1e-8 or (p["recorte_pct"] and media <= 0)):
                motivos.append("El cambio no mejora la contribución esperada; conserva la base.")
            if p["recorte_pct"]:
                if search.id != e.modelos["search"]["id"]:
                    motivos.append("La evidencia Search ha cambiado. Calcula una ejecución con la versión vigente.")
                if search.resultado["estado"] == "bloqueado":
                    motivos.append("La evidencia Search actual está bloqueada.")
                soporte = search.resultado["soporte"]
                if not soporte[0] <= p["recorte_pct"]/100 <= soporte[-1]:
                    motivos.append("El recorte queda fuera del soporte Search vigente.")
            if p["reinversion"]:
                if mmm.id != e.modelos["mmm"]["id"]:
                    motivos.append("El modelo MMM ha cambiado. Calcula una ejecución nueva.")
                if mmm.resultado["estado"] == "bloqueado" or not mmm.resultado["optimizable"]:
                    motivos.append("El MMM actual no está habilitado para aprobar reinversión.")
            if p["creatividad"]:
                actual = recurso_elegido(db, e.entradas["seleccion_creativa_id"])
                if actual != p["creatividad"]:
                    motivos.append("La evidencia de la propuesta creativa ha cambiado. Calcula una ejecución nueva.")
        filas.append(dict(id=key, nombre=nombre, aprobable=not motivos, motivos=sorted(set(motivos))))
    return filas


def contexto(db, eid):
    e = ejecucion(db, eid)
    d = db.scalar(select(Decision).where(Decision.ejecucion_id == eid))
    return dict(ejecucion=eid, escenario=e.escenario_id, revision=e.revision,
        decision=serializar(d) if d else None, planes=guardrails(db, e),
        alcance="Decisión simulada sobre una ejecución guardada. No activa publicidad ni modifica datos de negocio.")


def registrar(db, eid, entrada):
    bloquear(db)
    e = ejecucion(db, eid)
    anterior = db.scalar(select(Decision).where(Decision.ejecucion_id == eid))
    if anterior:
        if (anterior.estado == entrada.estado and anterior.motivo == entrada.motivo
                and anterior.evidencia.get("plan") == entrada.plan):
            return serializar(anterior)
        raise HTTPException(409, "Esta ejecución ya tiene una decisión terminal. Prepara otra ejecución para cambiarla.")
    comprobaciones = guardrails(db, e)
    control = next(f for f in comprobaciones if f["id"] == entrada.plan)
    if entrada.estado == "aprobado" and not control["aprobable"]:
        raise HTTPException(409, "Aprobación bloqueada: "+" ".join(control["motivos"]))
    p = plan_guardado(e, entrada.plan)
    d = Decision(id="dec-"+eid.removeprefix("ejec-"), snapshot_id=e.snapshot_id, ejecucion_id=eid,
        estado=entrada.estado, motivo=entrada.motivo, evidencia=dict(
            tipo="Decisión simulada · datos sintéticos", escenario=e.escenario_id, revision=e.revision,
            plan=entrada.plan, nombre_plan=control["nombre"], entradas=e.entradas, modelos=e.modelos,
            semilla=e.semilla, version=e.version, checksum_fuentes=e.checksum_fuentes,
            traza_draws=e.resultado["traza_draws"]["checksum"],
            periodo=dict(inicio=e.resultado["inicio"], fin=e.resultado["fin"]),
            metricas=p["metricas"] if p else None, delta=p["delta"] if p else None,
            banda=p["bandas"]["delta"] if p else None,
            presupuestos=p["presupuestos"] if p else None, guardrails=control,
            advertencias=e.resultado["advertencias"], activa_publicidad=False))
    db.add(d)
    evento(db, db.get(Escenario, e.escenario_id), entrada.estado, entrada.motivo, e.revision)
    db.commit()
    return serializar(d)
