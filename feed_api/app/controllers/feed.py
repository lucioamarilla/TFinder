from fastapi import HTTPException

from feed_api.app.db import get_connection
from feed_api.app.schemas import PostOut

# Ordenes permitidos. Van interpolados en el SQL, asi que tienen que ser una
# lista blanca y no un parametro.bind.
ORDENES = {
    "id": "p.id",
    "recientes": "p.creado_en DESC, p.id DESC",
    "antiguos": "p.creado_en, p.id",
    "votos": "p.votos DESC, p.id DESC",
}

LIMITE_MAX = 100


class PostNotFoundError(Exception):
    pass


def _serializar(fila):
    f = dict(fila)
    f["autorId"] = f.pop("autor_id", None)
    f["autorNombre"] = f.pop("autor_nombre", None)
    f["totalComentarios"] = f.pop("total_comentarios", None)
    f.pop("creado_en", None)
    return PostOut(**f)


def listar_publicaciones(
    tipo: str = None,
    autor_id: str = None,
    etiqueta: str = None,
    orden: str = "id",
    limit: int = 50,
    offset: int = 0,
):
    """Lista el feed con filtros opcionales y paginacion.

    Los filtros son todos opcionales: sin ninguno devuelve el listado completo
    que devolvia antes. `orden` se valida contra ORDENES porque se interpola en
    la sentencia; el resto viaja como parametro bind.
    """
    if orden not in ORDENES:
        raise HTTPException(
            status_code=400,
            detail=f"orden invalido: usar uno de {', '.join(sorted(ORDENES))}",
        )
    if not 1 <= limit <= LIMITE_MAX:
        raise HTTPException(
            status_code=400, detail=f"limit debe estar entre 1 y {LIMITE_MAX}"
        )
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset no puede ser negativo")

    condiciones = []
    params = []
    if tipo:
        condiciones.append("p.tipo = %s")
        params.append(tipo)
    if autor_id:
        condiciones.append("p.autor_id = %s")
        params.append(autor_id)
    if etiqueta:
        condiciones.append("p.etiqueta = %s")
        params.append(etiqueta)

    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    with get_connection() as conn:
        filas = conn.execute(
            f"SELECT * FROM publicaciones p {where} ORDER BY {ORDENES[orden]} "
            f"LIMIT %s OFFSET %s",
            (*params, limit, offset),
        ).fetchall()
    return [_serializar(f) for f in filas]
