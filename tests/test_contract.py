"""C2 · Contract tests FE↔BE: valida la forma de las responses contra el contrato documentado."""
import pytest

from fastapi.testclient import TestClient

from mesas_api.main import app as mesas_app


@pytest.fixture
def mesas_client():
    return TestClient(mesas_app)


def test_contrato_mesa_listado(mesas_client):
    r = mesas_client.get("/api/v1/mesas")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        m = data[0]
        for campo in ("id", "nombre", "sistema", "estado", "jugadores_max", "jugadores_actuales"):
            assert campo in m, f"falta campo {campo} en Mesa"


def test_contrato_error_envelope(mesas_client):
    r = mesas_client.get("/api/v1/mesas/999999")
    assert r.status_code in (404, 401)
    if r.status_code == 404:
        body = r.json()
        assert "error" in body
        assert "codigo" in body["error"]
        assert "mensaje" in body["error"]