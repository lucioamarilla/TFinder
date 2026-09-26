"""Envelope de error unificado para los cuatro servicios.

Los cuatro servicios deben responder TODOS los errores con la misma forma:

    {"error": {"codigo": <int>, "mensaje": <str>}}

FastAPI serializa sus `HTTPException` como `{"detail": "..."}`. Sin el manejador
de `HTTPException` registrado, cualquier `raise HTTPException(401, ...)` de una
dependencia de autenticacion se escapa con la forma por defecto y el cliente
recibe dos convenciones distintas segun a que servicio pegue. Por eso el
registro va en un solo lugar (`registrar_manejadores`) y no servicio por
servicio.
"""

import logging

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

__all__ = [
    "body_error",
    "manejar_http",
    "manejar_validacion",
    "manejar_error_interno",
    "registrar_manejadores",
]


def body_error(codigo, mensaje):
    """Construye el envelope canonico de error."""
    return {"error": {"codigo": codigo, "mensaje": mensaje}}


def manejar_http(request, exc: HTTPException):
    """HTTPException (401/403/404/409 lanzados a mano) -> envelope canonico."""
    detalle = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=body_error(exc.status_code, detalle),
    )


def manejar_validacion(request, exc: RequestValidationError):
    """RequestValidationError -> 400 con el detalle por campo."""
    piezas = []
    for detalle in exc.errors():
        loc = detalle.get("loc", [])
        campo = ".".join(str(p) for p in loc)
        msg = detalle.get("msg", "Valor invalido")
        piezas.append(f"{campo}: {msg}" if campo else msg)
    return JSONResponse(
        status_code=400,
        content=body_error(400, "; ".join(piezas) or "Datos de entrada invalidos"),
    )


def manejar_error_interno(servicio: str):
    """Construye el manejador de 500 con el logger del servicio."""

    logger = logging.getLogger(f"tfinder.{servicio}")

    def _handler(request, exc: Exception):
        logger.exception("Error no controlado en %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content=body_error(500, "Error interno del servidor"),
        )

    return _handler


def registrar_manejadores(app, servicio: str, adicionales: dict | None = None):
    """Registra los manejadores canonicos. `adicionales` mapea excepcion -> handler.

    El orden importa: las excepciones de dominio se resuelven por tipo exacto, asi
    que `adicionales` se aplica despues y no pisa nada.
    """
    app.add_exception_handler(HTTPException, manejar_http)
    app.add_exception_handler(RequestValidationError, manejar_validacion)
    app.add_exception_handler(Exception, manejar_error_interno(servicio))
    for exc_tipo, handler in (adicionales or {}).items():
        app.add_exception_handler(exc_tipo, handler)
