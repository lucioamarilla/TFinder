"""Invariante: los cuatro servicios usan el mismo envelope de error.

    {"error": {"codigo": <int>, "mensaje": <str>}}

FastAPI serializa sus HTTPException como {"detail": ...}. Registrando el
manejador generico de HTTPException en los cuatro servicios, cualquier
`raise HTTPException(401, ...)` de una dependencia de auth queda con la misma
forma que los errores de dominio.
"""

import importlib

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

pytestmark = pytest.mark.unit

SERVICIOS = ("mesas_api", "builds_api", "feed_api", "notif_api")


@pytest.mark.parametrize("servicio", SERVICIOS)
def test_registra_manejador_de_http_exception(servicio):
    app = importlib.import_module(f"{servicio}.main").app
    assert HTTPException in app.exception_handlers, (
        f"{servicio} no registra manejador de HTTPException: "
        "las dependencias de auth responderian con {'detail': ...}"
    )


@pytest.mark.parametrize("servicio", SERVICIOS)
def test_error_por_dependencia_usa_el_envelope_canonico(servicio):
    """Una ruta protegida sin token debe devolver {"error": {...}} en los cuatro."""
    app = importlib.import_module(f"{servicio}.main").app

    @app.get("/__test__/protegido")
    def _protegido():
        raise HTTPException(status_code=401, detail="Autenticación requerida")

    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/__test__/protegido")
    assert r.status_code == 401
    assert r.json() == {"error": {"codigo": 401, "mensaje": "Autenticación requerida"}}


def test_los_cuatro_comparten_el_mismo_modulo_de_errores():
    """Evita que un servicio vuelva a definir su propia copia del envelope."""
    from app.infra import errors as compartido

    for servicio in SERVICIOS:
        mod = importlib.import_module(f"{servicio}.app.errors")
        assert mod.manejar_http is compartido.manejar_http, (
            f"{servicio}.app.errors.manejar_http no viene de app.infra.errors"
        )
        assert mod.manejar_validacion is compartido.manejar_validacion


# --- Errores que genera el router, antes de la capa de manejadores ------------
# Starlette responde 404 y 405 sin pasar por los exception handlers, asi que
# los normaliza app/middleware/error_envelope.py.

RUTA_SOLO_POST = {
    "mesas_api": "/api/v1/matchmaking/1/abrir",
    "builds_api": "/api/v1/builds/1/pdf",
    "feed_api": "/api/v1/mesas/1/sesiones/1/diario/pdf",
    "notif_api": "/api/v1/notificaciones/1/leida",
}


@pytest.mark.parametrize("servicio", SERVICIOS)
def test_405_usa_el_envelope_canonico(servicio):
    app = importlib.import_module(f"{servicio}.main").app
    client = TestClient(app, raise_server_exceptions=False)
    r = client.get(RUTA_SOLO_POST[servicio])
    assert r.status_code == 405
    cuerpo = r.json()
    assert set(cuerpo) == {"error"}
    assert cuerpo["error"]["codigo"] == 405
    assert cuerpo["error"]["mensaje"] == "Método no permitido para este endpoint"


@pytest.mark.parametrize("servicio", SERVICIOS)
def test_404_de_ruta_inexistente_usa_el_envelope_canonico(servicio):
    app = importlib.import_module(f"{servicio}.main").app
    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/api/v1/no-existe-este-path")
    assert r.status_code == 404
    cuerpo = r.json()
    assert cuerpo["error"]["codigo"] == 404
    assert cuerpo["error"]["mensaje"] == "Recurso no encontrado"


def test_no_se_altera_una_respuesta_correcta():
    """El middleware solo toca errores: un 200 debe pasar intacto.

    Usa /live y no /health a proposito: /live responde sin tocar PostgreSQL,
    asi que este test unitario no necesita la base. /health hace SELECT 1 y
    pertenece a la suite de integracion.
    """
    app = importlib.import_module("mesas_api.main").app
    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/live")
    assert r.status_code == 200
    assert r.json() == {"estado": "vivo"}


def test_el_middleware_no_rompe_el_streaming():
    """SSE usa respuestas por chunks; el middleware no debe almacenarlas."""
    from starlette.applications import Starlette
    from starlette.responses import StreamingResponse
    from starlette.routing import Route

    from app.middleware.error_envelope import ErrorEnvelopeMiddleware

    async def _stream(request):
        async def _generador():
            for i in range(3):
                yield f"data: evento-{i}\n\n".encode()

        return StreamingResponse(_generador(), media_type="text/event-stream")

    app = Starlette(routes=[Route("/stream", _stream)])
    app.add_middleware(ErrorEnvelopeMiddleware)

    from starlette.testclient import TestClient

    with TestClient(app) as client:
        with client.stream("GET", "/stream") as respuesta:
            assert respuesta.status_code == 200
            assert respuesta.headers["content-type"].startswith("text/event-stream")
            cuerpo = "".join(
                trozo.decode() for trozo in respuesta.iter_raw()
            )
    assert "evento-0" in cuerpo and "evento-2" in cuerpo
