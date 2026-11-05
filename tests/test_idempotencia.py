"""Idempotencia por Idempotency-Key (B05/B06): misma petición → mismo resultado."""

import pytest

from tests.conftest import crear_mesa

pytestmark = pytest.mark.integration


def test_misma_key_no_duplica_solicitud_ni_vacante(client, token_gm, token_jugador):
    mesa_id = crear_mesa(client, token_gm, "Mesa idem", jugadores_max=1)

    base = {
        "Idempotency-Key": "clave-repetida-1",
        "Authorization": f"Bearer {token_jugador}",
    }
    primera = client.post(f"/api/v1/mesas/{mesa_id}/solicitudes", headers=base)
    segunda = client.post(f"/api/v1/mesas/{mesa_id}/solicitudes", headers=base)

    assert primera.status_code == segunda.status_code == 201
    assert primera.json() == segunda.json()
    assert primera.json()["estado"] == "pendiente"

    fila = client.get(
        f"/api/v1/mesas/{mesa_id}",
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()
    # P0.4: la solicitud nace pendiente; ocupa vacante el ACEPTAR (RF-15).
    assert fila["jugadores_actuales"] == 0