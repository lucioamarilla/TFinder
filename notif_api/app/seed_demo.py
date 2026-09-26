import os

from psycopg.types.json import Jsonb

from app.infra.logge import logger
from notif_api.app.db import get_connection

NOTIFICACIONES = (
    ("mesas", "solicitud", "Tu solicitud fue aceptada", "Mesa Demo Abierta", "/mesas/demo"),
    ("sesiones", "recordatorio", "La campaña comienza el viernes", "Mesa Demo Casi Llena", "/mesas/demo"),
    ("social", "comentario", "Nueva publicación de la comunidad", "TFinder Demo", "/feed"),
)

EVENTOS = (
    ("seed-demo-mesa", "mesa", "demo", "seed", '{"demo": true}', "seed-demo-correlation"),
    ("seed-demo-sesion", "sesion", "demo", "seed", '{"demo": true}', "seed-demo-correlation"),
)


def seed_demo_if_enabled():
    if os.getenv("DEMO_SEED_ENABLED", "false").lower() not in {"1", "true", "yes"}:
        return
    with get_connection() as conn, conn.transaction():
        for grupo, icono, mensaje, entidad, enlace in NOTIFICACIONES:
            existe = conn.execute("SELECT id FROM notificaciones WHERE entidad = %s", (entidad,)).fetchone()
            if existe is None:
                conn.execute(
                    "INSERT INTO notificaciones (grupo, icono, mensaje, entidad, detalle, enlace, fecha) VALUES (%s, %s, %s, %s, 'Notificación de demostración', %s, 'ahora')",
                    (grupo, icono, mensaje, entidad, Jsonb({"label": "Ver detalle", "to": enlace})),
                )
        for event_id, entidad_tipo, entidad_id, accion, metadata, correlation_id in EVENTOS:
            conn.execute(
                "INSERT INTO event_log (event_id, entidad_tipo, entidad_id, accion, metadata, correlation_id) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (event_id) WHERE event_id IS NOT NULL DO NOTHING",
                (event_id, entidad_tipo, entidad_id, accion, Jsonb(metadata), correlation_id),
            )
    logger.info("datos demo notif-api inicializados")
