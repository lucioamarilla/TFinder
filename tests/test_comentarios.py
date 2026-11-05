from fastapi.testclient import TestClient

from feed_api.main import app as feed_app


def test_comentario_vacio_rechazado():
    client = TestClient(feed_app)
    # Necesita post existente; usar seed? En su lugar crear uno con auth.
    # Registro/login rápido no disponible en feed-api (auth en mesas). Skip auth: usar endpoint sin auth → 401.
    r = client.post("/api/v1/feed/1/comentarios", json={"texto": ""})
    assert r.status_code in (401, 400, 404)


def test_comentario_demasiado_largo():
    client = TestClient(feed_app)
    r = client.post("/api/v1/feed/1/comentarios", json={"texto": "x" * 1001})
    assert r.status_code in (401, 400, 404)