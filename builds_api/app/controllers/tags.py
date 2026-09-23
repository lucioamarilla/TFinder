from builds_api.app.db import get_connection


class TagNotFoundError(Exception):
    pass


def listar_tags():
    with get_connection() as conn:
        filas = conn.execute("SELECT nombre FROM tags ORDER BY nombre").fetchall()
    return [fila["nombre"] for fila in filas]