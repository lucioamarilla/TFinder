import os

from psycopg.types.json import Jsonb

from app.infra.logge import logger
from builds_api.app.db import get_connection

BUILDS = (
    {
        "persona": "PF Demo",
        "handle": "@pf_demo",
        "autor": "Jugador Uno",
        "nombre": "Mago del Alba",
        "clase": "Mago",
        "raza": "Humano",
        "nivel": 3,
        "rol": "Soporte",
        "privacidad": "publico",
        "ficha": {"ataque": {"cuerpo": {"arma": "Bastón arcano"}}, "defensa": {"pg": 8}},
        "historial": [{"version": "1.0", "resumen": "Ficha demo inicial", "activa": True}],
    },
    {
        "persona": "Guerrera Demo",
        "handle": "@guerrera_demo",
        "autor": "Jugador Dos",
        "nombre": "Guardiana de Ustalav",
        "clase": "Guerrero",
        "raza": "Humana",
        "nivel": 4,
        "rol": "Defensa",
        "privacidad": "privado",
        "ficha": {"ataque": {"cuerpo": {"arma": "Espada larga"}}, "defensa": {"pg": 17}},
        "historial": [{"version": "1.0", "resumen": "Ficha demo inicial", "activa": True}],
    },
)

TAGS = ("PF1e", "Mago", "Guerrero", "Exploración", "Táctica", "Narrativa", "Novato", "Veterano", "Hechicero", "Combate", "Social", "Campaña", "Personaje")


def seed_demo_if_enabled():
    if os.getenv("DEMO_SEED_ENABLED", "false").lower() not in {"1", "true", "yes"}:
        return
    with get_connection() as conn, conn.transaction():
        for build in BUILDS:
            existe = conn.execute(
                "SELECT id FROM builds WHERE persona = %s AND nombre = %s AND COALESCE(mesa_id, 0) = 0",
                (build["persona"], build["nombre"]),
            ).fetchone()
            if existe is None:
                conn.execute(
                    "INSERT INTO builds (mesa_id, persona, handle, autor, categoria, nombre, display, clase, raza, arquetipo, nivel, rol, alineamiento, alineamiento_color, privacidad, actualizado, protagonista, detalle, favoritos, historial, ficha) VALUES (NULL, %s, %s, %s, 'mio', %s, %s, %s, %s, '', %s, %s, 'N', 'neutral', %s, 'DEMO', FALSE, 'Ficha cargada automáticamente para desarrollo.', 0, %s, %s)",
                    (build["persona"], build["handle"], build["autor"], build["nombre"], build["nombre"], build["clase"], build["raza"], build["nivel"], build["rol"], build["privacidad"], Jsonb(build["historial"]), Jsonb(build["ficha"])),
                )
        for nombre in TAGS:
            conn.execute("INSERT INTO tags (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING", (nombre,))
    logger.info("datos demo builds-api inicializados")
