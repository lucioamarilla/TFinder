from fastapi import APIRouter, Depends, Request, Response

from mesas_api.app.controllers.mesas import (
    actualizar_mesa_controller,
    crear_mesa_controller,
    eliminar_mesa_controller,
    listar_mesas_controller,
    obtener_mesa_controller,
)
from mesas_api.app.controllers.sesiones_controller import (
    SesionNotFoundError,
    cerrar_sesion_controller,
    confirmar_sesion_controller,
    crear_sesion_controller,
    listar_sesiones_controller,
)
from mesas_api.app.middleware.auth import requerir_roles, usuario_actual
from mesas_api.app.models.sesiones import listar_miembros
from mesas_api.app.schemas import MesaCreate, MesaOut, MesaUpdate, SesionOut
from mesas_api.app.services.eventos import publicar_solicitud

router = APIRouter(prefix="/api/v1/mesas")


@router.get("/{mesa_id}/miembros")
def miembros_mesa(mesa_id: int, _=Depends(usuario_actual)):
    obtener_mesa_controller(mesa_id)
    return {"mesa_id": mesa_id, "miembros": listar_miembros(mesa_id)}


@router.get("", response_model=list[MesaOut])
def listar_mesas():
    return listar_mesas_controller()


@router.get("/{mesa_id}", response_model=MesaOut)
def obtener_mesa(mesa_id: int):
    return obtener_mesa_controller(mesa_id)


@router.post("", response_model=MesaOut, status_code=201)
def crear_mesa(payload: MesaCreate, _=Depends(usuario_actual)):
    return crear_mesa_controller(payload)


@router.put("/{mesa_id}", response_model=MesaOut)
def actualizar_mesa(mesa_id: int, payload: MesaUpdate, _=Depends(usuario_actual)):
    return actualizar_mesa_controller(mesa_id, payload)


@router.delete("/{mesa_id}", status_code=204)
def eliminar_mesa(mesa_id: int, _=Depends(usuario_actual)):
    eliminar_mesa_controller(mesa_id)
    return Response(status_code=204)


@router.post("/{mesa_id}/solicitar", status_code=202)
def solicitar_union(
    mesa_id: int,
    request: Request,
    usuario: dict = Depends(usuario_actual),
):
    obtener_mesa_controller(mesa_id)
    publicar_solicitud(
        mesa_id,
        int(usuario["sub"]),
        correlation_id=request.scope.get("correlation_id"),
    )
    return {"estado": "pendiente"}


# ---- Sesiones de juego (cierre AE2) -----------------------------------------

@router.get("/{mesa_id}/sesiones", response_model=list[SesionOut])
def listar_sesiones_mesa(mesa_id: int, _=Depends(usuario_actual)):
    return listar_sesiones_controller(mesa_id)


@router.post("/{mesa_id}/sesiones", status_code=201, response_model=SesionOut)
def crear_sesion_mesa(mesa_id: int, _=Depends(requerir_roles("gm", "admin"))):
    """El GM crea una sesión de juego de la mesa (para el pase de asistencia)."""
    return crear_sesion_controller(mesa_id)


@router.post("/{mesa_id}/sesiones/{sesion_id}/confirmar")
def confirmar_sesion_mesa(
    mesa_id: int,
    sesion_id: int,
    request: Request,
    usuario: dict = Depends(requerir_roles("gm", "admin")),
):
    """Confirma la sesión y emite sesion.confirmada (notif + emails a miembros)."""
    return confirmar_sesion_controller(
        mesa_id,
        sesion_id,
        int(usuario["sub"]),
        correlation_id=request.scope.get("correlation_id"),
    )


@router.post("/{mesa_id}/sesiones/{sesion_id}/cerrar")
def cerrar_sesion_mesa(
    mesa_id: int,
    sesion_id: int,
    _=Depends(requerir_roles("gm", "admin")),
):
    return cerrar_sesion_controller(mesa_id, sesion_id)