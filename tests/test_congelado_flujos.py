"""CONGELADO: flujos de negocio con sus respuestas exactas (golden).

Antes de refactorizar la infraestructura, estos tests aferran los valores de
campo, los status codes y los mensajes de los flujos: registrarse/login/me,
CRUD de mesas, matchmaking con TTL, solicitar con idempotencia, QR single-use,
sesiones, diario, feed con filtros, builds/pdf y notificaciones.

El refactor debe reproducir exactamente estas respuestas.
"""

import pytest
from fastapi.testclient import TestClient

from builds_api.app.db import abrir_pool as abrir_pool_builds
from builds_api.app.db import get_connection as builds_conn
from builds_api.app.init_db import init_db as init_db_builds
from builds_api.main import app as builds_app
from feed_api.app.db import abrir_pool as abrir_pool_feed
from feed_api.app.db import get_connection as feed_conn
from feed_api.app.init_db import init_db as init_db_feed
from feed_api.main import app as feed_app
from notif_api.app.db import abrir_pool as abrir_pool_notif
from notif_api.app.db import get_connection as notif_conn
from notif_api.app.init_db import init_db as init_db_notif
from notif_api.main import app as notif_app
from notif_api.app.models.notif import guardar_notificacion
from tests.conftest import crear_mesa, crear_sesion

pytestmark = pytest.mark.integration

CAMPOS_MESA = {
    "id",
    "nombre",
    "sistema",
    "descripcion",
    "tono",
    "horario",
    "estado",
    "nivel_inicial",
    "jugadores_actuales",
    "jugadores_max",
    "fecha_creacion",
}


@pytest.fixture(scope="module", autouse=True)
def _pools():
    abrir_pool_builds(), init_db_builds()
    abrir_pool_feed(), init_db_feed()
    abrir_pool_notif(), init_db_notif()
    yield


@pytest.fixture(scope="module", autouse=True)
def _truncar_secundarias():
    with notif_conn() as conn:
        conn.execute("TRUNCATE notificaciones RESTART IDENTITY CASCADE")
    with builds_conn() as conn:
        conn.execute("TRUNCATE builds, tags RESTART IDENTITY CASCADE")
    with feed_conn() as conn:
        conn.execute("TRUNCATE publicaciones RESTART IDENTITY CASCADE")
    yield
    with notif_conn() as conn:
        conn.execute("TRUNCATE notificaciones RESTART IDENTITY CASCADE")
    with builds_conn() as conn:
        conn.execute("TRUNCATE builds, tags RESTART IDENTITY CASCADE")
    with feed_conn() as conn:
        conn.execute("TRUNCATE publicaciones RESTART IDENTITY CASCADE")


@pytest.fixture(scope="module")
def client_feed():
    return TestClient(feed_app)


@pytest.fixture(scope="module")
def client_builds():
    return TestClient(builds_app)


@pytest.fixture(scope="module")
def client_notif():
    return TestClient(notif_app)


# ---- autenticación ----------------------------------------------------------

def test_auth_flujo_completo_congelado(client):
    email = f"congelado_{id(object())}@tfinder.dev"
    credencial = {"email": email, "password": "secreto123", "nombre": "Congelado"}

    registro = client.post("/api/v1/auth/register", json=credencial)
    assert registro.status_code == 201
    body = registro.json()
    assert set(body) == {"access_token", "refresh_token", "rol"}

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "secreto123"},
    )
    assert login.status_code == 200
    assert set(login.json()) == {"access_token", "refresh_token", "rol"}

    duplicado = client.post("/api/v1/auth/register", json=credencial)
    assert duplicado.status_code == 400
    assert duplicado.json() == {
        "error": {"codigo": 400, "mensaje": "El email ya está registrado"}
    }

    access = login.json()["access_token"]
    auth = {"Authorization": f"Bearer {access}"}
    me = client.get("/api/v1/auth/me", headers=auth)
    assert me.status_code == 200
    payload = me.json()
    assert set(payload) == {"sub", "tipo", "jti", "rol", "email", "exp"}
    assert payload["rol"] == "usuario"
    assert payload["email"] == email

    renovacion = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login.json()["refresh_token"]},
    )
    assert renovacion.status_code == 200
    assert "access_token" in renovacion.json()

    salida = client.post("/api/v1/auth/logout", headers=auth)
    assert salida.status_code == 200

    me_tras_salir = client.get("/api/v1/auth/me", headers=auth)
    assert me_tras_salir.status_code == 401
    assert me_tras_salir.json()["error"]["codigo"] == 401


# ---- mesas + matchmaking + solicitudes --------------------------------------

def test_mesas_crud_congelado(client, token_gm):
    auth = {"Authorization": f"Bearer {token_gm}"}
    creacion = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa congelada", "sistema": "PF1e", "jugadores_max": 4},
        headers=auth,
    )
    assert creacion.status_code == 201
    mesa = creacion.json()
    assert set(mesa) == CAMPOS_MESA
    assert mesa["estado"] == "abierta"
    assert mesa["jugadores_actuales"] == 0

    edicion = client.put(
        f"/api/v1/mesas/{mesa['id']}",
        json={"estado": "cerrada"},
        headers=auth,
    )
    assert edicion.status_code == 200
    assert edicion.json()["estado"] == "cerrada"

    baja = client.delete(f"/api/v1/mesas/{mesa['id']}", headers=auth)
    assert baja.status_code == 204
    assert baja.content == b""


def test_matchmaking_llamado_congelado(client, token_gm):
    auth = {"Authorization": f"Bearer {token_gm}"}
    mesa_id = crear_mesa(client, token_gm, "Mesa mm congelada", jugadores_max=4)

    apertura = client.post(f"/api/v1/matchmaking/{mesa_id}/abrir", headers=auth)
    assert apertura.status_code == 200
    cuerpo = apertura.json()
    assert set(cuerpo) == {
        "id",
        "mesa_id",
        "estado",
        "llamada_abierta_at",
        "fecha_creacion",
        "matchmaking_id",
        "expira_en",
    }
    assert cuerpo["estado"] == "abierto"
    assert cuerpo["expira_en"] == 120
    assert cuerpo["matchmaking_id"] == cuerpo["id"]

    estado = client.get(f"/api/v1/matchmaking/{cuerpo['id']}/estado")
    assert estado.status_code == 200
    assert estado.json()["estado"] == "abierto"
    assert 0 < estado.json()["ttl_restante"] <= 120

    denegado = client.post(
        f"/api/v1/matchmaking/{mesa_id}/abrir",
        headers={"Authorization": "inventado"},
    )
    assert denegado.status_code == 401


def test_solicitud_con_idempotencia_congelado(client, token_gm, token_jugador):
    mesa_id = crear_mesa(client, token_gm, "Mesa idem congelada", jugadores_max=4)
    auth = {"Authorization": f"Bearer {token_jugador}", "Idempotency-Key": "congelada-1"}

    primera = client.post(f"/api/v1/mesas/{mesa_id}/solicitudes", headers=auth)
    assert primera.status_code == 201
    cuerpo = primera.json()
    assert cuerpo["estado"] == "aceptada"

    segunda = client.post(f"/api/v1/mesas/{mesa_id}/solicitudes", headers=auth)
    assert segunda.status_code == 201
    assert segunda.json() == cuerpo


def test_solicitar_por_evento_pendiente_congelado(client, token_gm, token_jugador):
    mesa_id = crear_mesa(client, token_gm, "Mesa pendiente congelada", jugadores_max=4)
    r = client.post(
        f"/api/v1/mesas/{mesa_id}/solicitar",
        headers={"Authorization": f"Bearer {token_jugador}"},
    )
    assert r.status_code == 202
    assert r.json() == {"estado": "pendiente"}


# ---- sesiones + QR ----------------------------------------------------------

def test_sesiones_y_qr_congelado(client, token_gm, token_jugador):
    mesa_id = crear_mesa(client, token_gm, "Mesa qr congelada", jugadores_max=4)
    auth_gm = {"Authorization": f"Bearer {token_gm}"}

    sesion = client.post(f"/api/v1/mesas/{mesa_id}/sesiones", headers=auth_gm)
    assert sesion.status_code == 201
    datos_sesion = sesion.json()
    assert set(datos_sesion) == {"id", "mesa_id", "estado", "fecha", "confirmada_at"}
    assert datos_sesion["estado"] == "abierta"
    assert datos_sesion["confirmada_at"] is None

    jugador_id = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token_jugador}"},
    ).json()["sub"]

    emitir = client.post(
        f"/api/v1/sesiones/{datos_sesion['id']}/qr",
        headers={"Authorization": f"Bearer {token_jugador}"},
    )
    assert emitir.status_code == 201
    qr = emitir.json()
    assert set(qr) == {"qr_data", "png_base64", "expira_en_seg", "sesion_id"}
    assert qr["expira_en_seg"] == 600
    assert qr["png_base64"].startswith("iVBOR")  # PNG en base64

    validar = {"usuario_id": jugador_id, "qr_data": qr["qr_data"]}
    primera = client.post(
        f"/api/v1/sesiones/{datos_sesion['id']}/qr/validar",
        json=validar,
        headers=auth_gm,
    )
    assert primera.status_code == 200
    assert primera.json() == {"asistencia": "registrada"}

    reuso = client.post(
        f"/api/v1/sesiones/{datos_sesion['id']}/qr/validar",
        json=validar,
        headers=auth_gm,
    )
    assert reuso.status_code == 409
    assert reuso.json()["error"]["codigo"] == 409


# ---- builds / feed / notificaciones -----------------------------------------

def test_builds_vacio_y_pdf_valida_existencia(client_builds, token_jugador):
    assert client_builds.get("/api/v1/builds").json() == []
    assert client_builds.get("/api/v1/tags").json() == []

    # Sin la fila del build, el pdf responde 404 con el envelope canónico.
    r = client_builds.post(
        "/api/v1/builds/7/pdf",
        headers={"Authorization": f"Bearer {token_jugador}"},
    )
    assert r.status_code == 404
    assert r.json() == {"error": {"codigo": 404, "mensaje": "Build 7 no encontrado"}}


def test_feed_vacio_y_filtros_congelado(client, client_feed, token_gm, token_jugador):
    mesa_id = crear_mesa(client, token_gm, "Mesa feed congelada", jugadores_max=4)
    r = client_feed.post(
        f"/api/v1/mesas/{mesa_id}/sesiones/1/diario",
        json={"titulo": "Diario congelado", "cuerpo": "Texto"},
        headers={"Authorization": f"Bearer {token_jugador}"},
    )
    assert r.status_code == 201
    datos = r.json()
    assert datos == {
        "id": datos["id"],
        "mesa_id": str(mesa_id),
        "sesion_id": 1,
        "titulo": "Diario congelado",
        "estado": "publicado",
    }

    listado = client_feed.get("/api/v1/feed").json()
    assert len(listado) == 1
    assert set(listado[0]) >= {"id", "tipo", "titulo", "cuerpo", "votos", "totalComentarios"}

    filtrado = client_feed.get("/api/v1/feed?tipo=post&orden=recientes&limit=10")
    assert filtrado.status_code == 200
    assert filtrado.json() == listado

    vacio_con_filtro_ajeno = client_feed.get("/api/v1/feed?tipo=wiki")
    assert vacio_con_filtro_ajeno.status_code == 200
    assert vacio_con_filtro_ajeno.json() == []


def test_notificaciones_listar_marcarleida_congelado(client, client_notif, token_jugador):
    jugador = int(
        client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token_jugador}"},
        ).json()["sub"]
    )
    guardar_notificacion(jugador, "noti congelada")

    listado = client_notif.get(
        "/api/v1/notificaciones",
        headers={"Authorization": f"Bearer {token_jugador}"},
    )
    assert listado.status_code == 200
    filas = listado.json()
    assert len(filas) == 1
    assert set(filas[0]) == {
        "id",
        "grupo",
        "icono",
        "leida",
        "autor",
        "mensaje",
        "entidad",
        "detalle",
        "enlace",
        "fecha",
        "creado_en",
    }
    assert filas[0]["leida"] is False
    assert filas[0]["mensaje"] == "noti congelada"

    leida = client_notif.patch(
        f"/api/v1/notificaciones/{filas[0]['id']}/leida",
        headers={"Authorization": f"Bearer {token_jugador}"},
    )
    assert leida.status_code == 200
    assert leida.json()["leida"] is True
