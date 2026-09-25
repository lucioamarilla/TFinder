from fastapi import APIRouter, Query
from typing import Optional

from feed_api.app.controllers.wiki import obtener_wiki

router = APIRouter(prefix="/api/v1")


@router.get("/wiki")
def listar_wiki(mesa_id: Optional[str] = Query(default=None, alias="mesa_id")):
    return obtener_wiki(mesa_id)