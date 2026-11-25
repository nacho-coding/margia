from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ParametrosPretest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, str_strip_whitespace=True)
    canal: Literal["meta", "tiktok", "youtube", "display"] = "meta"
    categoria: Literal["hogar", "moda", "belleza"] = "hogar"
    audiencia: str = Field("Cohorte 01", min_length=3, max_length=30)
    frecuencia: float = Field(2.5, ge=1, le=10)
    impresiones: int = Field(10000, ge=1000, le=1000000)
    objetivo: str = Field("Explorar una composición más clara para la colección", min_length=10, max_length=250)


class EvaluacionCreativa(BaseModel):
    id: str
    snapshot: str
    modelo: str
    version: str
    semilla: int
    entradas: ParametrosPretest
    estado: str
    evidencia: str
    ganador: str | None
    motivos: list[str]
    referencia: dict[str, Any]
    variantes: list[dict[str, Any]]
    brief: dict[str, Any]
    advertencias: list[str]
    reutilizada: bool = False


class SeleccionarCreativo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pretest_id: str = Field(min_length=1, max_length=60)
    variante_id: str = Field(min_length=1, max_length=40)


class SeleccionRespuesta(BaseModel):
    id: str
    pretest_id: str
    variante_id: str
    snapshot: str
    modelo: str
    evidencia: str
    multiplicador_demanda: Literal[1.0]
    efecto_identificado: Literal[False]
    motivo: str
    reutilizada: bool = False
