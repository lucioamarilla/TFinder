from unittest.mock import patch

from builds_api.app.consumers import mesa as builds_mesa


def test_procesar_mesa_eliminada_ok():
    with patch("builds_api.app.consumers.mesa.desvincular_builds_de_mesa") as dv:
        msg = {"event_id": "e1", "tipo": "mesa.eliminada", "mesa_id": 5, "correlation_id": "-"}
        assert builds_mesa._procesar(msg) is True
        dv.assert_called_once_with(5)


def test_procesar_tipo_invalido():
    msg = {"event_id": "e2", "tipo": "otro", "mesa_id": 5}
    assert builds_mesa._procesar(msg) is False


def test_procesar_sin_mesa_id():
    msg = {"event_id": "e3", "tipo": "mesa.eliminada", "mesa_id": None}
    assert builds_mesa._procesar(msg) is False