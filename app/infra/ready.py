import pika
from fastapi.responses import JSONResponse

from app.infra.rabbitmq import get_params
from app.infra.redis import get_redis


def _check_db(conectarse_db):
    try:
        with conectarse_db() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False


def evaluar_ready(conectarse_db) -> JSONResponse:
    """Chequea PostgreSQL (pool propio), Redis y RabbitMQ.

    'conectarse_db' es una callable del servicio que devuelve una conexión
    de su pool (el dueño de su propia *_db, B02).
    """
    dependencias = {
        "postgres": _check_db(conectarse_db),
        "redis": False,
        "rabbitmq": False,
    }
    try:
        dependencias["redis"] = bool(get_redis().ping())
    except Exception:
        dependencias["redis"] = False
    try:
        conn = pika.BlockingConnection(get_params())
        conn.close()
        dependencias["rabbitmq"] = True
    except Exception:
        dependencias["rabbitmq"] = False

    listo = all(dependencias.values())
    return JSONResponse(
        status_code=200 if listo else 503,
        content={
            "estado": "listo" if listo else "degradado",
            "dependencias": dependencias,
        },
    )