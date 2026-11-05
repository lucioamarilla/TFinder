"""Publicar diario de sesión (cierre AE2): persistencia + evento.

El endpoint POST /api/v1/mesas/{m}/sesiones/{s}/diario persiste la publicación
en publicaciones (feed_db) y emite sesion.diario_publicado a la cola
notif.sesion; el evento se verifica leyendo la cola con pika en el vhost de
pruebas (aislamiento del conftest).
"""

import json

import pika
import pytest
from fastapi.testclient import TestClient

from app.infra.rabbitmq import get_params
from feed_api.app.db import abrir_pool as abrir_pool_feed
from feed_api.app.db import get_connection
from feed_api.app.init_db import init_db as init_db_feed
from feed_api.main import app as feed_app
from notif_api.app.infra.amqp import COLA_SESION, declarar
from tests.conftest import crear_mesa

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def feed_db():
    abrir_pool_feed()
    init_db_feed()
    yield
    # el pool es global y se reutiliza entre modulos; no se cierra a proposito


@pytest.fixture
def client_feed(feed_db):
    """TestClient de feed-api sin lifespan (el pool es global compartido)."""
    return TestClient(feed_app)


@pytest.fixture(autouse=True)
def publicaciones_limpias(feed_db):
    with get_connection() as conn:
        conn.execute("TRUNCATE publicaciones RESTART IDENTITY CASCADE")
    yield
    with get_connection() as conn:
        conn.execute("TRUNCATE publicaciones RESTART IDENTITY CASCADE")


@pytest.fixture(autouse=True)
def cola_sesion_limpia():
    declarar()
    _purgar()
    yield
    _purgar()


def _purgar():
    conn = pika.BlockingConnection(get_params())
    try:
        conn.channel().queue_purge(queue=COLA_SESION)
    finally:
        conn.close()


def _leer_evento_sesion():
    conn = pika.BlockingConnection(get_params())
    try:
        canal = conn.channel()
        frame = canal.basic_get(queue=COLA_SESION, auto_ack=True)
        if frame[0] is None:
            return None
        return json.loads(frame[2])
    finally:
        conn.close()


def test_publicar_diario_persiste_y_emite_evento(client, client_feed, token_jugador, token_gm):
    mesa_id = crear_mesa(client, token_gm, "Mesa diario", jugadores_max=4)
    r = client_feed.post(
        f"/api/v1/mesas/{mesa_id}/sesiones/1/diario",
        json={"titulo": "Escaparon de la mazmorra", "cuerpo": "¡Sobrevivieron!"},
        headers={"Authorization": f"Bearer {token_jugador}"},
    )
    assert r.status_code == 201
    datos = r.json()
    assert datos["estado"] == "publicado"
    assert datos["sesion_id"] == 1

    # persistencia en feed_db (tabla propiedad del servicio)
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT tipo, titulo, cuerpo, autor_id FROM publicaciones WHERE id = %s",
            (datos["id"],),
        ).fetchone()
    assert fila["titulo"] == "Escaparon de la mazmorra"
    assert fila["cuerpo"] == "¡Sobrevivieron!"
    assert fila["tipo"] == "post"

    # evento de dominio en la cola que consume notif-api
    evento = _leer_evento_sesion()
    assert evento is not None
    assert evento["tipo"] == "sesion.diario_publicado"
    assert int(evento["mesa_id"]) == mesa_id
    assert evento["sesion_id"] == 1
    assert evento["titulo"] == "Escaparon de la mazmorra"


def test_publicar_diario_requiere_token(client_feed):
    r = client_feed.post(
        "/api/v1/mesas/1/sesiones/1/diario",
        json={"titulo": "t", "cuerpo": "c"},
    )
    assert r.status_code == 401


def test_publicar_diario_valida_el_cuerpo(client_feed, token_jugador):
    r = client_feed.post(
        "/api/v1/mesas/1/sesiones/1/diario",
        json={"titulo": "", "cuerpo": "c"},
        headers={"Authorization": f"Bearer {token_jugador}"},
    )
    assert r.status_code == 400
    assert r.json()["error"]["codigo"] == 400
    assert "titulo" in r.json()["error"]["mensaje"]
