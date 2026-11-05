from fastapi import APIRouter, Depends, status

from mesas_api.app.controllers import auth_controller
from mesas_api.app.middleware.auth import requerir_roles, usuario_actual
from mesas_api.app.models.auth_model import (
    ROL_USUARIO,
    decodificar_token,
)
from mesas_api.app.schemas import AuthLogin, AuthRefresh, AuthRegistro, PerfilUpdate

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: AuthRegistro):
    # El registro es publico: el rol siempre es "usuario". Los roles
    # "gm"/"admin" se otorgan fuera de esta via (seed o administracion).
    data.rol = ROL_USUARIO
    return auth_controller.registrar(data)


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