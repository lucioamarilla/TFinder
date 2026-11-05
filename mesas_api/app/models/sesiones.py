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


def cambiar_rol_miembro(mesa_id: int, usuario_id: int, nuevo_rol: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE miembros_mesa SET rol = %s WHERE mesa_id = %s AND usuario_id = %s",
            (nuevo_rol, mesa_id, usuario_id),
        )


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

# ---- F3: bitácora (anotaciones cronológicas) ---------------------------------

_ANOTACIONES_SELECT = """
    SELECT a.id, a.sesion_id, a.texto, a.creado_en, a.autor_id, u.nombre AS autor_nombre
    FROM anotaciones_sesion a
    JOIN usuarios u ON u.id = a.autor_id
    WHERE a.sesion_id = %s
    ORDER BY a.creado_en ASC, a.id ASC
"""


def agregar_anotacion(sesion_id: int, mesa_id: int, autor_id: int, texto: str):
    with get_connection() as conn, conn.transaction():
        fila = conn.execute(
            "INSERT INTO anotaciones_sesion (sesion_id, mesa_id, autor_id, texto)"
            " VALUES (%s, %s, %s, %s)"
            " RETURNING id, sesion_id, texto, creado_en, autor_id",
            (sesion_id, mesa_id, autor_id, texto),
        ).fetchone()
    return dict(fila)


def listar_anotaciones(sesion_id: int):
    with get_connection() as conn:
        filas = conn.execute(_ANOTACIONES_SELECT, (sesion_id,)).fetchall()
    return [dict(f) for f in filas]
