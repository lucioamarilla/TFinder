import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.infra.redis import get_redis
from app.infra.token import decodificar_token, sesion_valida
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


def guardar_sesion_familia(jti: str, usuario_id: int, ttl_seg: int = 86400):
    """Indexa el jti en la familia de sesiones del usuario (logout total)."""
    _r = get_redis()
    _r.sadd(f"sesiones_usuario:{usuario_id}", jti)
    _r.expire(f"sesiones_usuario:{usuario_id}", ttl_seg)


def revocar_sesion(jti: str):
    get_redis().delete(f"sesion:{jti}")


def revocar_familia(jti: str, usuario_id):
    """Revoca el access pedido y TODAS las sesiones hermanas (refresh incluidos)."""
    _r = get_redis()
    claves = _r.smembers(f"sesiones_usuario:{usuario_id}")
    for j in claves:
        _r.delete(f"sesion:{j.decode() if isinstance(j, bytes) else j}")
    _r.delete(f"sesiones_usuario:{usuario_id}")
    _r.delete(f"sesion:{jti}")

def obtener_perfil(usuario_id: int):
    from mesas_api.app.models.usuarios_lookup import obtener_usuario_por_id

    fila = obtener_usuario_por_id(usuario_id)
    if fila is None:
        return None
    return {
        "id": fila["id"],
        "email": fila["email"],
        "nombre": fila["nombre"],
        "rol": fila["rol"],
        "avatarUrl": fila.get("avatar_url"),
        "bio": fila.get("bio"),
    }


def actualizar_perfil(usuario_id: int, nombre=None, bio=None, avatar_url=None):
    from mesas_api.app.models.usuarios_lookup import actualizar_perfil as _ap

    fila = _ap(usuario_id, nombre=nombre, bio=bio, avatar_url=avatar_url)
    if fila is None:
        return None
    return {
        "id": fila["id"],
        "email": fila["email"],
        "nombre": fila["nombre"],
        "rol": fila["rol"],
        "avatarUrl": fila.get("avatar_url"),
        "bio": fila.get("bio"),
    }
