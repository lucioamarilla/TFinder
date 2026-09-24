import json
from datetime import datetime

from notif_api.app.db import get_connection


def _json(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def evento_ya_procesado(event_id: str) -> bool:
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT 1 FROM event_log WHERE event_id = %s", (event_id,)
        ).fetchone()
    return fila is not None


def registrar_evento(event_id: str, tipo: str, metadata: dict = None, correlation_id: str = "-"):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO event_log (event_id, entidad_tipo, accion, metadata, correlation_id)"
            " VALUES (%s, %s, %s, %s, %s)",
            (event_id, tipo, "consumido", json.dumps(metadata or {}), correlation_id),
        )


def guardar_notificacion(
    usuario_id: int,
    titulo: str,
    detalle: str = None,
    entidad: str = "mesa",
    enlace: dict = None,
):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO notificaciones (usuario_id, grupo, mensaje, detalle, entidad, enlace)"
            " VALUES (%s, 'mesas', %s, %s, %s, %s)",
            (usuario_id, titulo, detalle, entidad, json.dumps(enlace or {})),
        )


def registro_dlq(cola: str, payload, error: str):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO mensaje_dlq (cola, payload, error) VALUES (%s, %s, %s) RETURNING *",
            (cola, json.dumps(payload, ensure_ascii=False), error),
        )
        return dict(cursor.fetchone())


def reintentar_dlq(id: int):
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT * FROM mensaje_dlq WHERE id = %s", (id,)
        ).fetchone()
        if fila is None:
            return None
        conn.execute("DELETE FROM mensaje_dlq WHERE id = %s", (id,))
    return dict(fila)


def descartar_dlq(id: int):
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM mensaje_dlq WHERE id = %s RETURNING *", (id,)
        )
        fila = cursor.fetchone()
    return dict(fila) if fila else None


def listar_dlq(limite: int = 50):
    with get_connection() as conn:
        filas = conn.execute(
            "SELECT * FROM mensaje_dlq ORDER BY id DESC LIMIT %s", (limite,)
        ).fetchall()
    salida = []
    for fila in filas:
        f = dict(fila)
        f["payload"] = json.loads(f["payload"]) if isinstance(f["payload"], str) else f["payload"]
        f["fecha"] = _json(f.get("fecha"))
        salida.append(f)
    return salida


def crear_documento(doc_id: str, tipo: str, id_origen: int):
    """Idempotente: si el documento ya existe (reintento/replay) no falla."""
    if not isinstance(id_origen, int):
        raise ValueError(f"id_origen invalido: {id_origen!r}")
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO documentos (id, tipo, id_origen) VALUES (%s, %s, %s)"
            " ON CONFLICT (id) DO NOTHING",
            (doc_id, tipo, id_origen),
        )


def actualizar_documento(doc_id: str, ruta: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE documentos SET estado = 'listo', ruta = %s WHERE id = %s",
            (ruta, doc_id),
        )


def obtener_documento(doc_id: str):
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT * FROM documentos WHERE id = %s", (doc_id,)
        ).fetchone()
        return dict(fila) if fila else None


def registrar_email(destino: str, asunto: str, cuerpo: str, estado: str, error: str = None):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO emails (destino, asunto, cuerpo, estado, error)"
            " VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (destino, asunto, cuerpo, estado, error),
        )
        return cursor.fetchone()["id"]


def obtener_email(email_id: int):
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT * FROM emails WHERE id = %s", (email_id,)
        ).fetchone()
        return dict(fila) if fila else None


def actualizar_estado_email(email_id: int, estado: str, error: str = None):
    with get_connection() as conn:
        conn.execute(
            "UPDATE emails SET estado = %s, error = %s WHERE id = %s",
            (estado, error, email_id),
        )


def listar_emails(limite: int = 50):
    with get_connection() as conn:
        filas = conn.execute(
            "SELECT * FROM emails ORDER BY id DESC LIMIT %s", (limite,)
        ).fetchall()
    salida = []
    for fila in filas:
        f = dict(fila)
        f["fecha"] = _json(f.get("fecha"))
        salida.append(f)
    return salida