"""F1 · Comunidades reales y "mis mesas" para el header unificado.

RED previo: el feed no entendía el concepto de comunidad (solo etiqueta) y el
front no tenía ninguna fuente real de "mis mesas" (leía el simulador demo).
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from feed_api.app.db import abrir_pool as abrir_pool_feed
from feed_api.app.init_db import init_db as init_db_feed
from feed_api.main import app as feed_app

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module", autouse=True)
def _pools():
    abrir_pool_feed()
    init_db_feed()
    yield


@pytest.fixture(autouse=True)
def _limpieza_feed(_pools):
    from feed_api.app.db import get_connection as feed_conn

    with feed_conn() as conn:
        conn.execute("TRUNCATE publicaciones, likes_post, follows RESTART IDENTITY CASCADE")
    yield
    with feed_conn() as conn:
        conn.execute("TRUNCATE publicaciones, likes_post, follows RESTART IDENTITY CASCADE")


@pytest.fixture
def feed_client(_pools):
    return TestClient(feed_app)


@pytest.fixture
def feed_publica(feed_client):
    return feed_client


def _post(feed, auth, titulo, comunidad=None):
    cuerpo = {"titulo": titulo, "cuerpo": f"contenido de {titulo}"}
    if comunidad is not None:
        cuerpo["comunidad"] = comunidad
    r = feed.post("/api/v1/feed", json=cuerpo, headers=auth)
    assert r.status_code == 201, r.text
    return r.json()


# ---- comunidades: crear con comunidad + listado agregado -----------------------

def test_crear_post_con_comunidad(feed_client, token_jugador):
    auth = {"Authorization": f"Bearer {token_jugador}"}
    post = _post(feed_client, auth, "Post con comunidad", comunidad="VellmarCronistas")
    assert post["comunidad"] == "VellmarCronistas"


def test_comunidades_agregadas_con_conteo(feed_client, token_jugador):
    auth = {"Authorization": f"Bearer {token_jugador}"}
    _post(feed_client, auth, "Uno", comunidad="VellmarCronistas")
    _post(feed_client, auth, "Dos", comunidad="VellmarCronistas")
    _post(feed_client, auth, "Tres", comunidad="CompendioArcano")
    _post(feed_client, auth, "General sin comunidad")

    r = feed_client.get("/api/v1/feed/comunidades")
    assert r.status_code == 200
    lista = r.json()
    por_nombre = {c["comunidad"]: c["cantidad"] for c in lista}
    assert por_nombre.get("VellmarCronistas") == 2
    assert por_nombre.get("CompendioArcano") == 1
    assert all(c["comunidad"] for c in lista)


def test_filtrar_por_comunidad(feed_client, token_jugador):
    auth = {"Authorization": f"Bearer {token_jugador}"}
    suyo = _post(feed_client, auth, "Post de la cripta", comunidad="VellmarCronistas")
    _post(feed_client, auth, "Post ajeno", comunidad="CompendioArcano")
    _post(feed_client, auth, "Post sin comunidad")

    r = feed_client.get("/api/v1/feed", params={"comunidad": "VellmarCronistas"})
    assert r.status_code == 200
    lista = r.json()
    assert lista and all(p["comunidad"] == "VellmarCronistas" for p in lista)
    assert suyo["titulo"] in [p["titulo"] for p in lista]


# ---- mis mesas: fuente real para el header ------------------------------------

def test_mis_mesas_del_gm_y_miembros(client, token_gm, token_jugador):
    mesa_id = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa mías 1", "sistema": "pf1e", "jugadores_max": 3},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]
    client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa mías 2", "sistema": "pf1e", "estado": "cerrada"},
        headers={"Authorization": f"Bearer {token_gm}"},
    )

    # El jugador pide entrar y el GM lo acepta: pasa a ser miembro con rol jugador.
    sol = client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes",
        headers={"Authorization": f"Bearer {token_jugador}"},
    ).json()
    client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes/{sol['id']}/aceptar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )

    # El GM ve sus 2 mesas (con rol master); el jugador solo la aceptada (rol jugador).
    suyas = client.get(
        "/api/v1/mesas/mias", headers={"Authorization": f"Bearer {token_gm}"}
    ).json()
    mine = client.get(
        "/api/v1/mesas/mias", headers={"Authorization": f"Bearer {token_jugador}"}
    ).json()

    assert [m["id"] for m in suyas] == [mesa_id] + [
        m["id"] for m in suyas if m["id"] != mesa_id
    ] or {mesa_id} <= {m["id"] for m in suyas}
    assert {m["id"] for m in suyas} >= {mesa_id}
    assert len(suyas) == 2
    assert all(m.get("mi_rol") == "master" for m in suyas)
    assert [m["id"] for m in mine] == [mesa_id]
    assert mine[0]["mi_rol"] == "jugador"
    assert mine[0]["nombre"] == "Mesa mías 1"


def test_mis_mesas_requiere_sesion(client):
    r = client.get("/api/v1/mesas/mias")
    assert r.status_code == 401
