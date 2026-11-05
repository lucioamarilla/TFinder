"""Errores de builds-api. Delega el envelope canonico en app.infra.errors."""

from fastapi.responses import JSONResponse

from app.infra.errors import body_error as _body_error
from app.infra.errors import manejar_http, manejar_validacion
from builds_api.app.controllers.builds import (
    BuildNotFoundError,
    BuildProhibidoError,
    ValorInvalidoError,
)

__all__ = [
    "manejar_http",
    "manejar_no_encontrado",
    "manejar_prohibido_build",
    "manejar_valor_invalido_build",
    "manejar_validacion",
]


def manejar_no_encontrado(request, exc: BuildNotFoundError):
    return JSONResponse(status_code=404, content=_body_error(404, str(exc)))


def manejar_prohibido_build(request, exc: BuildProhibidoError):
    return JSONResponse(status_code=403, content=_body_error(403, str(exc)))


def manejar_valor_invalido_build(request, exc: ValorInvalidoError):
    return JSONResponse(status_code=400, content=_body_error(400, str(exc)))
