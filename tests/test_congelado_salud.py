"""CONGELADO: /health, /live y /ready de los cuatro servicios.

Estos tests aferran la salida exacta de los endpoints de salud ANTES de
cualquier refactor de infraestructura (fábrica crear_app). El refactor debe
mantener estas respuestas idénticas; si algo cambia, el test explota y se
decide explícitamente si actualizarlo de forma intencional.

Corre contra la infraestructura real (postgres, redis, rabbitmq igual que la
suite de integración).
"""

import pytest
from fastapi.testclient import TestClient

from builds_api.app.db import abrir_pool as abrir_pool_builds
from builds_api.app.init_db import init_db as init_db_builds
from builds_api.main import app as builds_app
from feed_api.app.db import abrir_pool as abrir_pool_feed
from feed_api.app.init_db import init_db as init_db_feed
from feed_api.main import app as feed_app
from mesas_api.app.db import abrir_pool as abrir_pool_mesas
from mesas_api.app.init_db import init_db as init_db_mesas
from mesas_api.main import app as mesas_app
from notif_api.app.db import abrir_pool as abrir_pool_notif
from notif_api.app.init_db import init_db as init_db_notif
from notif_api.main import app as notif_app

pytestmark = pytest.mark.integration

TITULOS = {
    "mesas-api": ("TFinder · Mesas API", "0.5.0"),
    "builds-api": ("TFinder · Builds API", "0.4.0"),
    "feed-api": ("TFinder · Feed API", "0.3.0"),
    "notif-api": ("TFinder · Notif API", "0.6.0"),
}
APPS = {
    "mesas-api": mesas_app,
    "builds-api": builds_app,
    "feed-api": feed_app,
    "notif-api": notif_app,
}


@pytest.fixture(scope="module", autouse=True)
def _pools():
    """Abre los cuatro pools una vez por modulo y no los cierra (global)."""
    abrir_pool_mesas(), init_db_mesas()
    abrir_pool_builds(), init_db_builds()
    abrir_pool_feed(), init_db_feed()
    abrir_pool_notif(), init_db_notif()
    yield


@pytest.fixture(scope="module")
def clients():
    return {nombre: TestClient(app) for nombre, app in APPS.items()}


def test_live_y_health_exactos(clients):
    for nombre, cliente in clients.items():
        assert cliente.get("/live").json() == {"estado": "vivo"}

        r = cliente.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok", "servicio": nombre}


def test_ready_listo_con_toda_la_infra(clients):
    for nombre, cliente in clients.items():
        r = cliente.get("/ready")
        assert r.status_code == 200
        assert r.json() == {
            "estado": "listo",
            "dependencias": {"postgres": True, "redis": True, "rabbitmq": True},
        }


def test_titulos_y_versiones_openapi_congelados():
    for clave, (titulo, version) in TITULOS.items():
        assert APPS[clave].title == titulo
        assert APPS[clave].version == version
