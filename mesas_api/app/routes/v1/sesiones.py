from fastapi import APIRouter, Depends

from mesas_api.app.controllers.sesiones_controller import (
    emitir_qr,
    validar_qr,
    anotacion_controller,
    anotaciones_controller,
)
from mesas_api.app.middleware.auth import usuario_actual
from mesas_api.app.models.mesa import rol_de


def _rol_de(mesa_id, usuario):
    return rol_de(mesa_id, int(usuario["sub"]))
from mesas_api.app.schemas import QROut, QrValidate

router = APIRouter(prefix="/api/v1/sesiones", tags=["sesiones"])


@router.post("/{sesion_id}/qr", status_code=201, response_model=QROut)
def emitir(sesion_id: int, usuario: dict = Depends(usuario_actual)):
    return emitir_qr(sesion_id, int(usuario["sub"]))


@router.post("/{sesion_id}/qr/validar", status_code=200)
def validar(
    sesion_id: int,
    body: QrValidate,
    usuario: dict = Depends(usuario_actual),
):
    """Solo el master de la mesa registra asistencia (validado por sesion)."""
    return validar_qr(sesion_id, body, usuario)


