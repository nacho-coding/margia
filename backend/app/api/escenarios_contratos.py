from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LimiteCanal(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    canal: str = Field(min_length=1, max_length=30)
    minimo: float = Field(ge=0, le=10000000)
    maximo: float = Field(ge=0, le=10000000)

    @model_validator(mode="after")
    def orden(self):
        if self.minimo > self.maximo:
            raise ValueError("El mínimo de inversión no puede superar el máximo.")
        return self


class ParametrosEscenario(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, str_strip_whitespace=True, validate_default=True)
    nombre: str = Field("Comparación de ahorro y reinversión", min_length=3, max_length=100)
    horizonte_dias: Literal[28] = 28
    mercado: None = None
    recorte_pct: float = Field(50, ge=0, le=100)
    reinversion_pct: float = Field(50, ge=0, le=100)
    canal_reinversion: str = Field("meta", min_length=1, max_length=30)
    seleccion_creativa_id: str | None = Field(None, min_length=1, max_length=60)
    simulacion_search_id: str | None = Field(None, min_length=1, max_length=60)
    coste_produccion: float = Field(0, ge=0, le=1000000)
    coste_experimento: float = Field(0, ge=0, le=1000000)
    cuota_plataforma: float = Field(0, ge=0, le=1000000)
    plataforma_comun: bool = False
    otros_costes: float = Field(0, ge=0, le=1000000)
    presupuesto_total: float | None = Field(None, ge=0, le=10000000)
    recorte_max_pct: float = Field(75, ge=0, le=100)
    riesgo_max_pct: float = Field(10, ge=0, le=100)
    limites: list[LimiteCanal] | None = Field(None, min_length=1, max_length=7)
    semilla: int = Field(265825, ge=0, le=2147483647)

    @model_validator(mode="after")
    def seleccion_y_limites(self):
        if self.coste_produccion and not self.seleccion_creativa_id:
            raise ValueError("Selecciona una propuesta guardada para imputar su producción.")
        if self.limites and len({limite.canal for limite in self.limites}) != len(self.limites):
            raise ValueError("Cada canal debe tener un único límite.")
        return self


class EjecucionEscenarioRespuesta(BaseModel):
    id: str
    escenario: str
    snapshot: str
    version: str
    semilla: int
    revision: int
    creado: str
    entradas: dict[str, Any]
    modelos: dict[str, Any]
    resultado: dict[str, Any]
    reutilizada: bool
