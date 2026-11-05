"""Concurrencia en la vertical P0.4.

Dos carreras distintas desde el flujo RF-14/15:
1. Creación: el mismo usuario spamea solicitudes concurrentes contra la misma
   mesa → el índice parcial `uq_solicitud_activa` decide: 1×201 + 9×409.
2. Aceptación: el GM (o dos admins) acepta solicitudes concurrentes cuando
   queda UNA vacante → el UPDATE condicional de cupo decide: 1×200 + N×409,
   con `jugadores_actuales == jugadores_max` final.
"""

import pytest
import uuid
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from tests.conftest import crear_mesa

pytestmark = pytest.mark.integration


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


def _solicitar_concurrente(client, mesa_id, tokens):
    def pedir(idx):
        local = TestClient(client.app)
        return local.post(
            f"/api/v1/mesas/{mesa_id}/solicitudes",
            headers={
                "Idempotency-Key": f"race-key-{idx}",
                "Authorization": f"Bearer {tokens[idx]}",
            },
        ).status_code

    with ThreadPoolExecutor(max_workers=len(tokens)) as ex:
        return list(ex.map(pedir, range(len(tokens))))


def test_doble_solicitud_concurrente_del_mismo_usuario(client, token_gm):
    mesa_id = crear_mesa(client, token_gm, "Mesa race misma persona", jugadores_max=1)
    token = _registrar_y_token(client, "usuario", 0)
    tokens = [token] * 10

    codigos = _solicitar_concurrente(client, mesa_id, tokens)

    # RN-07: una sola solicitud activa — el índice parcial decide la carrera.
    assert codigos.count(201) == 1
    assert codigos.count(409) == 9

    detalle = client.get(f"/api/v1/mesas/{mesa_id}").json()
    assert detalle["jugadores_actuales"] == 0


def test_solo_un_acepte_gana_la_ultima_vacante(client, token_gm, token_admin):
    mesa_id = crear_mesa(client, token_gm, "Mesa race acepte", jugadores_max=1)

    sol_ids = []
    for i in range(3):
        token = _registrar_y_token(client, "usuario", i)
        sol = client.post(
            f"/api/v1/mesas/{mesa_id}/solicitudes",
            headers={"Authorization": f"Bearer {token}"},
        ).json()
        sol_ids.append(sol["id"])

    def aceptar(sol_id):
        local = TestClient(client.app)
        return local.post(
            f"/api/v1/mesas/{mesa_id}/solicitudes/{sol_id}/aceptar",
            headers={"Authorization": f"Bearer {token_admin}"},
        ).status_code

    with ThreadPoolExecutor(max_workers=3) as ex:
        codigos = list(ex.map(aceptar, sol_ids))

    assert codigos.count(200) == 1
    assert codigos.count(409) == 2

    detalle = client.get(
        f"/api/v1/mesas/{mesa_id}",
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()
    assert detalle["jugadores_actuales"] == 1
    assert detalle["jugadores_actuales"] <= detalle["jugadores_max"]

    # La solicitud perdedora sigue 'pendiente': el rechazo queda a mano del GM.
    bandeja = client.get(
        f"/api/v1/mesas/{mesa_id}/solicitudes",
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()
    assert any(s["estado"] == "pendiente" for s in bandeja)
