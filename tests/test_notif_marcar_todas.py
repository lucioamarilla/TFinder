"""Marcar todas las notificaciones como leídas (cierre AE2).

PATCH /api/v1/notificaciones/leer-todas (spec notificaciones-vivo: marcar leída
y marcar todas). Marca las propias del usuario + las globales (usuario_id IS
NULL, filas compartidas), NO toca las de otros usuarios y es idempotente.
"""

import pytest
from fastapi.testclient import TestClient

from notif_api.app.controllers.notificaciones import marcar_leida
from notif_api.app.db import abrir_pool as abrir_pool_notif
from notif_api.app.db import get_connection
from notif_api.app.init_db import init_db as init_db_notif
from notif_api.app.models.notif import guardar_notificacion
from notif_api.main import app as notif_app

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def notif_db():
    abrir_pool_notif()
    init_db_notif()
    yield
    # el pool es global y se reutiliza entre modulos; no se cierra a proposito


@pytest.fixture
def client_notif(notif_db):
    """TestClient de notif-api sin lifespan (el pool es global compartido)."""
    return TestClient(notif_app)


@pytest.fixture(autouse=True)
def notificaciones_limpias(notif_db):
    with get_connection() as conn:
        conn.execute("TRUNCATE notificaciones RESTART IDENTITY CASCADE")
    yield
    with get_connection() as conn:
        conn.execute("TRUNCATE notificaciones RESTART IDENTITY CASCADE")


def _sub(client, token):
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    return int(resp.json()["sub"])


def _estados_por_usuario():
    with get_connection() as conn:
        filas = conn.execute(
            "SELECT usuario_id, leida FROM notificaciones ORDER BY id"
        ).fetchall()
    estados = {}
    for fila in filas:
        estados.setdefault(fila["usuario_id"], []).append(fila["leida"])
    return estados


def test_marcar_todas_leida_propias_y_globales(client, client_notif, token_jugador, token_gm):
    jugador = _sub(client, token_jugador)
    gm = _sub(client, token_gm)

    guardar_notificacion(jugador, "noti jugador 1")
    ya_leida = guardar_notificacion(jugador, "noti jugador 2 (ya leida)")
    marcar_leida(ya_leida, jugador)
    guardar_notificacion(None, "noti global")
    guardar_notificacion(gm, "noti del gm")

    r = client_notif.patch(
        "/api/v1/notificaciones/leer-todas",
        headers={"Authorization": f"Bearer {token_jugador}"},
    )
    assert r.status_code == 200
    # marca: la propia no leida + la global (la ya leida no cambia de estado)
    assert r.json() == {"actualizadas": 2}

    estados = _estados_por_usuario()
    assert all(estados[jugador])  # ambas del jugador quedan leidas
    assert estados[None] == [True]  # la global también
    assert estados[gm] == [False]  # las del gm NO se tocan


def test_marcar_todas_es_idempotente(client, client_notif, token_jugador):
    jugador = _sub(client, token_jugador)
    guardar_notificacion(jugador, "unico")

    primera = client_notif.patch(
        "/api/v1/notificaciones/leer-todas",
        headers={"Authorization": f"Bearer {token_jugador}"},
    )
    assert primera.status_code == 200
    assert primera.json() == {"actualizadas": 1}

    segunda = client_notif.patch(
        "/api/v1/notificaciones/leer-todas",
        headers={"Authorization": f"Bearer {token_jugador}"},
    )
    assert segunda.status_code == 200
    assert segunda.json() == {"actualizadas": 0}


def test_marcar_todas_requiere_token(client_notif):
    r = client_notif.patch("/api/v1/notificaciones/leer-todas")
    assert r.status_code == 401
