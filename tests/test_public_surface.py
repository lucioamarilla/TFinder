import importlib
import inspect
import pkgutil

import pytest

pytestmark = pytest.mark.unit

SERVICES = ("mesas_api", "builds_api", "feed_api", "notif_api")
MODULOS = (
    "app.infra.logge",
    "app.infra.redis",
    "app.infra.rabbitmq",
    "app.infra.ready",
    "app.middleware.log_context",
)


def _modulos_servicio():
    nombres = list(MODULOS)
    for servicio in SERVICES:
        paquete = importlib.import_module(servicio)
        nombres.extend(
            modulo.name
            for modulo in pkgutil.walk_packages(paquete.__path__, paquete.__name__ + ".")
        )
    return sorted(set(nombres))


def test_inventario_python_importa_todos_los_modulos_publicos():
    modulos = _modulos_servicio()
    assert len(modulos) > 40
    for nombre in modulos:
        assert importlib.import_module(nombre) is not None


def test_inventario_python_expone_funciones_publicas():
    modulos = _modulos_servicio()
    publicos = {}
    for nombre in modulos:
        modulo = importlib.import_module(nombre)
        publicos[nombre] = [
            item for item, valor in inspect.getmembers(modulo)
            if not item.startswith("_")
            and (inspect.isfunction(valor) or inspect.isclass(valor))
        ]
    publicos = {nombre: valores for nombre, valores in publicos.items() if valores}
    assert len(publicos) >= 30
    assert sum(len(valores) for valores in publicos.values()) > 100
