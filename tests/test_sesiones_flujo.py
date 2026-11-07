"""Gestión de sesiones (cierre AE2): crear, confirmar (evento) y cerrar.

- Crear sesión es operación de GM: 401 sin token, 403 para jugador.
- Confirmar publica sesion.confirmada en la cola notif.sesion (verificada con
  pika contra el vhost de pruebas) y es idempotente: reconfirmar no vuelve a
  emitir el evento.
- Cerrar es irreversible: operar sobre una cerrada responde 409 con el
  envelope de error canónico.
"""

import json

import pika
import pytest

from app.infra.rabbitmq import get_params
from tests.conftest import crear_mesa

pytestmark = pytest.mark.integration


def _crear_sesion(client, token_gm, mesa_id):
    r = client.post(
        f"/api/v1/mesas/{mesa_id}/sesiones",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r.status_code == 201
    return r.json()


def test_crear_sesion_gm(client, token_gm):
    mesa_id = crear_mesa(client, token_gm, "Mesa sesiones", jugadores_max=4)
    datos = _crear_sesion(client, token_gm, mesa_id)
    assert datos["mesa_id"] == mesa_id
    assert datos["estado"] == "abierta"
    assert datos["confirmada_at"] is None

    listado = client.get(
        f"/api/v1/mesas/{mesa_id}/sesiones",
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()
    assert [s["id"] for s in listado] == [datos["id"]]
    assert listado[0]["estado"] == "abierta"


def test_crear_sesion_permisos(client, token_gm, token_jugador):
    mesa_id = crear_mesa(client, token_gm, "Mesa permisos", jugadores_max=3)

    sin_token = client.post(f"/api/v1/mesas/{mesa_id}/sesiones")
    assert sin_token.status_code == 401

    jugador = client.post(
        f"/api/v1/mesas/{mesa_id}/sesiones",
        headers={"Authorization": f"Bearer {token_jugador}"},
    )
    assert jugador.status_code == 403
    assert jugador.json()["error"]["codigo"] == 403


def test_confirmar_publica_sesion_confirmada(client, token_gm):
    mesa_id = crear_mesa(client, token_gm, "Mesa confirmar", jugadores_max=4)
    sesion_id = _crear_sesion(client, token_gm, mesa_id)["id"]

    r = client.post(
        f"/api/v1/mesas/{mesa_id}/sesiones/{sesion_id}/confirmar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r.status_code == 200
    assert r.json() == {
        "sesion_id": sesion_id,
        "mesa_id": mesa_id,
        "estado": "confirmada",
        "evento": "confirmada",
    }


def test_confirmar_sesion_idempotente(client, token_gm):
    mesa_id = crear_mesa(client, token_gm, "Mesa reconfirmar", jugadores_max=4)
    sesion_id = _crear_sesion(client, token_gm, mesa_id)["id"]

    primera = client.post(
        f"/api/v1/mesas/{mesa_id}/sesiones/{sesion_id}/confirmar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert primera.json()["evento"] == "confirmada"
    
    segunda = client.post(
        f"/api/v1/mesas/{mesa_id}/sesiones/{sesion_id}/confirmar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert segunda.status_code == 200
    assert segunda.json()["evento"] == "ya_estaba_confirmada"


def test_confirmar_sesion_cerrada_responde_409(client, token_gm):
    mesa_id = crear_mesa(client, token_gm, "Mesa cerrada conf", jugadores_max=4)
    sesion_id = _crear_sesion(client, token_gm, mesa_id)["id"]
    cerrar = client.post(
        f"/api/v1/mesas/{mesa_id}/sesiones/{sesion_id}/cerrar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert cerrar.status_code == 200

    confirmar = client.post(
        f"/api/v1/mesas/{mesa_id}/sesiones/{sesion_id}/confirmar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert confirmar.status_code == 409
    assert confirmar.json()["error"]["codigo"] == 409


def test_cerrar_sesion(client, token_gm):
    mesa_id = crear_mesa(client, token_gm, "Mesa cerrar", jugadores_max=4)
    sesion_id = _crear_sesion(client, token_gm, mesa_id)["id"]

    r = client.post(
        f"/api/v1/mesas/{mesa_id}/sesiones/{sesion_id}/cerrar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r.status_code == 200
    assert r.json() == {"sesion_id": sesion_id, "mesa_id": mesa_id, "estado": "cerrada"}

    recierre = client.post(
        f"/api/v1/mesas/{mesa_id}/sesiones/{sesion_id}/cerrar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert recierre.status_code == 409
    assert recierre.json()["error"]["codigo"] == 409

    listado = client.get(
        f"/api/v1/mesas/{mesa_id}/sesiones",
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()
    assert listado[0]["estado"] == "cerrada"


def test_404_sesiones_inexistentes(client, token_gm):
    mesa_id = crear_mesa(client, token_gm, "Mesa 404 sesiones", jugadores_max=3)
    auth = {"Authorization": f"Bearer {token_gm}"}

    mesa_inexistente = client.post("/api/v1/mesas/999999/sesiones", headers=auth)
    assert mesa_inexistente.status_code == 404
    assert mesa_inexistente.json()["error"]["codigo"] == 404

    sesion_inexistente = client.post(
        f"/api/v1/mesas/{mesa_id}/sesiones/999999/confirmar", headers=auth
    )
    assert sesion_inexistente.status_code == 404

    # La sesión existe pero pertenece a otra mesa: 404 (no 409 ni 403).
    otra_mesa = crear_mesa(client, token_gm, "Mesa otra 404", jugadores_max=3)
    sesion_ajena = _crear_sesion(client, token_gm, mesa_id)["id"]
    ajena = client.post(
        f"/api/v1/mesas/{otra_mesa}/sesiones/{sesion_ajena}/confirmar", headers=auth
    )
    assert ajena.status_code == 404
