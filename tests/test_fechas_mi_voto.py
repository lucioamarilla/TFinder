"""Ciclo 13 · D-14: GET /mesas/{id}/fechas debe exponer mi_voto del votante.

Antes: la respuesta traia a_favor_nombres/en_contra_nombres (nombres, no ids),
asi que el frontend inferia el voto propio comparando strings — fragil.
Contrato nuevo: campo mi_voto ='a_favor' | 'en_contra' | None por fila, del
usuario autenticado de la peticion.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

pytestmark = pytest.mark.integration


def _auth_de(client):
    email = f"voto_{uuid.uuid4().hex[:8]}@tfinder.dev"
    r = client.post("/api/v1/auth/register", json={"email": email, "password": "secreto123", "nombre": "Votante Ana"})
    assert r.status_code == 201
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "secreto123"})
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_listado_fechas_incluye_mi_voto(client, token_gm):
    mesa_id = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa mi voto", "sistema": "pf1e"},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]

    auth_vot = _auth_de(client)
    client.post(f"/api/v1/mesas/{mesa_id}/solicitudes", headers=auth_vot)
    sol_id = client.get(f"/api/v1/mesas/{mesa_id}/solicitudes", headers={"Authorization": f"Bearer {token_gm}"}).json()[0]["id"]
    client.post(f"/api/v1/mesas/{mesa_id}/solicitudes/{sol_id}/aceptar", headers={"Authorization": f"Bearer {token_gm}"})

    futuro = (datetime.now(timezone.utc) + timedelta(days=9)).strftime("%Y-%m-%dT%H:%M:%S")
    fecha_1 = client.post(f"/api/v1/mesas/{mesa_id}/fechas", json={"propuesta": futuro}, headers={"Authorization": f"Bearer {token_gm}"}).json()["id"]
    futuro2 = (datetime.now(timezone.utc) + timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%S")
    fecha_2 = client.post(f"/api/v1/mesas/{mesa_id}/fechas", json={"propuesta": futuro2}, headers={"Authorization": f"Bearer {token_gm}"}).json()["id"]

    client.post(f"/api/v1/mesas/{mesa_id}/fechas/{fecha_1}/voto", json={"valor": "a_favor"}, headers=auth_vot)
    client.post(f"/api/v1/mesas/{mesa_id}/fechas/{fecha_2}/voto", json={"valor": "en_contra"}, headers=auth_vot)

    lista = client.get(f"/api/v1/mesas/{mesa_id}/fechas", headers=auth_vot).json()
    por_id = {f["id"]: f for f in lista}
    assert por_id[fecha_1]["mi_voto"] == "a_favor"
    assert por_id[fecha_2]["mi_voto"] == "en_contra"
