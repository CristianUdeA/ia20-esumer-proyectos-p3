"""Rutas HTTP del servicio local."""

from fastapi import APIRouter, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from pqrs_local.domain.models import (
    BorradorRequest,
    BorradorResponse,
    ClasificarRequest,
    Clasificacion,
    SaludResponse,
)
from pqrs_local.services.classification import classify_pqrs
from pqrs_local.services.drafting import prepare_draft


router = APIRouter()


@router.post("/clasificar", response_model=Clasificacion)
def clasificar(request: ClasificarRequest) -> Clasificacion:
    return classify_pqrs(request.texto_pqrs)


@router.post("/borrador", response_model=BorradorResponse)
def borrador(request: BorradorRequest) -> BorradorResponse:
    return prepare_draft(request)


@router.get("/salud", response_model=SaludResponse)
def salud() -> SaludResponse:
    return SaludResponse(
        status="ok",
        components={
            "api": "ready",
            "rag": "not_configured",
            "vertex": "not_configured",
        },
    )


async def safe_validation_error(
    _request: Request,
    _exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "code": "invalid_request",
            "message": "La solicitud no cumple el contrato; revise los campos sin incluir datos personales.",
            "review_required": True,
        },
    )
