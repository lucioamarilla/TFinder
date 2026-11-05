"""F3 · El modo sesión es una bitácora (pliego 2.3): registro cronológico de
acontecimientos por sesión, anotaciones de todos los integrantes con autor y
fecha-hora, historial persistente.

RED previo: no existían anotaciones ni endpoints; el modo sesión simulaba
combate (turnos/PV), prohibido por el pliego.
"""

import uuid

import pytest

pytestmark = pytest.mark.integration


def _registrar(client, nombre="Anotador F3"):
    email = f"f3_{uuid.uuid4().hex[:8]}@tfinder.dev"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secreto123", "nombre": nombre},
    )
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "secreto123"})
    return login.json()


def _mesa_con_miembro(client, token_gm):
    mesa = client.post(
        "/api/v1/mesas",
        json={"nombre": f"Mesa bitácora {uuid.uuid4().hex[:4]}", "sistema": "pf1e"},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()
    usuario = _registrar(client)
    sol = client.post(
        f"/api/v1/mesas/{mesa['id']}/solicitudes",
        headers={"Authorization": f"Bearer {usuario['access_token']}"},
    ).json()
    client.post(
        f"/api/v1/mesas/{mesa['id']}/solicitudes/{sol['id']}/aceptar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    return mesa["id"], usuario


def _sesion(client, token_gm, mesa_id):
    r = client.post(
        f"/api/v1/mesas/{mesa_id}/sesiones",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r.status_code == 201
    return r.json()["id"]


def _anotar(client, mesa_id, sesion_id, token, texto):
    return client.post(
        f"/api/v1/mesas/{mesa_id}/sesiones/{sesion_id}/anotaciones",
        json={"texto": texto},
        headers={"Authorization": f"Bearer {token}"},
    )


def test_master_y_jugadores_anotan_y_queda_cronologico(client, token_gm):
    from datetime import datetime, timezone

    mesa_id, usuario = _mesa_con_miembro(client, token_gm)
    sesion_id = _sesion(client, token_gm, mesa_id)

    gm_token = token_gm
    r1 = _anotar(client, mesa_id, sesion_id, gm_token, "Abrió la sesión en la taberna de los Bosques.")
    assert r1.status_code == 201, r1.text
    primera = r1.json()
    assert primera["texto"].startswith("Abrió la sesión")
    assert primera["autor_nombre"], "la anotación identificará a su autor"
    assert primera["creado_en"], "fecha y hora del servidor"

    miembro_token = usuario["access_token"]
    r2 = _anotar(client, mesa_id, sesion_id, miembro_token, "El barrendero se bebió la última pinta.")
    assert r2.status_code == 201
    r3 = _anotar(client, mesa_id, sesion_id, gm_token, "Llegó el mensajero con la carta sangrada.")

    historial = client.get(
        f"/api/v1/mesas/{mesa_id}/sesiones/{sesion_id}/anotaciones",
        headers={"Authorization": f"Bearer {miembro_token}"},
    ).json()

    assert len(historial) == 3
    fechas = [a["creado_en"] for a in historial]
    assert fechas == sorted(fechas), "orden cronológico (más viejo primero)"
    autores = {a["autor_nombre"] for a in historial}
    assert len(autores) >= 2, "varios integrantes anotaron"
    for a in historial:
        assert a["autor_nombre"].strip()
        datetime.fromisoformat(a["creado_en"].replace("Z", "+00:00"))


def test_anotacion_vacia_da_400(client, token_gm):
    mesa_id, _ = _mesa_con_miembro(client, token_gm)
    sesion_id = _sesion(client, token_gm, mesa_id)
    r = _anotar(client, mesa_id, sesion_id, token_gm, "   ")
    assert r.status_code == 400
    assert r.json()["error"]["codigo"] == 400


def test_solo_integrantes_leen_y_anotan(client, token_gm):
    mesa_id, usuario = _mesa_con_miembro(client, token_gm)
    sesion_id = _sesion(client, token_gm, mesa_id)
    ajeno = _registrar(client)

    r_anot = _anotar(client, mesa_id, sesion_id, ajeno["access_token"], "espia")
    assert r_anot.status_code == 403

    r_leer = client.get(
        f"/api/v1/mesas/{mesa_id}/sesiones/{sesion_id}/anotaciones",
        headers={"Authorization": f"Bearer {ajeno['access_token']}"},
    )
    assert r_leer.status_code == 403
