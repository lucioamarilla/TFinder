import importlib
import json
import pkgutil
from contextlib import nullcontext
from unittest.mock import Mock, patch

import pytest

from app.infra.logge import JsonFormatter, nuevo_correlation_id
from app.infra.ready import evaluar_ready
from mesas_api.app.models.auth_model import hash_password, verificar_password
from mesas_api.app.schemas import MesaCreate, MesaUpdate

pytestmark = pytest.mark.unit

SERVICES = ("mesas_api", "builds_api", "feed_api", "notif_api")


def test_correlation_id_tiene_formato_y_es_unico():
    primero = nuevo_correlation_id()
    segundo = nuevo_correlation_id()
    assert len(primero) == 16
    assert primero != segundo


def test_json_formatter_incluye_campos_observables():
    registro = Mock()
    registro.getMessage.return_value = "mensaje"
    registro.exc_info = None
    registro.name = "tfinder"
    registro.levelname = "INFO"
    registro.levelno = 20
    registro.correlation_id = "-"
    payload = JsonFormatter().format(registro)
    assert "mensaje" in payload
    assert "correlation_id" in payload
    assert "nivel" in payload


def test_password_hash_no_guarda_texto_plano():
    password = "contrasena-segura"
    hashed = hash_password(password)
    assert hashed != password
    assert verificar_password(password, hashed)
    assert not verificar_password("otra", hashed)


@pytest.mark.parametrize("payload", [
    {"nombre": "Mesa", "sistema": "PF1e"},
    {"nombre": "Mesa", "sistema": "PF1e", "jugadores_max": 4},
])
def test_schema_mesa_acepta_datos_validos(payload):
    assert MesaCreate(**payload).nombre == "Mesa"


def test_schema_mesa_rechaza_jugadores_invalidos():
    with pytest.raises(ValueError):
        MesaCreate(nombre="Mesa", sistema="PF1e", jugadores_max=0)


def test_schema_update_permite_campos_parciales():
    assert MesaUpdate(estado="cerrada").model_dump(exclude_none=True) == {
        "estado": "cerrada"
    }


def test_ready_reporta_dependencias():
    with patch("app.infra.ready.get_redis") as redis_mock, \
         patch("app.infra.ready.get_params", return_value=Mock()), \
         patch("app.infra.ready.pika") as pika_mock:
        redis_mock.return_value.ping.return_value = True
        pika_mock.BlockingConnection.return_value.close.return_value = None
        respuesta = evaluar_ready(lambda: nullcontext(Mock()))
    assert respuesta.status_code == 200
    cuerpo = json.loads(respuesta.body)
    assert cuerpo["estado"] == "listo"
    assert cuerpo["dependencias"] == {
        "postgres": True,
        "redis": True,
        "rabbitmq": True,
    }


def test_inventario_de_modulos_publicos_es_importable():
    modulos = []
    for servicio in SERVICES:
        paquete = importlib.import_module(servicio)
        modulos.extend(
            modulo.name
            for modulo in pkgutil.walk_packages(paquete.__path__, paquete.__name__ + ".")
        )
    assert len(modulos) > 30
    for nombre in modulos:
        importlib.import_module(nombre)
