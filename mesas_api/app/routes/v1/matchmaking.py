from fastapi import APIRouter, Depends

from mesas_api.app.controllers import matchmaking_controller
from mesas_api.app.middleware.auth import requerir_roles

router = APIRouter(prefix="/api/v1/matchmaking", tags=["matchmaking"])


@router.post("/{mesa_id}/abrir")
def abrir_llamado(mesa_id: int, _=Depends(requerir_roles("gm"))):
    return matchmaking_controller.abrir(mesa_id)


@router.get("/{mm_id}/estado")
def estado_llamado(mm_id: int):
    return matchmaking_controller.estado(mm_id)