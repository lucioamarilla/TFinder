"""Matchmaking: una mesa inexistente debe responder 404, no 500.

Regresion: matchmaking_controller.abrir insertaba en `matchmaking` sin
comprobar que la mesa existiera. El INSERT disparaba un ForeignKeyViolation
que ningun manejador capturas, y el endpoint terminaba en el handler generico
de 500 ("Error interno del servidor") en lugar del 404 con el envelope
estandar {"error": {"codigo": 404, ...}}.
"""

import pytest

from fastapi.testclient import TestClient

from mesas_api.main import app

pytestmark = pytest.mark.integration

MESA_INEXISTENTE = 99999


def test_abrir_llamado_de_mesa_inexistente_devuelve_404(client, token_gm):
    r = client.post(
        f"/api/v1/matchmaking/{MESA_INEXISTENTE}/abrir",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r.status_code == 404, f"se esperaba 404, vino {r.status_code}: {r.text}"
    assert r.json() == {
        "error": {"codigo": 404, "mensaje": f"Mesa {MESA_INEXISTENTE} no encontrada"}
    }


def test_no_deja_fila_huerfana_en_matchmaking_para_mesa_inexistente(client, token_gm):
    from mesas_api.app.db import get_connection

    client.post(
        f"/api/v1/matchmaking/{MESA_INEXISTENTE}/abrir",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT count(*) AS n FROM matchmaking WHERE mesa_id = %s",
            (MESA_INEXISTENTE,),
        ).fetchone()
    assert fila["n"] == 0, "un 404 no debe dejar filas huerfanas en matchmaking"


def test_mesa_existente_sigue_abriendo_200(client, token_gm):
    from tests.conftest import crear_mesa

    mesa_id = crear_mesa(client, token_gm, "Mesa matchmaking ok")
    r = client.post(
        f"/api/v1/matchmaking/{mesa_id}/abrir",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["estado"] == "abierto"
    assert cuerpo["mesa_id"] == mesa_id

    # el TTL vive en el endpoint de estado, no en la respuesta de abrir
    estado = client.get(f"/api/v1/matchmaking/{cuerpo['id']}/estado")
    assert estado.status_code == 200
    assert estado.json()["ttl_restante"] > 0
