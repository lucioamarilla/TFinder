"""Fábrica de pool por servicio (B02/RNF-04).

Cada servicio es dueño de una única base `*_db`. Los cuatro `db.py` eran
idénticos entre servicios salvo la URL y el nombre de la variable de entorno;
esta fábrica absorbe la maquinaria (pool con filas dict + ciclo abrir/cerrar
idempotente) y cada servicio solo declara su variable y su default.

La URL de la base sigue viniendo del `db.py` del servicio dueño — es la
consigna del RNF-04 y la vigila `tests/test_congelado_estructura.py`.
"""

import os

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


class PoolPropio:
    """Pool de la base dueña de un servicio, con ciclo abrir/cerrar idempotente."""

    def __init__(self, variable: str, url_default: str):
        self._variable = variable
        self._url_default = url_default
        self._pool = None
        self._abierto = False

    def _construir(self) -> ConnectionPool:
        if self._pool is None:
            self._pool = ConnectionPool(
                os.getenv(self._variable, self._url_default),
                min_size=1,
                max_size=5,
                open=False,
                kwargs={"row_factory": dict_row},
            )
        return self._pool

    @property
    def pool(self) -> ConnectionPool:
        return self._construir()

    def abrir(self):
        # Abre (o REABRE): psycopg_pool no permite reusar un pool abierto y
        # cerrado, así que si quedó cerrado (p. ej. el shutdown de un TestClient
        # o de un servidor de prueba) se reconstruye uno nuevo sobre el mismo
        # env-var. El ciclo sigue idempotente y seguro para reuso.
        cerrado_previamente = self._abierto and self._pool is not None and self._pool._closed
        if not self._abierto or cerrado_previamente:
            pool = ConnectionPool(
                os.getenv(self._variable, self._url_default),
                min_size=1,
                max_size=5,
                open=False,
                kwargs={"row_factory": dict_row},
            )
            pool.open()
            self._pool = pool
            self._abierto = True

    def cerrar(self):
        if self._abierto:
            self._pool.close()
            self._abierto = False

    def conectar(self):
        """Proxy de conexión para `with` (igual que pool.connection())."""
        return self._construir().connection()
