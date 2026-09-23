from fastapi import APIRouter, Depends, status

from mesas_api.app.controllers import auth_controller
from mesas_api.app.middleware.auth import requerir_roles, usuario_actual
from mesas_api.app.schemas import AuthLogin, AuthRefresh, AuthRegistro

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: AuthRegistro):
    return auth_controller.registrar(data)


@router.post("/login")
def login(data: AuthLogin):
    return auth_controller.iniciar_sesion(data)


@router.post("/refresh")
def refresh(data: AuthRefresh):
    return auth_controller.renovar_access(data)


@router.post("/logout")
def logout(payload: dict = Depends(usuario_actual)):
    return auth_controller.cerrar_sesion(payload["jti"])


@router.get("/me")
def me(payload: dict = Depends(usuario_actual)):
    return payload


@router.get("/admin-only")
def admin_only(_=Depends(requerir_roles("admin"))):
    return {"ok": True}