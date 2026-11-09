from fastapi import APIRouter, Depends, status

from mesas_api.app.controllers import auth_controller
from mesas_api.app.middleware.auth import requerir_roles, usuario_actual
from mesas_api.app.models.auth_model import (
    ROL_USUARIO,
    decodificar_token,
)
from mesas_api.app.schemas import (
    AuthLogin,
    AuthRefresh,
    AuthRegistro,
    ConfirmarRecupero,
    PerfilUpdate,
    SolicitudEmail,
    VerificarCodigo,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_202_ACCEPTED)
def register(data: AuthRegistro):
    # El registro es publico: el rol siempre es "usuario" (los roles "gm"/
    # "admin" se otorgan por seed o administracion).
    #
    # Ya NO crea la cuenta de una: guarda el registro PENDIENTE en Redis y
    # manda un codigo de 6 digitos al mail. La fila en PostgreSQL nace recien
    # en POST /register/verificar, con el codigo correcto => nunca entran a la
    # BD correos que no se pueden confirmar.
    data.rol = ROL_USUARIO
    return auth_controller.registrar(data)


@router.post("/register/verificar")
def verificar_registro(data: VerificarCodigo):
    """Confirma el registro con el codigo: crea el usuario y emite sesion."""
    return auth_controller.verificar_registro(data)


@router.post("/register/reenviar", status_code=status.HTTP_202_ACCEPTED)
def reenviar_registro(data: SolicitudEmail):
    """Reenvia el codigo del registro pendiente (cooldown de 60 s)."""
    return auth_controller.reenviar_registro(data)


@router.post("/recuperar", status_code=status.HTTP_202_ACCEPTED)
def recuperar(data: SolicitudEmail):
    # Respuesta genérica: nunca revela si el correo existe en la BD.
    return auth_controller.solicitar_recupero(data)


@router.post("/recuperar/verificar")
def recuperar_confirmar(data: ConfirmarRecupero):
    """Código + nueva contraseña. Revoca además toda sesión previa."""
    return auth_controller.confirmar_recupero(data)


@router.post("/login")
def login(data: AuthLogin):
    return auth_controller.iniciar_sesion(data)


@router.post("/refresh")
def refresh(data: AuthRefresh):
    return auth_controller.renovar_access(data)


@router.post("/logout")
def logout(payload: dict = Depends(usuario_actual)):
    return auth_controller.cerrar_sesion(payload["jti"], payload.get("sub"))


@router.get("/me")
def me(payload: dict = Depends(usuario_actual)):
    return payload


@router.get("/perfil")
def ver_perfil(payload: dict = Depends(usuario_actual)):
    return auth_controller.perfil(int(payload["sub"]))


@router.patch("/perfil")
def editar_perfil(payload: dict = Depends(usuario_actual), data: PerfilUpdate = None):
    if data is None:
        data = PerfilUpdate()
    return auth_controller.actualizar_perfil(
        int(payload["sub"]),
        nombre=data.nombre,
        bio=data.bio,
        avatar_url=data.avatarUrl or data.avatar_url,
    )


@router.get("/admin-only")
def admin_only(_=Depends(requerir_roles("admin"))):
    return {"ok": True}