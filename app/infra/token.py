"""Validación de tokens JWT y sesión Redis (B03), compartida.

Esta lógica estaba copiada 3 veces (mesas la delega en su auth_model; builds,
feed y notif la llevaban inline). La regla es una: el token se valida HS256
con JWT_SECRET y la sesión vive en Redis bajo `sesion:{jti}`. La EMISIÓN de
tokens sigue siendo responsabilidad de mesas-api (auth_model.crear_token +
guardar_sesion) — el resto solo valida.
"""

import os
import time

import jwt

from app.infra.redis import get_redis

_SECRET = os.getenv("JWT_SECRET", "dev-secret")

if _SECRET == "dev-secret":
    raise RuntimeError(
        "JWT_SECRET no puede ser el valor por defecto ('dev-secret'). "
        "Configurá JWT_SECRET en .env (generá uno con: openssl rand -hex 32)."
    )

_IDLE_MIN = int(os.getenv("SESSION_IDLE_MIN", "30"))


def decodificar_token(token: str) -> dict:
    return jwt.decode(token, _SECRET, algorithms=["HS256"])


def sesion_valida(jti: str) -> bool:
    r = get_redis()
    if r.exists(f"sesion:{jti}") != 1:
        return False
    clave = f"actividad:{jti}"
    ultima = r.get(clave)
    ahora = time.time()
    if ultima is not None:
        try:
            if ahora - float(ultima) > _IDLE_MIN * 60:
                r.delete(f"sesion:{jti}")
                r.delete(clave)
                return False
        except (TypeError, ValueError):
            pass
    r.setex(clave, _IDLE_MIN * 60 + 60, str(ahora))
    return True
