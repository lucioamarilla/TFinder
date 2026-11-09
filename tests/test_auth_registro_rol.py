"""El registro publico nunca debe otorgar un rol privilegiado.

El endpoint /api/v1/auth/register es abierto, asi que acepta el campo
`rol`. Las cuentas gm/admin se crean fuera de esa via (seed o administracion).

Con la verificación por código, el rol sobrevive el paso pendiente → verificar:
si el payload pide admin/gm, la cuenta final sigue siendo "usuario".
"""

import uuid

import pytest

pytestmark = pytest.mark.integration


def _registrar_y_verificar(client, rol=None):
    email = f"rol_{uuid.uuid4().hex[:10]}@tfinder.dev"
    cuerpo = {
        "email": email,
        "password": "secreto123",
        "nombre": "Alta publica",
    }
    if rol is not None:
        cuerpo["rol"] = rol
    r = client.post("/api/v1/auth/register", json=cuerpo)
    assert r.status_code == 202, r.text
    from tests.conftest import codigo_del_ultimo_mail

    codigo = codigo_del_ultimo_mail(destino=email)
    r = client.post("/api/v1/auth/register/verificar", json={"email": email, "codigo": codigo})
    assert r.status_code == 200, r.text
    return r.json(), email


def test_registro_sin_rol_crea_usuario(client):
    tokens, _ = _registrar_y_verificar(client)
    assert tokens["rol"] == "usuario"


def test_registro_no_escala_a_admin(client):
    tokens, _ = _registrar_y_verificar(client, "admin")
    assert tokens["rol"] == "usuario"


def test_registro_no_escala_a_gm(client):
    tokens, _ = _registrar_y_verificar(client, "gm")
    assert tokens["rol"] == "usuario"


def test_registro_pide_verificacion_antes_de_crear_la_cuenta(client):
    """El registro no crea la cuenta: emite 'pendiente' y el mail con código."""
    email = f"pend_{uuid.uuid4().hex[:10]}@tfinder.dev"
    r = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secreto123", "nombre": "Pendiente"},
    )
    assert r.status_code == 202, r.text
    assert r.json()["pendiente"] is True
    # Sin verificar, no hay sesión: login imposible y el usuario no existe.
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "secreto123"})
    assert login.status_code == 401


def test_cuenta_escalada_no_puede_entrar_como_admin(client):
    _, email = _registrar_y_verificar(client, "admin")
    login = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "secreto123"}
    )
    token = login.json()["access_token"]
    r = client.get("/api/v1/auth/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403
