"""P1.7 · Feed activo (RF-16/17/18, RN-10, VAL-34..37, 41..43):
crear publicación, like único (con toggle), follows.

RED previo: el feed era solo lectura (GET) y semillas.
"""

import pytest
from fastapi.testclient import TestClient

from feed_api.app.db import abrir_pool as abrir_pool_feed
from feed_api.app.db import get_connection as feed_conn
from feed_api.app.init_db import init_db as init_db_feed
from feed_api.main import app as feed_app
from tests.conftest import _crear_con_rol

pytestmark = pytest.mark.integration

FEED_TABLAS = "wiki_paginas, publicaciones, follows, likes_post"


@pytest.fixture(scope="module", autouse=True)
def _pools():
    abrir_pool_feed()
    init_db_feed()
    yield


@pytest.fixture(autouse=True)
def _limpieza(_pools):
    with feed_conn() as conn:
        conn.execute(f"TRUNCATE {FEED_TABLAS} RESTART IDENTITY CASCADE")
    yield
    with feed_conn() as conn:
        conn.execute(f"TRUNCATE {FEED_TABLAS} RESTART IDENTITY CASCADE")


@pytest.fixture
def feed():
    return TestClient(feed_app)


def _usuario_rol(rol="usuario"):
    token = _crear_con_rol(rol)
    return {"Authorization": f"Bearer {token}"}


# ---- RF-16: crear publicación --------------------------------------------------

def test_crear_publicacion(feed):
    auth = _usuario_rol()
    r = feed.post(
        "/api/v1/feed",
        json={"titulo": "Mi primera crónica", "cuerpo": "Hoy cayó el dragón", "tipo": "post"},
        headers=auth,
    )
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["titulo"] == "Mi primera crónica"
    assert cuerpo["tipo"] == "post"
    assert cuerpo["votos"] == 0


def test_publicacion_vacia_da_400(feed):
    auth = _usuario_rol()
    r = feed.post(
        "/api/v1/feed",
        json={"titulo": "", "cuerpo": "  "},
        headers=auth,
    )
    assert r.status_code == 400, "VAL-41: contenido no vacío"


def test_crear_sin_auth_da_401(feed):
    r = feed.post("/api/v1/feed", json={"titulo": "x", "cuerpo": "y"})
    assert r.status_code == 401


# ---- RF-17/VAL-43: like único con toggle ----------------------------------------

def test_like_unico_y_toggle(feed):
    auth = _usuario_rol()
    post_id = feed.post(
        "/api/v1/feed",
        json={"titulo": "Me gusta el feed", "cuerpo": "contenido", "tipo": "post"},
        headers=auth,
    ).json()["id"]

    r = feed.post(f"/api/v1/feed/{post_id}/like", headers=auth)
    assert r.status_code == 200
    assert r.json()["votos"] == 1
    assert r.json()["megusta"] is True

    otra = feed.post(f"/api/v1/feed/{post_id}/like", headers=auth)
    assert otra.status_code == 200, "el segundo like/quite es un toggle, no un 409 ruidoso"
    assert otra.json()["votos"] == 0
    assert otra.json()["megusta"] is False


def test_like_404(feed):
    auth = _usuario_rol()
    r = feed.post("/api/v1/feed/99999/like", headers=auth)
    assert r.status_code == 404, "VAL-42"


def test_likes_de_varios_usuarios_suman(feed):
    auth1 = _usuario_rol()
    post_id = feed.post(
        "/api/v1/feed",
        json={"titulo": "Popular", "cuerpo": "contenido", "tipo": "post"},
        headers=auth1,
    ).json()["id"]
    feed.post(f"/api/v1/feed/{post_id}/like", headers=auth1)
    res = feed.post(f"/api/v1/feed/{post_id}/like", headers=_usuario_rol())
    assert res.json()["votos"] == 2, "like de dos usuarios distintos suma 2 (1 por cabeza)"


# ---- RF-18/RN-10: follows --------------------------------------------------------

def _crear_post_y_sub(feed, auth):
    r = feed.post(
        "/api/v1/feed",
        json={"titulo": "Quién soy", "cuerpo": "contenido", "tipo": "post"},
        headers=auth,
    )
    assert r.status_code == 201
    return r.json()["autorId"]


def test_seguir_a_otro_usuario(feed):
    auth1 = _usuario_rol()
    auth2 = _usuario_rol("gm")
    sub1 = _crear_post_y_sub(feed, auth1)
    sub2 = _crear_post_y_sub(feed, auth2)

    r = feed.post(f"/api/v1/usuarios/{sub2}/seguir", headers=auth1)
    assert r.status_code == 200, "RF-18: seguir a otro usuario"
    assert r.json()["seguidores"] == 1

    duplicado = feed.post(f"/api/v1/usuarios/{sub2}/seguir", headers=auth1)
    assert duplicado.status_code == 409, " VAL no duplica follow previo"

    auto = feed.post(f"/api/v1/usuarios/{sub1}/seguir", headers=auth1)
    assert auto.status_code == 409, "RN-10: no te podés seguir a ti mismo"

    dejado = feed.post(f"/api/v1/usuarios/{sub2}/seguir", headers=_usuario_rol("admin"))
    assert dejado.status_code == 200, "cada usuario suma su propio follow"
