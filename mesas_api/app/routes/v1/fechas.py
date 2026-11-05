from typing import Literal

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from mesas_api.app.controllers import fechas_controller
from mesas_api.app.middleware.auth import usuario_actual

router = APIRouter(prefix="/api/v1/mesas/{mesa_id}/fechas", tags=["calendario"])


class PropuestaFecha(BaseModel):
    propuesta: str


class VotoValor(BaseModel):
    valor: Literal["a_favor", "en_contra"]


@router.post("", status_code=201)
def proponer_fecha(mesa_id: int, payload: PropuestaFecha, usuario: dict = Depends(usuario_actual)):
    """RF-10: el GM propone una fecha (VAL-29: no en el pasado)."""
    return fechas_controller.proponer_controller(mesa_id, usuario, payload.propuesta)


@router.get("")
def listar_fechas(mesa_id: int, usuario: dict = Depends(usuario_actual)):
    return fechas_controller.listar_controller(mesa_id, usuario)


@router.post("/{fecha_id}/voto")
def votar_fecha(
    mesa_id: int,
    fecha_id: int,
    payload: VotoValor,
    usuario: dict = Depends(usuario_actual),
):
    """RF-11/RN-06: voto editable a favor/en contra de un miembro."""
    return fechas_controller.votar_controller(mesa_id, fecha_id, usuario, payload.valor)


@router.delete("/{fecha_id}")
def descartar_fecha(mesa_id: int, fecha_id: int, usuario: dict = Depends(usuario_actual)):
    return fechas_controller.descartar_controller(mesa_id, fecha_id, usuario)


@router.post("/{fecha_id}/confirmar")
def confirmar_fecha(
    mesa_id: int,
    fecha_id: int,
    request: Request,
    usuario: dict = Depends(usuario_actual),
):
    """CA: la fecha ganadora confirmada nace sesión de juego."""
    return fechas_controller.confirmar_controller(
        mesa_id,
        fecha_id,
        usuario,
    )
