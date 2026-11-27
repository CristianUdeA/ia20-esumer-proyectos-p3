"""Modelos Pydantic utilizados por la API."""

from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


TipoPQRS = Literal["Petición", "Queja", "Reclamo", "Sugerencia"]
EstadoBorrador = Literal[
    "fundamentado",
    "sin fundamento",
    "revision_requerida",
    "no_disponible",
]


class SolicitudPQRS(BaseModel):
    model_config = ConfigDict(extra="forbid")

    texto_pqrs: str = Field(min_length=1, max_length=50000)
    correlation_id: UUID | None = None


class ClasificarRequest(SolicitudPQRS):
    pass


class BorradorRequest(SolicitudPQRS):
    pass


class Clasificacion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cliente: str | None = None
    contrato: str | None = None
    tipo: TipoPQRS
    categoria: str | None = None
    urgencia: str | None = None
    resumen: str | None = None
    nivel_confianza: float = Field(ge=0.0, le=1.0)
    motivo: str
    datos_ausentes: list[str] = Field(default_factory=list)
    revision_requerida: bool


class CitaFuente(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str
    version: str
    ubicacion: str
    fragmento: str


class BorradorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    texto_borrador: str | None = None
    estado: EstadoBorrador
    citas: list[CitaFuente] = Field(default_factory=list)
    revision_requerida: bool
    bloqueado_para_liberacion: Literal[True] = True
    motivo_revision: str | None = None


class SaludResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok", "degraded"]
    components: dict[str, Literal["ready", "unavailable", "not_configured"]]
