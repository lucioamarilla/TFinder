"""F5 · Foro: builds privadas nunca se adjuntan (pliego F5, validado en backend)."""

import os
import urllib.request
import socket
import threading
import time
import uuid

import pytest
import uvicorn
from fastapi.testclient import TestClient

from builds_api.app.db import abrir_pool as abrir_pool_builds
from builds_api.app.init_db import init_db as init_db_builds
from builds_api.main import app as builds_app
from feed_api.app.db import abrir_pool as abrir_pool_feed
from feed_api.app.init_db import init_db as init_db_feed
from feed_api.main import app as feed_app
from mesas_api.main import app as mesas_app
from tests.conftest import _crear_con_rol

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module", autouse=True)
def _pools():
    abrir_pool_builds()
    init_db_builds()
    abrir_pool_feed()
    init_db_feed()
    yield


@pytest.fixture
def feed_client(_pools):
    return TestClient(feed_app)


@pytest.fixture(scope="module", autouse=True)
def _mesas_real():
    puerto = 0
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        puerto = s.getsockname()[1]
    config = uvicorn.Config(mesas_app, host="127.0.0.1", port=puerto, log_level="warning", lifespan="off")
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


@pytest.fixture(scope="module", autouse=True)
def _builds_real():
    puerto = 0
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        puerto = s.getsockname()[1]
    from builds_api.main import app as _builds_app

    config = uvicorn.Config(_builds_app, host="127.0.0.1", port=puerto, log_level="warning", lifespan="off")
    servidor = uvicorn.Server(config)
    hilo = threading.Thread(target=servidor.run, daemon=True)
    hilo.start()
    for _ in range(60):
        if getattr(servidor, "started", False):
            break
        time.sleep(0.2)
    url_previa = os.environ.get("BUILDS_URL")
    os.environ["BUILDS_URL"] = f"http://127.0.0.1:{puerto}"
    yield
    if url_previa is None:
        os.environ.pop("BUILDS_URL", None)
    else:
        os.environ["BUILDS_URL"] = url_previa
    servidor.should_exit = True
    hilo.join(timeout=5)


def test_publicar_post_con_build_publica_ok(feed_client):
    auth = {"Authorization": f"Bearer {_crear_con_rol('usuario')}"}
    build_auth = {"Authorization": f"Bearer {_crear_con_rol('usuario')}"}
    r_build = None
    # crear un build público en builds-api (vía REST real)
    import urllib.request as _r

    builds_url = os.environ["BUILDS_URL"]
    token = build_auth["Authorization"].split(" ", 1)[1]
    import json as _j
    _req = urllib.request.Request(
        f"{builds_url}/api/v1/builds",
        data=_j.dumps({"titulo": "Mago del Alba", "clase": "Mago", "privacidad": "publico", "atributos": {}}).encode(),
        method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(_req) as _resp:
        resp_build = type("R", (), {"status_code": _resp.status, "text": _resp.read().decode(), "json": lambda self: _j.loads(self.text)})()

    assert resp_build.status_code == 201, resp_build.text
    build_id = resp_build.json()["id"]

    r = feed_client.post(
        "/api/v1/feed",
        json={"titulo": "Build compartida", "cuerpo": "Análisis", "tipo": "build", "embed": {"build_id": build_id}},
        headers=auth,
    )
    assert r.status_code == 201, r.text
    assert r.json().get("embed", {}).get("build_id") == build_id


def test_publicar_post_con_build_privada_se_rechaza(feed_client):
    import urllib.request as _r

    token = _crear_con_rol("usuario").split(" ")[1] if False else None
    auth = {"Authorization": f"Bearer {_crear_con_rol('usuario')}"}
    builds_url = os.environ["BUILDS_URL"]
    token_owner = auth["Authorization"].split(" ", 1)[1]
    import json as _j
    _req = urllib.request.Request(
        f"{builds_url}/api/v1/builds",
        data=_j.dumps({"titulo": "Sombra Privada", "clase": "Pícaro", "privacidad": "privado", "atributos": {}}).encode(),
        method="POST",
        headers={"Authorization": f"Bearer {token_owner}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(_req) as _resp:
        resp_build = type("R", (), {"status_code": _resp.status, "text": _resp.read().decode(), "json": lambda self: _j.loads(self.text)})()

    assert resp_build.status_code == 201
    build_id = resp_build.json()["id"]

    r = feed_client.post(
        "/api/v1/feed",
        json={"titulo": "Intento adjuntar privada", "cuerpo": "x", "tipo": "build", "embed": {"build_id": build_id}},
        headers=auth,
    )
    assert r.status_code == 409, "pliego F5: las builds privadas nunca se comparten"
    assert "build" in r.json()["error"]["mensaje"].lower() or "privada" in r.json()["error"]["mensaje"].lower()


def test_publicar_post_con_build_inexistente_se_rechaza(feed_client):
    auth = {"Authorization": f"Bearer {_crear_con_rol('usuario')}"}
    r = feed_client.post(
        "/api/v1/feed",
        json={"titulo": "x", "cuerpo": "y", "embed": {"build_id": 99999}},
        headers=auth,
    )
    assert r.status_code == 409
