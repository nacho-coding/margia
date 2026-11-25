from dataclasses import dataclass
from datetime import date, timedelta
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.contratos import Contexto, Fiabilidad, KPIs, Metrica, Periodo
from app.dominio.economia import cociente, contribucion
from app.modelos.mmm import VERSION as VERSION_MMM
from app.persistencia.db import get_db
from app.persistencia.tablas import Canal, MediosDiarios, Mercado, Modelo, NegocioDiario, Snapshot

Db = Annotated[Session, Depends(get_db)]
Dias = Literal[28, 56, 90, 365]


def snapshot_actual(db: Session) -> Snapshot:
    snapshot = db.scalar(select(Snapshot).order_by(Snapshot.corte.desc(), Snapshot.id).limit(1))
    if snapshot is None:
        raise HTTPException(503, "El mundo sintético aún no está inicializado. Reintenta en unos segundos.")
    return snapshot


@dataclass
class Filtro:
    snapshot: Snapshot
    dias: int
    mercado: str | None
    inicio: date
    fin: date

    def condiciones(self, tabla, anterior: bool = False):
        desplazamiento = timedelta(days=self.dias if anterior else 0)
        condiciones = [tabla.snapshot_id == self.snapshot.id,
                       tabla.fecha >= self.inicio-desplazamiento,
                       tabla.fecha <= self.fin-desplazamiento]
        if self.mercado:
            condiciones.append(tabla.mercado_id == self.mercado)
        return condiciones

    def periodo(self) -> Periodo:
        return Periodo(inicio=self.inicio, fin=self.fin, dias=self.dias, mercado=self.mercado,
                       snapshot=self.snapshot.id, anterior_inicio=self.inicio-timedelta(days=self.dias),
                       anterior_fin=self.inicio-timedelta(days=1))


def filtros(db: Db, dias: int = Query(28, ge=1, le=365), mercado: str | None = Query(None, pattern=r"^m\d{2}$")) -> Filtro:
    if dias not in (28, 56, 90, 365):
        raise HTTPException(422, "El periodo debe ser de 28, 56, 90 o 365 días.")
    snapshot = snapshot_actual(db)
    if mercado and db.get(Mercado, mercado) is None:
        raise HTTPException(422, "El mercado indicado no existe en este universo sintético.")
    return Filtro(snapshot, dias, mercado, snapshot.corte-timedelta(days=dias-1), snapshot.corte)


FiltroAPI = Annotated[Filtro, Depends(filtros)]


def contexto(db: Session) -> Contexto:
    snapshot = snapshot_actual(db)
    mercados = db.scalars(select(Mercado).order_by(Mercado.id)).all()
    return Contexto(empresa="AUREL Retail", snapshot=snapshot.id, corte=snapshot.corte,
                    inicio=snapshot.manifiesto["inicio"], semilla=snapshot.semilla,
                    version=snapshot.version, checksum=snapshot.checksum,
                    evidencia="Observado sintético", moneda="EUR",
                    mercados=[{"id": m.id, "nombre": m.nombre} for m in mercados],
                    manifiesto=snapshot.manifiesto,
                    modulos={"centro": "Datos observados", "medicion": "MMM nacional validado temporalmente y atribución descriptiva",
                             "one-search": "Datos observados; estimación pendiente", "creatividad": "Biblioteca observada; pretest pendiente",
                             "experimentos": "En desarrollo · Día 3", "escenarios": "En desarrollo · Día 4",
                             "fiabilidad": "Integridad de fuentes; incidencias alternativas pendientes"})


def totales(db: Session, filtro: Filtro, anterior: bool = False) -> dict:
    # Agregación independiente por fuente para evitar multiplicación de ventas al unir medios.
    negocio = db.execute(select(func.coalesce(func.sum(NegocioDiario.ventas_cent), 0),
                                func.coalesce(func.sum(NegocioDiario.margen_cent), 0),
                                func.coalesce(func.sum(NegocioDiario.pedidos), 0))
                         .where(*filtro.condiciones(NegocioDiario, anterior))).one()
    inversion = db.scalar(select(func.coalesce(func.sum(MediosDiarios.gasto_cent), 0))
                          .where(*filtro.condiciones(MediosDiarios, anterior)))
    ventas, margen, pedidos = negocio
    return dict(ventas=float(ventas)/100, margen=float(margen)/100, pedidos=int(pedidos),
                inversion=float(inversion)/100,
                contribucion=contribucion(float(margen)/100, float(inversion)/100))


def canales(db: Session, filtro: Filtro) -> list[dict]:
    filas = db.execute(select(Canal.id, Canal.nombre, Canal.color, Canal.tipo,
                              func.sum(MediosDiarios.gasto_cent), func.sum(MediosDiarios.impresiones),
                              func.sum(MediosDiarios.clics), func.sum(MediosDiarios.conversiones),
                              func.sum(MediosDiarios.ingresos_cent))
                       .join(MediosDiarios, MediosDiarios.canal_id == Canal.id)
                       .where(*filtro.condiciones(MediosDiarios))
                       .group_by(Canal.id).order_by(func.sum(MediosDiarios.gasto_cent).desc())).all()
    return [dict(id=f[0], nombre=f[1], color=f[2], tipo=f[3], inversion=float(f[4])/100,
                 impresiones=f[5], clics=f[6], conversiones=f[7], ingresos_atribuidos=float(f[8])/100,
                 roas_atribuido=cociente(float(f[8]), float(f[4])),
                 incremental=None, evidencia="Atribución sintética de plataforma") for f in filas]


def kpis(db: Session, filtro: Filtro) -> KPIs:
    actual, anterior = totales(db, filtro), totales(db, filtro, True)
    definiciones = [
        ("ventas", "Ventas netas", "EUR", "Ventas propias sin IVA y con devoluciones descontadas."),
        ("inversion", "Inversión en medios", "EUR", "Ocho canales pagados, incluido el coste de CRM. SEO y directo no añaden inversión."),
        ("pedidos", "Pedidos únicos", "pedidos", "Pedidos del negocio, generados una sola vez. No se suman conversiones de plataformas."),
        ("margen", "Margen bruto", "EUR", "Ventas netas menos coste directo de mercancía."),
        ("contribucion", "Contribución tras marketing", "EUR", "Margen bruto menos inversión de medios. Antes de costes de plataforma, experimentación y producción creativa."),
    ]
    metricas = [Metrica(id=i, nombre=n, valor=actual[i], anterior=anterior[i],
                       delta_pct=((actual[i]-anterior[i])/abs(anterior[i])*100 if anterior[i] else None),
                       unidad=u, definicion=d) for i, n, u, d in definiciones]
    negocios = db.execute(select(NegocioDiario.fecha, func.sum(NegocioDiario.ventas_cent),
                                 func.sum(NegocioDiario.pedidos), func.sum(NegocioDiario.margen_cent))
                          .where(*filtro.condiciones(NegocioDiario))
                          .group_by(NegocioDiario.fecha).order_by(NegocioDiario.fecha)).all()
    gastos = dict(db.execute(select(MediosDiarios.fecha, func.sum(MediosDiarios.gasto_cent))
                             .where(*filtro.condiciones(MediosDiarios))
                             .group_by(MediosDiarios.fecha)).all())
    serie = [dict(fecha=f[0].isoformat(), ventas=float(f[1])/100, pedidos=int(f[2]),
                  margen=float(f[3])/100, inversion=float(gastos.get(f[0], 0))/100) for f in negocios]
    return KPIs(periodo=filtro.periodo(), metricas=metricas, serie=serie, canales=canales(db, filtro),
                evidencia="Observado sintético", costes="Contribución observada antes de costes de plataforma, producción y experimentación.")


def fiabilidad(db: Session) -> Fiabilidad:
    snapshot = snapshot_actual(db)
    mercados = db.scalar(select(func.count()).select_from(Mercado))
    esperado = 730 * mercados
    negocios = db.scalar(select(func.count()).select_from(NegocioDiario).where(NegocioDiario.snapshot_id == snapshot.id))
    medios = db.scalar(select(func.count()).select_from(MediosDiarios).where(MediosDiarios.snapshot_id == snapshot.id))
    errores = db.scalar(select(func.count()).select_from(NegocioDiario)
                        .where(NegocioDiario.snapshot_id == snapshot.id,
                               NegocioDiario.margen_cent != NegocioDiario.ventas_cent-NegocioDiario.coste_cent))
    cobertura = min(negocios/esperado, medios/(esperado*8)) if esperado else 0
    bloqueado = cobertura < .95 or errores > 0
    reglas = [dict(id="cobertura", nombre="Cobertura crítica negocio y medios", valor=cobertura*100,
                   unidad="%", umbral="≥ 95 % del grano esperado", estado="bloqueado" if cobertura < .95 else "valido"),
              dict(id="margen", nombre="Reconciliación de margen", valor=errores,
                   unidad="filas incoherentes", umbral="0 filas", estado="bloqueado" if errores else "valido"),
              dict(id="unicidad", nombre="Unicidad y relaciones", valor=None,
                   unidad="", umbral="Claves primarias y FK en PostgreSQL", estado="valido")]
    conteos = snapshot.manifiesto["conteos"]
    fuentes = [dict(id=n, nombre=nombre, filas=conteos[n], dias=dias, cobertura=descripcion, estado=estado)
               for n, nombre, dias, descripcion, estado in [
                   ("negocio_diario", "Negocio propio", 730, "Completa · pedidos y ventas únicos", "bloqueado" if negocios < esperado else "valido"),
                   ("medios_diarios", "Inversión y atribución", 730, "Completa · ocho canales", "bloqueado" if medios < esperado*8 else "valido"),
                   ("busqueda_diaria", "Búsqueda SEO / SEM", 28, "Últimos 28 días; gasto SEM reconciliado", "limitado"),
                   ("campana_diaria", "Distribución por campaña", 7, "Últimos 7 días; no suma inversión adicional", "limitado"),
                   ("creatividad_diaria", "Rendimiento creativo", 28, "Mercados parciales por activo; no causal", "limitado"),
               ]]
    incidencias = [] if not bloqueado else [dict(causa="Cobertura crítica o margen incoherente", accion="Restablecer la demo o investigar el snapshot.")]
    modelos = db.scalars(select(Modelo).where(Modelo.snapshot_id == snapshot.id, Modelo.version == VERSION_MMM)).all()
    diagnostico = "Sin modelos ajustados todavía."
    if modelos:
        diagnostico = " ".join(f"{m.version}: {m.resultado['estado']}. " +
                              (" ".join(m.resultado['motivos']) or "Ajuste observacional nacional; optimización deshabilitada hasta calibración.")
                              for m in modelos)
    return Fiabilidad(snapshot=snapshot.id, estado="bloqueado" if bloqueado else "limitado", fuentes=fuentes,
                       reglas=reglas, incidencias=incidencias, checksum=snapshot.checksum,
                       diagnostico_modelos=diagnostico + " La cobertura parcial limita las fuentes indicadas.")
