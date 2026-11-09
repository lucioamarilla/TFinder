"""Errores de mesas-api. Reexporta el envelope canonico de app.infra.errors.

Los handlers de dominio (MesaNotFoundError, CupoAgotadoError, sesiones) son
propios de este servicio; la forma del cuerpo y los handlers genericos son
compartidos.
"""

from fastapi.responses import JSONResponse

from app.infra.errors import body_error as _body_error
from app.infra.errors import manejar_error_interno, manejar_http, manejar_validacion
from mesas_api.app.controllers.mesas import (
    CupoMenorError,
    MesaNotFoundError,
    MesaUsurpadoError,
)
from mesas_api.app.controllers.sesiones_controller import SesionNotFoundError
from mesas_api.app.controllers.solicitudes_controller import (
    AccionInvalidaError,
    CupoAgotadoError,
    MesaCerradaError,
    MesaNoExisteError,
    SolicitudDuplicadaError,
    SolicitudNoExisteError,
    SolicitudProhibidaError,
)
__all__ = [
    "manejar_conflicto",
    "manejar_error_interno",
    "manejar_http",
    "manejar_mesa_inexistente",
    "manejar_no_encontrado",
    "manejar_prohibido",
    "manejar_sesion_inexistente",
    "manejar_solicitud_inexistente",
    "manejar_validacion",
    "manejar_accion_invalida",
]


def manejar_no_encontrado(request, exc: MesaNotFoundError):
    return JSONResponse(status_code=404, content=_body_error(404, str(exc)))


def manejar_conflicto(request, exc):
    return JSONResponse(status_code=409, content=_body_error(409, str(exc)))


def manejar_prohibido(request, exc: MesaUsurpadoError | SolicitudProhibidaError):
    return JSONResponse(status_code=403, content=_body_error(403, str(exc)))


def manejar_solicitud_inexistente(request, exc: SolicitudNoExisteError):
    return JSONResponse(status_code=404, content=_body_error(404, str(exc)))


def manejar_accion_invalida(request, exc: AccionInvalidaError):
    return JSONResponse(status_code=400, content=_body_error(400, str(exc)))


def manejar_mesa_inexistente(request, exc: MesaNoExisteError):
    return JSONResponse(status_code=404, content=_body_error(404, str(exc)))


def manejar_sesion_inexistente(request, exc: SesionNotFoundError):
    return JSONResponse(status_code=404, content=_body_error(404, str(exc)))
