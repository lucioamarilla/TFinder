"""Normalizacion del envelope de error en el borde de la respuesta.

Los manejadores de excepcion cubren 401/403/404/409 que lanzan los endpoints y
las dependencias de autenticacion, pero hay errores que Starlette responde ANTES
de llegar a esa capa:

- 405 Method Not Allowed, cuando la ruta existe con otro metodo.
- 404 Not Found, cuando no matchea ninguna ruta.

Esos dos salen con `{"detail": "..."}` (o texto plano) y rompen la convencion
que comparten los cuatro servicios. Un middleware que reescribiera todas las
respuestas romperia el streaming de SSE, asi que solo se bufferizan las
respuestas de error: son cortas y no se transmiten en chunks.
"""

import json

__all__ = ["ErrorEnvelopeMiddleware", "canonicalizar"]

_MARCA = "x-tfinder-envelope"


def _texto_de_detail(detail):
    """Convierte el `detail` de FastAPI en una cadena legible.

    FastAPI usa un string para HTTPException y una lista de dicts para errores de
    validacion. En el segundo caso hay que aplanarla.
    """
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):
        piezas = []
        for item in detail:
            if isinstance(item, dict):
                loc = ".".join(str(p) for p in item.get("loc", []))
                msg = item.get("msg", "Valor invalido")
                piezas.append(f"{loc}: {msg}" if loc else msg)
            else:
                piezas.append(str(item))
        return "; ".join(piezas) or "Datos de entrada invalidos"
    return str(detail)


# Detalles que emite Starlette en ingles. El resto de la API responde en
# castellano, asi que se traducen en el borde para no mezclar idiomas.
_TRADUCCIONES = {
    404: {"Not Found": "Recurso no encontrado"},
    405: {"Method Not Allowed": "Método no permitido para este endpoint"},
    401: {"Unauthorized": "Autenticación requerida"},
    403: {"Forbidden": "Rol insuficiente"},
}


def _mensaje(detail, status):
    texto = _texto_de_detail(detail)
    return _TRADUCCIONES.get(status, {}).get(texto, texto)


def canonicalizar(cuerpo: bytes, status: int) -> bytes | None:
    """Devuelve el cuerpo normalizado, o None si no hay que tocarlo."""
    try:
        datos = json.loads(cuerpo)
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(datos, dict):
        return None
    if "error" in datos:
        return None  # ya canonico
    if "detail" in datos:
        mensaje = _mensaje(datos["detail"], status)
    else:
        return None
    return json.dumps(
        {"error": {"codigo": status, "mensaje": mensaje}}, ensure_ascii=False
    ).encode()


class ErrorEnvelopeMiddleware:
    """Reescribe a `{"error": {"codigo", "mensaje"}}` las respuestas de error
    que no pasaron por los manejadores de excepcion."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Solo se bufferiza si la respuesta es un error con cuerpo JSON. El SSE
        # (200) y las descargas de PDF pasan de largo sin almacenar nada.
        buffer = None
        inicio = None
        status = 0

        async def send_wrapper(message):
            nonlocal buffer, inicio, status

            if message["type"] == "http.response.start":
                status = message["status"]
                ctype = dict(
                    (k.decode().lower(), v.decode().lower())
                    for k, v in message.get("headers", [])
                )
                ya_canonico = ctype.get(_MARCA) == "1"
                if status >= 400 and "json" in ctype.get("content-type", "") and not ya_canonico:
                    buffer = bytearray()
                    inicio = message
                    return
                await send(message)
                return

            if message["type"] == "http.response.body":
                if buffer is not None:
                    buffer.extend(message.get("body", b""))
                    if message.get("more_body"):
                        return
                    cuerpo = canonicalizar(bytes(buffer), status) or bytes(buffer)
                    cabeceras = [
                        (k, v)
                        for k, v in (inicio or {}).get("headers", [])
                        if k.decode().lower() != "content-length"
                    ]
                    cabeceras.append((b"content-length", str(len(cuerpo)).encode()))
                    cabeceras.append((_MARCA.encode(), b"1"))
                    await send({**(inicio or {}), "headers": cabeceras})
                    await send(
                        {"type": "http.response.body", "body": cuerpo, "more_body": False}
                    )
                    return
                await send(message)
                return

            await send(message)

        await self.app(scope, receive, send_wrapper)
