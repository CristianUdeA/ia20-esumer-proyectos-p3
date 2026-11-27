"""Enumeraciones de dominio."""

from enum import Enum


class TipoPQRS(str, Enum):
    PETICION = "Petición"
    QUEJA = "Queja"
    RECLAMO = "Reclamo"
    SUGERENCIA = "Sugerencia"


class EstadoBorrador(str, Enum):
    FUNDAMENTADO = "fundamentado"
    SIN_FUNDAMENTO = "sin fundamento"
    REVISION_REQUERIDA = "revision_requerida"
    NO_DISPONIBLE = "no_disponible"
