"""F5 · Perfil real (mesas-api): nombre, avatar, bio, actividad."""

import uuid

import pytest

pytestmark = pytest.mark.integration


def test_perfil_devuelve_y_actualiza_datos(client, token_gm):
    r = client.get("/api/v1/auth/perfil", headers={"Authorization": f"Bearer {token_gm}"})
    assert r.status_code == 200
    assert r.json()["email"] == "test_gm_f61b9f3442@tfinder.dev" or "@" in r.json()["email"]
    assert "avatarUrl" in r.json()

    r2 = client.patch(
        "/api/v1/auth/perfil",
        json={"nombre": "GM Ostirion", "bio": "Director de campañas.", "avatarUrl": "/api/v1/uploads/abc"},
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r2.status_code == 200
    assert r2.json()["nombre"] == "GM Ostirion"
    assert r2.json()["bio"] == "Director de campañas."
    assert r2.json()["avatarUrl"] == "/api/v1/uploads/abc"

    r3 = client.get("/api/v1/auth/perfil", headers={"Authorization": f"Bearer {token_gm}"})
    assert r3.json()["avatarUrl"] == "/api/v1/uploads/abc"
    assert r3.json()["bio"] == "Director de campañas."


def test_perfil_sin_auth_da_401(client):
    assert client.get("/api/v1/auth/perfil").status_code == 401
    assert client.patch("/api/v1/auth/perfil", json={"nombre": "x"}).status_code == 401


def test_perfil_valida_nombre_vacio(client, token_gm):
    r = client.patch("/api/v1/auth/perfil", json={"nombre": "  "}, headers={"Authorization": f"Bearer {token_gm}"})
    assert r.status_code == 400
