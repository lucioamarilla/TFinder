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
    "mesa.solicitud_gm": ("Nueva solicitud de unión", "Un jugador pidió entrar a la mesa {mesa_id}"),
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
    gm_id = mensaje.get("gm_id")
    # RF-22/RF-23: la solicitud de unión avisa al GM de la mesa; el resto de los
    # eventos (aceptada/expulsada) avisan al jugador implicado.
    if tipo == "mesa.solicitada" and gm_id:
        usuario_id = gm_id
        titulo, plantilla = REGLA["mesa.solicitud_gm"]
        enlace_to = f"/mesas/{mesa_id}/gestion/solicitudes"
    else:
        usuario_id = mensaje.get("usuario_id") or gm_id
        enlace_to = f"/mesas/{mesa_id}"
    label = "revisar solicitudes" if tipo == "mesa.solicitada" else "ver mesa"
    notif_id = guardar_notificacion(
        usuario_id=usuario_id,
        titulo=titulo,
        detalle=plantilla.format(mesa_id=mesa_id),
        entidad="mesa",
        enlace={"label": label, "to": enlace_to},
    )
    hub.publicar(
        usuario_id,
        {
            "id": notif_id,
            "titulo": titulo,
            "detalle": plantilla.format(mesa_id=mesa_id),
            "entidad": "mesa",
            "enlace": {"label": label, "to": enlace_to},
        },
    )
    registrar_evento(
        mensaje["event_id"], tipo, {"mesa_id": mesa_id},
        correlation_id=mensaje.get("correlation_id", "-"),
    )
    return True


def run():
    consumir(COLA_MESA, _procesar)