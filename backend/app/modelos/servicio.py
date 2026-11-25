"""Carga observada, entrenamiento batch y consulta de versiones inmutables."""
import hashlib
import json
import time
from datetime import timedelta

import numpy as np
from fastapi import HTTPException
from sqlalchemy import Integer, func, select, text
from sqlalchemy.orm import Session

from app.api.consultas import Filtro, snapshot_actual
from app.dominio.economia import contribucion
from app.modelos.mmm import CONTROLES, VERSION, adstock, entrenar, hill
from app.persistencia.db import SessionLocal
from app.persistencia.tablas import Canal, MediosDiarios, Mercado, Modelo, NegocioDiario, Snapshot


def semanas_observadas(db: Session, snapshot: Snapshot) -> tuple[list[dict], list[dict]]:
    # 104 bloques completos de siete días terminados en el corte. Dos días iniciales
    # quedan fuera de este ajuste; no se convierten en una falsa semana de dos días.
    inicio = snapshot.corte-timedelta(days=727)
    mercados = db.scalar(select(func.count()).select_from(Mercado))
    canales = [dict(id=c.id, nombre=c.nombre, color=c.color, tipo=c.tipo)
               for c in db.scalars(select(Canal).where(Canal.tipo == "demanda").order_by(Canal.id))]
    negocio = db.execute(select(NegocioDiario.fecha, func.sum(NegocioDiario.pedidos),
                                 func.sum(NegocioDiario.margen_cent),
                                 func.avg(NegocioDiario.promocion.cast(Integer)),
                                 func.count())
                          .where(NegocioDiario.snapshot_id == snapshot.id, NegocioDiario.fecha >= inicio,
                                 NegocioDiario.fecha <= snapshot.corte)
                          .group_by(NegocioDiario.fecha).order_by(NegocioDiario.fecha)).all()
    medios = db.execute(select(MediosDiarios.fecha, MediosDiarios.canal_id,
                                func.sum(MediosDiarios.gasto_cent), func.count())
                         .where(MediosDiarios.snapshot_id == snapshot.id, MediosDiarios.fecha >= inicio,
                                MediosDiarios.fecha <= snapshot.corte)
                         .group_by(MediosDiarios.fecha, MediosDiarios.canal_id)).all()
    if len(negocio) != 728 or any(f[-1] != mercados for f in negocio):
        raise ValueError("MMM bloqueado: cobertura diaria incompleta de pedidos propios.")
    if len(medios) != 728*(len(canales)+1) or any(f[-1] != mercados for f in medios):
        raise ValueError("MMM bloqueado: cobertura diaria incompleta de inversión.")
    gastos = {(f[0], f[1]): float(f[2])/100 for f in medios}
    ids = [c.id for c in db.scalars(select(Canal).order_by(Canal.id))]
    semanas = []
    for i in range(0, 728, 7):
        bloque = negocio[i:i+7]
        semanas.append(dict(inicio=bloque[0][0].isoformat(), fin=bloque[-1][0].isoformat(),
                            pedidos=int(sum(f[1] for f in bloque)), margen=float(sum(f[2] for f in bloque))/100,
                            promocion=float(sum(f[3] for f in bloque))/7,
                            gasto={c: sum(gastos[(f[0], c)] for f in bloque) for c in ids}))
    return semanas, canales


def asegurar_modelo(db: Session, snapshot: Snapshot) -> Modelo:
    db.execute(text("SELECT pg_advisory_xact_lock(260725)"))
    existente = db.scalar(select(Modelo).where(Modelo.snapshot_id == snapshot.id, Modelo.version == VERSION))
    if existente:
        return existente
    inicio = time.perf_counter()
    semanas, canales = semanas_observadas(db, snapshot)
    resultado = entrenar(semanas, canales, snapshot.semilla)
    resultado.update(snapshot=snapshot.id, checksum_snapshot=snapshot.checksum,
                     corte=snapshot.corte.isoformat(), segundos_ajuste=round(time.perf_counter()-inicio, 3))
    # El ID incluye el snapshot: igual dataset en otra foto no comparte artefacto.
    identidad = hashlib.sha256(f"{snapshot.id}:{resultado['id']}".encode()).hexdigest()[:20]
    resultado["id"] = f"mmm-{identidad}"
    modelo = Modelo(id=resultado["id"], snapshot_id=snapshot.id, version=VERSION,
                    checksum_datos=resultado["checksum_datos"], resultado=resultado)
    db.add(modelo)
    db.flush()
    return modelo


def modelo_actual(db: Session, snapshot: Snapshot) -> Modelo:
    modelo = db.scalar(select(Modelo).where(Modelo.snapshot_id == snapshot.id, Modelo.version == VERSION))
    if modelo is None:
        raise HTTPException(503, "El modelo aún no está preparado. Comprueba el arranque del backend y reintenta.")
    return modelo


def ficha(modelo: Modelo) -> dict:
    resultado = modelo.resultado
    return {k: v for k, v in resultado.items() if k not in ("serie", "curvas", "parametros")}


def medicion(db: Session, filtro: Filtro) -> dict:
    modelo = modelo_actual(db, filtro.snapshot)
    resultado = modelo.resultado
    base = dict(modelo=ficha(modelo), periodo=filtro.periodo(), aplicable=filtro.mercado is None,
                serie=[], curvas=[], resumen=[], cobertura="Solo semanas completas contenidas en el periodo seleccionado.")
    if filtro.mercado:
        return dict(**base, motivo="El MMM es nacional y no se desagrega por mercado. Selecciona todos los mercados para consultar el modelo; la tabla de atribución sí conserva tu filtro.")
    serie = [s for s in resultado["serie"] if s["inicio"] >= filtro.inicio.isoformat() and s["fin"] <= filtro.fin.isoformat()]
    resumen = []
    parametros = resultado["parametros"]
    indices = [i for i, s in enumerate(resultado["serie"]) if s["inicio"] >= filtro.inicio.isoformat() and s["fin"] <= filtro.fin.isoformat()]
    for j, canal in enumerate(resultado["curvas"]):
        cid = canal["id"]
        pedidos = sum(s["componentes"][cid] for s in serie)
        margen = sum(s["componentes"][cid]*(s["margen_por_pedido"] or 0) for s in serie)
        gasto = sum(s["gasto"][cid] for s in serie)
        exposicion = np.array([s["gasto"][cid] for s in resultado["serie"]])/parametros["escala_gasto"][j]
        cargas = hill(adstock(exposicion, parametros["persistencia"]), parametros["k"])[indices]
        betas = np.array(parametros["bootstrap_coeficientes"])[:, len(CONTROLES)+j]
        limites_pedidos = np.quantile(betas*cargas.sum(), [.05, .95])
        margen_por_pedido = np.array([s["margen_por_pedido"] or 0 for s in serie])
        limites_saldo = np.quantile(betas*float(cargas @ margen_por_pedido)-gasto, [.05, .95])
        resumen.append(dict(id=cid, nombre=canal["nombre"], color=canal["color"], pedidos_modelados=pedidos,
                            pedidos_p05=float(limites_pedidos[0]), pedidos_p95=float(limites_pedidos[1]),
                            saldo_p05=float(limites_saldo[0]), saldo_p95=float(limites_saldo[1]),
                            margen_asignado=margen, inversion=gasto, saldo_modelado=contribucion(margen, gasto)))
    return dict(**{**base, "serie": serie, "curvas": resultado["curvas"], "resumen": resumen}, motivo=None)


if __name__ == "__main__":
    with SessionLocal.begin() as db:
        modelo = asegurar_modelo(db, snapshot_actual(db))
        print(json.dumps(dict(modelo=modelo.id, version=modelo.version,
                              estado=modelo.resultado["estado"], segundos=modelo.resultado["segundos_ajuste"])))
