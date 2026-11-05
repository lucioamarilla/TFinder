"""Modelo del calendario con votación de fechas (RF-10/RF-11, P1.5)."""

from datetime import datetime, timezone

from mesas_api.app.db import get_connection


class PropuestaPasadaError(Exception):
    """VAL-29: la fecha propuesta no puede estar en el pasado."""


_NDF = "%Y-%m-%dT%H:%M:%S"


def _parsear(when: str) -> datetime:
    texto = str(when).strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(texto)
    except ValueError:
        try:
            return datetime.strptime(texto, _NDF)
        except ValueError:
            raise ValueError("Formato de fecha inválido. Usá ISO 8601.") from None


def es_miembro_jugador(mesa_id: int, usuario_id: int) -> bool:
    """El votante debe ser miembro aceptado de la mesa (VAL-31)."""
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT 1 FROM solicitudes_uniones WHERE mesa_id = %s AND usuario_id = %s"
            " AND estado = 'aceptada'",
            (mesa_id, usuario_id),
        ).fetchone()
        return fila is not None


def proponer_fecha(mesa_id: int, propuesta: str, propuesto_por: int):
    when = _parsear(propuesta)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    if when <= datetime.now(timezone.utc):
        raise PropuestaPasadaError("La fecha propuesta no puede ser en el pasado.")
    with get_connection() as conn:
        fila = conn.execute(
            "INSERT INTO fechas_propuestas (mesa_id, propuesta, propuesto_por)"
            " VALUES (%s, %s, %s) RETURNING id, mesa_id, propuesta, estado, propuesto_por",
            (mesa_id, when, propuesto_por),
        ).fetchone()
        return dict(fila)


def listar_fechas(mesa_id: int):
    with get_connection() as conn:
        filas = conn.execute(
            """
            SELECT f.id, f.mesa_id, f.propuesta, f.estado, f.propuesto_por,
                   COALESCE(SUM(CASE WHEN v.valor = 'a_favor' THEN 1 ELSE 0 END), 0) AS a_favor,
                   COALESCE(SUM(CASE WHEN v.valor = 'en_contra' THEN 1 ELSE 0 END), 0) AS en_contra
            FROM fechas_propuestas f
            LEFT JOIN votos_fechas v ON v.propuesta_id = f.id
            WHERE f.mesa_id = %s
            GROUP BY f.id
            ORDER BY f.propuesta
            """,
            (mesa_id,),
        ).fetchall()
        return [dict(f) for f in filas]


def obtener_fecha(mesa_id: int, fecha_id: int):
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT * FROM fechas_propuestas WHERE mesa_id = %s AND id = %s",
            (mesa_id, fecha_id),
        ).fetchone()
        return dict(fila) if fila else None


def votar_fecha(propuesta_id: int, usuario_id: int, valor: str):
    """RN-06: un voto editable por usuario y propuesta (upsert)."""
    with get_connection() as conn, conn.transaction():
        fila = conn.execute(
            "INSERT INTO votos_fechas (propuesta_id, usuario_id, valor)"
            " VALUES (%s, %s, %s)"
            " ON CONFLICT (propuesta_id, usuario_id)"
            " DO UPDATE SET valor = EXCLUDED.valor"
            " RETURNING propuesta_id, usuario_id, valor",
            (propuesta_id, usuario_id, valor),
        ).fetchone()
        return dict(fila)


def descartar_fecha(propuesta_id: int):
    with get_connection() as conn, conn.transaction():
        cursor = conn.execute(
            "UPDATE fechas_propuestas SET estado = 'descartada'"
            " WHERE id = %s AND estado = 'propuesta' RETURNING id",
            (propuesta_id,),
        )
        return cursor.fetchone() is not None


def confirmar_fecha(propuesta_id: int, mesa_id: int):
    """CA: confirmar la fecha ganadora nace una sesión de juego."""
    with get_connection() as conn, conn.transaction():
        fila = conn.execute(
            "UPDATE fechas_propuestas SET estado = 'confirmada', confirmada_at = now()"
            " WHERE id = %s AND mesa_id = %s AND estado = 'propuesta' RETURNING *",
            (propuesta_id, mesa_id),
        ).fetchone()
        if fila is None:
            return None
        sesion = conn.execute(
            "INSERT INTO sesiones (mesa_id, fecha) VALUES (%s, %s)"
            " RETURNING id, mesa_id, fecha, estado",
            (mesa_id, fila["propuesta"]),
        ).fetchone()
    return {"propuesta": dict(fila), "sesion": dict(sesion)}
