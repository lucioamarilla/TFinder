"""notif-api con autenticacion: los avisos son por usuario y la ops es de admin.

Cubre B-02 de docs/AUDITORIA_CIERRE_AE2.md: GET /notificaciones, PATCH
/notificaciones/{id}/leida y /notificaciones/stream requieren sesion, y
dlq/event-log exigen rol admin.
"""

import pytest
from fastapi.testclient import TestClient

import notif_api.main as notif_api_main
from notif_api.app.db import abrir_pool as abrir_pool_notif
from notif_api.app.db import get_connection
from notif_api.app.init_db import init_db as init_db_notif
from notif_api.main import app

NOTIF_TABLAS = "event_log, mensaje_dlq, documentos, notificaciones, emails"
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def notif_db():
    abrir_pool_notif()
    init_db_notif()
    yield
    # el pool es global y se reutiliza entre modulos; no se cierra a proposito


@pytest.fixture(autouse=True)
def notif_limpia(notif_db):
    with get_connection() as conn:
        conn.execute(f"TRUNCATE {NOTIF_TABLAS} RESTART IDENTITY CASCADE")
    yield
    with get_connection() as conn:
        conn.execute(f"TRUNCATE {NOTIF_TABLAS} RESTART IDENTITY CASCADE")


def _insertar_notificacion(mensaje, usuario_id=None):
    with get_connection() as conn:
        fila = conn.execute(
            "INSERT INTO notificaciones (grupo, icono, mensaje, usuario_id)"
            " VALUES ('mesas', 'solicitud', %s, %s) RETURNING id",
            (mensaje, usuario_id),
        ).fetchone()
    return fila["id"]


def _usuario(token):
    from notif_api.app.middleware.auth import decodificar_token

    return int(decodificar_token(token)["sub"])


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_listar_requiere_token(notif_limpia):
    client = TestClient(app)
    assert client.get("/api/v1/notificaciones").status_code == 401


def test_marcar_leida_requiere_token(notif_limpia, token_jugador):
    id_notif = _insertar_notificacion("aviso", usuario_id=_usuario(token_jugador))
    client = TestClient(app)
    assert client.patch(f"/api/v1/notificaciones/{id_notif}/leida").status_code == 401


def test_lista_solo_las_del_usuario_y_las_globales(notif_limpia, token_gm, token_jugador):
    propio = _insertar_notificacion("para el gm", usuario_id=_usuario(token_gm))
    ajeno = _insertar_notificacion("para el jugador", usuario_id=_usuario(token_jugador))
    _insertar_notificacion("aviso del sistema", usuario_id=None)

    client = TestClient(app)
    r = client.get("/api/v1/notificaciones", headers=_auth(token_gm))
    assert r.status_code == 200
    ids = {n["id"] for n in r.json()}
    assert propio in ids
    assert ajeno not in ids
    assert len(ids) == 2  # la propia + la global


def test_solo_no_leidas_filtra(notif_limpia, token_gm):
    usuario = _usuario(token_gm)
    leida = _insertar_notificacion("ya leida", usuario_id=usuario)
    _insertar_notificacion("pendiente", usuario_id=usuario)
    with get_connection() as conn:
        conn.execute("UPDATE notificaciones SET leida = TRUE WHERE id = %s", (leida,))

    client = TestClient(app)
    r = client.get("/api/v1/notificaciones?solo_no_leidas=true", headers=_auth(token_gm))
    assert r.status_code == 200
    assert [n["mensaje"] for n in r.json()] == ["pendiente"]


def test_marcar_leida_no_toca_aviso_ajeno(notif_limpia, token_jugador, token_gm):
    ajeno = _insertar_notificacion("para el jugador", usuario_id=_usuario(token_jugador))

    client = TestClient(app)
    r = client.patch(f"/api/v1/notificaciones/{ajeno}/leida", headers=_auth(token_gm))
    assert r.status_code == 404

    with get_connection() as conn:
        fila = conn.execute(
            "SELECT leida FROM notificaciones WHERE id = %s", (ajeno,)
        ).fetchone()
    assert fila["leida"] is False


def test_marcar_leida_propia(notif_limpia, token_gm):
    propia = _insertar_notificacion("para el gm", usuario_id=_usuario(token_gm))

    client = TestClient(app)
    r = client.patch(f"/api/v1/notificaciones/{propia}/leida", headers=_auth(token_gm))
    assert r.status_code == 200
    assert r.json()["leida"] is True


def test_stream_requiere_token(notif_limpia):
    client = TestClient(app)
    assert client.get("/api/v1/notificaciones/stream").status_code == 401


def test_stream_ignora_usuario_id_ajeno(notif_limpia):
    """El usuario_id por query ya no se acepta: sale del token."""
    parametros = notif_api_main.app.openapi()["paths"][
        "/api/v1/notificaciones/stream"
    ]["get"].get("parameters", [])
    nombres = {p["name"] for p in parametros}
    assert "usuario_id" not in nombres


def test_event_log_no_acepta_usuario_no_admin(notif_limpia, token_jugador):
    client = TestClient(app)
    r = client.get("/api/v1/event-log", headers=_auth(token_jugador))
    assert r.status_code == 403


def test_emails_requiere_admin(notif_limpia, token_gm):
    client = TestClient(app)
    r = client.get("/api/v1/emails", headers=_auth(token_gm))
    assert r.status_code == 403
    assert client.get("/api/v1/emails").status_code == 401


def test_pdf_requiere_sesion(notif_limpia):
    client = TestClient(app)
    assert client.get("/api/v1/pdf/inexistente.pdf").status_code == 401
