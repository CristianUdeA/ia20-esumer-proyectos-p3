"""Resolución segura de credenciales mediante ADC o identidad de carga de trabajo."""

import os


def get_secret_reference() -> str | None:
    """Devuelve únicamente una referencia configurada; nunca el valor secreto."""

    return os.getenv("GOOGLE_SECRET_MANAGER_SECRET_ID") or None
