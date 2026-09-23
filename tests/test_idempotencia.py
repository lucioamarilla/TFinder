"""Idempotencia por Idempotency-Key (B05/B06): misma petición → mismo resultado."""

from tests.conftest import crear_mesa


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

    fila = client.get(
        f"/api/v1/mesas/{mesa_id}",
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()
    assert fila["jugadores_actuales"] == 1