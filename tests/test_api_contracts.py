import importlib

import pytest

pytestmark = pytest.mark.unit

SERVICES = ("mesas_api", "builds_api", "feed_api", "notif_api")
EXPECTED_ROUTES = {
    "mesas_api": 18,
    "builds_api": 7,
    "feed_api": 5,
    "notif_api": 9,
}


@pytest.mark.parametrize("servicio", SERVICES)
def test_openapi_declara_rutas_publicas(servicio):
    app = importlib.import_module(f"{servicio}.main").app
    esquema = app.openapi()
    rutas = [ruta for ruta in esquema["paths"] if not ruta.startswith("/openapi")]
    assert len(rutas) >= 4
    assert esquema["info"]["title"]


@pytest.mark.parametrize("servicio,minimo", EXPECTED_ROUTES.items())
def test_conteo_de_rutas_contratado(servicio, minimo):
    app = importlib.import_module(f"{servicio}.main").app
    assert len([ruta for ruta in app.openapi()["paths"]]) >= minimo
