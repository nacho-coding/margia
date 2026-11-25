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
