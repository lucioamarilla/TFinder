"""Auth real (B03). La validación es compartida: ver app/infra/token.py."""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.infra.token import decodificar_token, sesion_valida

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


def auth_opcional(request) -> dict | None:
    """Payload del JWT si viene y es válido; None si falta (lecturas públicas)."""
    header = request.headers.get("Authorization") or ""
    if not header.startswith("Bearer "):
        return None
    creds = header.removeprefix("Bearer ").strip()
    if not creds:
        return None
    try:
        payload = decodificar_token(creds)
    except Exception:
        return None
    if payload.get("tipo") == "refresh" or not sesion_valida(payload["jti"]):
        return None
    return payload
