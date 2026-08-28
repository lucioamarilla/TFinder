from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.controllers.mesas_controller import MesaNotFoundError


def _body_error(codigo, mensaje):
    return {"error": {"codigo": codigo, "mensaje": mensaje}}


def manejar_no_encontrado(request, exc: MesaNotFoundError):
    return JSONResponse(status_code=404, content=_body_error(404, str(exc)))


def manejar_validacion(request, exc: RequestValidationError):
    piezas = []
    for detalle in exc.errors():
        loc = detalle.get("loc", [])
        campo = ".".join(str(p) for p in loc)
        msg = detalle.get("msg", "Valor invalido")
        piezas.append(f"{campo}: {msg}" if campo else msg)
    return JSONResponse(
        status_code=400,
        content=_body_error(400, "; ".join(piezas) or "Datos de entrada invalidos"),
    )