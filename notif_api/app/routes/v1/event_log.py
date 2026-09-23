from fastapi import APIRouter, Query
from typing import Optional

from notif_api.app.controllers.event_log import listar_eventos
from notif_api.app.schemas import EventOut

router = APIRouter(prefix="/api/v1")


@router.get("/event-log", response_model=list[EventOut])
def listar_eventos_endpoint(
    entidad_tipo: Optional[str] = Query(default=None, alias="entidad_tipo"),
    entidad_id: Optional[str] = Query(default=None, alias="entidad_id"),
):
    return listar_eventos(entidad_tipo, entidad_id)