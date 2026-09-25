import os

import redis


def get_redis() -> redis.Redis:
    """Devuelve el cliente Redis configurado por REDIS_URL.

    Default local alineado con docker-compose.yml (redis host publicado en 6390).
    """
    url = os.getenv("REDIS_URL", "redis://localhost:6390/0")
    return redis.from_url(
        url,
        socket_connect_timeout=2.0,
        socket_timeout=2.0,
        socket_keepalive=True,
    )