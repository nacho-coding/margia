from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DisenoGeo(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, str_strip_whitespace=True)
    nombre: str = Field("Recorte geográfico de SEM marca", min_length=3, max_length=100)
    objetivo: str = Field("Medir el cambio total de pedidos propios al reducir SEM marca", min_length=10, max_length=500)
    hipotesis: str | None = Field(None, max_length=80)
    mercados: list[str] | None = Field(None, min_length=8, max_length=24)
    recorte_pct: float = Field(50, ge=0, le=100)
    dias: Literal[14, 28, 42, 56] = 28
    pre_dias: Literal[28, 56, 84] = 56
    semilla: int = Field(260776, ge=0, le=2_147_483_647)
    coste: float = Field(1000, ge=0, le=1_000_000)
    cuota_plataforma: float = Field(0, ge=0, le=1_000_000)
    limite_perdida_pct: float = Field(5, gt=0, le=20)
    kpi: Literal["pedidos_propios"] = "pedidos_propios"

    @model_validator(mode="after")
    def seleccion_pareada(self):
        if self.mercados is not None and (len(set(self.mercados)) != len(self.mercados) or len(self.mercados) % 2):
            raise ValueError("Selecciona mercados distintos y en número par.")
        return self


class DetalleGeo(BaseModel):
    id: str
    snapshot: str
    tipo: str
    estado: str
    origen: str
    inicio_pre: str
    fin_pre: str
    inicio_post: str
    fin: str
    recorte: float
    semilla: int
    protocolo: dict[str, Any]
    asignaciones: list[dict[str, Any]]
    observaciones: list[dict[str, Any]]
    reutilizada: bool = False


class CatalogoGeo(BaseModel):
    filas: list[dict[str, Any]]
    mercados: list[dict[str, str]]
    defecto: DisenoGeo
    modelo: str
    hipotesis: str
    corte: str
    snapshot: str
