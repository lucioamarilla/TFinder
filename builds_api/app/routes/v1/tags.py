from fastapi import APIRouter

from builds_api.app.controllers.tags import listar_tags

router = APIRouter(prefix="/api/v1")


@router.get("/tags")
def listar_tags_endpoint():
    return listar_tags()