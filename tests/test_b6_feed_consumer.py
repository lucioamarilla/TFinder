from unittest.mock import patch

from feed_api.app.consumers import mesa as feed_mesa


def test_procesar_mesa_eliminada_ok():
    with patch("feed_api.app.consumers.mesa.get_connection") as gc:
        conn = gc.return_value.__enter__.return_value
        msg = {"event_id": "e1", "tipo": "mesa.eliminada", "mesa_id": 5, "correlation_id": "-"}
        assert feed_mesa._procesar(msg) is True
        conn.execute.assert_called()


def test_procesar_tipo_invalido():
    msg = {"event_id": "e2", "tipo": "otro", "mesa_id": 5}
    assert feed_mesa._procesar(msg) is False