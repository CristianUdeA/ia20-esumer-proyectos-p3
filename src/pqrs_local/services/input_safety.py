"""Guardas locales de seguridad de entrada."""

import re


_CONTROL_MARKERS = re.compile(
    r"(?i)\b(ignora|ignore|sobrescribe|override|marca|cerrar|resuelto|"
    r"instrucciones|sistema|prompt|desactiva|bypass)\b"
)
_PII_MARKERS = re.compile(
    r"(?i)(MARCADOR_(?:PII|PRIVADO|SINTETICO)[A-Z0-9_]*)"
)


def sanitize_for_controlled_context(text: str) -> str:
    """Devuelve etiquetas no identificables para contextos controlados."""

    if not isinstance(text, str):
        return ""

    if _PII_MARKERS.search(text):
        return "MARCADOR_PRIVADO_ELIMINADO"
    if _CONTROL_MARKERS.search(text):
        return "INSTRUCCION_DE_CLIENTE_DESCONFIADA"
    return "TEXTO_LIBRE_PQRS_NO_INTERPRETADO"
