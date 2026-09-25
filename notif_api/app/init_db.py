import os

from notif_api.app.db import get_pool


def _leer_ddl():
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
    with open(ruta, encoding="utf-8") as f:
        return f.read()


def init_db():
    ddl = _leer_ddl()
    with get_pool().connection() as conn:
        for sentencia in ddl.split(";"):
            sentencia = sentencia.strip()
            if sentencia:
                conn.execute(sentencia)