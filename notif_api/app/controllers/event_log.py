from datetime import datetime

from notif_api.app.db import get_connection
from notif_api.app.schemas import EventOut


def _serializar(fila):
    f = dict(fila)
    f["entidadTipo"] = f.pop("entidad_tipo", None)
    f["entidadId"] = f.pop("entidad_id", None)
    f["usuarioId"] = f.pop("usuario_id", None)
    ocurrido = f.pop("ocurrido_en", None)
    if isinstance(ocurrido, datetime):
        f["ocurridoEn"] = ocurrido.isoformat()
    else:
        f["ocurridoEn"] = ocurrido
    return EventOut(**f)


def listar_eventos(entidad_tipo=None, entidad_id=None):
    con_filtros = entidad_tipo is not None or entidad_id is not None
    with get_connection() as conn:
        if con_filtros:
            clausulas = []
            params = []
            if entidad_tipo:
                clausulas.append("entidad_tipo = %s")
                params.append(entidad_tipo)
            if entidad_id:
                clausulas.append("entidad_id = %s")
                params.append(entidad_id)
            where = " AND ".join(clausulas)
            filas = conn.execute(
                f"SELECT * FROM event_log WHERE {where} ORDER BY id DESC", tuple(params)
            ).fetchall()
        else:
            filas = conn.execute("SELECT * FROM event_log ORDER BY id DESC").fetchall()
    return [_serializar(f) for f in filas]