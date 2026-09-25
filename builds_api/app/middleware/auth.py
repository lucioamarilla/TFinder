import os

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.infra.redis import get_redis

_SECRET = os.getenv("JWT_SECRET", "dev-secret")
_bearer = HTTPBearer(auto_error=False)


def decodificar_token(token: str) -> dict:
    return jwt.decode(token, _SECRET, algorithms=["HS256"])


def sesion_valida(jti: str) -> bool:
    return get_redis().exists(f"sesion:{jti}") == 1


def usuario_actual(creds: HTTPAuthorizationCredentials = Depends(_bearer)):
    if creds is None:
        raise HTTPException(status_code=401, detail="Autenticación requerida")
    try:
        payload = decodificar_token(creds.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    if payload.get("tipo") == "refresh":
        raise HTTPException(status_code=401, detail="Use el access_token")
    if not sesion_valida(payload["jti"]):
        raise HTTPException(status_code=401, detail="Sesión revocada o expirada")
    return payload


def requerir_roles(*roles):
    def inner(payload: dict = Depends(usuario_actual)):
        if payload["rol"] not in roles:
            raise HTTPException(status_code=403, detail="Rol insuficiente")
        return payload

    return inner