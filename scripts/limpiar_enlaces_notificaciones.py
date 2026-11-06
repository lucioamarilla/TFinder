#!/usr/bin/env python3
"""Auditoría de navegación · sanea enlaces muertos en notificaciones.

El seed demo del entorno dejó filas de notificaciones con:
  - enlace.to = "/mesas/demo" (mesa sin id numérico) -> "Mesa no encontrada"
  - enlace.to = "/mesas/{id}/gestion/solicitudes" (ruta que NO existe:
    la bandeja del GM es /gestion/jugadores) -> NotFound

REMAP:
  /mesas/demo              -> /mesas            (catálogo, destino seguro)
  .../gestion/solicitudes  -> .../gestion/jugadores  (pestaña real)

Uso:
    python scripts/limpiar_enlaces_notificaciones.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ.setdefault(
    "NOTIF_DATABASE_URL",
    "postgresql://tfinder:tfinder@localhost:5432/notif_db",
)

from dotenv import load_dotenv

load_dotenv()

from notif_api.app.db import abrir_pool, cerrar_pool, get_connection


def main():
    abrir_pool()
    remapeados = 0
    corregidos = 0
    with get_connection() as conn:
        filas = conn.execute(
            "SELECT id, enlace::text AS enlace_txt FROM notificaciones WHERE enlace IS NOT NULL"
        ).fetchall()
        for fila in filas:
            try:
                enlace = json.loads(fila["enlace_txt"])
            except (TypeError, json.JSONDecodeError):
                continue
            to = enlace.get("to") if isinstance(enlace, dict) else None
            if not to or not isinstance(to, str):
                continue
            to_nuevo = None
            if to == "/mesas/demo" or (to.startswith("/mesas/") and to.removeprefix("/mesas/").split("/")[0] == "demo"):
                to_nuevo = "/mesas"
            elif to.endswith("/gestion/solicitudes"):
                to_nuevo = to[:-len("/gestion/solicitudes")] + "/gestion/jugadores"
            if to_nuevo is None:
                continue
            enlace["to"] = to_nuevo
            conn.execute(
                "UPDATE notificaciones SET enlace = %s WHERE id = %s",
                (json.dumps(enlace), fila["id"]),
            )
            if to == "/mesas/demo":
                remapeados += 1
            else:
                corregidos += 1
    cerrar_pool()
    print(f"enlaces remapeados a /mesas: {remapeados}")
    print(f"enlaces a gestion/jugadores corregidos: {corregidos}")


if __name__ == "__main__":
    main()
