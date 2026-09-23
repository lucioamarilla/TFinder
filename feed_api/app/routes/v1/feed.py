from fastapi import APIRouter

from feed_api.app.controllers.feed import listar_publicaciones
from feed_api.app.schemas import PostOut

router = APIRouter(prefix="/api/v1")


@router.get("/feed", response_model=list[PostOut])
def listar_feed():
    return listar_publicaciones()