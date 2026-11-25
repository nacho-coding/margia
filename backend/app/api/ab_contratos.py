from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DisenoAB(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, str_strip_whitespace=True)
    pretest_id: str = Field(min_length=1, max_length=60)
    control: str = Field(min_length=1, max_length=40)
    tratamientos: list[str] = Field(min_length=1, max_length=2)
    nombre: str = Field("Contraste de propuestas creativas", min_length=3, max_length=100)
    hipotesis: str = Field("Contrastar si la propuesta cambia el CTR frente al control", min_length=10, max_length=350)
    impresiones_por_brazo: int = Field(50000, ge=500, le=200000)
    dias: Literal[7, 14, 28] = 14
    presupuesto_por_brazo: float = Field(500, ge=0, le=1000000)
    coste_produccion: float = Field(250, ge=0, le=1000000)
    semilla: int = Field(264928, ge=0, le=2147483647)

    @model_validator(mode="after")
    def brazos_distintos(self):
        brazos = [self.control, *self.tratamientos]
        if len(set(brazos)) != len(brazos) or any(not 1 <= len(b) <= 40 for b in brazos):
            raise ValueError("Selecciona propuestas distintas del mismo pretest para cada brazo.")
        return self


class AccionAB(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DetalleAB(BaseModel):
    id: str
    snapshot: str
    estado: str
    origen: str
    semilla: int
    inicio: str
    fin: str
    protocolo: dict[str, Any]
    asignaciones: list[dict[str, Any]]
    observaciones: list[dict[str, Any]]
    reutilizada: bool = False
