from notif_api.app.consumers._base import consumir
from notif_api.app.infra.amqp import COLA_SESION
from notif_api.app.models.notif import (
    evento_ya_procesado,
    guardar_notificacion,
    registrar_evento,
)

REGLA = {
    "sesion.confirmada": ("Sesión confirmada", "La sesión de la mesa {mesa_id} quedó confirmada"),
    "sesion.diario_publicado": ("Diario publicado", "Se publicó el diario de la sesión de la mesa {mesa_id}"),
}


def _procesar(mensaje: dict) -> bool:
    if evento_ya_procesado(mensaje["event_id"]):
        return True
    tipo = mensaje.get("tipo")
    regla = REGLA.get(tipo)
    if regla is None:
        return False
    titulo, plantilla = regla
    mesa_id = mensaje.get("mesa_id")
    guardar_notificacion(
        usuario_id=mensaje.get("usuario_id"),
        titulo=titulo,
        detalle=plantilla.format(mesa_id=mesa_id),
        entidad="sesion",
        enlace={"/mesas/{id}".format(id=mesa_id): "ver mesa"},
    )
    registrar_evento(mensaje["event_id"], tipo, {"mesa_id": mesa_id})
    return True


def run():
    consumir(COLA_SESION, _procesar)