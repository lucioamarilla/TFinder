from mesas_api.app.db import get_connection


def obtener_sesion(sesion_id):
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT * FROM sesiones WHERE id = %s", (sesion_id,)
        ).fetchone()
        return dict(fila) if fila else None


def registrar_asistencia(sesion_id: int, usuario_id: int) -> bool:
    """Idempotente: unique (sesion_id, usuario_id) evita duplicar asistencia."""
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO asistencias (sesion_id, usuario_id) VALUES (%s, %s)"
            " ON CONFLICT (sesion_id, usuario_id) DO NOTHING"
            " RETURNING id",
            (sesion_id, usuario_id),
        )
        return cursor.fetchone() is not None