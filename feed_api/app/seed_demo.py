import os

from psycopg.types.json import Jsonb

from app.infra.logge import logger
from feed_api.app.db import get_connection

PUBLICACIONES = (
    ("post", "Admin Demo", "¡TFinder Demo disponible!", "Explorá las cuentas y mesas de demostración.", "seed-demo-post", {"icono": "✦", "titulo": "Mesa Demo Abierta", "boton": "Ver mesa"}),
    ("build", "Jugador Uno", "Build de mago listo", "Una ficha pública para probar la biblioteca de personajes.", "seed-demo-build", {"icono": "✧", "titulo": "Mago del Alba", "boton": "Abrir build"}),
    ("wiki", "GM Demo", "Guía de la campaña", "Las primeras páginas de la wiki de demostración.", "seed-demo-wiki", {"icono": "▤", "titulo": "Bienvenida a la campaña", "boton": "Leer wiki"}),
)

WIKI = (
    ("demo-mesa", "notas", "Bienvenida a la campaña", "Página inicial", "Nota"),
    ("demo-mesa", "reglas", "Reglas de mesa", "Reglas de la campaña demo", "Regla"),
)


def seed_demo_if_enabled():
    if os.getenv("DEMO_SEED_ENABLED", "false").lower() not in {"1", "true", "yes"}:
        return
    with get_connection() as conn, conn.transaction():
        for tipo, autor, titulo, cuerpo, etiqueta, embed in PUBLICACIONES:
            existe = conn.execute("SELECT id FROM publicaciones WHERE etiqueta = %s", (etiqueta,)).fetchone()
            if existe is None:
                conn.execute(
                    "INSERT INTO publicaciones (tipo, autor, autor_nombre, iniciales, tiempo, titulo, cuerpo, votos, total_comentarios, embed, comentarios, etiqueta) VALUES (%s, %s, %s, %s, 'ahora', %s, %s, 1, 0, %s, %s, %s)",
                    (tipo, autor, autor, autor[:2].upper(), titulo, cuerpo, Jsonb(embed), Jsonb([]), etiqueta),
                )
        for mesa_id, carpeta, titulo, resumen, tipo in WIKI:
            existe = conn.execute(
                "SELECT id FROM wiki_paginas WHERE mesa_id = %s AND carpeta = %s AND titulo = %s",
                (mesa_id, carpeta, titulo),
            ).fetchone()
            if existe is None:
                conn.execute(
                    "INSERT INTO wiki_paginas (mesa_id, carpeta, titulo, tipo, fecha, resumen, contenido) VALUES (%s, %s, %s, %s, '27 de septiembre de 2026', %s, %s)",
                    (mesa_id, carpeta, titulo, tipo, resumen, Jsonb([{"tipo": "parrafo", "texto": f"Contenido demo de {titulo}."}])),
                )
    logger.info("datos demo feed-api inicializados")
