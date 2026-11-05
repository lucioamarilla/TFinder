"""P1.6 · Wiki CRUD con visibilidad (RF-08/RF-09, RN-05, VAL-25..28).

La verificación de propiedad/miembro es cross-servicio: feed_api pregunta por
REST a mesas-api (contrato B09). Para ejercitarlo de verdad, el fixture levanta
mesas-api en un hilo uvicorn y apunta MESA_URL al puerto creado.
"""

import json
import os
import socket
import threading
import time
import uuid

import pytest
import uvicorn
from fastapi.testclient import TestClient

from feed_api.app.db import abrir_pool as abrir_pool_feed
from feed_api.app.db import get_connection as feed_conn
from feed_api.app.init_db import init_db as init_db_feed
from feed_api.main import app as feed_app
from mesas_api.main import app as mesas_app
from tests.conftest import _crear_con_rol

pytestmark = pytest.mark.integration

WIKI_TABLA = "wiki_paginas"


@pytest.fixture(scope="module", autouse=True)
def _pools():
    abrir_pool_feed()
    init_db_feed()
    yield


@pytest.fixture(scope="module")
def _mesas_local():
    """mesas-api REAL en un puerto efímero (para los contratos REST de la wiki)."""
    puerto = 0
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        puerto = s.getsockname()[1]
    config = uvicorn.Config(
        mesas_app,
        host="127.0.0.1",
        port=puerto,
        log_level="warning",
        lifespan="off",  # el ciclo de pools lo maneja el entorno de pruebas
    )
    servidor = uvicorn.Server(config)
    hilo = threading.Thread(target=servidor.run, daemon=True)
    hilo.start()
    for _ in range(60):
        if getattr(servidor, "started", False):
            break
        time.sleep(0.2)
    url_anterior = os.environ.get("MESA_URL")
    os.environ["MESA_URL"] = f"http://127.0.0.1:{puerto}"
    yield f"http://127.0.0.1:{puerto}"
    if url_anterior is None:
        os.environ.pop("MESA_URL", None)
    else:
        os.environ["MESA_URL"] = url_anterior
    servidor.should_exit = True
    hilo.join(timeout=5)


@pytest.fixture
def mesas_client(_mesas_local):
    return TestClient(mesas_app)


@pytest.fixture(autouse=True)
def _limpieza(_pools):
    with feed_conn() as conn:
        conn.execute(f"TRUNCATE {WIKI_TABLA} RESTART IDENTITY CASCADE")
    yield
    with feed_conn() as conn:
        conn.execute(f"TRUNCATE {WIKI_TABLA} RESTART IDENTITY CASCADE")


@pytest.fixture
def gm(_mesas_local):
    """(mesa_id, headers) de un GM con su mesa en os datos de prueba."""
    token = _crear_con_rol("gm")
    mesas = TestClient(mesas_app)
    r = mesas.post(
        "/api/v1/mesas",
        json={"nombre": f"Mesa wiki {uuid.uuid4().hex[:4]}", "sistema": "pf1e"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    return r.json()["id"], {"Authorization": f"Bearer {token}"}


def _jugador_miembro(mesas_client, mesa_id, token_gm):
    token = _crear_con_rol("usuario")
    r = mesas_client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    sol_id = r.json()["id"]
    r = mesas_client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes/{sol_id}/aceptar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r.status_code == 200
    return token


def _publicar(gcgm_headers, mesa_id, cuerpo):
    from feed_api.main import app as _feed

    feed = TestClient(_feed)
    return feed.post(f"/api/v1/mesas/{mesa_id}/wiki", json=cuerpo, headers=gcgm_headers)


# ---- RF-08: crear ------------------------------------------------------------

def test_gm_crea_pagina_con_visibilidad_por_defecto(gm):
    mesa_id, headers = gm
    r = _publicar(headers, mesa_id, {"titulo": "El Pérulo", "tipo": "NPC", "cuerpo": "Historia"})
    assert r.status_code == 201, "RF-08: el GM crea páginas"
    cuerpo = r.json()
    assert cuerpo["titulo"] == "El Pérulo"
    assert cuerpo["visibilidad"] == "jugadores", "RN-05: default según visibilidad del MVP"
    assert cuerpo["tipo"] == "NPC"


def test_titulo_y_tipo_validados(gm):
    mesa_id, headers = gm
    vacio = _publicar(headers, mesa_id, {"titulo": "", "tipo": "Nota"})
    assert vacio.status_code == 400, "VAL-25"

    equivocado = _publicar(headers, mesa_id, {"titulo": "X", "tipo": "Orco"})
    assert equivocado.status_code == 400, "VAL-26"
    assert "NPC, Lugar, Criatura, Nota, Sesión" in equivocado.json()["error"]["mensaje"]


def test_solo_el_gm_de_la_mesa_crea(gm):
    mesa_id, headers = gm
    token_otro = _crear_con_rol("gm")
    ajeno = {"Authorization": f"Bearer {token_otro}"}
    r = _publicar(ajeno, mesa_id, {"titulo": "Invasión", "tipo": "Lugar"})
    assert r.status_code == 403, "RN-02: la wiki es del GM propietario"


def test_el_admin_tambien_puede_crear(_mesas_local, gm):
    mesa_id, _ = gm
    token_admin = _crear_con_rol("admin")
    r = _publicar({"Authorization": f"Bearer {token_admin}"}, mesa_id, {"titulo": "Nota", "tipo": "Nota"})
    assert r.status_code == 201


# ---- RF-09: leer con visibilidad ---------------------------------------------

def test_pagina_con_repertorio_de_visibilidad_visible(gm):
    mesa_id, headers = gm
    r = _publicar(
        headers,
        mesa_id,
        {"titulo": "Manifiesto", "tipo": "Nota", "cuerpo": "Para todos", "visibilidad": "publica"},
    )
    pagina_id = r.json()["id"]
    feed = TestClient(feed_app)
    anonimo = feed.get(f"/api/v1/wiki/{pagina_id}")
    assert anonimo.status_code == 200, "RN-05: visibilidad 'publica' para todos"


def test_pagina_jugadores_miembro_ve_y_anonimo_no(gm, mesas_client):
    mesa_id, headers = gm
    r = _publicar(headers, mesa_id, {"titulo": "Reino", "tipo": "Lugar", "cuerpo": "Mapa"})
    pagina_id = r.json()["id"]

    token_mi = _jugador_miembro(mesas_client, mesa_id, headers["Authorization"].split(" ")[1])
    feed = TestClient(feed_app)

    miembro = feed.get(f"/api/v1/wiki/{pagina_id}", headers={"Authorization": f"Bearer {token_mi}"})
    assert miembro.status_code == 200

    anonimo = feed.get(f"/api/v1/wiki/{pagina_id}")
    assert anonimo.status_code == 403, "VAL-28: sin sesión / membresía no se ve"


def test_pagina_privada_solo_el_gm(gm, mesas_client):
    mesa_id, headers = gm
    r = _publicar(
        headers,
        mesa_id,
        {"titulo": "Secretos", "tipo": "Nota", "cuerpo": "Trampa", "visibilidad": "privada"},
    )
    pagina_id = r.json()["id"]
    feed = TestClient(feed_app)

    token_mi = _jugador_miembro(mesas_client, mesa_id, headers["Authorization"].split(" ")[1])
    miembro = feed.get(
        f"/api/v1/wiki/{pagina_id}",
        headers={"Authorization": f"Bearer {token_mi}"},
    )
    assert miembro.status_code == 403, "RN-05: 'privada' es solo del GM"

    gm_de_nuevo = feed.get(f"/api/v1/wiki/{pagina_id}", headers=headers)
    assert gm_de_nuevo.status_code == 200


def test_listado_incluye_visibilidad(gm):
    mesa_id, headers = gm
    _publicar(headers, mesa_id, {"titulo": "Maestro", "tipo": "Nota"})
    feed = TestClient(feed_app)
    r = feed.get("/api/v1/wiki", params={"mesa_id": str(mesa_id)})
    assert r.status_code == 200
    lista = r.json()["paginas"]
    assert lista
    assert all("visibilidad" in p for p in lista)


# ---- editar / eliminar --------------------------------------------------------

def test_el_gm_edita_y_otro_no_puede(gm):
    mesa_id, headers = gm
    pagina_id = _publicar(headers, mesa_id, {"titulo": "Draft", "tipo": "Nota", "cuerpo": "v1"}).json()["id"]
    feed = TestClient(feed_app)
    r = feed.put(
        f"/api/v1/wiki/{pagina_id}",
        json={"cuerpo": "v2", "visibilidad": "publica"},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["visibilidad"] == "publica"

    token_otro = _crear_con_rol("gm")
    usurpa = feed.put(
        f"/api/v1/wiki/{pagina_id}",
        json={"cuerpo": "hack"},
        headers={"Authorization": f"Bearer {token_otro}"},
    )
    assert usurpa.status_code == 403


def test_borrar_pagina(gm):
    mesa_id, headers = gm
    pagina_id = _publicar(headers, mesa_id, {"titulo": "Temporal", "tipo": "Nota"}).json()["id"]
    feed = TestClient(feed_app)
    assert feed.delete(f"/api/v1/wiki/{pagina_id}", headers=headers).status_code == 204
    assert feed.get(f"/api/v1/wiki/{pagina_id}").status_code == 404


def test_404_pagina_inexistente(gm):
    feed = TestClient(feed_app)
    r = feed.get("/api/v1/wiki/99999")
    assert r.status_code == 404
    assert r.json()["error"]["codigo"] == 404
