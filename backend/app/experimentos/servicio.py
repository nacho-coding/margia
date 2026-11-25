"""Orquesta diseño, mundo, evaluación y sustitución; fuera de los estimadores."""
import hashlib
import json
from datetime import UTC, datetime, timedelta

import numpy as np
from fastapi import HTTPException
from sqlalchemy import func, select, text

from app.api.consultas import Filtro, fiabilidad, snapshot_actual, totales
from app.api.geo_contratos import DisenoGeo
from app.datos.mundo_geo import ejecutar_mundo_geo
from app.dominio.economia import comparar_captura
from app.modelos.geo import VERSION, VERSION_SEARCH_GEO, disenar_geo, estimar_geo
from app.modelos.informacion import valor_informacion
from app.modelos.search import respuesta_recorte
from app.modelos.search_servicio import search_actual
from app.persistencia.tablas import (
    AsignacionExperimento as A,
)
from app.persistencia.tablas import (
    Experimento,
    MediosDiarios,
    Mercado,
    Modelo,
    NegocioDiario,
)
from app.persistencia.tablas import (
    ObservacionExperimento as O,
)


def cargar_series(db, snapshot, mercados, pre_dias):
    inicio = snapshot.corte-timedelta(days=pre_dias-1)
    series = {mid: dict(pedidos=[], gasto=[]) for mid in mercados}
    for tipo, campo, destino in ((NegocioDiario, NegocioDiario.pedidos, "pedidos"),
                                  (MediosDiarios, MediosDiarios.gasto_cent, "gasto")):
        filtros = [tipo.snapshot_id == snapshot.id, tipo.fecha >= inicio, tipo.fecha <= snapshot.corte,
                   tipo.mercado_id.in_(mercados)]
        if tipo == MediosDiarios:
            filtros.append(tipo.canal_id == "sem_marca")
        for mid, _, valor in db.execute(select(tipo.mercado_id, tipo.fecha, campo).where(*filtros)
                                        .order_by(tipo.mercado_id, tipo.fecha)):
            series[mid][destino].append(valor)
    if any(len(s[k]) != pre_dias for s in series.values() for k in ("pedidos", "gasto")):
        raise HTTPException(422, "Cobertura incompleta del preperiodo; no se puede diseñar ni ejecutar.")
    return series


def catalogo(db):
    snapshot = snapshot_actual(db)
    modelo = search_actual(db, snapshot)
    filas = db.scalars(select(Experimento).where(Experimento.snapshot_id == snapshot.id)
                       .order_by(Experimento.inicio_post.desc(), Experimento.id)).all()
    return dict(filas=[dict(id=e.id, nombre=e.protocolo.get("entradas", {}).get("nombre", "Histórico de arranque"),
        tipo=e.tipo, estado=e.estado, origen=e.origen, recorte=e.recorte, inicio=e.inicio_post.isoformat(),
        fin=e.fin.isoformat()) for e in filas],
        mercados=[dict(id=m.id, nombre=m.nombre) for m in db.scalars(select(Mercado).order_by(Mercado.id))],
        defecto=DisenoGeo(hipotesis=modelo.resultado["hipotesis"]), modelo=modelo.id,
        hipotesis=modelo.resultado["hipotesis"], corte=snapshot.corte.isoformat(), snapshot=snapshot.id)


def detalle(db, eid, reutilizada=False):
    e = db.get(Experimento, eid)
    if not e or e.snapshot_id != snapshot_actual(db).id:
        raise HTTPException(404, "El experimento no pertenece al snapshot activo.")
    asignaciones = db.scalars(select(A).where(A.experimento_id == eid).order_by(A.par_id, A.brazo)).all()
    obs = db.scalars(select(O).where(O.experimento_id == eid).order_by(O.mercado_id, O.periodo)).all()
    return dict(id=e.id, snapshot=e.snapshot_id, tipo=e.tipo, estado=e.estado, origen=e.origen,
        inicio_pre=e.inicio_pre.isoformat(), fin_pre=(e.inicio_post-timedelta(days=1)).isoformat(), inicio_post=e.inicio_post.isoformat(), fin=e.fin.isoformat(),
        recorte=e.recorte, semilla=e.semilla, protocolo=e.protocolo, reutilizada=reutilizada,
        asignaciones=[dict(mercado=a.mercado_id, par=a.par_id, brazo=a.brazo, probabilidad=a.probabilidad) for a in asignaciones],
        observaciones=[dict(mercado=o.mercado_id, periodo=o.periodo, pedidos=o.pedidos,
                           gasto_cent=o.gasto_cent, presupuesto_cent=o.presupuesto_cent) for o in obs])


def informacion_diseno(db, snapshot, entrada, plan, modelo):
    filtro = Filtro(snapshot, 28, None, snapshot.corte-timedelta(days=27), snapshot.corte)
    actual = totales(db, filtro)
    gasto = float(db.scalar(select(func.sum(MediosDiarios.gasto_cent)).where(
        *filtro.condiciones(MediosDiarios), MediosDiarios.canal_id == "sem_marca")))/100
    _, draws = respuesta_recorte(modelo.resultado, entrada.recorte_pct/100)
    # Prior empírico completo: no omitir colas pequeñas que cambian la acción.
    estados = np.asarray(draws, dtype=float)
    ahorro = gasto*entrada.recorte_pct/100
    utilidades = np.array([comparar_captura(actual["pedidos"], actual["margen"], actual["inversion"], gasto,
        entrada.recorte_pct/100, ahorro*tau, entrada.cuota_plataforma)["delta"] for tau in estados])
    sigma = plan["se_tasa_prevista"]
    info = valor_informacion([np.zeros(len(estados)), utilidades], estados, sigma or 0)
    pedidos_t = plan["pedidos_tratados_previstos"]
    margen_t = pedidos_t*(actual["margen"]/actual["pedidos"])
    gasto_t = plan["presupuesto_tratado"]
    delta_prueba = np.array([comparar_captura(pedidos_t, margen_t, gasto_t, gasto_t,
        entrada.recorte_pct/100, plan["ahorro_tratado"]*tau)["delta"] for tau in estados])
    mejor_durante = info["ev_sin_informacion"]*entrada.dias/28
    demora = max(0., mejor_durante-float(delta_prueba.mean()))
    costes = entrada.coste+demora
    neto = info["evsi"]-costes
    motivos = []
    if entrada.dias != 28 or (entrada.mercados is not None and len(entrada.mercados) != 24):
        motivos.append("El prior nacional mide 28 días; este diseño requiere transporte no contrastado.")
    if modelo.resultado["estado"] == "bloqueado":
        motivos.append("El prior Search está bloqueado.")
    if entrada.recorte_pct/100 not in modelo.resultado["soporte"]:
        motivos.append("Intensidad no observada exactamente en el prior: EVSI exploratorio.")
    if info["error_numerico"] > .01:
        motivos.append("La integración excede la tolerancia numérica de 0,01 €; no usar como recomendación.")
    return dict(**info, coste_experimento=entrada.coste, coste_oportunidad_prueba=demora,
        perdida_esperada_prueba=float(np.maximum(-delta_prueba, 0).mean()), costes_totales=costes,
        valor_neto=neto, motivos=motivos, acciones=["Mantener", "Recortar"],
        recomendacion="Valor exploratorio; evidencia insuficiente para recomendar" if motivos else
            "Experimentar" if neto > 0 else "La prueba no compensa frente a la mejor acción actual",
        horizonte=f"{entrada.dias} días de prueba y 28 días posteriores de decisión; estabilidad condicional al snapshot",
        advertencias=["Prior de parámetros discretizado; likelihood normal aproximado derivado del MDE, no potencia garantizada.",
            "Comparador: mejor acción actual en ambos periodos. Se resta coste de prueba y oportunidad frente a actuar durante ella, una sola vez.",
            "La pérdida esperada durante la prueba se muestra como riesgo; ya está recogida en el coste de oportunidad y no vuelve a restarse.",
            "Reinversión pendiente de escenarios; aquí solo mantener o recortar. Cuota de plataforma incremental en los 28 días de decisión."])


def crear(db, entrada):
    db.execute(text("SELECT pg_advisory_xact_lock(260725)"))
    snapshot = snapshot_actual(db)
    modelo = search_actual(db, snapshot)
    if entrada.hipotesis and entrada.hipotesis != modelo.resultado["hipotesis"]:
        raise HTTPException(404, "La hipótesis no pertenece a la evidencia activa.")
    todos = list(db.scalars(select(Mercado.id).order_by(Mercado.id)))
    ids = sorted(entrada.mercados if entrada.mercados is not None else todos)
    if not set(ids) <= set(todos):
        raise HTTPException(422, "Hay mercados que no pertenecen al universo sintético.")
    identidad = hashlib.sha256(json.dumps(dict(entradas=entrada.model_dump(), snapshot=snapshot.id,
        modelo=modelo.id, version=VERSION), sort_keys=True).encode()).hexdigest()[:24]
    eid = f"geo-{identidad}"
    if db.get(Experimento, eid):
        return detalle(db, eid, True)
    series = cargar_series(db, snapshot, ids, entrada.pre_dias)
    plan = disenar_geo(series, entrada.semilla, entrada.dias, entrada.recorte_pct/100)
    tasa_previa, _ = respuesta_recorte(modelo.resultado, entrada.recorte_pct/100)
    plan["efecto_previo_pedidos"] = tasa_previa*plan["ahorro_tratado"]
    plan["potencia_insuficiente"] = abs(plan["efecto_previo_pedidos"]) < plan["mde_pedidos"]
    protocolo = dict(version=VERSION, entradas=entrada.model_dump(), modelo_previo=modelo.id,
        hipotesis=modelo.resultado["hipotesis"], plan=plan,
        informacion=informacion_diseno(db, snapshot, entrada, plan, modelo),
        estado_datos=fiabilidad(db).estado, semilla_mundo=snapshot.semilla,
        eventos=[dict(estado="disenado", fecha=datetime.now(UTC).isoformat(), motivo="Protocolo y asignación congelados antes de observar el post")],
        supuestos=["Preperiodo real del snapshot; post posterior al corte solo se genera al ejecutar.",
            "Rama sintética condicionada: repite perfil de los últimos 28 días, con ruido común y por mercado. No es previsión del negocio.",
            "Sin parada anticipada, sin spillover y con efectos transportables bajo estabilidad temporal.",
            "MDE aproximado a partir de cambios pre y suelo Poisson; alfa 5 %, potencia objetivo 80 %.",
            "Aceptar sustituye evidencia: distintas ramas sintéticas sobre los mismos mercados no se acumulan como pruebas independientes."])
    e = Experimento(id=eid, snapshot_id=snapshot.id, tipo="geo_search", estado="disenado",
        origen="Nuevo experimento sintético del usuario; sin activación publicitaria",
        inicio_pre=snapshot.corte-timedelta(days=entrada.pre_dias-1), inicio_post=snapshot.corte+timedelta(days=1),
        fin=snapshot.corte+timedelta(days=entrada.dias), recorte=entrada.recorte_pct/100, semilla=entrada.semilla,
        protocolo=protocolo)
    db.add(e)
    db.flush()
    for a in plan["asignaciones"]:
        db.add(A(experimento_id=eid, mercado_id=a["mercado"], par_id=a["par"], brazo=a["brazo"], probabilidad=.5))
    db.commit()
    return detalle(db, eid)


def accion(db, eid, paso):
    db.execute(text("SELECT pg_advisory_xact_lock(260725)"))
    d = detalle(db, eid)
    e = db.get(Experimento, eid)
    if e.tipo != "geo_search":
        raise HTTPException(409, "Los históricos de arranque son inmutables.")
    p = e.protocolo.copy()
    entrada = DisenoGeo(**p["entradas"])
    snapshot = snapshot_actual(db)
    if paso == "ejecutar":
        if e.estado != "disenado":
            return detalle(db, eid, True)
        if fiabilidad(db).estado == "bloqueado":
            raise HTTPException(409, "La integridad de los datos bloquea la ejecución.")
        series = cargar_series(db, snapshot, [a["mercado"] for a in d["asignaciones"]], entrada.pre_dias)
        todos = list(db.scalars(select(Mercado.id).order_by(Mercado.id)))
        escala = float(db.scalar(select(func.sum(MediosDiarios.gasto_cent)).where(
            MediosDiarios.snapshot_id == snapshot.id, MediosDiarios.canal_id == "sem_marca")))/(730*24)
        obs = ejecutar_mundo_geo(series, d["asignaciones"], entrada.dias, e.recorte, e.semilla, snapshot.semilla, todos, escala)
        for o in obs:
            db.add(O(experimento_id=eid, mercado_id=o["mercado"], periodo=o["periodo"], pedidos=o["pedidos"],
                     gasto_cent=o["gasto_cent"], presupuesto_cent=o["presupuesto_cent"]))
        p["ejecucion"] = dict(version=VERSION, seed_sequence=[e.semilla, 3202, 3203],
            fecha_simulada=e.fin.isoformat(), evidencia="Experimento simulado: observaciones nuevas, rama separada del negocio")
        e.estado = "simulado"
    elif paso == "evaluar":
        if e.estado in ("evaluado", "aceptado"):
            return detalle(db, eid, True)
        if e.estado != "simulado":
            raise HTTPException(409, "Ejecuta el experimento antes de evaluarlo.")
        r = estimar_geo(d["asignaciones"], d["observaciones"], entrada.pre_dias, entrada.dias)
        motivos = []
        if len(d["asignaciones"]) != 24 or r["numero_pares"] < 8:
            motivos.append("Cobertura insuficiente para sustituir el modelo nacional: requiere los 24 mercados y al menos ocho pares.")
        if entrada.dias != 28:
            motivos.append("Horizonte incompatible con el modelo Search de 28 días.")
        if e.recorte == 0 or r["ahorro"] <= 0:
            motivos.append("Tratamiento nulo: no identifica cambio de pedidos por euro ahorrado.")
        placebo = p["plan"]["placebo"]["ic95"]
        if not placebo[0] <= 0 <= placebo[1] or p["plan"]["max_diferencia_tendencia"] > .15:
            motivos.append("Placebo o pretrends no compatibles; revisar emparejamiento.")
        if r["contrafactual_tratado"] <= 0 or r["ic95"][0] < -entrada.limite_perdida_pct/100*r["contrafactual_tratado"]:
            motivos.append("El intervalo supera el límite de pérdida de pedidos preespecificado.")
        if r["ic95"][1]-r["ic95"][0] > .10*r["contrafactual_tratado"]:
            motivos.append("Precisión insuficiente: semiancho del IC superior al 5 % del contrafactual tratado.")
        if fiabilidad(db).estado == "bloqueado":
            motivos.append("La integridad del snapshot bloquea actualizar evidencia.")
        r.update(compatible=not motivos, motivos=motivos,
            recomendacion="Puede sustituir la evidencia Search en esta intensidad" if not motivos else "Abstención: conservar evidencia anterior")
        p["evaluacion"] = r
        e.estado = "evaluado"
    elif paso == "aceptar":
        if e.estado == "aceptado":
            return detalle(db, eid, True)
        if e.estado != "evaluado" or not p["evaluacion"]["compatible"]:
            raise HTTPException(409, "Se requiere una evaluación compatible antes de actualizar evidencia.")
        if fiabilidad(db).estado == "bloqueado":
            raise HTTPException(409, "La integridad de datos impide actualizar evidencia.")
        anterior = search_actual(db, snapshot)
        if anterior.id != p["modelo_previo"]:
            raise HTTPException(409, "La evidencia ha cambiado desde el diseño. Crea un experimento con la versión vigente.")
        r = p["evaluacion"]
        checksum = hashlib.sha256(json.dumps(dict(asignaciones=d["asignaciones"],
            observaciones=d["observaciones"], pre_dias=entrada.pre_dias, post_dias=entrada.dias,
            recorte=e.recorte), sort_keys=True).encode()).hexdigest()
        existente = db.scalar(select(Modelo).where(Modelo.snapshot_id == snapshot.id,
            Modelo.version == VERSION_SEARCH_GEO, Modelo.checksum_datos == checksum))
        if existente:
            if existente.id != anterior.id:
                raise HTTPException(409, "Estas observaciones ya se aceptaron en una versión anterior. Se conserva la evidencia vigente.")
            p["actualizacion"] = dict(modelo=existente.id, sustituye=anterior.id,
                metodo="Evidencia idéntica: se conserva la versión vigente, sin nueva estimación")
            p["eventos"] = p["eventos"]+[dict(estado="aceptado", fecha=datetime.now(UTC).isoformat(), motivo="aceptar evidencia idéntica")]
            e.estado, e.protocolo = "aceptado", p
            db.commit()
            return detalle(db, eid, True)
        rng = np.random.default_rng(np.random.SeedSequence([e.semilla, 3204]))
        draws = (r["tasa"]+r["se_tasa"]*rng.standard_t(r["numero_pares"]-1, size=400)).reshape(-1, 1)
        mid = "search-geo-"+hashlib.sha256(f"{eid}:{VERSION_SEARCH_GEO}".encode()).hexdigest()[:20]
        resultado = dict(anterior.resultado, id=mid, version=VERSION_SEARCH_GEO, origen="Experimento geográfico aceptado",
            checksum_datos=checksum, semilla=e.semilla, estado="limitado", motivos=[],
            soporte=[e.recorte], tasas=[r["tasa"]], draws=draws.tolist(), pares=r["numero_pares"], experimentos=1,
            metodo=r["metodo"], replicas=400, placebo=p["plan"]["placebo"], estratos=[],
            intervalos=[dict(recorte=e.recorte, tasa=r["tasa"], p05=float(np.quantile(draws, .05)), p95=float(np.quantile(draws, .95)))],
            experimento_actual=eid, modelo_anterior=anterior.id,
            fecha_simulada=e.fin.isoformat(),
            advertencias=r["advertencias"]+["Evidencia sustituida, sin pooling de ramas dependientes; versiones anteriores conservadas.",
                "Soporte exclusivamente en la intensidad ejecutada; otros recortes e intensidades son hipótesis.",
                "Draws t del ratio linealizado por pares; incertidumbre aproximada, sin garantía de cobertura de transporte."])
        db.add(Modelo(id=mid, snapshot_id=snapshot.id, version=VERSION_SEARCH_GEO,
                      checksum_datos=checksum, resultado=resultado))
        p["actualizacion"] = dict(modelo=mid, sustituye=anterior.id, metodo="Sustitución, sin sumar evidencia dependiente")
        e.estado = "aceptado"
    else:
        raise HTTPException(404, "Acción experimental desconocida.")
    p["eventos"] = p["eventos"]+[dict(estado=e.estado, fecha=datetime.now(UTC).isoformat(), motivo=paso)]
    e.protocolo = p
    db.commit()
    return detalle(db, eid)
