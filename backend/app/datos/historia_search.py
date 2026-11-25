"""Fixtures históricas explícitas: ramas experimentales del mismo mundo.

No reescribe negocio_diario ni pretende ser una ejecución nueva del usuario.
Solo este generador accede al mecanismo latente; el estimador lee observaciones.
"""
import json

import numpy as np
from sqlalchemy import func, select, text

from app.datos.captura import estructura_mercados, factor_pedidos
from app.persistencia.tablas import (
    AsignacionExperimento,
    Experimento,
    MediosDiarios,
    Mercado,
    NegocioDiario,
    ObservacionExperimento,
)

VERSION = "historia-search-1.0.0"
RECORTES = (0, .25, .5, .75)*3


def construir_historia(negocio, gastos, mercados, snapshot_id, semilla):
    dias = sorted({n["fecha"] for n in negocio})
    if len(dias) != 730 or len(mercados) != 24:
        raise ValueError("Los históricos Search requieren el universo completo de 24 mercados.")
    n = {(f["fecha"], f["mercado_id"]): f["pedidos"] for f in negocio}
    gasto = {(f["fecha"], f["mercado_id"]): f["gasto_cent"] for f in gastos}
    if len(n) != 730*24 or len(gasto) != 730*24:
        raise ValueError("Cobertura incompleta para generar históricos experimentales.")
    _, recuperacion = estructura_mercados(np.random.default_rng(np.random.SeedSequence(semilla).spawn(5)[0]))
    escala = sum(gasto.values())/(730*24)  # céntimos/día/mercado, igual al generador base
    volumen = {m["id"]: sum(n[(d, m["id"])] for d in dias[:28]) for m in mercados}
    pares = []
    for estrato in sorted({m["grupo"] for m in mercados}):
        orden = sorted([m for m in mercados if m["grupo"] == estrato], key=lambda m: volumen[m["id"]])
        pares.extend((orden[i], orden[i+1]) for i in range(0, len(orden), 2))
    indice = {m["id"]: i for i, m in enumerate(mercados)}
    experimentos, asignaciones, observaciones = [], [], []
    for i, recorte in enumerate(RECORTES):
        rng = np.random.default_rng(np.random.SeedSequence([semilla, 3100, i]))
        eid = f"hist-search-{snapshot_id}-{i+1:02}"
        pre, post = dias[i*56:i*56+28], dias[i*56+28:i*56+56]
        experimentos.append(dict(id=eid, snapshot_id=snapshot_id, tipo="historico_search", estado="historico",
            origen="Fixture histórica sintética de arranque; no ejecución nueva",
            inicio_pre=pre[0], inicio_post=post[0], fin=post[-1], recorte=recorte, semilla=semilla,
            protocolo=dict(version=VERSION, kpi="pedidos_propios", dias=28, canal="sem_marca",
                ambito="Todas las consultas de marca; sin identificación por consulta",
                emparejamiento="Volumen del primer preperiodo dentro de estrato; pares congelados",
                aleatorizacion="Dentro de cada par; probabilidad 0,5; RNG SeedSequence raíz, 3100, índice",
                seed_sequence=[semilla, 3100, i],
                ruido="Poisson de pedidos sobre rama contrafactual del negocio observado",
                independencia="Periodos no solapados; mercados repetidos, agrupar incertidumbre por par")))
        for j, pareja in enumerate(pares):
            tratado = int(rng.integers(0, 2))
            for k, mercado in enumerate(pareja):
                mid = mercado["id"]
                tratamiento = k == tratado
                asignaciones.append(dict(experimento_id=eid, mercado_id=mid, par_id=f"par-{j+1:02}",
                    brazo="tratamiento" if tratamiento else "control", probabilidad=.5))
                for periodo, fechas in (("pre", pre), ("post", post)):
                    presupuesto = sum(gasto[(d, mid)] for d in fechas)
                    aplicado = recorte if tratamiento and periodo == "post" else 0
                    invertido = int(round(presupuesto*(1-aplicado)))
                    media = sum(n[(d, mid)] for d in fechas)
                    if aplicado:
                        # Ratio de captura del mismo mecanismo. No se guardan contrafactuales
                        # de pedidos en las observaciones entregadas al estimador.
                        antes = factor_pedidos(presupuesto/28, escala, recuperacion[indice[mid]])
                        despues = factor_pedidos(invertido/28, escala, recuperacion[indice[mid]])
                        media *= despues/antes
                    pedidos = int(rng.poisson(media)) if periodo == "post" else int(media)
                    observaciones.append(dict(experimento_id=eid, mercado_id=mid, periodo=periodo,
                        pedidos=pedidos, gasto_cent=invertido, presupuesto_cent=presupuesto))
    return experimentos, asignaciones, observaciones


def asegurar_historia(db, snapshot):
    db.execute(text("SELECT pg_advisory_xact_lock(260725)"))
    existentes = db.scalar(select(func.count()).select_from(Experimento).where(
        Experimento.snapshot_id == snapshot.id, Experimento.tipo == "historico_search"))
    if existentes:
        # Completar procedencia del prototipo sin cambiar observaciones ni ajustes.
        for i, e in enumerate(db.scalars(select(Experimento).where(Experimento.snapshot_id == snapshot.id,
                Experimento.tipo == "historico_search").order_by(Experimento.id))):
            if "seed_sequence" not in e.protocolo:
                e.semilla = snapshot.semilla
                e.protocolo = {**e.protocolo, "seed_sequence": [snapshot.semilla, 3100, i]}
        return
    negocio = [dict(fecha=f.fecha, mercado_id=f.mercado_id, pedidos=f.pedidos) for f in db.scalars(
        select(NegocioDiario).where(NegocioDiario.snapshot_id == snapshot.id).order_by(NegocioDiario.fecha, NegocioDiario.mercado_id))]
    gastos = [dict(fecha=f.fecha, mercado_id=f.mercado_id, gasto_cent=f.gasto_cent) for f in db.scalars(
        select(MediosDiarios).where(MediosDiarios.snapshot_id == snapshot.id, MediosDiarios.canal_id == "sem_marca"))]
    mercados = [dict(id=m.id, grupo=m.grupo) for m in db.scalars(select(Mercado).order_by(Mercado.id))]
    experimentos, asignaciones, observaciones = construir_historia(negocio, gastos, mercados, snapshot.id, snapshot.semilla)
    for tipo, filas in ((Experimento, experimentos), (AsignacionExperimento, asignaciones), (ObservacionExperimento, observaciones)):
        db.execute(tipo.__table__.insert(), filas)


if __name__ == "__main__":
    from app.api.consultas import snapshot_actual
    from app.modelos.search_servicio import asegurar_search
    from app.persistencia.db import SessionLocal
    with SessionLocal.begin() as db:
        snapshot = snapshot_actual(db)
        asegurar_historia(db, snapshot)
        modelo = asegurar_search(db, snapshot)
        print(json.dumps(dict(modelo=modelo.id, estado=modelo.resultado["estado"], origen="Históricos de arranque")))
