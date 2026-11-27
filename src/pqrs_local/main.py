"""Punto de entrada de la API local PQRS."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from pqrs_local.api.routes import router
from pqrs_local.api.routes import safe_validation_error


app = FastAPI(title="PQRS local - clasificación y borradores", version="1.0.0")
app.include_router(router)
app.add_exception_handler(RequestValidationError, safe_validation_error)
