from fastapi import HTTPException

from mesas_api.app.models.auth_model import (
    actualizar_password_hash,
    crear_token,
    crear_usuario,
    decodificar_token,
    guardar_sesion,
    guardar_sesion_familia,
    hash_password,
    necesita_rehash,
    obtener_usuario_por_email,
    revocar_familia,
    revocar_sesion,
    sesion_valida,
    verificar_password,
)
from mesas_api.app.schemas import AuthLogin, AuthRefresh, AuthRegistro


def _emitir_tokens(usuario):
    claims = {"sub": str(usuario["id"]), "rol": usuario["rol"], "email": usuario["email"]}
    access = crear_token(claims, tipo="access")
    refresh = crear_token(claims, tipo="refresh")
    guardar_sesion(decodificar_token(access)["jti"], usuario["id"])
    guardar_sesion(decodificar_token(refresh)["jti"], usuario["id"])
    guardar_sesion_familia(decodificar_token(access)["jti"], usuario["id"])
    guardar_sesion_familia(decodificar_token(refresh)["jti"], usuario["id"])
    return {
        "access_token": access,
        "refresh_token": refresh,
        "rol": usuario["rol"],
        "perfil": {
            "id": usuario["id"],
            "email": usuario["email"],
            "nombre": usuario.get("nombre") or "",
            "rol": usuario["rol"],
        },
    }


def registrar(data: AuthRegistro):
    if obtener_usuario_por_email(data.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    usuario = crear_usuario(data.email, data.password, data.nombre, data.rol)
    return _emitir_tokens(usuario)


def iniciar_sesion(data: AuthLogin):
    usuario = obtener_usuario_por_email(data.email)
    if not usuario or not verificar_password(data.password, usuario["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    if necesita_rehash(usuario["password_hash"]):
        try:
            actualizar_password_hash(usuario["id"], hash_password(data.password))
        except Exception:
            pass
    return _emitir_tokens(usuario)


def renovar_access(data: AuthRefresh):
    payload = decodificar_token(data.refresh_token)
    if payload.get("tipo") != "refresh":
        raise HTTPException(status_code=401, detail="Use el refresh_token")
    if not sesion_valida(payload.get("jti")):
        raise HTTPException(status_code=401, detail="Sesión revocada o expirada")
    claims = {k: payload[k] for k in ("sub", "rol", "email")}
    access = crear_token(claims, tipo="access")
    guardar_sesion(decodificar_token(access)["jti"], int(payload["sub"]))
    guardar_sesion_familia(decodificar_token(access)["jti"], int(payload["sub"]))
    return {"access_token": access}


def perfil(usuario_id: int):
    from mesas_api.app.models.auth_model import obtener_perfil

    fila = obtener_perfil(usuario_id)
    if fila is None:
        raise HTTPException(status_code=404, detail="El perfil no existe")
    return fila


def actualizar_perfil(usuario_id: int, nombre=None, bio=None, avatar_url=None):
    from mesas_api.app.models.auth_model import actualizar_perfil as _ap

    try:
        fila = _ap(usuario_id, nombre=nombre, bio=bio, avatar_url=avatar_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    if fila is None:
        raise HTTPException(status_code=404, detail="El perfil no existe")
    return fila


def cerrar_sesion(jti: str, usuario_id=None):
    if usuario_id:
        revocar_familia(jti, usuario_id)
    else:
        revocar_sesion(jti)
    return {"ok": True}