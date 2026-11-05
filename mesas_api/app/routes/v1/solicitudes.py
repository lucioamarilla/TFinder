from fastapi import APIRouter, Depends, Header, Request
from typing import Literal

from mesas_api.app.controllers.solicitudes_controller import (
    crear_solicitud_controller,
    listar_solicitudes_controller,
    responder_solicitud_controller,
)
from mesas_api.app.middleware.auth import usuario_actual

router = APIRouter(prefix="/api/v1/mesas/{mesa_id}/solicitudes", tags=["solicitudes"])


@router.post("", status_code=201)
def crear_solicitud(
    mesa_id: int,
    request: Request,
    idempotency_key: str = Header(alias="Idempotency-Key", default=None),
    usuario: dict = Depends(usuario_actual),
):
    """RF-14: solicitud 'pendiente'; idempotente por Idempotency-Key (RF-24)."""
    return crear_solicitud_controller(
        mesa_id,
        int(usuario["sub"]),
        idem_key=idempotency_key,
        correlation_id=request.scope.get("correlation_id"),
    )


@router.get("")
def listar_solicitudes(
    mesa_id: int,
    estado: Literal["pendiente", "aceptada", "rechazada"] | None = None,
    usuario: dict = Depends(usuario_actual),
):
    """Bandeja del GM propietario (RF-15)."""
    return listar_solicitudes_controller(mesa_id, usuario, estado=estado)


@router.post("/{solicitud_id}/aceptar")
def aceptar_solicitud(
    mesa_id: int,
    solicitud_id: int,
    request: Request,
    usuario: dict = Depends(usuario_actual),
):
    """RF-15/RN-08: aceptar hace miembro (cupo atómico). VAL-23: solo el GM."""
    return responder_solicitud_controller(
        mesa_id,
        solicitud_id,
        "aceptar",
        usuario,
        correlation_id=request.scope.get("correlation_id"),
    )


@router.post("/{solicitud_id}/rechazar")
def rechazar_solicitud(
    mesa_id: int,
    solicitud_id: int,
    request: Request,
    usuario: dict = Depends(usuario_actual),
):
    """RF-15: rechazar cierra la solicitud (sin consumir cupo)."""
    return responder_solicitud_controller(
        mesa_id,
        solicitud_id,
        "rechazar",
        usuario,
        correlation_id=request.scope.get("correlation_id"),
    )
