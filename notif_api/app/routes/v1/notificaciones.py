from fastapi import APIRouter, Query

from notif_api.app.controllers.notificaciones import listar_notificaciones
from notif_api.app.schemas import NotificacionOut

router = APIRouter(prefix="/api/v1")


@router.get("/notificaciones", response_model=list[NotificacionOut])
def listar_notificaciones_endpoint(
    solo_no_leidas: bool = Query(default=False, alias="solo_no_leidas"),
):
    return listar_notificaciones(solo_no_leidas)