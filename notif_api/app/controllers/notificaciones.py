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


def listar_notificaciones(usuario_id, solo_no_leidas=False):
    with get_connection() as conn:
        if solo_no_leidas:
            filas = conn.execute(
                "SELECT * FROM notificaciones"
                " WHERE (usuario_id = %s OR usuario_id IS NULL) AND leida = FALSE"
                " ORDER BY id DESC",
                (usuario_id,),
            ).fetchall()
        else:
            filas = conn.execute(
                "SELECT * FROM notificaciones"
                " WHERE usuario_id = %s OR usuario_id IS NULL"
                " ORDER BY id DESC",
                (usuario_id,),
            ).fetchall()
    return [NotificacionOut(**_dict_fila(fila)) for fila in filas]


def marcar_leida(id: int, usuario_id):
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE notificaciones SET leida = TRUE"
            " WHERE id = %s AND (usuario_id = %s OR usuario_id IS NULL)"
            " RETURNING *",
            (id, usuario_id),
        )
        fila = cursor.fetchone()
        if fila is None:
            raise NotificacionNotFoundError(id)
    return NotificacionOut(**_dict_fila(fila))
