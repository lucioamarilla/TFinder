from feed_api.app.db import get_connection
from feed_api.app.schemas import PostOut


class PostNotFoundError(Exception):
    pass


def _serializar(fila):
    f = dict(fila)
    f["autorId"] = f.pop("autor_id", None)
    f["autorNombre"] = f.pop("autor_nombre", None)
    f["totalComentarios"] = f.pop("total_comentarios", None)
    f.pop("creado_en", None)
    return PostOut(**f)


def listar_publicaciones():
    with get_connection() as conn:
        filas = conn.execute("SELECT * FROM publicaciones ORDER BY id").fetchall()
    return [_serializar(f) for f in filas]