"""RAG local con fuentes aprobadas."""

from pqrs_local.domain.models import CitaFuente


def retrieve_approved_sources(_controlled_text: str) -> list[CitaFuente]:
    """Stub seguro: no devuelve fuentes hasta que exista un índice aprobado."""

    return []
