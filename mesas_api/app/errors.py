"""Errores de mesas-api. Reexporta el envelope canonico de app.infra.errors.

Los handlers de dominio (MesaNotFoundError, CupoAgotadoError, QR) son propios de
este servicio; la forma del cuerpo y los handlers genericos son compartidos.
"""

from fastapi.responses import JSONResponse

from app.infra.errors import body_error as _body_error
from app.infra.errors import manejar_error_interno, manejar_http, manejar_validacion
from mesas_api.app.controllers.mesas import MesaNotFoundError
from mesas_api.app.controllers.sesiones_controller import SesionNotFoundError
from mesas_api.app.controllers.solicitudes_controller import (
    CupoAgotadoError,
    MesaNoExisteError,
    SolicitudEnProcesoError,
)
from mesas_api.app.services.qr_asistencia import _Conflict, _Invalid

__all__ = [
    "manejar_conflicto",
    "manejar_error_interno",
    "manejar_http",
    "manejar_mesa_inexistente",
    "manejar_no_encontrado",
    "manejar_qr_conflicto",
    "manejar_qr_invalido",
    "manejar_sesion_inexistente",
    "manejar_validacion",
]


def manejar_no_encontrado(request, exc: MesaNotFoundError):
    return JSONResponse(status_code=404, content=_body_error(404, str(exc)))


def manejar_conflicto(request, exc):
    return JSONResponse(status_code=409, content=_body_error(409, str(exc)))


def manejar_mesa_inexistente(request, exc: MesaNoExisteError):
    return JSONResponse(status_code=404, content=_body_error(404, str(exc)))


def manejar_sesion_inexistente(request, exc: SesionNotFoundError):
    return JSONResponse(status_code=404, content=_body_error(404, str(exc)))


def manejar_qr_conflicto(request, exc: _Conflict):
    return JSONResponse(status_code=409, content=_body_error(409, str(exc)))


def manejar_qr_invalido(request, exc: _Invalid):
    return JSONResponse(status_code=400, content=_body_error(400, str(exc)))
