from fastapi import APIRouter

from builds_api.app.controllers.tags import listar_tags
from builds_api.app.schemas import TagOut

router = APIRouter(prefix="/api/v1")


@router.get("/tags", response_model=list[TagOut])
def listar_tags_endpoint():
    return listar_tags()
