import os

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

DEFAULT_DATABASE_URL = "postgresql://tfinder:tfinder@localhost:5432/feed_db"

_pool = None
_abierto = False


def get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            os.getenv("FEED_DATABASE_URL", DEFAULT_DATABASE_URL),
            min_size=1,
            max_size=5,
            open=False,
            kwargs={"row_factory": dict_row},
        )
    return _pool


def abrir_pool():
    global _abierto
    pool = get_pool()
    if not _abierto:
        pool.open()
        _abierto = True


def cerrar_pool():
    global _abierto
    if _abierto:
        get_pool().close()
        _abierto = False


def get_connection():
    return get_pool().connection()