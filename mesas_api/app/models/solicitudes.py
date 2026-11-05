from mesas_api.app.db import get_connection


class CupoAgotadoError(Exception):
    """El UPDATE de mesa no ganó ninguna vacante: no hay cupo disponible."""


class SolicitudNoProcesableError(Exception):
    """La solicitud ya no está 'pendiente': fue aceptada o rechazada."""


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
            """
            SELECT s.*, u.nombre AS nombre, u.email AS email
            FROM solicitudes_uniones s
            LEFT JOIN usuarios u ON u.id = s.usuario_id
            WHERE s.mesa_id = %s ORDER BY s.id DESC
            """,
            (mesa_id,),
        ).fetchall()
        return [dict(fila) for fila in filas]


def listar_solicitudes_con_estado(mesa_id: int, estado=None):
    with get_connection() as conn:
        if estado:
            filas = conn.execute(
                """
                SELECT s.*, u.nombre AS nombre, u.email AS email
                FROM solicitudes_uniones s
                LEFT JOIN usuarios u ON u.id = s.usuario_id
                WHERE s.mesa_id = %s AND s.estado = %s ORDER BY s.id DESC
                """,
                (mesa_id, estado),
            ).fetchall()
        else:
            filas = listar_solicitudes(mesa_id)
        return [dict(fila) for fila in filas]


def obtener_solicitud(mesa_id: int, solicitud_id: int):
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT * FROM solicitudes_uniones WHERE mesa_id = %s AND id = %s",
            (mesa_id, solicitud_id),
        ).fetchone()
        return dict(fila) if fila else None


def existe_solicitud_pendiente(mesa_id: int, usuario_id: int) -> bool:
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT 1 FROM solicitudes_uniones WHERE mesa_id = %s AND usuario_id = %s"
            " AND estado = 'pendiente'",
            (mesa_id, usuario_id),
        ).fetchone()
        return fila is not None


def aceptar_solicitud(solicitud_id: int, mesa_id: int):
    """Acepta (RF-15/RN-08) en una sola transacción: estado + cupo + membresía.

    La aceptación consume la última vacante atómicamente: si el UPDATE de mesa
    no gana el cupo, la excepción revierte el estado de la solicitud a
    'pendiente' (postcondición preservada). El aceptado entra a miembros_mesa
    con rol 'jugador' (principio 2.1: roles contextuales por mesa).
    """
    with get_connection() as conn, conn.transaction():
        cursor = conn.execute(
            "UPDATE solicitudes_uniones SET estado = 'aceptada'"
            " WHERE id = %s AND mesa_id = %s AND estado = 'pendiente' RETURNING *",
            (solicitud_id, mesa_id),
        )
        fila = cursor.fetchone()
        if fila is None:
            raise SolicitudNoProcesableError("La solicitud ya ha sido procesada.")
        cursor_mesa = conn.execute(
            "UPDATE mesas SET jugadores_actuales = jugadores_actuales + 1"
            " WHERE id = %s AND (jugadores_max IS NULL OR jugadores_actuales < jugadores_max)"
            " RETURNING id",
            (mesa_id,),
        )
        if cursor_mesa.fetchone() is None:
            raise CupoAgotadoError("Cupo agotado: no quedan vacantes")
        conn.execute(
            "INSERT INTO miembros_mesa (mesa_id, usuario_id, rol)"
            " VALUES (%s, %s, 'jugador') ON CONFLICT (mesa_id, usuario_id) DO NOTHING",
            (mesa_id, fila["usuario_id"]),
        )
        return dict(fila)


def rechazar_solicitud(solicitud_id: int, mesa_id: int):
    with get_connection() as conn, conn.transaction():
        cursor = conn.execute(
            "UPDATE solicitudes_uniones SET estado = 'rechazada'"
            " WHERE id = %s AND mesa_id = %s AND estado = 'pendiente' RETURNING *",
            (solicitud_id, mesa_id),
        )
        fila = cursor.fetchone()
        if fila is None:
            raise SolicitudNoProcesableError("La solicitud ya ha sido procesada.")
        return dict(fila)


def expulsar_miembro(mesa_id: int, usuario_id: int):
    """Elimina la membresía aceptada (y cualquier pendiente viva) y libera cupo.

    Postcondición: se emite mesa.expulsada, no queda solicitud activa del
    usuario en esa mesa, la fila en miembros_mesa desaparece (rol contextual
    perdido) y la vacante vuelve (greatest(...,0)).
    """
    with get_connection() as conn, conn.transaction():
        cursor = conn.execute(
            "DELETE FROM solicitudes_uniones"
            " WHERE mesa_id = %s AND usuario_id = %s AND estado = 'aceptada' RETURNING id",
            (mesa_id, usuario_id),
        )
        hubo = cursor.fetchone() is not None
        conn.execute(
            "DELETE FROM solicitudes_uniones"
            " WHERE mesa_id = %s AND usuario_id = %s AND estado = 'pendiente'",
            (mesa_id, usuario_id),
        )
        conn.execute(
            "DELETE FROM miembros_mesa WHERE mesa_id = %s AND usuario_id = %s AND rol = 'jugador'",
            (mesa_id, usuario_id),
        )
        nuevo_cupo = None
        if hubo:
            fila = conn.execute(
                "UPDATE mesas SET jugadores_actuales = greatest(jugadores_actuales - 1, 0)"
                " WHERE id = %s RETURNING jugadores_actuales",
                (mesa_id,),
            ).fetchone()
            nuevo_cupo = fila["jugadores_actuales"] if fila else None
    return hubo, nuevo_cupo

def salir_de_mesa(mesa_id: int, usuario_id: int):
    """F2: baja voluntaria del JUGADOR (no del master).

    Elimina la membresía 'jugador' (y pendientes vivas), libera el cupo y
    limpia solicitudes. Nunca toca al master: transferencia/eliminación de
    mesa es un flujo aparte (futuro).
    """
    with get_connection() as conn, conn.transaction():
        cursor = conn.execute(
            "DELETE FROM miembros_mesa WHERE mesa_id = %s AND usuario_id = %s AND rol = 'jugador' RETURNING usuario_id",
            (mesa_id, usuario_id),
        )
        hubo = cursor.fetchone() is not None
        conn.execute(
            "DELETE FROM solicitudes_uniones"
            " WHERE mesa_id = %s AND usuario_id = %s AND estado = 'pendiente'",
            (mesa_id, usuario_id),
        )
        nuevo_cupo = None
        if hubo:
            fila = conn.execute(
                "UPDATE mesas SET jugadores_actuales = greatest(jugadores_actuales - 1, 0)"
                " WHERE id = %s RETURNING jugadores_actuales",
                (mesa_id,),
            ).fetchone()
            nuevo_cupo = fila["jugadores_actuales"] if fila else None
    return hubo, nuevo_cupo
