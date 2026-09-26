from fastapi import APIRouter, Query

from feed_api.app.controllers.feed import LIMITE_MAX, listar_publicaciones
from feed_api.app.schemas import PostOut

router = APIRouter(prefix="/api/v1")


@router.get("/feed", response_model=list[PostOut])
def listar_feed(
    tipo: str | None = Query(
        None, description="post | build | wiki", pattern="^(post|build|wiki)$"
    ),
    autor_id: str | None = Query(None, description="Id del autor, tal como se publico"),
    etiqueta: str | None = Query(None, description="Etiqueta exacta de la publicacion"),
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
        orden=orden,
        limit=limit,
        offset=offset,
    )
