import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from notif_api.app.controllers.notificaciones import (
    NotificacionNotFoundError,
    listar_notificaciones,
    marcar_leida,
)
from notif_api.app.schemas import NotificacionOut
from notif_api.app.services.stream import hub

logger = logging.getLogger("tfinder.notif")

router = APIRouter(prefix="/api/v1")


@router.get("/notificaciones", response_model=list[NotificacionOut])
def listar_notificaciones_endpoint(
    solo_no_leidas: bool = Query(default=False, alias="solo_no_leidas"),
):
    return listar_notificaciones(solo_no_leidas)


@router.get("/notificaciones/stream")
def notificaciones_stream(
    usuario_id: Optional[int] = Query(default=None, alias="usuario_id"),
):
    """SSE: emite en vivo cada notificacion nueva (filtrable por usuario_id)."""

    async def generar():
        suscriptor = hub.suscribir(usuario_id)
        try:
            async for chunk in hub.iterar(suscriptor):
                yield chunk
        finally:
            hub.desuscribir(suscriptor)

    return StreamingResponse(
        generar(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.patch("/notificaciones/{id}/leida", response_model=NotificacionOut)
def marcar_leida_endpoint(id: int):
    try:
        return marcar_leida(id)
    except NotificacionNotFoundError:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")