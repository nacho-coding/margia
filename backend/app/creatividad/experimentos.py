"""Orquestador A/B: protocolo, mundo separado, inferencia y versiones por contexto."""
import hashlib
import json
from datetime import UTC, datetime, timedelta

import numpy as np
from fastapi import HTTPException
from sqlalchemy import select, text

from app.api.ab_contratos import DisenoAB
from app.api.consultas import fiabilidad, snapshot_actual
from app.creatividad.servicio import consultar, historial
from app.datos.mundo_ab import VERSION_MUNDO_AB, decodificar, ejecutar_mundo_ab
from app.modelos.ab import VERSION_AB, estimar_ab, huella_observaciones, plan_ab
from app.persistencia.tablas import Experimento, Modelo


def huella(objeto):
    return hashlib.sha256(json.dumps(objeto, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def contexto_pretest(pretest):
    return {k: pretest["entradas"][k] for k in ("canal", "categoria", "audiencia", "frecuencia")}


def clave_contexto(pretest):
    return huella(dict(snapshot=pretest["snapshot"], contexto=contexto_pretest(pretest), recursos=[
        {k: v.get(k) for k in ("id", "asset", "sha256", "version_recurso", "version_presentacion", "texto")}
        for v in pretest["variantes"]]))


def vigente(db, snapshot_id, clave):
    modelos = db.scalars(select(Modelo).where(Modelo.snapshot_id == snapshot_id,
        Modelo.version == VERSION_AB, Modelo.resultado["clave_contexto"].as_string() == clave)).all()
    if not modelos:
        return None
    anteriores = {m.resultado.get("modelo_anterior") for m in modelos}
    hojas = [m for m in modelos if m.id not in anteriores]
    if len(hojas) != 1:
        raise HTTPException(503, "La cadena de aprendizaje creativo es ambigua. Revisa su integridad.")
    return hojas[0]


def resumen_modelo(modelo):
    if not modelo:
        return None
    return dict(id=modelo.id, **{k: v for k, v in modelo.resultado.items() if k != "draws_ctr"})


def aprendizaje(db, pretest_id):
    p = consultar(db, pretest_id)
    return dict(pretest=p["id"], modelo=resumen_modelo(vigente(db, p["snapshot"], clave_contexto(p))))


def catalogo(db):
    snapshot = snapshot_actual(db)
    experimentos = db.scalars(select(Experimento).where(Experimento.snapshot_id == snapshot.id,
        Experimento.tipo == "ab_creativo").order_by(Experimento.id)).all()
    return dict(snapshot=snapshot.id, corte=snapshot.corte.isoformat(), pretests=historial(db)["filas"],
        defecto=dict(nombre="Contraste de propuestas creativas", hipotesis="Contrastar si la propuesta cambia el CTR frente al control",
            impresiones_por_brazo=50000, dias=14, presupuesto_por_brazo=500, coste_produccion=250,
            semilla=snapshot.semilla+4203),
        filas=[dict(id=e.id, nombre=e.protocolo["entradas"]["nombre"], estado=e.estado,
            pretest=e.protocolo["entradas"]["pretest_id"], contexto=e.protocolo["contexto"],
            inicio=e.inicio_post.isoformat(), fin=e.fin.isoformat()) for e in experimentos])


def registro(db, eid):
    e = db.get(Experimento, eid)
    if not e or e.snapshot_id != snapshot_actual(db).id or e.tipo != "ab_creativo":
        raise HTTPException(404, "La prueba A/B no pertenece al snapshot activo.")
    return e


def detalle(db, eid, reutilizada=False):
    e = registro(db, eid)
    p = e.protocolo
    publico = {k: v for k, v in p.items() if k not in ("asignaciones", "observaciones")}
    if "evaluacion" in publico:
        publico["evaluacion"] = {k: v for k, v in publico["evaluacion"].items() if k != "draws_ctr"}
    return dict(id=e.id, snapshot=e.snapshot_id, estado=e.estado, origen=e.origen, semilla=e.semilla,
        inicio=e.inicio_post.isoformat(), fin=e.fin.isoformat(), protocolo=publico, reutilizada=reutilizada,
        observaciones=p.get("observaciones", []),
        asignaciones=[{k: v for k, v in a.items() if k != "datos"} for a in p.get("asignaciones", [])])


def crear(db, entrada):
    db.execute(text("SELECT pg_advisory_xact_lock(260725)"))
    snapshot = snapshot_actual(db)
    pretest = consultar(db, entrada.pretest_id)
    ids = [entrada.control, *entrada.tratamientos]
    variantes = {v["id"]: v for v in pretest["variantes"]}
    if not set(ids) <= variantes.keys():
        raise HTTPException(422, "Los brazos deben pertenecer al mismo pretest guardado.")
    clave = clave_contexto(pretest)
    anterior = vigente(db, snapshot.id, clave)
    plan = plan_ab(pretest["referencia"]["ctr"], entrada.impresiones_por_brazo, len(ids),
        round(entrada.presupuesto_por_brazo*100), round(entrada.coste_produccion*100))
    protocolo = dict(version=VERSION_AB, mundo=VERSION_MUNDO_AB, entradas=entrada.model_dump(),
        contexto=contexto_pretest(pretest), clave_contexto=clave,
        modelo_historico=pretest["modelo"], modelo_previo=anterior.id if anterior else None,
        variantes=[variantes[i] for i in ids], plan=plan)
    eid = "ab-"+huella(dict(snapshot=snapshot.id, protocolo=protocolo))[:24]
    if db.get(Experimento, eid):
        return detalle(db, eid, True)
    protocolo["eventos"] = [dict(estado="disenado", fecha=datetime.now(UTC).isoformat(), accion="Congelar protocolo")]
    db.add(Experimento(id=eid, snapshot_id=snapshot.id, tipo="ab_creativo", estado="disenado",
        origen="Prueba A/B creativa del mundo sintético", inicio_pre=snapshot.corte,
        inicio_post=snapshot.corte+timedelta(days=1), fin=snapshot.corte+timedelta(days=entrada.dias),
        recorte=0, semilla=entrada.semilla, protocolo=protocolo))
    db.commit()
    return detalle(db, eid)


def comprobar_asignaciones(e, p):
    entrada = DisenoAB(**p["entradas"])
    brazos = [v["id"] for v in p["variantes"]]
    fechas = [(e.inicio_post+timedelta(days=d)).isoformat() for d in range(entrada.dias)]
    if [a["fecha"] for a in p.get("asignaciones", [])] != fechas:
        raise ValueError("Asignaciones incompletas o fechas ajenas al protocolo.")
    if {o["fecha"] for o in p.get("observaciones", [])} != set(fechas):
        raise ValueError("Observaciones fuera del calendario congelado.")
    for d, a in enumerate(p["asignaciones"]):
        asignados = decodificar(a)
        if np.any(asignados >= len(brazos)):
            raise ValueError("Una oportunidad tiene un brazo desconocido.")
        n = entrada.impresiones_por_brazo//entrada.dias+(d < entrada.impresiones_por_brazo % entrada.dias)
        for i, brazo in enumerate(brazos):
            obs = [o for o in p["observaciones"] if o["fecha"] == a["fecha"] and o["brazo"] == brazo]
            if len(obs) != 1 or int((asignados == i).sum()) != n or obs[0]["impresiones"] != n:
                raise ValueError("Exposición no reconciliada con las oportunidades asignadas.")


def accion(db, eid, paso):
    db.execute(text("SELECT pg_advisory_xact_lock(260725)"))
    e = registro(db, eid)
    p = e.protocolo.copy()
    entrada = DisenoAB(**p["entradas"])
    snapshot = snapshot_actual(db)
    brazos = [v["id"] for v in p["variantes"]]
    reutilizada = False
    if paso == "ejecutar":
        if e.estado != "disenado":
            return detalle(db, eid, True)
        if fiabilidad(db).estado == "bloqueado":
            raise HTTPException(409, "La integridad del snapshot impide ejecutar la prueba.")
        asignaciones, observaciones = ejecutar_mundo_ab(p["contexto"], p["variantes"], e.inicio_post.isoformat(),
            entrada.dias, entrada.impresiones_por_brazo, round(entrada.presupuesto_por_brazo*100),
            e.semilla, snapshot.semilla)
        p.update(asignaciones=asignaciones, observaciones=observaciones,
            ejecucion=dict(version_mundo=VERSION_MUNDO_AB, inicio_simulado=e.inicio_post.isoformat(), fin_simulado=e.fin.isoformat(),
                semilla=e.semilla, substreams=[4201, 4202], unidad=p["plan"]["unidad"],
                evidencia="Observaciones sintéticas nuevas; rama separada, sin añadirlas a ventas propias"))
        e.estado = "simulado"
    elif paso == "evaluar":
        if e.estado in ("evaluado", "aceptado"):
            return detalle(db, eid, True)
        if e.estado != "simulado":
            raise HTTPException(409, "Ejecuta la prueba antes de evaluarla.")
        try:
            comprobar_asignaciones(e, p)
            r = estimar_ab(p["observaciones"], brazos, entrada.control, entrada.impresiones_por_brazo,
                entrada.dias, round(entrada.presupuesto_por_brazo*100), round(entrada.coste_produccion*100), e.semilla)
        except ValueError as error:
            raise HTTPException(409, str(error)) from error
        if fiabilidad(db).estado == "bloqueado":
            r["compatible"] = False
            r["motivos"].append("La integridad del snapshot impide guardar aprendizaje.")
        r["checksum_asignaciones"] = huella([a["sha256"] for a in p["asignaciones"]])
        p["evaluacion"] = r
        e.estado = "evaluado"
    elif paso == "aceptar":
        if e.estado == "aceptado":
            return detalle(db, eid, True)
        if e.estado != "evaluado" or not p["evaluacion"]["compatible"]:
            raise HTTPException(409, "Se requiere una evaluación compatible antes de guardar aprendizaje.")
        if fiabilidad(db).estado == "bloqueado":
            raise HTTPException(409, "La integridad del snapshot impide guardar aprendizaje.")
        try:
            comprobar_asignaciones(e, p)
        except ValueError as error:
            raise HTTPException(409, str(error)) from error
        if huella_observaciones(p["observaciones"]) != p["evaluacion"]["checksum_observaciones"] or huella(
            [a["sha256"] for a in p["asignaciones"]]) != p["evaluacion"]["checksum_asignaciones"]:
            raise HTTPException(409, "Las observaciones o asignaciones cambiaron después de evaluar; no se puede guardar ese aprendizaje.")
        anterior = vigente(db, snapshot.id, p["clave_contexto"])
        checksum = huella(dict(clave=p["clave_contexto"], observaciones=p["observaciones"],
            asignaciones=[a["sha256"] for a in p["asignaciones"]], control=entrada.control, version=VERSION_AB))
        existente = db.scalar(select(Modelo).where(Modelo.snapshot_id == snapshot.id,
            Modelo.version == VERSION_AB, Modelo.checksum_datos == checksum))
        if existente:
            if not anterior or existente.id != anterior.id:
                raise HTTPException(409, "Estas observaciones ya están en una versión anterior; se conserva la vigente.")
            p["actualizacion"] = dict(modelo=anterior.id, modelo_anterior=anterior.resultado.get("modelo_anterior"),
                metodo="Evidencia idéntica reutilizada; no acumular ni estrechar incertidumbre")
            reutilizada = True
        else:
            if (anterior.id if anterior else None) != p["modelo_previo"]:
                raise HTTPException(409, "El aprendizaje cambió desde el diseño. Diseña con la versión vigente.")
            r = p["evaluacion"]
            mid = "creatividad-ab-"+checksum[:20]
            estimaciones = [dict(f, ctr_modelo=(f["clics"]+.5)/(f["impresiones"]+1),
                p05=float(np.quantile(draw, .05)), p95=float(np.quantile(draw, .95)))
                for f, draw in zip(r["filas"], r["draws_ctr"], strict=True)]
            resultado = dict(version=VERSION_AB, clave_contexto=p["clave_contexto"], contexto=p["contexto"],
                experimento=e.id, pretest=entrada.pretest_id, modelo_historico=p["modelo_historico"],
                modelo_anterior=anterior.id if anterior else None, fecha_simulada=e.fin.isoformat(), semilla=e.semilla,
                estado="limitado", estimaciones=estimaciones, contrastes=r["contrastes"], draws_ctr=r["draws_ctr"],
                replicas=r["replicas"], incertidumbre=r["incertidumbre_modelo"],
                multiplicador_demanda=1., efecto_economico_identificado=False,
                metodo="Respuesta CTR por brazo con prior Jeffreys; sustituye evidencia del contexto, sin pooling",
                advertencias=p["plan"]["advertencias"]+[
                    "Alcance exclusivo de canal, audiencia, frecuencia, categoría y recursos congelados; no se transporta a otros contextos.",
                    "Aprender CTR no identifica demanda ni contribución. Multiplicador económico conservado en 1.",
                    "Las ramas pueden compartir oportunidades y mecanismo; se sustituyen, sin sumar evidencia independiente."])
            db.add(Modelo(id=mid, snapshot_id=snapshot.id, version=VERSION_AB, checksum_datos=checksum, resultado=resultado))
            p["actualizacion"] = dict(modelo=mid, modelo_anterior=resultado["modelo_anterior"], metodo="Sustitución por contexto; versiones anteriores conservadas")
        e.estado = "aceptado"
    else:
        raise HTTPException(404, "Acción A/B desconocida.")
    p["eventos"] = p["eventos"]+[dict(estado=e.estado, fecha=datetime.now(UTC).isoformat(), accion=paso)]
    e.protocolo = p
    db.commit()
    return detalle(db, eid, reutilizada)


def asignaciones_csv(db, eid):
    e = registro(db, eid)
    if e.estado == "disenado":
        raise HTTPException(409, "Las oportunidades se asignan únicamente al ejecutar la prueba.")
    p = e.protocolo
    comprobar_asignaciones(e, p)
    # Copia inmutable pequeña antes de cerrar la dependencia de DB.
    asignaciones, brazos = list(p["asignaciones"]), [v["id"] for v in p["variantes"]]

    def filas():
        yield "fecha;oportunidad_sintetica;brazo;probabilidad\n"
        bloque = []
        for a in asignaciones:
            for i, brazo in enumerate(decodificar(a)):
                bloque.append(f"{a['fecha']};{a['fecha']}-{i+1};{brazos[int(brazo)]};{1/len(brazos)}\n")
                if len(bloque) == 4096:
                    yield "".join(bloque)
                    bloque.clear()
        if bloque:
            yield "".join(bloque)
    return filas()


def modelo_guardado(db, mid):
    modelo = db.get(Modelo, mid)
    if not modelo or modelo.snapshot_id != snapshot_actual(db).id or modelo.version != VERSION_AB:
        raise HTTPException(404, "El modelo A/B no pertenece al snapshot activo.")
    return resumen_modelo(modelo)
