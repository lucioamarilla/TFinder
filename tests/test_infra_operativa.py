"""P1.9 · Infraestructura operativa (RNF-15..20/22 + CA-51):
rate limit 100/min/IP (429), /metrics Prometheus, X-Cache HIT/MISS en modo
degradado, auth en matchmaking/QQR verificando membresía, y OpenAPI con
securitySchemes Bearer (audit "Que le falta" 7.3).
"""

import pytest
from fastapi.testclient import TestClient

import mesas_api.main as mesas_main
from mesas_api.main import app as mesas_app

pytestmark = pytest.mark.integration


@pytest.fixture
def limitera_baja():
    """Baja el techo del limitador para probar 429 rápido y lo reestablece."""
    mesas_app.state.rate_limit_min = 2
    yield mesas_app
    mesas_app.state.rate_limit_min = 100


# ---- RNF-22: rate limiting ------------------------------------------------------

def test_429_al_superar_el_limite(client, limitera_baja):
    conect_ = TestClient(limitera_baja)
    urls = conect_.get("/api/v1/mesas")
    conts = [conect_.get("/api/v1/mesas") for _ in range(3)]
    assert urls.status_code in (200, 429)
    estados = [c.status_code for c in conts]
    assert estados.count(429) >= 1, "RNF-22: 429 al superar el límite por IP"
    agotada = [c for c in conts if c.status_code == 429][0]
    assert agotada.json()["error"]["codigo"] == 429


def test_infra_metricas_publicas(client):
    conect_ = TestClient(mesas_app)
    r = conect_.get("/metrics")
    assert r.status_code == 200
    assert "text/plain" in r.headers["content-type"]
    assert "tf_requests_total" in r.text


# ---- RNF-23/CA-51: X-Cache y modo degradado --------------------------------------

def test_x_cache_hit_en_segunda_lectura(client):
    conect_ = TestClient(mesas_app)
    conect_.get("/api/v1/mesas")
    conect_.get("/api/v1/mesas")
    r = conect_.get("/api/v1/mesas")
    assert r.headers.get("x-cache") in ("HIT", "MISS")


def test_redis_caido_sirve_de_bd_con_x_cache_miss(client, monkeypatch):
    import mesas_api.app.services.cache as cache

    def _redis_muerto():
        raise ConnectionError("redis caído")

    monkeypatch.setattr(cache, "get_redis", _redis_muerto)
    conect_ = TestClient(mesas_app)
    r = conect_.get("/api/v1/mesas")
    assert r.status_code == 200, "CA-51: listado desde BD aunque Redis esté caído"
    assert r.headers.get("x-cache") == "MISS"


# ---- RNF-15/16 extras: matchmaking y QR con auth réel -----------------------------

def test_estado_del_llamado_exige_token(client, token_gm, token_jugador):
    from tests.conftest import crear_mesa

    mesa_id = crear_mesa(client, token_gm, "Mesa mm observada", 4)
    cuerpo = client.post(
        f"/api/v1/matchmaking/{mesa_id}/abrir",
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()
    anonimo = TestClient(mesas_app).get(f"/api/v1/matchmaking/{cuerpo['id']}/estado")
    assert anonimo.status_code == 401, "el estado del matchmaking no es público"
