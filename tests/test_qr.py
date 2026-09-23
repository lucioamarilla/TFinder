"""QR de asistencia single-use (B07): segunda validación rechazada con 409."""

from tests.conftest import crear_mesa, crear_sesion


def test_qr_no_es_reutilizable(client, token_gm, token_jugador):
    mesa_id = crear_mesa(client, token_gm, "Mesa qr", jugadores_max=4)
    sesion_id = crear_sesion(mesa_id)

    jugador_id = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token_jugador}"},
    ).json()["sub"]

    emitido = client.post(
        f"/api/v1/sesiones/{sesion_id}/qr",
        headers={"Authorization": f"Bearer {token_jugador}"},
    )
    assert emitido.status_code == 201
    qr_data = emitido.json()["qr_data"]
    assert qr_data != ""

    valida = {"usuario_id": jugador_id, "qr_data": qr_data}
    primera = client.post(
        f"/api/v1/sesiones/{sesion_id}/qr/validar",
        json=valida,
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert primera.status_code == 200

    segunda = client.post(
        f"/api/v1/sesiones/{sesion_id}/qr/validar",
        json=valida,
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert segunda.status_code == 409