from fastapi import APIRouter, Depends, Query

from feed_api.app.controllers.feed import (
    LIMITE_MAX,
    PostCreate,
    crear_publicacion,
    dar_like,
    listar_comunidades,
    listar_publicaciones,
    listar_siguimientos,
    seguir_a,
)
from feed_api.app.middleware.auth import usuario_actual
from feed_api.app.schemas import PostOut

router = APIRouter(prefix="/api/v1")


@router.get("/feed/comunidades")
def listar_comunidades_endpoint():
    """F1: lista real de comunidades del feed (conteo de publicaciones)."""
    return listar_comunidades()


@router.get("/feed", response_model=list[PostOut])
def listar_feed(
    tipo: str | None = Query(
        None, description="post | build | wiki", pattern="^(post|build|wiki)$"
    ),
    autor_id: str | None = Query(None, description="Id del autor, tal como se publico"),
    etiqueta: str | None = Query(None, description="Etiqueta exacta de la publicacion"),
    comunidad: str | None = Query(None, description="Comunidad exacta (sin prefijo t/)"),
    orden: str = Query("id", description="id | recientes | antiguos | votos"),
    limit: int = Query(50, ge=1, le=LIMITE_MAX, description="Cantidad maxima de items"),
    offset: int = Query(0, ge=0, description="Cantidad de items a saltear"),
):
    """Feed social con filtros y paginacion.

    Sin parametros devuelve el listado completo. `tipo` se valida con un patron
    para que un valor invalido produzca 400 de validacion y no un filtro vacio.
    """
    return listar_publicaciones(
        tipo=tipo,
        autor_id=autor_id,
        etiqueta=etiqueta,
        comunidad=comunidad,
        orden=orden,
        limit=limit,
        offset=offset,
    )


@router.post("/feed", response_model=PostOut, status_code=201)
def publicar_feed(payload: PostCreate, usuario: dict = Depends(usuario_actual)):
    """RF-16: el usuario autenticado publica su contenido (VAL-41)."""
    return crear_publicacion(usuario, payload)


@router.post("/feed/{post_id}/like")
def dar_like_a(post_id: int, usuario: dict = Depends(usuario_actual)):
    """RF-17/VAL-43: like único por usuario (toggle)."""
    return dar_like(post_id, str(usuario["sub"]))


@router.post("/usuarios/{usuario_id}/seguir")
def seguir(usuario_id: str, usuario: dict = Depends(usuario_actual)):
    """RF-18/RN-10: seguir a otro usuario (sin duplicar ni autofollow)."""
    return seguir_a(str(usuario_id), str(usuario["sub"]))


@router.get("/usuarios/{usuario_id}/seguidores")
def seguidores(usuario_id: str):
    return listar_siguimientos(str(usuario_id))
