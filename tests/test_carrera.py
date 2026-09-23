"""Carrera por la última vacante (B06): N concurrentes contra 1 cupo."""

import uuid
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from tests.conftest import crear_mesa


def _registrar_y_token(client, rol, idx):
    email = f"race_{idx}_{uuid.uuid4().hex[:8]}@{rol}.tfinder"
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secreto123",
            "nombre": f"Race {idx}",
            "rol": rol,
        },
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "secreto123"},
    )
    return login.json()["access_token"]


def test_solo_uno_gana_la_ultima_vacante(client, token_gm):
    mesa_id = crear_mesa(client, token_gm, "Mesa race", jugadores_max=1)

    tokens = [_registrar_y_token(client, "usuario", i) for i in range(10)]

    def pedir(i):
        local = TestClient(client.app)
        return local.post(
            f"/api/v1/mesas/{mesa_id}/solicitudes",
            headers={
                "Idempotency-Key": f"race-key-{i}",
                "Authorization": f"Bearer {tokens[i]}",
            },
        ).status_code

    with ThreadPoolExecutor(max_workers=10) as ex:
        codigos = list(ex.map(pedir, range(10)))

    assert codigos.count(201) == 1
    assert codigos.count(409) == 9

    fila = client.get(
        f"/api/v1/mesas/{mesa_id}",
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()
    assert fila["jugadores_actuales"] <= fila["jugadores_max"]
    assert fila["jugadores_actuales"] == 1