"""Smoke tests del backend TFinder (estructura reorganizada)."""

from fastapi.testclient import TestClient

from app.main import app


def test_mesas_vacio_200():
    with TestClient(app) as client:
        resp = client.get("/api/v1/mesas")
        assert resp.status_code == 200
        assert resp.json() == []


def test_mesa_no_encontrada_404():
    with TestClient(app) as client:
        resp = client.get("/api/v1/mesas/99999")
        assert resp.status_code == 404
        body = resp.json()
        assert body["error"]["codigo"] == 404
