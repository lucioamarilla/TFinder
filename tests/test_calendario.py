"""P1.5 · Calendario con votación de fechas (RF-10/RF-11, RN-06/RN-17,
VAL-29..32): el GM propone, los jugadores votan (único voto editable), y la
fecha confirmada nace sesión.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

pytestmark = pytest.mark.integration


def _fecha_futura():
    return (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")


def _usuario(client):
    email = f"cal_{uuid.uuid4().hex[:8]}@tfinder.dev"
    r = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secreto123", "nombre": "Jugador Calendario"},
    )
    assert r.status_code == 201
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "secreto123"})
    return login.json()


def _mesa(client, token_gm):
    r = client.post(
        "/api/v1/mesas",
        json={"nombre": f"Mesa cal {uuid.uuid4().hex[:4]}", "sistema": "pf1e"},
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r.status_code == 201
    return r.json()["id"]


def _miembro(client, mesa_id, token_gm):
    usuario = _usuario(client)
    sol = client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes",
        headers={"Authorization": f"Bearer {usuario['access_token']}"},
    ).json()
    client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes/{sol['id']}/aceptar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    return usuario


# ---- RF-10: proponer ---------------------------------------------------------

def test_gm_propone_fecha_futura(client, token_gm):
    mesa_id = _mesa(client, token_gm)
    r = client.post(
        f"/api/v1/mesas/{mesa_id}/fechas",
        json={"propuesta": _fecha_futura()},
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["estado"] == "propuesta"
    assert cuerpo["votos"] == {"a_favor": 0, "en_contra": 0}
    assert "propuesta" in cuerpo


def test_fecha_pasada_se_rechaza(client, token_gm):
    mesa_id = _mesa(client, token_gm)
    r = client.post(
        f"/api/v1/mesas/{mesa_id}/fechas",
        json={"propuesta": "2024-01-01T18:00:00"},
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r.status_code == 400, "VAL-29: la fecha propuesta no puede estar en el pasado"


def test_propuesta_sin_auth_da_401(client, token_gm):
    mesa_id = _mesa(client, token_gm)
    r = client.post(f"/api/v1/mesas/{mesa_id}/fechas", json={"propuesta": _fecha_futura()})
    assert r.status_code == 401


def test_solo_el_gm_propone(client, token_gm, token_jugador):
    mesa_id = _mesa(client, token_gm)
    r = client.post(
        f"/api/v1/mesas/{mesa_id}/fechas",
        json={"propuesta": _fecha_futura()},
        headers={"Authorization": f"Bearer {token_jugador}"},
    )
    assert r.status_code == 403, "RF-10: propone el GM de la mesa"


# ---- RF-11/RN-06: votar ------------------------------------------------------

def test_miembro_vota_y_puede_cambiar_su_voto(client, token_gm):
    mesa_id = _mesa(client, token_gm)
    fecha_id = client.post(
        f"/api/v1/mesas/{mesa_id}/fechas",
        json={"propuesta": _fecha_futura()},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]

    usuario = _miembro(client, mesa_id, token_gm)
    auth = {"Authorization": f"Bearer {usuario['access_token']}"}

    r = client.post(
        f"/api/v1/mesas/{mesa_id}/fechas/{fecha_id}/voto",
        json={"valor": "a_favor"},
        headers=auth,
    )
    assert r.status_code == 200
    cuerpo = client.get(
        f"/api/v1/mesas/{mesa_id}/fechas", headers=auth
    ).json()[0]
    assert cuerpo["votos"] == {"a_favor": 1, "en_contra": 0}

    cambio = client.post(
        f"/api/v1/mesas/{mesa_id}/fechas/{fecha_id}/voto",
        json={"valor": "en_contra"},
        headers=auth,
    )
    assert cambio.status_code == 200, "RN-06: puede actualizar, no duplicar"
    cuerpo2 = client.get(f"/api/v1/mesas/{mesa_id}/fechas", headers=auth).json()[0]
    assert cuerpo2["votos"] == {"a_favor": 0, "en_contra": 1}


def test_voto_de_un_no_miembro_da_403(client, token_gm):
    mesa_id = _mesa(client, token_gm)
    fecha_id = client.post(
        f"/api/v1/mesas/{mesa_id}/fechas",
        json={"propuesta": _fecha_futura()},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]
    ajeno = _usuario(client)
    r = client.post(
        f"/api/v1/mesas/{mesa_id}/fechas/{fecha_id}/voto",
        json={"valor": "a_favor"},
        headers={"Authorization": f"Bearer {ajeno['access_token']}"},
    )
    assert r.status_code == 403, "VAL-31: solo miembros de la mesa votan"


def test_el_gm_no_vota_su_propia_propuesta(client, token_gm, token_jugador):
    mesa_id = _mesa(client, token_gm)
    usuario = _miembro(client, mesa_id, token_gm)
    fecha_id = client.post(
        f"/api/v1/mesas/{mesa_id}/fechas",
        json={"propuesta": _fecha_futura()},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]
    r = client.post(
        f"/api/v1/mesas/{mesa_id}/fechas/{fecha_id}/voto",
        json={"valor": "a_favor"},
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r.status_code == 403, "RN-17: el GM no vota las fechas que propone"


def test_valor_de_voto_invalido_da_400(client, token_gm):
    mesa_id = _mesa(client, token_gm)
    usuario = _miembro(client, mesa_id, token_gm)
    fecha_id = client.post(
        f"/api/v1/mesas/{mesa_id}/fechas",
        json={"propuesta": _fecha_futura()},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]
    r = client.post(
        f"/api/v1/mesas/{mesa_id}/fechas/{fecha_id}/voto",
        json={"valor": "tal vez"},
        headers={"Authorization": f"Bearer {usuario['access_token']}"},
    )
    assert r.status_code == 400, "VAL-30: 'a favor' o 'en contra'"


def test_votar_fecha_descartada_da_409(client, token_gm):
    mesa_id = _mesa(client, token_gm)
    usuario = _miembro(client, mesa_id, token_gm)
    fecha_id = client.post(
        f"/api/v1/mesas/{mesa_id}/fechas",
        json={"propuesta": _fecha_futura()},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]
    client.delete(
        f"/api/v1/mesas/{mesa_id}/fechas/{fecha_id}",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    r = client.post(
        f"/api/v1/mesas/{mesa_id}/fechas/{fecha_id}/voto",
        json={"valor": "a_favor"},
        headers={"Authorization": f"Bearer {usuario['access_token']}"},
    )
    assert r.status_code == 409


# ---- Confirmar la fecha ganadora ---------------------------------------------

def test_confirmar_fecha_crea_la_sesion(client, token_gm):
    mesa_id = _mesa(client, token_gm)
    fecha_id = client.post(
        f"/api/v1/mesas/{mesa_id}/fechas",
        json={"propuesta": _fecha_futura()},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]

    r = client.post(
        f"/api/v1/mesas/{mesa_id}/fechas/{fecha_id}/confirmar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r.status_code == 200

    sesiones = client.get(
        f"/api/v1/mesas/{mesa_id}/sesiones",
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()
    assert len(sesiones) == 1, "confirmar la fecha nace una sesión de juego"
