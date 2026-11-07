#!/usr/bin/env python3
"""Crea o actualiza la cuenta de servicio de notif-api en mesas_db.

La cuenta se usa para que notif-api consulte membresías en mesas-api.
Es idempotente: si el email ya existe, solo actualiza el hash si la
contraseña de `.env` cambió.

Uso local:
    python scripts/bootstrap_service_account.py

Uso en contenedor:
    docker compose run --rm --no-deps \
      -v "$PWD/scripts:/app/scripts:ro" \
      -v "$PWD/.env:/app/.env:ro" \
      mesas-api python /app/scripts/bootstrap_service_account.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv

load_dotenv(os.path.join(ROOT, ".env"))

from mesas_api.app.db import abrir_pool, cerrar_pool
from mesas_api.app.init_db import init_db
from mesas_api.app.models.auth_model import (
    actualizar_password_hash,
    crear_usuario,
    hash_password,
    obtener_usuario_por_email,
    verificar_password,
)


def main() -> int:
    email = os.getenv("MESAS_EMAIL", "email_svc@tfinder.dev").strip().lower()
    password = os.getenv("MESAS_PASSWORD", "")
    nombre = os.getenv("MESAS_NOMBRE", "Cuenta de servicio").strip() or "Cuenta de servicio"

    if not email:
        print("MESAS_EMAIL requerido", file=sys.stderr)
        return 1
    if len(password) < 8:
        print("MESAS_PASSWORD requerido (mínimo 8 caracteres)", file=sys.stderr)
        return 1

    abrir_pool()
    try:
        init_db()
        existente = obtener_usuario_por_email(email)
        if existente is None:
            usuario = crear_usuario(email, password, nombre, "usuario")
            print(f"Cuenta de servicio creada: {usuario['email']} (id={usuario['id']})")
            return 0

        if verificar_password(password, existente["password_hash"]):
            print(f"Cuenta de servicio ya existe y la contraseña coincide: {email}")
            return 0

        actualizar_password_hash(existente["id"], hash_password(password))
        print(f"Cuenta de servicio existente; contraseña actualizada: {email}")
        return 0
    finally:
        cerrar_pool()


if __name__ == "__main__":
    sys.exit(main())
