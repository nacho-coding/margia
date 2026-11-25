from datetime import date, datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.persistencia.db import Base


class Snapshot(Base):
    __tablename__ = "snapshot"
    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    corte: Mapped[date] = mapped_column(Date)
    semilla: Mapped[int] = mapped_column(Integer)
    version: Mapped[str] = mapped_column(String(30))
    checksum: Mapped[str] = mapped_column(String(64))
    manifiesto: Mapped[dict] = mapped_column(JSON)
    estado: Mapped[str] = mapped_column(String(20), default="valido")
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Mercado(Base):
    __tablename__ = "mercado"
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80))
    region: Mapped[str] = mapped_column(String(30))
    tamano: Mapped[float] = mapped_column(Float)
    grupo: Mapped[str] = mapped_column(String(30))


class Canal(Base):
    __tablename__ = "canal"
    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(60))
    tipo: Mapped[str] = mapped_column(String(30))
    color: Mapped[str] = mapped_column(String(10))


class Campana(Base):
    __tablename__ = "campana"
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    canal_id: Mapped[str] = mapped_column(ForeignKey("canal.id"))
    nombre: Mapped[str] = mapped_column(String(100))
    categoria: Mapped[str] = mapped_column(String(30))
    objetivo: Mapped[str] = mapped_column(String(40))
    inicio: Mapped[date] = mapped_column(Date)
    fin: Mapped[date] = mapped_column(Date)


class Creativo(Base):
    __tablename__ = "creativo"
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    campana_id: Mapped[str] = mapped_column(ForeignKey("campana.id"))
    nombre: Mapped[str] = mapped_column(String(100))
    asset: Mapped[str] = mapped_column(String(150))
    formato: Mapped[str] = mapped_column(String(40))
    atributos: Mapped[dict] = mapped_column(JSON)
    licencia: Mapped[str] = mapped_column(String(120))


class GrupoBusqueda(Base):
    __tablename__ = "grupo_busqueda"
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    intencion: Mapped[str] = mapped_column(String(40))
    elegible: Mapped[bool] = mapped_column(Boolean)


class NegocioDiario(Base):
    __tablename__ = "negocio_diario"
    __table_args__ = (
        CheckConstraint("pedidos >= 0 AND ventas_cent >= 0 AND coste_cent >= 0"),
        CheckConstraint("margen_cent = ventas_cent - coste_cent"),
        Index("ix_negocio_fecha_mercado", "snapshot_id", "fecha", "mercado_id"),
    )
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("snapshot.id"), primary_key=True)
    fecha: Mapped[date] = mapped_column(Date, primary_key=True)
    mercado_id: Mapped[str] = mapped_column(ForeignKey("mercado.id"), primary_key=True)
    pedidos: Mapped[int] = mapped_column(Integer)
    ventas_cent: Mapped[int] = mapped_column(BigInteger)
    coste_cent: Mapped[int] = mapped_column(BigInteger)
    margen_cent: Mapped[int] = mapped_column(BigInteger)
    visitas: Mapped[int] = mapped_column(Integer)
    promocion: Mapped[bool] = mapped_column(Boolean)
    demanda_proxy: Mapped[float] = mapped_column(Float)


class MediosDiarios(Base):
    __tablename__ = "medios_diarios"
    __table_args__ = (
        CheckConstraint("gasto_cent >= 0 AND conversiones >= 0 AND ingresos_cent >= 0"),
        CheckConstraint("clics IS NULL OR (clics >= 0 AND clics <= impresiones)"),
        Index("ix_medios_fecha_mercado", "snapshot_id", "fecha", "mercado_id", "canal_id"),
    )
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("snapshot.id"), primary_key=True)
    fecha: Mapped[date] = mapped_column(Date, primary_key=True)
    mercado_id: Mapped[str] = mapped_column(ForeignKey("mercado.id"), primary_key=True)
    canal_id: Mapped[str] = mapped_column(ForeignKey("canal.id"), primary_key=True)
    gasto_cent: Mapped[int] = mapped_column(BigInteger)
    impresiones: Mapped[int | None] = mapped_column(BigInteger)
    clics: Mapped[int | None] = mapped_column(Integer)
    conversiones: Mapped[int] = mapped_column(Integer)
    ingresos_cent: Mapped[int] = mapped_column(BigInteger)
    fuente: Mapped[str] = mapped_column(String(50))
    ventana_dias: Mapped[int] = mapped_column(Integer)


class CampanaDiaria(Base):
    __tablename__ = "campana_diaria"
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("snapshot.id"), primary_key=True)
    fecha: Mapped[date] = mapped_column(Date, primary_key=True)
    mercado_id: Mapped[str] = mapped_column(ForeignKey("mercado.id"), primary_key=True)
    campana_id: Mapped[str] = mapped_column(ForeignKey("campana.id"), primary_key=True)
    gasto_cent: Mapped[int] = mapped_column(BigInteger)


class BusquedaDiaria(Base):
    __tablename__ = "busqueda_diaria"
    __table_args__ = (
        CheckConstraint("clics >= 0 AND clics <= impresiones AND gasto_cent >= 0"),
        CheckConstraint("fuente IN ('SEO', 'SEM')"),
        Index("ix_busqueda_snapshot_fecha", "snapshot_id", "fecha", "mercado_id"),
    )
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("snapshot.id"), primary_key=True)
    fecha: Mapped[date] = mapped_column(Date, primary_key=True)
    mercado_id: Mapped[str] = mapped_column(ForeignKey("mercado.id"), primary_key=True)
    grupo_id: Mapped[str] = mapped_column(ForeignKey("grupo_busqueda.id"), primary_key=True)
    fuente: Mapped[str] = mapped_column(String(8), primary_key=True)
    impresiones: Mapped[int] = mapped_column(Integer)
    clics: Mapped[int] = mapped_column(Integer)
    gasto_cent: Mapped[int] = mapped_column(BigInteger)
    conversiones: Mapped[int | None] = mapped_column(Integer)
    posicion: Mapped[float | None] = mapped_column(Float)
    competencia: Mapped[float] = mapped_column(Float)


class CreatividadDiaria(Base):
    __tablename__ = "creatividad_diaria"
    __table_args__ = (
        CheckConstraint("clics >= 0 AND clics <= impresiones AND conversiones <= clics"),
        Index("ix_creatividad_snapshot_fecha", "snapshot_id", "fecha", "mercado_id"),
    )
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("snapshot.id"), primary_key=True)
    fecha: Mapped[date] = mapped_column(Date, primary_key=True)
    mercado_id: Mapped[str] = mapped_column(ForeignKey("mercado.id"), primary_key=True)
    creativo_id: Mapped[str] = mapped_column(ForeignKey("creativo.id"), primary_key=True)
    impresiones: Mapped[int] = mapped_column(Integer)
    clics: Mapped[int] = mapped_column(Integer)
    conversiones: Mapped[int] = mapped_column(Integer)
    gasto_cent: Mapped[int] = mapped_column(BigInteger)
    frecuencia: Mapped[float] = mapped_column(Float)


class Decision(Base):
    __tablename__ = "decision"
    __table_args__ = (UniqueConstraint("ejecucion_id"),)
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("snapshot.id"))
    ejecucion_id: Mapped[str] = mapped_column(String(50))
    estado: Mapped[str] = mapped_column(String(25))
    motivo: Mapped[str] = mapped_column(String(1000))
    evidencia: Mapped[dict] = mapped_column(JSON)
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Modelo(Base):
    __tablename__ = "modelo"
    __table_args__ = (UniqueConstraint("snapshot_id", "version", "checksum_datos"),)
    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("snapshot.id"), index=True)
    version: Mapped[str] = mapped_column(String(30))
    checksum_datos: Mapped[str] = mapped_column(String(64))
    resultado: Mapped[dict] = mapped_column(JSON)
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Experimento(Base):
    __tablename__ = "experimento"
    __table_args__ = (CheckConstraint("recorte >= 0 AND recorte <= 1"),)
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("snapshot.id"), index=True)
    tipo: Mapped[str] = mapped_column(String(30))
    estado: Mapped[str] = mapped_column(String(30))
    origen: Mapped[str] = mapped_column(String(120))
    inicio_pre: Mapped[date] = mapped_column(Date)
    inicio_post: Mapped[date] = mapped_column(Date)
    fin: Mapped[date] = mapped_column(Date)
    recorte: Mapped[float] = mapped_column(Float)
    semilla: Mapped[int] = mapped_column(Integer)
    protocolo: Mapped[dict] = mapped_column(JSON)


class AsignacionExperimento(Base):
    __tablename__ = "asignacion_experimento"
    __table_args__ = (CheckConstraint("brazo IN ('control', 'tratamiento')"),)
    experimento_id: Mapped[str] = mapped_column(ForeignKey("experimento.id"), primary_key=True)
    mercado_id: Mapped[str] = mapped_column(ForeignKey("mercado.id"), primary_key=True)
    par_id: Mapped[str] = mapped_column(String(20))
    brazo: Mapped[str] = mapped_column(String(20))
    probabilidad: Mapped[float] = mapped_column(Float)


class ObservacionExperimento(Base):
    __tablename__ = "observacion_experimento"
    __table_args__ = (
        ForeignKeyConstraint(["experimento_id", "mercado_id"],
                             ["asignacion_experimento.experimento_id", "asignacion_experimento.mercado_id"]),
        CheckConstraint("periodo IN ('pre', 'post')"),
        CheckConstraint("pedidos >= 0 AND gasto_cent >= 0 AND presupuesto_cent >= 0"),
    )
    experimento_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    mercado_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    periodo: Mapped[str] = mapped_column(String(10), primary_key=True)
    pedidos: Mapped[int] = mapped_column(Integer)
    gasto_cent: Mapped[int] = mapped_column(BigInteger)
    presupuesto_cent: Mapped[int] = mapped_column(BigInteger)


class SimulacionSearch(Base):
    __tablename__ = "simulacion_search"
    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("snapshot.id"), index=True)
    modelo_id: Mapped[str] = mapped_column(ForeignKey("modelo.id"))
    entradas: Mapped[dict] = mapped_column(JSON)
    resultado: Mapped[dict] = mapped_column(JSON)
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PretestCreativo(Base):
    __tablename__ = "pretest_creativo"
    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("snapshot.id"), index=True)
    modelo_id: Mapped[str] = mapped_column(ForeignKey("modelo.id"))
    entradas: Mapped[dict] = mapped_column(JSON)
    resultado: Mapped[dict] = mapped_column(JSON)
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SeleccionCreativa(Base):
    __tablename__ = "seleccion_creativa"
    __table_args__ = (UniqueConstraint("pretest_id", "variante_id"),)
    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    pretest_id: Mapped[str] = mapped_column(ForeignKey("pretest_creativo.id"), index=True)
    variante_id: Mapped[str] = mapped_column(String(40))
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Escenario(Base):
    __tablename__ = "escenario"
    __table_args__ = (CheckConstraint("revision >= 1"),)
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("snapshot.id"), index=True)
    nombre: Mapped[str] = mapped_column(String(100))
    revision: Mapped[int] = mapped_column(Integer, default=1)
    estado: Mapped[str] = mapped_column(String(25))
    parametros: Mapped[dict] = mapped_column(JSON)
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Ejecucion(Base):
    __tablename__ = "ejecucion"
    __table_args__ = (CheckConstraint("revision >= 1"),)
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    escenario_id: Mapped[str] = mapped_column(ForeignKey("escenario.id"), index=True)
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("snapshot.id"), index=True)
    revision: Mapped[int] = mapped_column(Integer)
    version: Mapped[str] = mapped_column(String(30))
    semilla: Mapped[int] = mapped_column(Integer)
    entradas: Mapped[dict] = mapped_column(JSON)
    modelos: Mapped[dict] = mapped_column(JSON)
    checksum_fuentes: Mapped[str] = mapped_column(String(64))
    resultado: Mapped[dict] = mapped_column(JSON)
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
