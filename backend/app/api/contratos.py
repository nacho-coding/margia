from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


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


class ParametrosSearch(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    recorte_pct: float = Field(50, ge=0, le=100)
    cuota_plataforma: float = Field(0, ge=0, le=1_000_000)
    coste_experimento: float = Field(0, ge=0, le=1_000_000)
    plataforma_comun: bool = False
    hipotesis: str | None = Field(None, max_length=80)


class BandaSearch(BaseModel):
    p05: float
    p50: float
    p95: float
    probabilidad_perdida: float
    delta_pedidos_p05: float
    delta_pedidos_p95: float
    replicas: int
    metodo: str


class BalanceSearch(BaseModel):
    pedidos: float
    margen: float
    inversion: float
    plataforma: float
    experimento: float
    contribucion: float


class PasoEconomico(BaseModel):
    nombre: str
    importe: float
    offset: float
    altura: float
    favorable: bool


class EvaluacionSearch(BaseModel):
    periodo: Periodo
    modelo: str
    version: str
    hipotesis: str
    semilla: int
    evidencia: str
    entradas: ParametrosSearch
    recuperacion: float | None
    tasa_pedidos_por_euro: float
    inversion_marca: float
    extrapolado: bool
    motivos: list[str]
    estado: str
    recomendacion: str
    base: BalanceSearch
    alternativa: BalanceSearch
    ahorro: float
    delta_pedidos: float
    cambio_margen: float
    costes_incrementales: float
    delta: float
    margen_pedido: float | None
    perdida_maxima_pedidos: float | None
    desglose: list[PasoEconomico]
    banda: BandaSearch
    advertencias: list[str]


class SimulacionSearchRespuesta(BaseModel):
    id: str
    reutilizada: bool
    resultado: EvaluacionSearch


class EvidenciaSearch(BaseModel):
    modelo: dict[str, Any]
    periodo: Periodo
    serie: list[dict[str, Any]]
    defecto: ParametrosSearch
    soporte_pct: list[float]


class RadarSearch(BaseModel):
    periodo: Periodo
    filas: list[dict[str, Any]]
    criterio: str
