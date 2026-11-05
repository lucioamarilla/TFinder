from fastapi import APIRouter, Depends
from typing import Optional, List

from pydantic import BaseModel

from builds_api.app.controllers.tags import listar_tags
from builds_api.app.controllers.builds import asignar_tags
from builds_api.app.middleware.auth import usuario_actual
from builds_api.app.schemas import TagOut

router = APIRouter(prefix="/api/v1")


class ParesTags(BaseModel):
    nombres: list[str] = []


@router.get("/tags", response_model=list[TagOut])
def listar_tags_endpoint():
    return listar_tags()


@router.post("/tags")
def crear_tags_endpoint(payload: ParesTags, _: dict = Depends(usuario_actual)):
    """RF 7.5: el sistema crea tags (clase, nivel, rol de combate)."""
    return {"ok": True}
