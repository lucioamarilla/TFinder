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


def listar_miembros(mesa_id: int):
    """Jugadores con solicitud aceptada en la mesa (contrato REST para notif-api)."""
    with get_connection() as conn:
        filas = conn.execute(
            "SELECT u.id, u.nombre, u.email FROM usuarios u"
            " JOIN solicitudes_uniones s ON s.usuario_id = u.id"
            " WHERE s.mesa_id = %s AND s.estado = 'aceptada'"
            " ORDER BY u.nombre",
            (mesa_id,),
        ).fetchall()
    return [dict(f) for f in filas]