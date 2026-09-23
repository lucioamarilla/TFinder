import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.infra.redis import get_redis
from mesas_api.app.db import get_connection

_SECRET = os.getenv("JWT_SECRET", "dev-secret")
_EXP_MIN = int(os.getenv("JWT_EXP_MIN", "1440"))  # 24 h

ROL_USUARIO = "usuario"
ROLES = ("usuario", "gm", "admin")

_ITERACIONES = 120_000


def hash_password(pw: str) -> str:
    salt = uuid.uuid4().hex
    digest = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), _ITERACIONES).hex()
    return f"{salt}${digest}"


def verificar_password(pw: str, almacenado: str) -> bool:
    try:
        salt, digest = almacenado.split("$")
    except ValueError:
        return False
    calc = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), _ITERACIONES).hex()
    return calc == digest


def crear_token(payload: dict, tipo="access") -> str:
    p = {
        **payload,
        "tipo": tipo,
        "jti": uuid.uuid4().hex,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=_EXP_MIN),
    }
    return jwt.encode(p, _SECRET, algorithm="HS256")


def decodificar_token(token: str) -> dict:
    return jwt.decode(token, _SECRET, algorithms=["HS256"])


def crear_usuario(email, password, nombre, rol=ROL_USUARIO):
    with get_connection() as conn:
        return conn.execute(
            """
            INSERT INTO usuarios (email, password_hash, nombre, rol)
            VALUES (%s, %s, %s, %s)
            RETURNING id, email, nombre, rol
            """,
            (email, hash_password(password), nombre, rol),
        ).fetchone()


def obtener_usuario_por_email(email):
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, email, password_hash, nombre, rol FROM usuarios WHERE email = %s",
            (email,),
        ).fetchone()


def guardar_sesion(jti: str, usuario_id: int, ttl_seg: int = 86400):
    get_redis().setex(f"sesion:{jti}", ttl_seg, str(usuario_id))


def revocar_sesion(jti: str):
    get_redis().delete(f"sesion:{jti}")


def sesion_valida(jti: str) -> bool:
    return get_redis().exists(f"sesion:{jti}") == 1