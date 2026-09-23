import json
from datetime import date, datetime

from app.infra.redis import get_redis

PREFIJO = "idem:solicitud:"
TTL = 86400


def _serializar(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Tipo no serializable: {type(obj).__name__}")


def obtener_resultado(key: str):
    data = get_redis().get(PREFIJO + key)
    return json.loads(data) if data is not None else None


def guardar_resultado(key: str, resultado):
    get_redis().setex(
        PREFIJO + key,
        TTL,
        json.dumps(resultado, ensure_ascii=False, default=_serializar),
    )