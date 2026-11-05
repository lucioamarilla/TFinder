"""CONGELADO: envelope de error canónico de los cuatro servicios.

Aferra la forma exacta de cada clase de error ANTES del refactor de
infraestructura: el refactor debe reproducir estas respuestas tal cual
(400/401/403/404/405 con {"error": {"codigo", "mensaje"}}).
"""

import pytest
from fastapi.testclient import TestClient

from builds_api.main import app as builds_app
from feed_api.main import app as feed_app
from mesas_api.main import app as mesas_app
from notif_api.main import app as notif_app

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module", autouse=True)
def _pools():
    from feed_api.app.db import abrir_pool as abrir_pool_feed
    from mesas_api.app.db import abrir_pool as abrir_pool_mesas

    abrir_pool_mesas()
    abrir_pool_feed()
    yield


@pytest.fixture(scope="module")
def mesas():
    return TestClient(mesas_app)


@pytest.fixture(scope="module")
def builds():
    return TestClient(builds_app)


@pytest.fixture(scope="module")
def feed():
    return TestClient(feed_app)


@pytest.fixture(scope="module")
def notif():
    return TestClient(notif_app)


def test_404_ruta_inexistente_canonica_en_los_cuatro(mesas, builds, feed, notif, token_gm):
    auth = {"Authorization": f"Bearer {token_gm}"}
    esperado = {"error": {"codigo": 404, "mensaje": "Recurso no encontrado"}}
    for cliente in (mesas, builds, feed, notif):
        assert cliente.post("/api/v1/inexistente-para-refactor", headers=auth).json() == esperado


def test_401_autenticacion_requerida(mesas, builds, feed, notif):
    esperado = {"error": {"codigo": 401, "mensaje": "Autenticación requerida"}}
    assert mesas.post("/api/v1/mesas", json={}).json() == esperado
    assert builds.post("/api/v1/builds/1/pdf").json() == esperado
    assert feed.post("/api/v1/mesas/1/sesiones/1/diario", json={}).json() == esperado
    assert notif.patch("/api/v1/notificaciones/leer-todas").json() == esperado


def test_403_rol_insuficiente(mesas, notif, token_gm):
    esperado = {"error": {"codigo": 403, "mensaje": "Rol insuficiente"}}
    assert (
        mesas.get("/api/v1/auth/admin-only", headers={"Authorization": f"Bearer {token_gm}"}).json()
        == esperado
    )
    assert (
        notif.get(
            "/api/v1/dlq", headers={"Authorization": f"Bearer {token_gm}"}
        ).json()
        == esperado
    )


def test_404_dominio_con_mensajes_congelados(mesas, token_gm):
    auth = {"Authorization": f"Bearer {token_gm}"}
    assert mesas.get("/api/v1/mesas/999999").json() == {
        "error": {"codigo": 404, "mensaje": "Mesa 999999 no encontrada"}
    }
    assert mesas.post("/api/v1/mesas/999999/sesiones", headers=auth).json() == {
        "error": {"codigo": 404, "mensaje": "Mesa 999999 no encontrada"}
    }


def test_405_metodo_no_permitido(mesas, builds):
    r = mesas.delete("/api/v1/auth/me")
    assert r.status_code == 405
    assert r.json() == {"error": {"codigo": 405, "mensaje": "Método no permitido para este endpoint"}}

    rb = builds.delete("/api/v1/builds/1")
    assert rb.status_code == 405
    assert rb.json() == {"error": {"codigo": 405, "mensaje": "Método no permitido para este endpoint"}}


def test_400_validacion_con_detalle_de_campos(mesas, token_gm, feed, token_jugador):
    auth = {"Authorization": f"Bearer {token_gm}"}
    r = mesas.post("/api/v1/mesas", json={"nombre": "x", "estado": "otra-cosa"}, headers=auth)
    assert r.status_code == 400
    assert r.json() == {
        "error": {
            "codigo": 400,
            "mensaje": "body.sistema: Field required; body.estado: Input should be 'abierta' or 'cerrada'",
        }
    }

    rf = feed.get("/api/v1/feed?orden=volteado", headers={"Authorization": f"Bearer {token_jugador}"})
    assert rf.status_code == 400
    assert rf.json() == {
        "error": {
            "codigo": 400,
            "mensaje": "orden invalido: usar uno de antiguos, id, recientes, votos",
        }
    }
