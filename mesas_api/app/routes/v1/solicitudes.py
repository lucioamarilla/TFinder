from fastapi import APIRouter, Depends, Header

from mesas_api.app.controllers.solicitudes_controller import solicitar_union
from mesas_api.app.middleware.auth import usuario_actual

router = APIRouter(prefix="/api/v1/mesas/{mesa_id}/solicitudes", tags=["solicitudes"])


@router.post("", status_code=201)
def crear_solicitud(
    mesa_id: int,
    idempotency_key: str = Header(alias="Idempotency-Key", default=None),
    usuario: dict = Depends(usuario_actual),
):
    return solicitar_union(mesa_id, int(usuario["sub"]), idempotency_key)