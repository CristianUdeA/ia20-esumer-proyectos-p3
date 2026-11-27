"""Política de bloqueo y fundamento de borradores."""

from pqrs_local.domain.models import BorradorResponse, CitaFuente


def unfounded(reason: str = "No se encontró una fuente oficial aprobada") -> BorradorResponse:
    return BorradorResponse(
        texto_borrador=None,
        estado="sin fundamento",
        citas=[],
        revision_requerida=True,
        bloqueado_para_liberacion=True,
        motivo_revision=reason,
    )


def grounded(text: str, citations: list[CitaFuente]) -> BorradorResponse:
    if not citations:
        return unfounded()
    return BorradorResponse(
        texto_borrador=text,
        estado="fundamentado",
        citas=citations,
        revision_requerida=True,
        bloqueado_para_liberacion=True,
        motivo_revision="Revisión humana requerida antes de cualquier liberación",
    )
