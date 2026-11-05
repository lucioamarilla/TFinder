from typing import Optional

from fastapi import HTTPException
from psycopg import errors as pg_errors
from pydantic import BaseModel

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


class PostCreate(BaseModel):
    """RF-16: contenido de la publicación (VAL-41: no vacío)."""

    titulo: str
    cuerpo: str
    tipo: str = "post"
    etiqueta: Optional[str] = None
    autor: Optional[str] = None


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


# ---- P1.7: feed activo (RF-16/17/18) -----------------------------------------

def crear_publicacion(usuario, datos):
    """RF-16: usuario autenticado publica su contenido (VAL-41 no vacío)."""
    if hasattr(datos, "model_dump"):
        datos = datos.model_dump()
    titulo = (datos.get("titulo") or "").strip()
    cuerpo = (datos.get("cuerpo") or "").strip()
    if not titulo or not cuerpo:
        raise HTTPException(status_code=400, detail="El contenido de la publicación no puede estar vacío.")
    tipo = datos.get("tipo") or "post"
    if tipo not in ("post", "build", "wiki"):
        raise HTTPException(status_code=400, detail="El tipo debe ser post, build o wiki.")
    nombre = usuario.get("email", "").split("@")[0]
    with get_connection() as conn:
        fila = conn.execute(
            "INSERT INTO publicaciones (tipo, autor_id, autor_nombre, iniciales,"
            " tiempo, titulo, cuerpo, etiqueta, horas)"
            " VALUES (%s, %s, %s, %s, 'ahora', %s, %s, %s, 0) RETURNING *",
            (
                tipo,
                str(usuario["sub"]),
                datos.get("autor") or nombre or "Autor",
                (nombre or "AV")[:2].upper(),
                titulo,
                cuerpo,
                datos.get("etiqueta"),
            ),
        ).fetchone()
    return _serializar(fila)


def dar_like(post_id: int, usuario_id: str):
    """RF-17/VAL-43: like único por usuario — si ya existe lo quita (toggle)."""
    with get_connection() as conn, conn.transaction():
        fila = conn.execute(
            "SELECT id FROM publicaciones WHERE id = %s", (post_id,)
        ).fetchone()
        if fila is None:
            raise HTTPException(status_code=404, detail="La publicación no existe.")
        ya = conn.execute(
            "SELECT 1 FROM likes_post WHERE post_id = %s AND usuario_id = %s",
            (post_id, usuario_id),
        ).fetchone()
        if ya:
            conn.execute(
                "DELETE FROM likes_post WHERE post_id = %s AND usuario_id = %s",
                (post_id, usuario_id),
            )
            conn.execute(
                "UPDATE publicaciones SET votos = greatest(votos - 1, 0) WHERE id = %s",
                (post_id,),
            )
            megusta = False
        else:
            conn.execute(
                "INSERT INTO likes_post (post_id, usuario_id) VALUES (%s, %s)",
                (post_id, usuario_id),
            )
            conn.execute(
                "UPDATE publicaciones SET votos = votos + 1 WHERE id = %s",
                (post_id,),
            )
            megusta = True
        total = conn.execute(
            "SELECT votos FROM publicaciones WHERE id = %s", (post_id,)
        ).fetchone()
    return {"id": post_id, "votos": total["votos"], "megusta": megusta}


def seguir_a(objetivo_id: str, seguidor_id: str):
    """RF-18/RN-10: sigue, no duplica y no autofollow."""
    if objetivo_id == seguidor_id:
        raise HTTPException(status_code=409, detail="No puedes seguirte a ti mismo.")
    with get_connection() as conn, conn.transaction():
        try:
            conn.execute(
                "INSERT INTO follows (seguidor_id, seguido_id) VALUES (%s, %s)",
                (seguidor_id, objetivo_id),
            )
        except pg_errors.UniqueViolation:
            raise HTTPException(
                status_code=409, detail="Ya sigues a este usuario."
            ) from None
        conteo = conn.execute(
            "SELECT COUNT(*) AS total FROM follows WHERE seguido_id = %s", (objetivo_id,)
        ).fetchone()
    return {"objetivo_id": objetivo_id, "seguidores": int(conteo["total"])}


def listar_siguimientos(objetivo_id: str):
    with get_connection() as conn:
        conteo = conn.execute(
            "SELECT COUNT(*) AS total FROM follows WHERE seguido_id = %s", (objetivo_id,)
        ).fetchone()
    return {"objetivo_id": objetivo_id, "seguidores": int(conteo["total"])}
