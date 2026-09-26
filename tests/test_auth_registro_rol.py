"""El registro publico nunca debe otorgar un rol privilegiado.

El endpoint /api/v1/auth/register es abierto, asi que acepta el campo
`rol`. Las cuentas gm/admin se crean fuera de esa via (seed o administracion).
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from mesas_api.main import app

pytestmark = pytest.mark.integration


def _registrar(client, rol=None):
    email = f"rol_{uuid.uuid4().hex[:10]}@tfinder.dev"
    cuerpo = {
        "email": email,
        "password": "secreto123",
        "nombre": "Alta publica",
    }
    if rol is not None:
        cuerpo["rol"] = rol
    return client.post("/api/v1/auth/register", json=cuerpo), email


def test_registro_sin_rol_crea_usuario(client):
    r, _ = _registrar(client)
    assert r.status_code == 201
    assert r.json()["rol"] == "usuario"


def test_registro_no_escala_a_admin(client):
    r, _ = _registrar(client, "admin")
    assert r.status_code == 201
    assert r.json()["rol"] == "usuario"


def test_registro_no_escala_a_gm(client):
    r, _ = _registrar(client, "gm")
    assert r.status_code == 201
    assert r.json()["rol"] == "usuario"


def test_cuenta_escalada_no_puede_entrar_como_admin(client):
    _, email = _registrar(client, "admin")
    login = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "secreto123"}
    )
    token = login.json()["access_token"]
    r = client.get("/api/v1/auth/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403
