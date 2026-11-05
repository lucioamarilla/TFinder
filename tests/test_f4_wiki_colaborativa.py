"""F4 · Wiki colaborativa: los jugadores proponen, el master resuelve
(pliego F4): contribuciones con estados pendiente | aprobada | rechazada.
"""

import os
import socket
import threading
import time
import uuid

import pytest
import uvicorn


def _textoDe(pagina):
    contenido = pagina.get("contenido") or []
    piezas = []
    for b in contenido:
        if isinstance(b, str):
            piezas.append(b)
        elif isinstance(b, dict):
            piezas.append(str(b.get("texto") or ""))
    return " ".join(piezas)
from fastapi.testclient import TestClient

from feed_api.app.db import abrir_pool as abrir_pool_feed
from feed_api.app.init_db import init_db as init_db_feed
from feed_api.main import app as feed_app
from mesas_api.main import app as mesas_app

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module", autouse=True)
def _pools_feed():
    abrir_pool_feed()
    init_db_feed()
    yield


@pytest.fixture
def feed_client(_pools_feed):
    return TestClient(feed_app)


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


# crea mesa + página + jugador registrado/aceptado
def _mesa_y_paginas(client, token_gm, rider=None):
    feed = rider
    r = client.post(
        "/api/v1/mesas",
        json={"nombre": f"Mesa wiki F4 {uuid.uuid4().hex[:4]}", "sistema": "pf1e"},
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r.status_code == 201
    mesa_id = r.json()["id"]
    email = f"f4_{uuid.uuid4().hex[:8]}@tfinder.dev"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secreto123", "nombre": "Colaborador F4", "rol": "usuario"},
    )
    login = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "secreto123"}
    ).json()
    auth_p = {"Authorization": f"Bearer {login['access_token']}"}
    sol = client.post(f"/api/v1/mesas/{mesa_id}/solicitudes", headers=auth_p).json()
    client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes/{sol['id']}/aceptar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    r_pag = feed.post(
        f"/api/v1/mesas/{mesa_id}/wiki",
        json={"titulo": "El corredor", "tipo": "Lugar"},
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r_pag.status_code == 201, r_pag.text
    return mesa_id, r_pag.json()["id"], {"Authorization": f"Bearer {token_gm}"}, auth_p


def test_jugador_propone_contribucion_pendiente(client, token_gm, feed_client):
    mesa_id, pag_id, auth_gm, auth_p = _mesa_y_paginas(client, token_gm, feed_client)
    r = feed_client.post(
        f"/api/v1/mesas/{mesa_id}/wiki/{pag_id}/contribuciones",
        json={"cuerpo": [{"texto": "El corredor respira sal. Olor de bahía."}]},
        headers=auth_p,
    )
    assert r.status_code == 201, r.text
    cuerpo = r.json()
    assert cuerpo["estado"] == "pendiente"
    assert (cuerpo["autorNombre"] or "").strip()


def test_contribucion_requiere_texto_no_vacio(client, token_gm, feed_client):
    mesa_id, pag_id, _, auth_p = _mesa_y_paginas(client, token_gm, feed_client)
    r = feed_client.post(
        f"/api/v1/mesas/{mesa_id}/wiki/{pag_id}/contribuciones",
        json={"cuerpo": []},
        headers=auth_p,
    )
    assert r.status_code == 400


def test_solo_el_master_ve_pendientes_y_resuelve(client, token_gm, feed_client):
    mesa_id, pag_id, auth_gm, auth_p = _mesa_y_paginas(client, token_gm, feed_client)
    contrib = feed_client.post(
        f"/api/v1/mesas/{mesa_id}/wiki/{pag_id}/contribuciones",
        json={"cuerpo": [{"texto": "Cambio propuesto del corredor"}]},
        headers=auth_p,
    ).json()
    contrib_id = contrib["id"]

    lista = feed_client.get(
        f"/api/v1/mesas/{mesa_id}/wiki/contribuciones?estado=pendiente", headers=auth_gm
    )
    assert lista.status_code == 200, lista.text
    assert any(c["id"] == contrib_id for c in lista.json())

    ok = feed_client.post(
        f"/api/v1/mesas/{mesa_id}/wiki/contribuciones/{contrib_id}/aprobar", headers=auth_gm
    )
    assert ok.status_code == 200, ok.text
    assert ok.json()["estado"] == "aprobada"

    pagina = feed_client.get(
        f"/api/v1/wiki/{pag_id}",
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()
    texto_contenido = _textoDe(pagina)
    assert "Cambio propuesto del corredor" in texto_contenido, "la aprobación aplica el contenido"

    ok2 = feed_client.post(
        f"/api/v1/mesas/{mesa_id}/wiki/contribuciones/{contrib_id}/aprobar", headers=auth_gm
    )
    assert ok2.status_code == 409, "una contribución ya resuelta no reprocesa"


def test_rechazar_contribucion(client, token_gm, feed_client):
    mesa_id, pag_id, auth_gm, auth_p = _mesa_y_paginas(client, token_gm, feed_client)
    contrib = feed_client.post(
        f"/api/v1/mesas/{mesa_id}/wiki/{pag_id}/contribuciones",
        json={"cuerpo": [{"texto": "La luna es de queso"}]},
        headers=auth_p,
    ).json()
    r = feed_client.post(
        f"/api/v1/mesas/{mesa_id}/wiki/contribuciones/{contrib['id']}/rechazar",
        headers=auth_gm,
    )
    assert r.status_code == 200
    assert r.json()["estado"] == "rechazada"

    pagina = feed_client.get(
        f"/api/v1/wiki/{pag_id}",
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()
    assert "queso" not in _textoDe(pagina)
