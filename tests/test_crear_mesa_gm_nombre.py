"""Ciclo 12 · D-17: la respuesta de crear mesa debe traer gm_nombre.

Antes: crear_mesa.devuelve SELECT * FROM mesas sin el JOIN de usuarios, por lo
que MesaOut salia con gm_nombre=None y el frontend mostraba el GM vacio hasta
recargar. Contrato: igual que listar/obtener (JOIN usuarios.nombre).
"""

import pytest

pytestmark = pytest.mark.integration


def test_crear_mesa_devuelve_gm_nombre(client, token_gm):
    r = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa con GM nombrado", "sistema": "pf1e", "jugadores_max": 4},
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo.get("gm_id"), "la mesa debe registrar quién la creó (RN-02)"
    assert cuerpo.get("gm_nombre"), "crear debe incluir el nombre visible del GM (D-17)"
