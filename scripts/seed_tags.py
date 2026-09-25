"""Seed del catalogo de tags en builds_db (B02).

Siembra la tabla `tags` si esta vacia. Uso:
    python scripts/seed_tags.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from builds_api.app.db import abrir_pool, cerrar_pool, get_pool

TAGS = [
    "Guia de Build",
    "Debate Tactico",
    "Entrada de Wiki",
    "Cronica de Sesion",
    "Pregunta de Reglas OGL",
    "Debate de Reglas",
    "Guerrero",
    "Mago",
    "Paladin",
    "Picaro",
    "Clerigo",
    "Explorador",
    "Alquimista",
]


def main():
    abrir_pool()
    try:
        with get_pool().connection() as conn:
            conteo = conn.execute("SELECT COUNT(*) AS n FROM tags").fetchone()["n"]
            if conteo:
                print(f"Tags ya sembrados ({conteo}). Nada que hacer.")
                return
            for tag in TAGS:
                conn.execute(
                    "INSERT INTO tags (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING",
                    (tag,),
                )
        print(f"Sembrados {len(TAGS)} tags en builds_db.")
    finally:
        cerrar_pool()


if __name__ == "__main__":
    main()