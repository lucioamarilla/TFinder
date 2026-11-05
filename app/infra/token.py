"""Validación de tokens JWT y sesión Redis (B03), compartida.

Esta lógica estaba copiada 3 veces (mesas la delega en su auth_model; builds,
feed y notif la llevaban inline). La regla es una: el token se valida HS256
con JWT_SECRET y la sesión vive en Redis bajo `sesion:{jti}`. La EMISIÓN de
tokens sigue siendo responsabilidad de mesas-api (auth_model.crear_token +
guardar_sesion) — el resto solo valida.
"""

import os

import jwt

from app.infra.redis import get_redis

_SECRET = os.getenv("JWT_SECRET", "dev-secret")


def decodificar_token(token: str) -> dict:
    return jwt.decode(token, _SECRET, algorithms=["HS256"])


def sesion_valida(jti: str) -> bool:
    return get_redis().exists(f"sesion:{jti}") == 1
