"""Caché con invalidación (B02): 1ª llamada a PostgreSQL, 2ª servida de Redis."""

from unittest.mock import patch

from tests.conftest import crear_mesa


def test_listado_usa_db_solo_en_miss_y_write_invalida(client, token_gm):
    crear_mesa(client, token_gm, "Mesa cache A")
    llamadas = []

    def contador(*args, **kwargs):
        llamadas.append(1)
        from mesas_api.app.models.mesa import listar_mesas

        return listar_mesas(*args, **kwargs)

    with patch(
        "mesas_api.app.controllers.mesas.listar_mesas", side_effect=contador
    ) as spy:
        primer_get = client.get("/api/v1/mesas")
        assert primer_get.status_code == 200
        assert len(llamadas) == 1

        segundo_get = client.get("/api/v1/mesas")
        assert segundo_get.status_code == 200
        assert len(llamadas) == 1

        crear_mesa(client, token_gm, "Mesa cache B")
        tercer_get = client.get("/api/v1/mesas")
        assert tercer_get.status_code == 200
        assert len(llamadas) == 2

    assert [m["nombre"] for m in tercer_get.json()] == [
        "Mesa cache A",
        "Mesa cache B",
    ]