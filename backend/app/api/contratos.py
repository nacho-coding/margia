from datetime import date
from typing import Any, Literal

from pydantic import BaseModel


class Salud(BaseModel):
    estado: Literal["listo"]
    base_datos: Literal["PostgreSQL"]
    snapshot: str


class Contexto(BaseModel):
    empresa: str
    snapshot: str
    corte: date
    inicio: date
    semilla: int
    version: str
    checksum: str
    evidencia: str
    moneda: str
    mercados: list[dict[str, str]]
    manifiesto: dict[str, Any]
    modulos: dict[str, str]


class Metrica(BaseModel):
    id: str
    nombre: str
    valor: float | int
    anterior: float | int
    delta_pct: float | None
    unidad: Literal["EUR", "pedidos"]
    definicion: str


class Periodo(BaseModel):
    inicio: date
    fin: date
    dias: int
    mercado: str | None
    snapshot: str
    anterior_inicio: date
    anterior_fin: date


class KPIs(BaseModel):
    periodo: Periodo
    metricas: list[Metrica]
    serie: list[dict[str, Any]]
    canales: list[dict[str, Any]]
    evidencia: str
    costes: str


class TablaDatos(BaseModel):
    periodo: Periodo
    filas: list[dict[str, Any]]
    total: int
    pagina: int
    paginas: int
    evidencia: str
    cobertura: str
    advertencias: list[str]


class Fiabilidad(BaseModel):
    snapshot: str
    estado: Literal["valido", "limitado", "bloqueado"]
    fuentes: list[dict[str, Any]]
    reglas: list[dict[str, Any]]
    incidencias: list[dict[str, Any]]
    diagnostico_modelos: str
    checksum: str


class ConfirmacionReset(BaseModel):
    confirmacion: Literal["RESTABLECER DEMO"]


class FichaModelo(BaseModel):
    id: str
    version: str
    snapshot: str
    corte: date
    semilla: int
    checksum_datos: str
    checksum_snapshot: str
    configuracion: dict[str, Any]
    estado: Literal["limitado", "bloqueado"]
    optimizable: bool
    motivos: list[str]
    ambito: str
    objetivo: str
    unidad: str
    semanas: int
    train_inicio: date
    train_fin: date
    holdout_inicio: date
    holdout_fin: date
    folds: list[dict[str, date]]
    diagnostico: dict[str, Any]
    incertidumbre: str
    advertencias: list[str]
    segundos_ajuste: float


class SemanaModelo(BaseModel):
    inicio: date
    fin: date
    observado: float
    predicho: float
    baseline: float
    efectos: float
    residual: float
    componentes: dict[str, float]
    p05: float
    p95: float
    ancho_banda: float
    naive: float | None
    particion: Literal["train", "holdout"]
    margen_por_pedido: float | None
    gasto: dict[str, float]


class PuntoCurva(BaseModel):
    inversion: float
    pedidos: float
    p05: float
    p95: float
    ancho_banda: float
    marginal: float
    extrapolado: bool


class CurvaModelo(BaseModel):
    id: str
    nombre: str
    color: str
    tipo: str
    minimo: float
    maximo: float
    referencia: float
    stock_previo_normalizado: float
    horizonte_dias: int
    puntos: list[PuntoCurva]


class SaldoModelo(BaseModel):
    id: str
    nombre: str
    color: str
    pedidos_modelados: float
    pedidos_p05: float
    pedidos_p95: float
    saldo_p05: float
    saldo_p95: float
    margen_asignado: float
    inversion: float
    saldo_modelado: float


class MedicionModelo(BaseModel):
    modelo: FichaModelo
    periodo: Periodo
    aplicable: bool
    motivo: str | None
    cobertura: str
    serie: list[SemanaModelo]
    curvas: list[CurvaModelo]
    resumen: list[SaldoModelo]


class InventarioModelos(BaseModel):
    filas: list[FichaModelo]


class CurvasModelo(BaseModel):
    modelo: str
    curvas: list[CurvaModelo]
