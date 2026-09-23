import json

from app.infra.redis import get_redis

CACHE_MESAS_TTL = 60
PREFIJO = "cache:mesas:list"


def obtener_listado_cachead():
    r = get_redis()
    data = r.get(PREFIJO)
    if data is not None:
        return json.loads(data)
    return None


def guardar_listado(lista: list):
    r = get_redis()
    r.setex(PREFIJO, CACHE_MESAS_TTL, json.dumps(lista, ensure_ascii=False))


def invalidar_listado():
    get_redis().delete(PREFIJO)