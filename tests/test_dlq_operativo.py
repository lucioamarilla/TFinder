"""DLQ operativo (#34): reintentar y descartar un mensaje de dlq.general via notif-api."""

import pytest
from fastapi.testclient import TestClient

from notif_api.app.db import abrir_pool as abrir_pool_notif
from notif_api.app.init_db import init_db as init_db_notif
from notif_api.main import app

NOTIF_TABLAS = "event_log, mensaje_dlq, documentos, notificaciones, emails"


@pytest.fixture(scope="module")
def notif_db():
    abrir_pool_notif()
    init_db_notif()
    yield
    # el pool es global y se reutiliza entre modulos; no se cierra a proposito


@pytest.fixture(autouse=True)
def notif_limpia(notif_db):
    from notif_api.app.db import get_connection

    with get_connection() as conn:
        conn.execute(f"TRUNCATE {NOTIF_TABLAS} RESTART IDENTITY CASCADE")
    yield
    with get_connection() as conn:
        conn.execute(f"TRUNCATE {NOTIF_TABLAS} RESTART IDENTITY CASCADE")


def _insertar_dlq(cola="dlq.general", payload=None, error="fallo simulado"):
    from notif_api.app.db import get_connection

    with get_connection() as conn:
        fila = conn.execute(
            "INSERT INTO mensaje_dlq (cola, payload, error)"
            " VALUES (%s, %s, %s) RETURNING *",
            (
                cola,
                __import__("json").dumps(
                    payload
                    or {"event_id": "t-dlq-op", "tipo": "mesa.desconocida", "mesa_id": 1}
                ),
                error,
            ),
        ).fetchone()
    return fila["id"]


def _count_dlq():
    from notif_api.app.db import get_connection

    with get_connection() as conn:
        return conn.execute("SELECT count(*) AS n FROM mensaje_dlq").fetchone()["n"]


def test_listar_dlq(notif_limpia):
    _insertar_dlq()
    client = TestClient(app)
    r = client.get("/api/v1/dlq")
    assert r.status_code == 200
    assert len(r.json()) >= 1
    assert r.json()[0]["cola"] == "dlq.general"


def test_reintentar_dlq_lo_quita_de_la_tabla(notif_limpia):
    _insertar_dlq()
    antes = _count_dlq()
    client = TestClient(app)
    r = client.post("/api/v1/dlq/1/reintentar")
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert _count_dlq() == antes - 1


def test_descartar_dlq(notif_limpia):
    _insertar_dlq()
    client = TestClient(app)
    r = client.delete("/api/v1/dlq/1")
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert _count_dlq() == 0


def test_dlq_id_inexistente_404(notif_limpia):
    client = TestClient(app)
    r1 = client.post("/api/v1/dlq/999/reintentar")
    r2 = client.delete("/api/v1/dlq/999")
    assert r1.status_code == 404
    assert r2.status_code == 404