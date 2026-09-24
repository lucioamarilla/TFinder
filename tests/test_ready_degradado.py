"""ready/live (#34): /ready devuelve listo cuando todo OK y degradado si una dependencia falla."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Los 4 servicios importan evaluar_ready desde el modulo compartido app.infra.ready.
MODULOS = [
    "mesas_api.main",
    "builds_api.main",
    "feed_api.main",
    "notif_api.main",
]


def _app_por_modulo(modulo):
    import importlib

    return importlib.import_module(modulo).app


@pytest.mark.parametrize("modulo", MODULOS)
def test_ready_listo(modulo):
    app = _app_por_modulo(modulo)
    with patch("app.infra.ready.get_redis") as redis_mock, \
         patch("app.infra.ready.pika") as pika_mock, \
         patch("app.infra.ready._check_db", return_value=True):
        redis_mock.return_value.ping.return_value = True
        conn_mock = pika_mock.BlockingConnection.return_value
        client = TestClient(app)
        r = client.get("/ready")
    assert r.status_code == 200
    body = r.json()
    assert body["estado"] == "listo"
    assert body["dependencias"] == {
        "postgres": True,
        "redis": True,
        "rabbitmq": True,
    }


@pytest.mark.parametrize("modulo", MODULOS)
@pytest.mark.parametrize("dep", ["redis", "rabbitmq", "postgres"])
def test_ready_degradado(modulo, dep):
    app = _app_por_modulo(modulo)
    with patch("app.infra.ready.get_redis") as redis_mock, \
         patch("app.infra.ready.pika") as pika_mock, \
         patch("app.infra.ready._check_db", return_value=True):
        if dep == "redis":
            redis_mock.return_value.ping.side_effect = Exception("redis caido")
            conn_mock = pika_mock.BlockingConnection.return_value
        elif dep == "rabbitmq":
            redis_mock.return_value.ping.return_value = True
            pika_mock.BlockingConnection.side_effect = Exception("rabbit caido")
        else:  # postgres
            redis_mock.return_value.ping.return_value = True
            conn_mock = pika_mock.BlockingConnection.return_value
            with patch("app.infra.ready._check_db", return_value=False):
                client = TestClient(app)
                r = client.get("/ready")
            assert r.status_code == 503
            assert r.json()["estado"] == "degradado"
            assert r.json()["dependencias"][dep] is False
            return
        client = TestClient(app)
        r = client.get("/ready")
    assert r.status_code == 503
    body = r.json()
    assert body["estado"] == "degradado"
    assert body["dependencias"][dep] is False