from notif_api.app.consumers._base import consumir
from notif_api.app.infra.amqp import COLA_MESA
from notif_api.app.models.notif import (
    evento_ya_procesado,
    guardar_notificacion,
    registrar_evento,
)
from notif_api.app.services.stream import hub

REGLA = {
    "mesa.solicitada": ("Solicitud enviada", "Solicitaste unirte a la mesa {mesa_id}"),
    "mesa.aceptada": ("Solicitud aceptada", "Tu solicitud para la mesa {mesa_id} fue aceptada"),
    "mesa.expulsada": ("Expulsado de la mesa", "Fuiste expulsado de la mesa {mesa_id}"),
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
    usuario_id = mensaje.get("usuario_id")
    notif_id = guardar_notificacion(
        usuario_id=usuario_id,
        titulo=titulo,
        detalle=plantilla.format(mesa_id=mesa_id),
        entidad="mesa",
        enlace={"/mesas/{id}".format(id=mesa_id): "ver mesa"},
    )
    hub.publicar(
        usuario_id,
        {
            "id": notif_id,
            "titulo": titulo,
            "detalle": plantilla.format(mesa_id=mesa_id),
            "entidad": "mesa",
            "enlace": {"/mesas/{id}".format(id=mesa_id): "ver mesa"},
        },
    )
    registrar_evento(
        mensaje["event_id"], tipo, {"mesa_id": mesa_id},
        correlation_id=mensaje.get("correlation_id", "-"),
    )
    return True


def run():
    consumir(COLA_MESA, _procesar)