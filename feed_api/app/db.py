"""Pool del servicio feed-api: dueño de feed_db (RNF-04/B02)."""

from app.infra.pg import PoolPropio

_url = "postgresql://tfinder:tfinder@localhost:5432/feed_db"

_pool = PoolPropio("FEED_DATABASE_URL", _url)

abrir_pool = _pool.abrir
cerrar_pool = _pool.cerrar


def get_pool():
    return _pool.pool


def get_connection():
    return _pool.conectar()


# La URL de la base vive en este único archivo (dueño de la base).
DEFAULT_DATABASE_URL = _url
