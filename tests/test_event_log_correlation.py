"""event-log por correlation_id (#34): el filtro devuelve solo el recorrido pedido."""

import json

import pytest
from fastapi.testclient import TestClient

from notif_api.app.db import abrir_pool as abrir_pool_notif
from notif_api.app.db import get_connection
from notif_api.app.init_db import init_db as init_db_notif
from notif_api.main import app


@pytest.fixture(scope="module")
def notif_db():
    abrir_pool_notif()
    init_db_notif()
    yield
    # el pool es global y se reutiliza entre modulos; no se cierra a proposito


@pytest.fixture(autouse=True)
def event_log_limpio(notif_db):
    with get_connection() as conn:
        conn.execute("TRUNCATE event_log RESTART IDENTITY CASCADE")
    yield
    with get_connection() as conn:
        conn.execute("TRUNCATE event_log RESTART IDENTITY CASCADE")


CID_A = "a1b2c3d4e5f60718"
CID_B = "99990000aaaa0000"


def _insertar(cid, tipo, event_id):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO event_log (event_id, entidad_tipo, accion, metadata, correlation_id)"
            " VALUES (%s, %s, 'consumido', %s, %s)",
            (event_id, tipo, json.dumps({}), cid),
        )


def test_filtro_por_correlation_id(event_log_limpio):
    _insertar(CID_A, "mesa.solicitada", "ev-a-0001")
    _insertar(CID_A, "mesa.aceptada", "ev-a-0002")
    _insertar(CID_B, "mesa.solicitada", "ev-b-0001")

    client = TestClient(app)
    r = client.get(f"/api/v1/event-log?correlation_id={CID_A}")
    assert r.status_code == 200
    eventos = r.json()
    assert len(eventos) == 2
    assert all(e["correlationId"] == CID_A for e in eventos)
    assert {e["entidadTipo"] for e in eventos} == {"mesa.solicitada", "mesa.aceptada"}


def test_filtro_sin_resultados(event_log_limpio):
    _insertar(CID_A, "mesa.solicitada", "ev-a-0001")
    client = TestClient(app)
    r = client.get("/api/v1/event-log?correlation_id=ffffffffffffffff")
    assert r.status_code == 200
    assert r.json() == []