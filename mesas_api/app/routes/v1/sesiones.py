from fastapi import APIRouter, Depends

from mesas_api.app.controllers.sesiones_controller import (
    anotacion_controller,
    anotaciones_controller,
    marcar_asistencia_controller,
)
from mesas_api.app.middleware.auth import usuario_actual

router = APIRouter(prefix="/api/v1/sesiones", tags=["sesiones"])


@router.post("/{sesion_id}/asistencia", status_code=200)
def marcar_asistencia(sesion_id: int, usuario: dict = Depends(usuario_actual)):
    return marcar_asistencia_controller(sesion_id, usuario)