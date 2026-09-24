import logging

from fastapi import APIRouter, HTTPException, Query

from notif_api.app.controllers.notificaciones import (
    NotificacionNotFoundError,
    listar_notificaciones,
    marcar_leida,
)
from notif_api.app.schemas import NotificacionOut

logger = logging.getLogger("tfinder.notif")

router = APIRouter(prefix="/api/v1")


@router.get("/notificaciones", response_model=list[NotificacionOut])
def listar_notificaciones_endpoint(
    solo_no_leidas: bool = Query(default=False, alias="solo_no_leidas"),
):
    return listar_notificaciones(solo_no_leidas)


@router.patch("/notificaciones/{id}/leida", response_model=NotificacionOut)
def marcar_leida_endpoint(id: int):
    try:
        return marcar_leida(id)
    except NotificacionNotFoundError:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")