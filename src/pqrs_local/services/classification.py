"""Clasificación local determinista de PQRS."""

import re

from pqrs_local.domain.models import Clasificacion


CONFIDENCE_THRESHOLD = 0.70

_TYPE_PATTERNS = {
    "Petición": (
        r"\b(solicito|solicitud|quisiera|necesito|deseo|solicitar|"
        r"informaci[oó]n|copia|revisar|consultar)\b"
    ),
    "Queja": (
        r"\b(queja|problema|fall[aao]|lento|caido|caído|intermitente|"
        r"desconecta|inconforme|molesto|no funciona|internet|servicio)\b"
    ),
    "Reclamo": (
        r"\b(reclamo|cobro|cobraron|duplicad|devuelv|factura|reembolso|"
        r"injust[oia]|descuento|rob[oó]|dinero|acceso indebido)\b"
    ),
    "Sugerencia": (
        r"\b(sugerencia|sugiero|ser[ií]a [uú]til|propongo|mejorar|"
        r"podr[ií]an|avisos|proponer)\b"
    ),
}


def _normalize(text: str) -> str:
    return text.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")


def classify_pqrs(text: str) -> Clasificacion:
    """Clasifica sin transmitir ni persistir el texto del caso."""

    if not isinstance(text, str) or not text.strip():
        return Clasificacion(
            tipo="Petición",
            nivel_confianza=0.0,
            motivo="Texto ausente",
            datos_ausentes=["texto_pqrs"],
            revision_requerida=True,
        )

    normalized = _normalize(text)

    reclam_markers = re.search(
        r"(cobr|factur|dinero|reembols|devuel|devoluci|duplicad|indebid|descuent|aument|reconexion)",
        normalized,
    )
    suggestion_markers = re.search(
        r"(suger|propongo|seria|podrian|mejoraria|mejorar)",
        normalized,
    )
    petition_markers = re.search(
        r"\b(solicito|solicitud|quisiera|necesito|deseo|solicitar|informaci|copia|trasladar|instalacion|conocer)\b",
        normalized,
    )
    complaint_markers = re.search(
        r"(queja|problema|fallo|falla|lento|caido|intermitente|desconecta|inconforme|molesto|no funciona|se�al|senal|señal|router|velocidad|equipos pierden)",
        normalized,
    )

    if reclam_markers:
        tipo = "Reclamo"
        score_count = 1
        reason = "Clasificación local basada en palabras controladas"
    elif suggestion_markers:
        tipo = "Sugerencia"
        score_count = 1
        reason = "Clasificación local basada en palabras controladas"
    elif complaint_markers and not petition_markers:
        tipo = "Queja"
        score_count = 1
        reason = "Clasificación local basada en palabras controladas"
    elif petition_markers:
        tipo = "Petición"
        score_count = 1
        reason = "Clasificación local basada en palabras controladas"
    else:
        tipo = "Queja" if "internet" in normalized or "servicio" in normalized else "Petición"
        score_count = 0
        reason = "Contenido insuficiente o clasificación ambigua"

    tied = False
    short_or_unknown = len(text.strip()) < 12 or score_count == 0
    if short_or_unknown:
        confidence = 0.55
    else:
        confidence = 0.92

    if any(marker in normalized for marker in ("ignora", "ignore", "marca como", "bypass")):
        confidence = min(confidence, 0.58)
        reason = "Posible instrucción ajena; el texto se trató como datos"

    category = None
    if re.search(r"\b(factura|cobro|reclamo|dinero|pago)\b", normalized):
        category = "facturacion"
    elif re.search(r"\b(internet|wifi|tecnico|tecnico|señal|senal|conexion|conexion)\b", normalized):
        category = "falla_tecnica"
    elif re.search(r"\b(instalacion|traslado|cobertura|plan)\b", normalized):
        category = "servicio"

    urgency = None
    if re.search(r"\b(hoy|urgente|inmediata|inmediatamente|trabajo|sin servicio)\b", normalized):
        urgency = "Alta"
    elif re.search(r"\b(ma�ana|manana|pr[oó]ximo|cop[aí]a|informaci[oó]n)\b", normalized):
        urgency = "Media"
    else:
        urgency = "Baja"

    missing = []
    if len(text.strip()) < 12:
        missing.append("resumen")

    return Clasificacion(
        cliente=None,
        contrato=None,
        tipo=tipo,
        categoria=category,
        urgencia=urgency,
        resumen=None,
        nivel_confianza=round(confidence, 2),
        motivo=reason,
        datos_ausentes=missing,
        revision_requerida=confidence < CONFIDENCE_THRESHOLD or bool(missing),
    )
