from fastapi import HTTPException

from mesas_api.app.models.auth_model import (
    actualizar_password_hash,
    crear_token,
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
from mesas_api.app.schemas import (
    AuthLogin,
    AuthRefresh,
    AuthRegistro,
    ConfirmarRecupero,
    SolicitudEmail,
    VerificarCodigo,
)


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
    from mesas_api.app.services import verificacion

    # Registro pendiente: NO crea el usuario. Deja los datos en Redis hasta que
    # el usuario confirme el código enviado a su mail (POST /register/verificar).
    return verificacion.registrar(
        data.email,
        hash_password(data.password),
        data.nombre,
        data.rol,
    )


def verificar_registro(data: VerificarCodigo):
    from mesas_api.app.services import verificacion

    return verificacion.verificar_registro(data.email, data.codigo)


def reenviar_registro(data: SolicitudEmail):
    from mesas_api.app.services import verificacion

    return verificacion.reenviar_registro(data.email)


def solicitar_recupero(data: SolicitudEmail):
    from mesas_api.app.services import verificacion

    return verificacion.solicitar_recupero(data.email)


def confirmar_recupero(data: ConfirmarRecupero):
    from mesas_api.app.services import verificacion

    return verificacion.confirmar_recupero(
        data.email, data.codigo, hash_password(data.nueva_password)
    )


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