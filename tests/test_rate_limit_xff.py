"""Auditoría de navegación · el cupo del rate limit es del CLIENTE REAL.

ANTES: la ventana RNF-22 usaba request.client.host. Detrás del proxy nginx del
despliegue esa dirección es SIEMPRE la IP del frontend: todos los usuarios
compartían un único cubo de 100/min y la navegación normal de 2-3 personas
generaba 429 que la UI mostraba como "No encontramos la mesa"/"vacío".

DESPUES: se respeta X-Forwarded-For (nginx ya lo firma); cada cliente real
tiene su propio cupo y la 429 viaja con Retry-After, el estándar para no
reintentar a ciegas. La cifra RNF-22 (100/min) no se cambia.

Nota: el autouse estado_limpio (integration) hace flushdb entre tests, por lo
que cada ejemplo arranca con el bucket vacío.
"""

import pytest

import mesas_api.main as mesas_main

pytestmark = pytest.mark.integration


@pytest.fixture
def limitera_baja():
    mesas_main.app.state.rate_limit_min = 3
    yield
    mesas_main.app.state.rate_limit_min = 100


def test_cada_cliente_conserva_su_propio_cupo(client, limitera_baja):
    ff_a = "203.0.113.10"
    ff_b = "203.0.113.99"
    for _ in range(3):
        r = client.get("/api/v1/mesas", headers={"X-Forwarded-For": ff_a})
        assert r.status_code == 200, f"primera racha de A: {r.status_code}"
    assert client.get("/api/v1/mesas", headers={"X-Forwarded-For": ff_a}).status_code == 429, \
        "A agota SU cupo"
    r_b = client.get("/api/v1/mesas", headers={"X-Forwarded-For": ff_b})
    assert r_b.status_code == 200, "B nunca comparte el cubo de A"


def test_xff_usa_el_primer_salto_de_la_cadena(client, limitera_baja):
    ff = "203.0.113.44"
    for _ in range(3):
        r = client.get("/api/v1/mesas", headers={"X-Forwarded-For": f"{ff}, 10.0.0.9"})
        assert r.status_code == 200
    r = client.get("/api/v1/mesas", headers={"X-Forwarded-For": f"{ff}, 10.0.0.9"})
    assert r.status_code == 429, "la cadena XFF usa el primer salto como cliente"


def test_la_429_lleva_retry_after(client, limitera_baja):
    ff = "203.0.113.77"
    for _ in range(4):
        r = client.get("/api/v1/mesas", headers={"X-Forwarded-For": ff})
    assert r.status_code == 429
    assert r.headers.get("Retry-After"), "la 429 debe viajar con Retry-After"
