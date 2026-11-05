from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel

from builds_api.app.controllers.builds import (
    asignar_tags,
    actualizar_build,
    crear_build,
    desvincular_build,
    eliminar_build,
    listar_builds_filtradas,
    obtener_build,
    publicar_build,
    restaurar_build,
    vincular_build,
)
from builds_api.app.middleware.auth import auth_opcional, usuario_actual
from builds_api.app.schemas import BuildOut

router = APIRouter(prefix="/api/v1/builds")


class ParesTags(BaseModel):
    nombres: list[str] = []


@router.get("", response_model=list[BuildOut])
def listar_builds_endpoint(
    request: Request,
    mesa_id: Optional[int] = Query(default=None, alias="mesa_id"),
    autor_id: Optional[str] = Query(default=None),
    tag: Optional[str] = Query(default=None, max_length=48),
):
    """Listado público; oculta 'borrador'/'privado' de otras personas (RN-11)."""
    listado = listar_builds_filtradas(mesa_id=mesa_id, autor_id=autor_id, tag=tag)
    usuario = auth_opcional(request)
    if usuario is None:
        return [b for b in listado if b.privacidad == "publico"]
    es_admin = usuario.get("rol") == "admin"
    propio = lambda b: b.autorId is not None and str(b.autorId) == str(usuario["sub"])
    return [b for b in listado if b.privacidad == "publico" or es_admin or propio(b)]


@router.get("/{build_id}", response_model=BuildOut)
def obtener_build_endpoint(build_id: int):
    return obtener_build(build_id)


@router.post("", response_model=BuildOut, status_code=201)
def crear_build_endpoint(payload: dict, usuario: dict = Depends(usuario_actual)):
    """RF-19: crear build (VAL-44/45) — nace 'borrador' y publicable después."""
    return crear_build(usuario, payload)


@router.put("/{build_id}", response_model=BuildOut)
def actualizar_build_endpoint(
    build_id: int, payload: dict, usuario: dict = Depends(usuario_actual)
):
    """RN-11/VAL-38 + RN-19: edita el propio y apila la versión previa."""
    return actualizar_build(build_id, usuario, payload)


@router.delete("/{build_id}", status_code=204)
def eliminar_build_endpoint(build_id: int, usuario: dict = Depends(usuario_actual)):
    eliminar_build(build_id, usuario)
    return None


@router.post("/{build_id}/publicar", response_model=BuildOut)
def publicar_build_endpoint(build_id: int, usuario: dict = Depends(usuario_actual)):
    """RF-20: publicar lo vuelve público (RN-14: solo el creador)."""
    return publicar_build(build_id, usuario)


@router.post("/{build_id}/vincular/{mesa_id}", response_model=BuildOut)
def vincular_build_endpoint(
    build_id: int,
    mesa_id: int,
    request: Request,
    usuario: dict = Depends(usuario_actual),
):
    """RF-21/RN-12/VAL-40: solo si el creador es miembro aceptado de la mesa."""
    return vincular_build(build_id, mesa_id, usuario, request.headers.get("Authorization"))


@router.delete("/{build_id}/vincular", response_model=BuildOut)
def desvincular_build_endpoint(build_id: int, usuario: dict = Depends(usuario_actual)):
    return desvincular_build(build_id, usuario)


@router.post("/{build_id}/restaurar/{indice}", response_model=BuildOut)
def restaurar_build_endpoint(
    build_id: int, indice: int, usuario: dict = Depends(usuario_actual)
):
    """RN-19: restaura una versión anterior del historial."""
    return restaurar_build(build_id, indice, usuario)


@router.post("/{build_id}/tags")
def asignar_tags_endpoint(
    build_id: int,
    payload: ParesTags,
    request: Request,
    usuario: dict = Depends(usuario_actual),
):
    return asignar_tags(build_id, usuario, payload.nombres, request.headers.get("Authorization"))
