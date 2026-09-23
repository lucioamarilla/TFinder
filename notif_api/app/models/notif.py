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


def registrar_evento(event_id: str, tipo: str, metadata: dict = None):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO event_log (event_id, entidad_tipo, accion, metadata)"
            " VALUES (%s, %s, %s, %s)",
            (event_id, tipo, "consumido", json.dumps(metadata or {})),
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