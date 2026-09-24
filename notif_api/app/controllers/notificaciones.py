from notif_api.app.db import get_connection
from notif_api.app.schemas import NotificacionOut


class NotificacionNotFoundError(Exception):
    pass


def _dict_fila(fila):
    datos = dict(fila)
    creado = datos.get("creado_en")
    if creado is not None:
        datos["creado_en"] = creado.isoformat()
    return datos


def listar_notificaciones(solo_no_leidas=False):
    with get_connection() as conn:
        if solo_no_leidas:
            filas = conn.execute(
                "SELECT * FROM notificaciones WHERE leida = FALSE ORDER BY id DESC"
            ).fetchall()
        else:
            filas = conn.execute("SELECT * FROM notificaciones ORDER BY id DESC").fetchall()
    return [NotificacionOut(**_dict_fila(fila)) for fila in filas]


def marcar_leida(id: int):
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE notificaciones SET leida = TRUE WHERE id = %s RETURNING *", (id,)
        )
        fila = cursor.fetchone()
        if fila is None:
            raise NotificacionNotFoundError(id)
    return NotificacionOut(**_dict_fila(fila))