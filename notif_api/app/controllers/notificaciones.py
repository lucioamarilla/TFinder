from notif_api.app.db import get_connection
from notif_api.app.schemas import NotificacionOut


class NotificacionNotFoundError(Exception):
    pass


def listar_notificaciones(solo_no_leidas=False):
    with get_connection() as conn:
        if solo_no_leidas:
            filas = conn.execute(
                "SELECT * FROM notificaciones WHERE leida = FALSE ORDER BY id DESC"
            ).fetchall()
        else:
            filas = conn.execute("SELECT * FROM notificaciones ORDER BY id DESC").fetchall()
    return [NotificacionOut(**dict(fila)) for fila in filas]