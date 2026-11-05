"""P1.8 · Builds activos (RF-19/20/21, RN-11/12/19, VAL-37..40/44/45) y tags.

La verificación de membresía para VINCULAR es cross-servicio: builds-api
pregunta por REST a mesas-api (contrato B09).
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
from mesas_api.main import app as mesas_app
from tests.conftest import _crear_con_rol

pytestmark = pytest.mark.integration

BUILDS_TABLAS = (
    "builds_tags, builds, tags"
)


@pytest.fixture(scope="module", autouse=True)
def _pools():
    abrir_pool_builds()
    init_db_builds()
    yield


@pytest.fixture(autouse=True)
def _limpieza(_pools):
    with builds_conn() as conn:
        conn.execute(f"TRUNCATE {BUILDS_TABLAS} RESTART IDENTITY CASCADE")
    yield
    with builds_conn() as conn:
        conn.execute(f"TRUNCATE {BUILDS_TABLAS} RESTART IDENTITY CASCADE")


@pytest.fixture(scope="module", autouse=True)
def _mesas_local():
    """mesas-api REAL en un puerto efímero para los puentes REST de vincular."""
    puerto = 0
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        puerto = s.getsockname()[1]
    config = uvicorn.Config(mesas_app, host="127.0.0.1", port=puerto, log_level="warning")
    servidor = uvicorn.Server(config)
    hilo = threading.Thread(target=servidor.run, daemon=True)
    hilo.start()
    for _ in range(60):
        if getattr(servidor, "started", False):
            break
        time.sleep(0.2)
    url_anterior = os.environ.get("MESA_URL")
    os.environ["MESA_URL"] = f"http://127.0.0.1:{puerto}"
    yield puerto
    if url_anterior is None:
        os.environ.pop("MESA_URL", None)
    else:
        os.environ["MESA_URL"] = url_anterior
    servidor.should_exit = True
    hilo.join(timeout=5)


@pytest.fixture
def builds():
    return TestClient(builds_app)


def _auth(rol="usuario"):
    return {"Authorization": f"Bearer {_crear_con_rol(rol)}"}


FICHA_OK = {
    "titulo": "Aldren Valeros",
    "clase": "Guerrero",
    "raza": "Humano",
    "nivel": 5,
    "roles": ["Defensa"],
    "atributos": {"fue": 16, "des": 14, "con": 14, "int": 10, "sab": 12, "car": 8},
}


# ---- RF-19: crear (VAL-44/45) -------------------------------------------------

def test_crear_build_con_clase_y_atributos(builds):
    auth = _auth()
    r = builds.post("/api/v1/builds", json=ficha_ok(), headers=auth)
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["clase"] == "Guerrero"
    assert cuerpo["privacidad"] == "borrador", "RF-19: 'crea y publicable después'"


def ficha_ok():
    return dict(FICHA_OK)


def test_clase_obligatoria(builds):
    auth = _auth()
    mala = dict(FICHA_OK)
    mala.pop("clase")
    r = builds.post("/api/v1/builds", json=mala, headers=auth)
    assert r.status_code == 400, "VAL-44"
    assert "clase" in r.json()["error"]["mensaje"].lower()


def test_atributos_fuera_de_rango(builds):
    auth = _auth()
    mala = dict(FICHA_OK)
    mala["atributos"] = {**FICHA_OK["atributos"], "fue": 25}
    r = builds.post("/api/v1/builds", json=mala, headers=auth)
    assert r.status_code == 400, "VAL-45: atributo entre 3 y 18"
    assert "Fue" in r.json()["error"]["mensaje"]


def test_creacion_requiere_auth(builds):
    r = builds.post("/api/v1/builds", json=ficha_ok())
    assert r.status_code == 401


# ---- RN-11: propiedad ----------------------------------------------------------

def test_solo_el_propietario_edita(builds):
    auth = _auth()
    build_id = builds.post("/api/v1/builds", json=ficha_ok(), headers=auth).json()["id"]

    r = builds.put(f"/api/v1/builds/{build_id}", json={"nivel": 6}, headers=auth)
    assert r.status_code == 200
    assert r.json()["nivel"] == 6

    usurpa = builds.put(f"/api/v1/builds/{build_id}", json={"nivel": 20}, headers=_auth("gm"))
    assert usurpa.status_code == 403, "VAL-38"


def test_borrar_es_solo_del_propietario(builds):
    auth = _auth()
    build_id = builds.post("/api/v1/builds", json=ficha_ok(), headers=auth).json()["id"]
    usurpa = builds.delete(f"/api/v1/builds/{build_id}", headers=_auth("gm"))
    assert usurpa.status_code == 403
    r = builds.delete(f"/api/v1/builds/{build_id}", headers=auth)
    assert r.status_code == 204
    assert builds.get(f"/api/v1/builds/{build_id}").status_code == 404, "VAL-37"


# ---- RN-19: historial -----------------------------------------------------------

def test_editar_apila_version_y_puede_restaurar(builds):
    auth = _auth()
    build_id = builds.post("/api/v1/builds", json=ficha_ok(), headers=auth).json()["id"]

    builds.put(f"/api/v1/builds/{build_id}", json={"nivel": 6}, headers=auth)
    builds.put(f"/api/v1/builds/{build_id}", json={"nivel": 7}, headers=auth)

    cuerpo = builds.get(f"/api/v1/builds/{build_id}", headers=auth).json()
    assert len(cuerpo["historial"]) == 2, "RN-19: cada edición apila una versión"

    r = builds.post(f"/api/v1/builds/{build_id}/restaurar/0", headers=auth)
    assert r.status_code == 200
    recuperado = builds.get(f"/api/v1/builds/{build_id}", headers=auth).json()
    assert recuperado["nivel"] == 5, "restaurar vuelve al snapshot viejo"


# ---- RF-20: publicar -------------------------------------------------------------

def test_publicar_hace_publico(builds):
    auth = _auth()
    build_id = builds.post("/api/v1/builds", json=ficha_ok(), headers=auth).json()["id"]
    r = builds.post(f"/api/v1/builds/{build_id}/publicar", headers=auth)
    assert r.status_code == 200
    assert r.json()["privacidad"] == "publico"


# ---- RF-21/RN-12/VAL-40: vincular a mesa ------------------------------------------

def _mesa_con_gm(mesas_client):
    token = _crear_con_rol("gm")
    r = mesas_client.post(
        "/api/v1/mesas",
        json={"nombre": f"Mesa builds {uuid.uuid4().hex[:4]}", "sistema": "pf1e"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    return r.json()["id"], token


@pytest.fixture
def mesas_client(_mesas_local):
    return TestClient(mesas_app)


def test_vincular_exige_miembros(builds, mesas_client):
    auth = _auth()
    build_id = builds.post("/api/v1/builds", json=ficha_ok(), headers=auth).json()["id"]
    mesa_id, token_gm = _mesa_con_gm(mesas_client)

    ajeno = builds.post(
        f"/api/v1/builds/{build_id}/vincular/{mesa_id}", headers=auth
    )
    assert ajeno.status_code == 403, "VAL-40: el creador debe ser miembro"

    # El creador entra a la mesa y recién entonces víncula.
    sol = mesas_client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes", headers=auth
    ).json()
    mesas_client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes/{sol['id']}/aceptar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    r = builds.post(f"/api/v1/builds/{build_id}/vincular/{mesa_id}", headers=auth)
    assert r.status_code == 200
    assert r.json()["mesaId"] == mesa_id

    r = builds.delete(f"/api/v1/builds/{build_id}/vincular", headers=auth)
    assert r.status_code == 200
    assert r.json()["mesaId"] is None


# ---- tags ---------------------------------------------------------------------------

def test_asignar_tags_y_filtrar(builds):
    builds.post(
        "/api/v1/tags", json={"nombres": ["Guerrero", "Defensa"]}, headers=_auth()
    )
    auth = _auth()
    body = builds.post("/api/v1/builds", json=ficha_ok(), headers=auth).json()
    r = builds.post(
        f"/api/v1/builds/{body['id']}/tags",
        json={"nombres": ["Guerrero", "Defensa"]},
        headers=auth,
    )
    assert r.status_code == 200

    filtrado = builds.get("/api/v1/builds", params={"tag": "Guerrero"})
    assert filtrado.status_code == 200
    assert filtrado.json() and all(b["id"] == body["id"] or b["clase"] == "Guerrero" for b in filtrado.json())

    tags = builds.get("/api/v1/tags").json()
    nombres = {t["nombre"] for t in tags}
    assert {"Guerrero", "Defensa"} <= nombres
