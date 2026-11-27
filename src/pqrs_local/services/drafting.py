"""Servicio consultivo de borradores."""

from pqrs_local.domain.models import BorradorRequest, BorradorResponse
from pqrs_local.services.draft_policy import unfounded
from pqrs_local.services.input_safety import sanitize_for_controlled_context
from pqrs_local.services.rag import retrieve_approved_sources


def prepare_draft(request: BorradorRequest) -> BorradorResponse:
    # Solo los metadatos controlados se usan para retrieval; el texto no se persiste.
    controlled_context = sanitize_for_controlled_context(request.texto_pqrs)
    try:
        citations = retrieve_approved_sources(controlled_context)
    except Exception:
        return BorradorResponse(
            texto_borrador=None,
            estado="no_disponible",
            citas=[],
            revision_requerida=True,
            bloqueado_para_liberacion=True,
            motivo_revision="Fuente o generación no disponible",
        )

    if not citations:
        return unfounded()

    # El servicio P1 no genera texto sin una integración real aprobada.
    return unfounded("No existe un generador aprobado disponible en el entorno local")
