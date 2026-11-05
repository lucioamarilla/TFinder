"""F5 · Uploads de imágenes (pliego F5 — perfil y foro)."""

import io

import pytest
from fastapi.testclient import TestClient

from feed_api.app.db import abrir_pool as abrir_pool_feed
from feed_api.app.init_db import init_db as init_db_feed
from feed_api.main import app as feed_app
from tests.conftest import _crear_con_rol

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module", autouse=True)
def _pools_feed():
    abrir_pool_feed()
    init_db_feed()
    yield


@pytest.fixture
def feed_client(_pools_feed):
    return TestClient(feed_app)


def _png_bytes():
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 32


def test_subir_png_ok(feed_client):
    auth = {"Authorization": f"Bearer {_crear_con_rol('usuario')}"}
    r = feed_client.post(
        "/api/v1/uploads",
        files={"upload": ("avatar.png", io.BytesIO(_png_bytes()), "image/png")},
        headers=auth,
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["mime"] == "image/png"
    assert body["url"].endswith(body["id"])
    # descarga pública
    desc = feed_client.get(f"/api/v1/uploads/{body['id']}")
    assert desc.status_code == 200
    assert desc.headers["content-type"] == "image/png"


def test_mime_no_permitido_da_400(feed_client):
    auth = {"Authorization": f"Bearer {_crear_con_rol('usuario')}"}
    r = feed_client.post(
        "/api/v1/uploads",
        files={"upload": ("x.gif", io.BytesIO(b"GIF89a"), "image/gif")},
        headers=auth,
    )
    assert r.status_code == 400


def test_subir_sin_auth_da_401(feed_client):
    r = feed_client.post(
        "/api/v1/uploads",
        files={"upload": ("avatar.png", io.BytesIO(_png_bytes()), "image/png")},
    )
    assert r.status_code == 401
