from datetime import datetime

from mesas_api.app.db import get_connection


def crear_o_reabrir(mesa_id: int, estado: str = "llamada_abierta") -> dict:
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT * FROM matchmaking WHERE mesa_id = %s", (mesa_id,)
        ).fetchone()
        if fila is None:
            cursor = conn.execute(
                "INSERT INTO matchmaking (mesa_id, estado, llamada_abierta_at)"
                " VALUES (%s, %s, now()) RETURNING id",
                (mesa_id, estado),
            )
            mm_id = cursor.fetchone()["id"]
        else:
            cursor = conn.execute(
                "UPDATE matchmaking SET estado = %s, llamada_abierta_at = now()"
                " WHERE id = %s RETURNING id",
                (estado, fila["id"]),
            )
            mm_id = cursor.fetchone()["id"]
        fila = conn.execute("SELECT * FROM matchmaking WHERE id = %s", (mm_id,)).fetchone()
        return dict(fila)


def ultimo_matchmaking(mesa_id: int):
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT * FROM matchmaking WHERE mesa_id = %s ORDER BY id DESC LIMIT 1",
            (mesa_id,),
        ).fetchone()
        return dict(fila) if fila else None


def _iso(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj