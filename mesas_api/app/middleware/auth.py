from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from mesas_api.app.models.auth_model import decodificar_token, sesion_valida

_bearer = HTTPBearer(auto_error=False)


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