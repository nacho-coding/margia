"""Evidencia Search, economía común y radar sobre el snapshot compartido."""
import hashlib
import json

import numpy as np
from fastapi import HTTPException
from sqlalchemy import func, select, text

from app.api.consultas import fiabilidad, totales
from app.dominio.economia import comparar_captura
from app.modelos.search import VERSION, ajustar_search, respuesta_recorte
from app.persistencia.tablas import (
    AsignacionExperimento as A,
)
from app.persistencia.tablas import (
    BusquedaDiaria,
    Experimento,
    GrupoBusqueda,
    MediosDiarios,
    Mercado,
    Modelo,
    ObservacionExperimento,
    SimulacionSearch,
)


def filas_experimentales(db, snapshot):
    experimentos = db.scalars(select(Experimento).where(Experimento.snapshot_id == snapshot.id,
        Experimento.tipo == "historico_search").order_by(Experimento.id)).all()
    filas = []
    for e in experimentos:
        if e.fin > snapshot.corte or e.inicio_pre >= e.inicio_post or e.inicio_post > e.fin:
            raise ValueError("Fecha experimental fuera del corte o protocolo incoherente.")
        asignaciones = db.scalars(select(A).where(A.experimento_id == e.id).order_by(A.par_id, A.brazo)).all()
        observaciones = db.scalars(select(ObservacionExperimento).where(ObservacionExperimento.experimento_id == e.id)).all()
        obs = {(o.mercado_id, o.periodo): o for o in observaciones}
        pares = sorted({a.par_id for a in asignaciones})
        if len(asignaciones) != 24 or len(observaciones) != 48:
            raise ValueError("Histórico experimental incompleto; no ajustar ni recomendar.")
        for par in pares:
            miembros = [a for a in asignaciones if a.par_id == par]
            if len(miembros) != 2 or {a.brazo for a in miembros} != {"control", "tratamiento"}:
                raise ValueError("Asignación pareada incorrecta.")
            control = next(a.mercado_id for a in miembros if a.brazo == "control")
            tratado = next(a.mercado_id for a in miembros if a.brazo == "tratamiento")
            tc, cc = obs[(tratado, "post")], obs[(control, "post")]
            filas.append(dict(experimento=e.id, par=par, recorte=e.recorte,
                estrato=db.get(Mercado, control).grupo,
                pre_t=obs[(tratado, "pre")].pedidos, pre_c=obs[(control, "pre")].pedidos,
                post_t=tc.pedidos, post_c=cc.pedidos,
                ahorro=(tc.presupuesto_cent-tc.gasto_cent)/100))
    return filas, experimentos


def asegurar_search(db, snapshot):
    db.execute(text("SELECT pg_advisory_xact_lock(260725)"))
    existente = db.scalar(select(Modelo).where(Modelo.snapshot_id == snapshot.id, Modelo.version == VERSION))
    if existente:
        return existente
    filas, experimentos = filas_experimentales(db, snapshot)
    resultado = ajustar_search(filas, snapshot.semilla)
    identidad = hashlib.sha256(f"{snapshot.id}:{VERSION}:{resultado['checksum_datos']}".encode()).hexdigest()[:20]
    resultado.update(id=f"search-{identidad}", snapshot=snapshot.id, corte=snapshot.corte.isoformat(),
        hipotesis=f"hip-marca-{identidad}", canal="sem_marca", alcance="SEM marca completo",
        grupos=list(db.scalars(select(GrupoBusqueda.id).where(GrupoBusqueda.elegible).order_by(GrupoBusqueda.id))),
        historicos=[dict(id=e.id, inicio_pre=e.inicio_pre.isoformat(), inicio_post=e.inicio_post.isoformat(),
            fin=e.fin.isoformat(), recorte=e.recorte, origen=e.origen) for e in experimentos])
    modelo = Modelo(id=resultado["id"], snapshot_id=snapshot.id, version=VERSION,
                    checksum_datos=resultado["checksum_datos"], resultado=resultado)
    db.add(modelo)
    db.flush()
    return modelo


def search_actual(db, snapshot):
    modelo = db.scalar(select(Modelo).where(Modelo.snapshot_id == snapshot.id, Modelo.version == VERSION))
    if not modelo:
        raise HTTPException(503, "La evidencia histórica Search todavía no está preparada. Revisa el arranque y reintenta.")
    return modelo


def evidencia(db, filtro):
    modelo = search_actual(db, filtro.snapshot).resultado
    publicos = {k: v for k, v in modelo.items() if k != "draws"}
    filas = db.execute(select(BusquedaDiaria.fecha, BusquedaDiaria.fuente, func.sum(BusquedaDiaria.clics))
        .where(*filtro.condiciones(BusquedaDiaria)).group_by(BusquedaDiaria.fecha, BusquedaDiaria.fuente)
        .order_by(BusquedaDiaria.fecha)).all()
    fechas = sorted({f[0] for f in filas})
    clics = {(f[0], f[1]): f[2] for f in filas}
    return dict(modelo=publicos, periodo=filtro.periodo(),
        serie=[dict(fecha=d.isoformat(), seo=clics.get((d, "SEO")), sem=clics.get((d, "SEM"))) for d in fechas],
        defecto=dict(recorte_pct=50, cuota_plataforma=0, coste_experimento=0, plataforma_comun=False),
        soporte_pct=[c*100 for c in modelo["soporte"]])


def evaluar_search(db, filtro, entrada):
    modelo = search_actual(db, filtro.snapshot)
    m = modelo.resultado
    if entrada.hipotesis and entrada.hipotesis != m["hipotesis"]:
        raise HTTPException(404, "La hipótesis no pertenece a la evidencia del snapshot activo.")
    recorte = entrada.recorte_pct/100
    actual = totales(db, filtro)
    gasto = float(db.scalar(select(func.coalesce(func.sum(MediosDiarios.gasto_cent), 0)).where(
        *filtro.condiciones(MediosDiarios), MediosDiarios.canal_id == "sem_marca")))/100
    tasa, draws = respuesta_recorte(m, recorte)
    ahorro = gasto*recorte

    def valorar(tau):
        return comparar_captura(actual["pedidos"], actual["margen"], actual["inversion"], gasto,
            recorte, ahorro*float(tau), entrada.cuota_plataforma, entrada.coste_experimento, entrada.plataforma_comun)

    try:
        resultado = valorar(tasa)
        replicas = [valorar(t) for t in draws]
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
    deltas = np.array([r["delta"] for r in replicas])
    pedidos = np.array([r["delta_pedidos"] for r in replicas])
    p05, p50, p95 = np.quantile(deltas, [.05, .5, .95])
    riesgo = float(np.mean(deltas < -1e-8))
    motivos = list(m["motivos"])
    extrapolado = recorte != 0 and not m["soporte"][0] <= recorte <= m["soporte"][-1]
    if extrapolado:
        motivos.append("Recorte fuera del soporte experimental: hipótesis extrapolada, sin recomendación.")
    if filtro.mercado:
        motivos.append("Estimación agrupada nacional aplicada como hipótesis al mercado; requiere validación local.")
    if filtro.dias != 28:
        motivos.append("El experimento mide 28 días; otros horizontes requieren estabilidad no contrastada.")
    if fiabilidad(db).estado == "bloqueado":
        motivos.append("La integridad de datos bloquea la evaluación económica.")
    if recorte == 0:
        recomendacion = "Mantener la inversión"
    elif motivos:
        recomendacion = "No actuar con esta hipótesis"
    elif resultado["delta"] <= 0 or riesgo > .10:
        recomendacion = "Mantener; el beneficio o el riesgo no justifican el recorte"
    else:
        recomendacion = "Oportunidad favorable para contrastar en un nuevo experimento"
    return dict(periodo=filtro.periodo().model_dump(mode="json"), modelo=modelo.id, version=m["version"],
        hipotesis=m["hipotesis"], semilla=m["semilla"], evidencia="Estimación desde históricos experimentales sintéticos",
        entradas=entrada.model_dump(), recuperacion=None, tasa_pedidos_por_euro=tasa,
        inversion_marca=gasto, extrapolado=extrapolado, motivos=motivos,
        estado="bloqueado" if m["estado"] == "bloqueado" or fiabilidad(db).estado == "bloqueado" else "hipotesis" if motivos else "evaluado",
        recomendacion=recomendacion, **resultado,
        banda=dict(p05=float(p05), p50=float(p50), p95=float(p95), probabilidad_perdida=riesgo,
            delta_pedidos_p05=float(np.quantile(pedidos, .05)), delta_pedidos_p95=float(np.quantile(pedidos, .95)),
            replicas=m["replicas"], metodo="Bootstrap por par; base, margen por pedido y transporte temporal fijos"),
        advertencias=m["advertencias"]+["Contrafactual del periodo observado, no predicción de un futuro desconocido.",
            "Contribución incremental neta condicionada a evidencia y supuestos; no activa publicidad."])


def guardar_simulacion(db, filtro, entrada):
    db.execute(text("SELECT pg_advisory_xact_lock(260725)"))
    resultado = evaluar_search(db, filtro, entrada)
    identidad = hashlib.sha256(json.dumps(resultado, sort_keys=True).encode()).hexdigest()[:24]
    sid = f"sim-search-{identidad}"
    existente = db.get(SimulacionSearch, sid)
    if not existente:
        db.add(SimulacionSearch(id=sid, snapshot_id=filtro.snapshot.id, modelo_id=resultado["modelo"],
            entradas=entrada.model_dump(), resultado=resultado))
        db.commit()
    return dict(id=sid, reutilizada=existente is not None, resultado=resultado)


def oportunidades(db, filtro, entrada):
    evaluacion = evaluar_search(db, filtro, entrada)
    favorable = evaluacion["delta"] > 0 and not evaluacion["motivos"] and evaluacion["banda"]["probabilidad_perdida"] <= .10
    tarjeta = dict(id=evaluacion["hipotesis"], canal="sem_marca", titulo="Evaluar el recorte de SEM marca",
        modelo=evaluacion["modelo"], prioridad=1, impacto=evaluacion["delta"], banda=evaluacion["banda"],
        coste=evaluacion["costes_incrementales"], recorte_pct=entrada.recorte_pct,
        estado="Contrastar" if favorable else "No actuar", recomendacion=evaluacion["recomendacion"],
        motivos=evaluacion["motivos"], url=f"/one-search?dias={filtro.dias}"+
            (f"&mercado={filtro.mercado}" if filtro.mercado else "")+f"&hipotesis={evaluacion['hipotesis']}#simulador")
    return dict(periodo=filtro.periodo(), filas=[tarjeta],
        criterio="Impacto esperado neto, riesgo de pérdida y coste. Una hipótesis de marca; sus grupos se solapan y no se suman.")
