import importlib
import inspect

import pytest
from pydantic import BaseModel

pytestmark = pytest.mark.unit

MODULOS = (
    "mesas_api.app.schemas",
    "builds_api.app.schemas",
    "feed_api.app.schemas",
    "notif_api.app.schemas",
)


@pytest.mark.parametrize("nombre", MODULOS)
def test_schemas_expuestos_generan_json_schema(nombre):
    modulo = importlib.import_module(nombre)
    schemas = []
    for _, valor in inspect.getmembers(modulo, inspect.isclass):
        if valor.__module__ == nombre and issubclass(valor, BaseModel):
            schemas.append(valor)
    assert schemas
    for schema in schemas:
        documento = schema.model_json_schema()
        assert documento["type"] == "object"
        assert documento["properties"]
