from fastapi import APIRouter, Depends, Request, Response

from mesas_api.app.controllers.mesas import (
    actualizar_mesa_controller,
    crear_mesa_controller,
    eliminar_mesa_controller,
    listar_mesas_controller,
    obtener_mesa_controller,
)
from mesas_api.app.controllers.sesiones_controller import SesionNotFoundError
from mesas_api.app.middleware.auth import usuario_actual
from mesas_api.app.models.sesiones import listar_miembros
from mesas_api.app.schemas import MesaCreate, MesaOut, MesaUpdate
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