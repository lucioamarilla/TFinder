from fastapi import APIRouter, Query
from typing import Optional

from builds_api.app.controllers.builds import (
    listar_builds,
    obtener_build,
)
from builds_api.app.schemas import BuildOut

router = APIRouter(prefix="/api/v1/builds")


@router.get("", response_model=list[BuildOut])
def listar_builds_endpoint(mesa_id: Optional[int] = Query(default=None, alias="mesa_id")):
    return listar_builds(mesa_id)


@router.get("/{build_id}", response_model=BuildOut)
def obtener_build_endpoint(build_id: int):
    return obtener_build(build_id)