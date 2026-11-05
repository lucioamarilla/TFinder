"""F2 · Membresías por mesa y cierre de filtraciones (pliego 2.1/2.4).

RED previo:
- No existe `miembros_mesa` con rol por mesa; el "Master" era un rol global.
- L-01: GET /mesas/{id}/miembros accesible por cualquier autenticado.
- L-02: GET /mesas/{id}/sesiones ídem.
- L-03: GET /mesas/{id}/fechas ídem.
- L-04: GET /api/v1/builds/{id} público y expone builds privadas por ID.
- L-05: GET /api/v1/wiki lista páginas privadas de campañas ajenas.
- Los gates de sesiones/QR/matchmaking dependen del rol GLOBAL gm.
"""

import os
import socket
import threading
import time
import uuid

import pytest
import uvicorn
from fastapi.testclient import TestClient

from builds_api.app.db import abrir_pool as abrir_pool_builds
from builds_api.app.db import get_connection as builds_conn
from builds_api.app.init_db import init_db as init_db_builds
from builds_api.main import app as builds_app
from feed_api.app.db import abrir_pool as abrir_pool_feed
from feed_api.app.init_db import init_db as init_db_feed
from mesas_api.main import app as mesas_app
from tests.conftest import _crear_con_rol

pytestmark = pytest.mark.integration

BUILDS_TABLAS = "builds, tags"


@pytest.fixture(scope="module", autouse=True)
def _pools():
    abrir_pool_builds()
    init_db_builds()
    abrir_pool_feed()
    init_db_feed()
    yield


@pytest.fixture
def builds_client(_pools):
    return TestClient(builds_app)


@pytest.fixture(autouse=True)
def _limpieza_builds(_pools):
    with builds_conn() as conn:
        conn.execute(f"TRUNCATE {BUILDS_TABLAS} RESTART IDENTITY CASCADE")
    yield
    with builds_conn() as conn:
        conn.execute(f"TRUNCATE {BUILDS_TABLAS} RESTART IDENTITY CASCADE")


@pytest.fixture(scope="module", autouse=True)
def _mesas_real():
    puerto = 0
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        puerto = s.getsockname()[1]
    config = uvicorn.Config(
        mesas_app, host="127.0.0.1", port=puerto, log_level="warning", lifespan="off"
    )
    servidor = uvicorn.Server(config)
    hilo = threading.Thread(target=servidor.run, daemon=True)
    hilo.start()
    for _ in range(60):
        if getattr(servidor, "started", False):
            break
        time.sleep(0.2)
    url_previa = os.environ.get("MESA_URL")
    os.environ["MESA_URL"] = f"http://127.0.0.1:{puerto}"
    yield
    if url_previa is None:
        os.environ.pop("MESA_URL", None)
    else:
        os.environ["MESA_URL"] = url_previa
    servidor.should_exit = True
    hilo.join(timeout=5)


def _registrar(client, nombre="Jugador F2"):
    email = f"f2_{uuid.uuid4().hex[:8]}@tfinder.dev"
    r = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secreto123", "nombre": nombre},
    )
    assert r.status_code == 201
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "secreto123"})
    return login.json()


def _mesa(client, token, nombre="Mesa F2"):
    r = client.post(
        "/api/v1/mesas",
        json={"nombre": nombre, "sistema": "pf1e", "jugadores_max": 4},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201, r.text
    return r.json()


# ---- panel del jugador: salirse de una mesa donde es jugador -------------------

def test_jugador_puede_salir_de_la_mesa(client, token_gm):
    mesa_id = _mesa(client, token_gm)["id"]
    usuario = _registrar(client)
    sol = client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes",
        headers={"Authorization": f"Bearer {usuario['access_token']}"},
    ).json()
    client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes/{sol['id']}/aceptar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    auth = {"Authorization": f"Bearer {usuario['access_token']}"}

    r = client.delete(f"/api/v1/mesas/{mesa_id}/miembros/mi", headers=auth)
    assert r.status_code == 200, "el jugador puede salirse por su cuenta"
    detalle = client.get(f"/api/v1/mesas/{mesa_id}").json()
    assert detalle["jugadores_actuales"] == 0, "el cupo vuelve al salirse"

    # tras salirse ya NO es miembro: la lectura de sesiones vuelve a 403
    assert client.get(f"/api/v1/mesas/{mesa_id}/sesiones", headers=auth).status_code == 403


def test_master_no_puede_salir_por_esta_via(client, token_gm):
    mesa_id = _mesa(client, token_gm)["id"]
    r = client.delete(
        f"/api/v1/mesas/{mesa_id}/miembros/mi",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r.status_code == 409, "el master transfiere o elimina la mesa (futuro), no sale"


# ---- 2.1: crear mesa => master -------------------------------------------------

def test_crear_mesa_registra_master_en_membresias(client, token_gm):
    mesa_id = _mesa(client, token_gm, "Mesa master f2")["id"]

    miembros = client.get(
        f"/api/v1/mesas/{mesa_id}/miembros", headers={"Authorization": f"Bearer {token_gm}"}
    ).json()["miembros"]

    master = [m for m in miembros if m.get("rol") == "master"]
    assert master, "el creador de la mesa figura como master (2.1)"
    assert master[0]["email"].endswith("@tfinder.dev")


def test_solicitud_aceptada_convierte_miembro_rol_jugador(client, token_gm):
    mesa_id = _mesa(client, token_gm, "Mesa mem f2")["id"]
    usuario = _registrar(client)
    sol = client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes",
        headers={"Authorization": f"Bearer {usuario['access_token']}"},
    ).json()
    client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes/{sol['id']}/aceptar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )

    miembros = client.get(
        f"/api/v1/mesas/{mesa_id}/miembros", headers={"Authorization": f"Bearer {token_gm}"}
    ).json()["miembros"]
    target = [m for m in miembros if m["email"] == usuario["perfil"]["email"]]
    assert target and target[0]["rol"] == "jugador", "RN-08: el aceptado entra como jugador"


# ---- 2.4: gates por membresía (no rol global) -----------------------------------

def test_solo_el_master_de_la_mesa_crea_sesiones(client, token_gm, token_jugador):
    """El rol global del usuario NO habilita administrar sesiones ajenas."""
    mesa_id = _mesa(client, token_gm, "Mesa sesiones f2")["id"]

    r = client.post(
        f"/api/v1/mesas/{mesa_id}/sesiones",
        headers={"Authorization": f"Bearer {token_jugador}"},
    )
    assert r.status_code == 403, "solo el master de ESA mesa administra sesiones"


def test_matchmaking_abertura_es_del_master(client, token_gm, token_jugador):
    mesa_id = _mesa(client, token_gm, "Mesa mm f2")["id"]
    r = client.post(
        f"/api/v1/matchmaking/{mesa_id}/abrir",
        headers={"Authorization": f"Bearer {token_jugador}"},
    )
    assert r.status_code == 403


# ---- 2.4: cierre de filtraciones ------------------------------------------------

def test_miembros_y_sesiones_no_son_de_ajenos(client, token_gm):
    mesa_id = _mesa(client, token_gm)["id"]
    extrano = _registrar(client)

    for ruta in (f"/api/v1/mesas/{mesa_id}/miembros", f"/api/v1/mesas/{mesa_id}/sesiones"):
        r = client.get(ruta, headers={"Authorization": f"Bearer {extrano['access_token']}"})
        assert r.status_code == 403, f"{ruta} no debe exponer contenido de mesa ajena"


def test_fechas_de_mesa_ajena_no_legibles(client, token_gm):
    mesa_id = _mesa(client, token_gm)["id"]
    extrano = _registrar(client)
    r = client.get(
        f"/api/v1/mesas/{mesa_id}/fechas",
        headers={"Authorization": f"Bearer {extrano['access_token']}"},
    )
    assert r.status_code == 403

    ok = client.get(f"/api/v1/mesas/{mesa_id}/fechas", headers={"Authorization": f"Bearer {token_gm}"})
    assert ok.status_code == 200


def test_miembro_si_ve_miembros_sesiones_fechas(client, token_gm):
    mesa_id = _mesa(client, token_gm)["id"]
    usuario = _registrar(client)
    sol = client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes",
        headers={"Authorization": f"Bearer {usuario['access_token']}"},
    ).json()
    client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes/{sol['id']}/aceptar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    auth = {"Authorization": f"Bearer {usuario['access_token']}"}
    assert client.get(f"/api/v1/mesas/{mesa_id}/miembros", headers=auth).status_code == 200
    assert client.get(f"/api/v1/mesas/{mesa_id}/sesiones", headers=auth).status_code == 200
    assert client.get(f"/api/v1/mesas/{mesa_id}/fechas", headers=auth).status_code == 200


def test_servicio_email_puede_listar_miembros(client, token_gm):
    """El puente B09 (emails de sesiones) usa credenciales de servicio."""
    from tests.conftest import crear_mesa

    mesa_id = crear_mesa(client, token_gm)
    cred = client.post(
        "/api/v1/auth/login",
        json={"email": "email_svc@tfinder.dev", "password": "DemoTFinder123!"},
    )
    if cred.status_code != 200:
        pytest.skip("cuenta de servicio no sembrada en la DB de pruebas")
    auth = {"Authorization": f"Bearer {cred.json()['access_token']}"}
    r = client.get(f"/api/v1/mesas/{mesa_id}/miembros", headers=auth)
    assert r.status_code == 200, "el servicio de email necesita el contrato B09"


# ---- 2.4-F5: build privada solo la lee su creador ----------------------------------

def test_build_privada_solo_su_creador(builds_client):
    auth = {"Authorization": f"Bearer {_crear_con_rol('usuario')}"}
    otro = {"Authorization": f"Bearer {_crear_con_rol('usuario')}"}

    ficha = {
        "titulo": "Sombra Privada",
        "clase": "Picaro",
        "raza": "Humano",
        "atributos": {"fue": 10, "des": 18, "con": 12, "int": 10, "sab": 10, "car": 14},
        "visibilidad": "privado",
    }
    build_id = builds_client.post("/api/v1/builds", json=ficha, headers=auth).json()["id"]

    assert builds_client.get(f"/api/v1/builds/{build_id}", headers=auth).status_code == 200
    assert builds_client.get(f"/api/v1/builds/{build_id}").status_code == 404
    assert builds_client.get(f"/api/v1/builds/{build_id}", headers=otro).status_code == 404


# ---- 2.4-F4: listado wiki filtra privadas según el llamante ------------------------

def test_listado_wiki_filtra_privadas(client, token_gm):
    import uuid as _uuid

    from feed_api.main import app as feed_app

    feed = TestClient(feed_app)
    mesa_id = _mesa(client, token_gm, f"Mesa wiki f2 {_uuid.uuid4().hex[:4]}")["id"]

    r_pub = feed.post(
        f"/api/v1/mesas/{mesa_id}/wiki",
        headers={"Authorization": f"Bearer {token_gm}"},
        json={"titulo": "Manifiesto_publico", "tipo": "Nota", "visibilidad": "publica"},
    )
    assert r_pub.status_code == 201
    r_priv = feed.post(
        f"/api/v1/mesas/{mesa_id}/wiki",
        headers={"Authorization": f"Bearer {token_gm}"},
        json={"titulo": "Secretos del Master", "tipo": "Nota", "visibilidad": "privada"},
    )
    assert r_priv.status_code == 201

    anon = feed.get("/api/v1/wiki", params={"mesa_id": str(mesa_id)})
    titulos = [p["titulo"] for p in anon.json()["paginas"]]
    assert "Manifiesto_publico" in titulos
    assert "Secretos del Master" not in titulos, "L-05 cerrado: listado sin privadas de otros"

    master = feed.get(
        "/api/v1/wiki", params={"mesa_id": str(mesa_id)},
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    titulos_master = [p["titulo"] for p in master.json()["paginas"]]
    assert "Secretos del Master" in titulos_master, "el master ve sus privadas en el listado"
