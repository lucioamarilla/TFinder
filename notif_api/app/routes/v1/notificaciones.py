import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from notif_api.app.controllers.notificaciones import (
    NotificacionNotFoundError,
    listar_notificaciones,
    marcar_leida,
)
from notif_api.app.middleware.auth import usuario_actual
from notif_api.app.schemas import NotificacionOut
from notif_api.app.services.stream import hub

logger = logging.getLogger("tfinder.notif")

router = APIRouter(prefix="/api/v1")


@router.get("/notificaciones", response_model=list[NotificacionOut])
def listar_notificaciones_endpoint(
    usuario: dict = Depends(usuario_actual),
    solo_no_leidas: bool = Query(default=False, alias="solo_no_leidas"),
):
    return listar_notificaciones(int(usuario["sub"]), solo_no_leidas)


@router.get("/notificaciones/stream")
def notificaciones_stream(usuario: dict = Depends(usuario_actual)):
    """SSE: emite en vivo cada notificacion nueva (solo del usuario autenticado)."""

    usuario_id = int(usuario["sub"])

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
def marcar_leida_endpoint(id: int, usuario: dict = Depends(usuario_actual)):
    try:
        return marcar_leida(id, int(usuario["sub"]))
    except NotificacionNotFoundError:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
