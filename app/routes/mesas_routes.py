from fastapi import APIRouter, Response

from app.controllers.mesas_controller import (
    actualizar_mesa_controller,
    crear_mesa_controller,
    eliminar_mesa_controller,
    listar_mesas_controller,
    obtener_mesa_controller,
)
from app.models.mesas_model import MesaCreate, MesaOut, MesaUpdate

router = APIRouter(prefix="/api/v1/mesas")


@router.get("", response_model=list[MesaOut])
def listar_mesas():
    return listar_mesas_controller()


@router.get("/{mesa_id}", response_model=MesaOut)
def obtener_mesa(mesa_id: int):
    return obtener_mesa_controller(mesa_id)


@router.post("", response_model=MesaOut, status_code=201)
def crear_mesa(payload: MesaCreate):
    return crear_mesa_controller(payload)


@router.put("/{mesa_id}", response_model=MesaOut)
def actualizar_mesa(mesa_id: int, payload: MesaUpdate):
    return actualizar_mesa_controller(mesa_id, payload)


@router.delete("/{mesa_id}", status_code=204)
def eliminar_mesa(mesa_id: int):
    eliminar_mesa_controller(mesa_id)
    return Response(status_code=204)