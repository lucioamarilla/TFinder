import os

from app.infra.logge import logger
from mesas_api.app.db import get_connection
from mesas_api.app.models.auth_model import hash_password

DEMO_USERS = (
    ("admin@tfinder.dev", "Admin Demo", "admin"),
    ("gm@tfinder.dev", "GM Demo", "gm"),
    ("jugador1@tfinder.dev", "Jugador Uno", "usuario"),
    ("jugador2@tfinder.dev", "Jugador Dos", "usuario"),
    ("jugador3@tfinder.dev", "Jugador Tres", "usuario"),
    ("email_svc@tfinder.dev", "Servicio Email", "usuario"),
)

DEMO_MESAS = (
    ("Mesa Demo Abierta", "PF1e", "Campaña abierta para explorar el flujo principal.", "Exploración y%", "Viernes 20:00", "abierta", 1, 4, 2),
    ("Mesa Demo Casi Llena", "PF1e", "Campaña con una sola vacante para probar concurrencia.", "Táctica y misterio", "Sábado 18:00", "abierta", 3, 4, 3),
    ("Mesa Demo Cerrada", "D&D 5e", "Campaña histórica que ya no acepta solicitudes.", "Narrativa", "Sin reuniones", "cerrada", 5, 6, 0),
)


def seed_demo_if_enabled():
    if os.getenv("DEMO_SEED_ENABLED", "false").lower() not in {"1", "true", "yes"}:
        return
    password = os.getenv("DEMO_SEED_PASSWORD", "DemoTFinder123!")
    with get_connection() as conn, conn.transaction():
        usuarios = {}
        for email, nombre, rol in DEMO_USERS:
            fila = conn.execute("SELECT id FROM usuarios WHERE email = %s", (email,)).fetchone()
            if fila is None:
                fila = conn.execute(
                    "INSERT INTO usuarios (email, password_hash, rol, nombre) VALUES (%s, %s, %s, %s) RETURNING id",
                    (email, hash_password(password), rol, nombre),
                ).fetchone()
            usuarios[email] = fila["id"]

        mesas = {}
        for nombre, sistema, descripcion, tono, horario, estado, nivel, maximo, ocupacion in DEMO_MESAS:
            fila = conn.execute(
                "SELECT id FROM mesas WHERE nombre = %s AND sistema = %s AND descripcion = %s",
                (nombre, sistema, descripcion),
            ).fetchone()
            if fila is None:
                fila = conn.execute(
                    "INSERT INTO mesas (nombre, sistema, descripcion, tono, horario, estado, nivel_inicial, jugadores_max, jugadores_actuales) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    (nombre, sistema, descripcion, tono, horario, estado, nivel, maximo, ocupacion),
                ).fetchone()
            mesas[nombre] = fila["id"]

        miembros = (
            ("Mesa Demo Abierta", "jugador1@tfinder.dev", "demo-open-1"),
            ("Mesa Demo Abierta", "jugador2@tfinder.dev", "demo-open-2"),
            ("Mesa Demo Casi Llena", "jugador1@tfinder.dev", "demo-full-1"),
            ("Mesa Demo Casi Llena", "jugador2@tfinder.dev", "demo-full-2"),
            ("Mesa Demo Casi Llena", "jugador3@tfinder.dev", "demo-full-3"),
        )
        for nombre_mesa, email, idem_key in miembros:
            existe = conn.execute(
                "SELECT id FROM solicitudes_uniones WHERE mesa_id = %s AND usuario_id = %s AND idem_key = %s",
                (mesas[nombre_mesa], usuarios[email], idem_key),
            ).fetchone()
            if existe is None:
                conn.execute(
                    "INSERT INTO solicitudes_uniones (mesa_id, usuario_id, estado, idem_key) VALUES (%s, %s, 'aceptada', %s)",
                    (mesas[nombre_mesa], usuarios[email], idem_key),
                )

        pendiente = conn.execute(
            "SELECT id FROM solicitudes_uniones WHERE mesa_id = %s AND usuario_id = %s AND idem_key = %s",
            (mesas["Mesa Demo Cerrada"], usuarios["jugador3@tfinder.dev"], "demo-closed-pending"),
        ).fetchone()
        if pendiente is None:
            conn.execute(
                "INSERT INTO solicitudes_uniones (mesa_id, usuario_id, estado, idem_key) VALUES (%s, %s, 'pendiente', %s)",
                (mesas["Mesa Demo Cerrada"], usuarios["jugador3@tfinder.dev"], "demo-closed-pending"),
            )

        matchmaking = conn.execute(
            "SELECT id FROM matchmaking WHERE mesa_id = %s ORDER BY id LIMIT 1",
            (mesas["Mesa Demo Casi Llena"],),
        ).fetchone()
        if matchmaking is None:
            conn.execute(
                "INSERT INTO matchmaking (mesa_id, estado, llamada_abierta_at) VALUES (%s, 'llamada_abierta', now())",
                (mesas["Mesa Demo Casi Llena"],),
            )

        sesiones = {}
        for nombre_mesa, estado in (("Mesa Demo Abierta", "abierta"), ("Mesa Demo Cerrada", "cerrada")):
            fila = conn.execute(
                "SELECT id FROM sesiones WHERE mesa_id = %s AND estado = %s ORDER BY id LIMIT 1",
                (mesas[nombre_mesa], estado),
            ).fetchone()
            if fila is None:
                fila = conn.execute(
                    "INSERT INTO sesiones (mesa_id, estado) VALUES (%s, %s) RETURNING id",
                    (mesas[nombre_mesa], estado),
                ).fetchone()
            sesiones[nombre_mesa] = fila["id"]

        for email in ("jugador1@tfinder.dev", "jugador2@tfinder.dev"):
            conn.execute(
                "INSERT INTO asistencias (sesion_id, usuario_id) VALUES (%s, %s) ON CONFLICT (sesion_id, usuario_id) DO NOTHING",
                (sesiones["Mesa Demo Abierta"], usuarios[email]),
            )

    logger.info("datos demo mesas-api inicializados")
