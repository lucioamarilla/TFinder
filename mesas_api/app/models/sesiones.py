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
    """Miembros de la mesa (F2: desde miembros_mesa con rol contextual).

    Contrato REST para notif-api (emails de sesión) y para la bandeja/FE.
    """
    with get_connection() as conn:
        filas = conn.execute(
            "SELECT u.id, u.nombre, u.email, m.rol"
            " FROM miembros_mesa m"
            " JOIN usuarios u ON u.id = m.usuario_id"
            " WHERE m.mesa_id = %s"
            " ORDER BY (m.rol = 'master') DESC, u.nombre",
            (mesa_id,),
        ).fetchall()
    return [dict(f) for f in filas]


# ---- Gestión de sesiones (cierre AE2) ---------------------------------------

_CAMPOS_SESION = "id, mesa_id, fecha, estado, confirmada_at"


def crear_sesion_db(mesa_id: int) -> dict:
    with get_connection() as conn:
        fila = conn.execute(
            "INSERT INTO sesiones (mesa_id) VALUES (%s)"
            f" RETURNING {_CAMPOS_SESION}",
            (mesa_id,),
        ).fetchone()
    return dict(fila)


def listar_sesiones_db(mesa_id: int) -> list[dict]:
    with get_connection() as conn:
        filas = conn.execute(
            f"SELECT {_CAMPOS_SESION}"
            " FROM sesiones WHERE mesa_id = %s"
            " ORDER BY id DESC",
            (mesa_id,),
        ).fetchall()
    return [dict(f) for f in filas]


def obtener_sesion_de_mesa(sesion_id: int, mesa_id: int) -> dict | None:
    """La sesión debe existir Y pertenecer a esa mesa; si no, None -> 404."""
    with get_connection() as conn:
        fila = conn.execute(
            f"SELECT {_CAMPOS_SESION}"
            " FROM sesiones WHERE id = %s AND mesa_id = %s",
            (sesion_id, mesa_id),
        ).fetchone()
    return dict(fila) if fila else None


def confirmar_sesion_db(sesion_id: int) -> bool:
    """Fija confirmada_at una única vez. False si ya estaba confirmada."""
    with get_connection() as conn:
        filas = conn.execute(
            "UPDATE sesiones SET confirmada_at = now()"
            " WHERE id = %s AND confirmada_at IS NULL AND estado = 'abierta'"
            " RETURNING confirmada_at",
            (sesion_id,),
        ).fetchall()
    return bool(filas)


def cerrar_sesion_db(sesion_id: int) -> dict | None:
    """Cierra la sesión abierta. None si ya estaba cerrada (carrera)."""
    with get_connection() as conn:
        fila = conn.execute(
            "UPDATE sesiones SET estado = 'cerrada' WHERE id = %s"
            " AND estado = 'abierta'"
            f" RETURNING {_CAMPOS_SESION}",
            (sesion_id,),
        ).fetchone()
    return dict(fila) if fila else None