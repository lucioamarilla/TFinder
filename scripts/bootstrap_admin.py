#!/usr/bin/env python3
"""Crea el primer usuario administrador en mesas_db (sin seed demo).

Uso:
    python scripts/bootstrap_admin.py
"""
import getpass
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv

load_dotenv()

from mesas_api.app.db import abrir_pool, cerrar_pool, get_connection
from mesas_api.app.init_db import init_db
from mesas_api.app.models.auth_model import crear_usuario, obtener_usuario_por_email


def main():
    abrir_pool()
    init_db()
    email = input("Email del admin: ").strip().lower()
    if not email:
        print("Email requerido")
        sys.exit(1)
    if obtener_usuario_por_email(email):
        print("Ese email ya existe.")
        sys.exit(1)
    nombre = input("Nombre: ").strip() or "Admin"
    password = getpass.getpass("Contraseña: ")
    if len(password) < 8:
        print("La contraseña debe tener al menos 8 caracteres.")
        sys.exit(1)
    usuario = crear_usuario(email, password, nombre, "admin")
    print(f"Admin creado: {usuario['email']} (id={usuario['id']})")
    cerrar_pool()


if __name__ == "__main__":
    main()