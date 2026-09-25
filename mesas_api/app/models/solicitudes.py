from mesas_api.app.db import get_connection


def crear_solicitud(mesa_id: int, usuario_id: int, estado: str = "pendiente", idem_key: str = None):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO solicitudes_uniones (mesa_id, usuario_id, estado, idem_key)"
            " VALUES (%s, %s, %s, %s) RETURNING *",
            (mesa_id, usuario_id, estado, idem_key),
        )
        return dict(cursor.fetchone())


def obtener_solicitud_por_key(mesa_id: int, usuario_id: int, idem_key: str):
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT * FROM solicitudes_uniones WHERE mesa_id = %s AND usuario_id = %s"
            " AND idem_key = %s ORDER BY id DESC LIMIT 1",
            (mesa_id, usuario_id, idem_key),
        ).fetchone()
        return dict(fila) if fila else None


def listar_solicitudes(mesa_id: int):
    with get_connection() as conn:
        filas = conn.execute(
            "SELECT * FROM solicitudes_uniones WHERE mesa_id = %s ORDER BY id DESC",
            (mesa_id,),
        ).fetchall()
        return [dict(fila) for fila in filas]