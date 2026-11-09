"""P0.3 · Sesión real FE→BE — logout mata TODA la familia de sesiones, y la
respuesta de auth expone el perfil para que el frontend no necesite un segundo
viaje a /auth/me.

RED previo: logout revocaba sólo el jti del access; el refresh_tokem seguía
vivo y permitía continuar la sesión después del logout.
RED previo: register/login devolvía {access_token, refresh_token, rol} sin
perfil.
"""

import uuid

import pytest

pytestmark = pytest.mark.integration


def _registro(client, email=None):
    email = email or f"test_{uuid.uuid4().hex[:10]}@tfinder.dev"
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secreto123", "nombre": "Dora Exploradora"},
    )
    assert resp.status_code == 202
    from tests.conftest import codigo_del_ultimo_mail

    codigo = codigo_del_ultimo_mail(destino=email)
    resp = client.post("/api/v1/auth/register/verificar", json={"email": email, "codigo": codigo})
    assert resp.status_code == 200
    return email, resp.json()


def test_logout_invalida_tambien_el_refresh(client):
    _, tokens = _registro(client)
    access, refresh = tokens["access_token"], tokens["refresh_token"]

    r = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200

    # El access viejo ya no sirve.
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 401

    # Y el refresh de esa sesión tampoco (familia completa revocada).
    renov = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert renov.status_code == 401, (
        "el logout debe revocar toda la familia de sesiones (access + refresh)"
    )


def test_refresh_renovado_aun_es_valido_si_no_hubo_logout(client):
    _, tokens = _registro(client)
    renov = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert renov.status_code == 200
    assert "access_token" in renov.json()


def test_register_y_login_devuelven_el_perfil(client):
    email, tokens = _registro(client)
    perfil = tokens.get("perfil")
    assert isinstance(perfil, dict), "el registro debe incluir el perfil del usuario"
    assert perfil["email"] == email
    assert perfil["rol"] == "usuario"
    assert perfil["nombre"].strip()

    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "secreto123"})
    assert resp.status_code == 200
    assert resp.json()["perfil"]["nombre"].strip()


def test_comprobar_dos_usuarios_tiene_familias_independientes(client):
    _, tokens_a = _registro(client)
    _, tokens_b = _registro(client)

    client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {tokens_a['access_token']}"})

    # La sesión del usuario B no puede morir por el logout de A.
    me_b = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens_b['access_token']}"}
    )
    assert me_b.status_code == 200
