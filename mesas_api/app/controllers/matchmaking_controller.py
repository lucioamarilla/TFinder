from mesas_api.app.controllers.solicitudes_controller import MesaNoExisteError
from mesas_api.app.models import matchmaking as matchmaking_model
from mesas_api.app.models.mesa import obtener_mesa_por_id
from mesas_api.app.services import llamado as llamado_service


def abrir(mesa_id: int) -> dict:
    # Sin esta comprobacion el INSERT de matchmaking_model.crear_o_reabrir
    # dispara un ForeignKeyViolation que nadie maneja y el endpoint responde
    # 500 en vez de 404. Mismo criterio que solicitud_union.
    if obtener_mesa_por_id(mesa_id) is None:
        raise MesaNoExisteError(f"Mesa {mesa_id} no encontrada")

    registro = matchmaking_model.crear_o_reabrir(mesa_id)
    efimero = llamado_service.abrir_llamado(registro["id"])
    return {**_iso(registro), **efimero}


def estado(mm_id: int) -> dict:
    return llamado_service.estado_llamado(mm_id)


def _iso(obj):
    if "llamada_abierta_at" in obj:
        obj = {**obj, "llamada_abierta_at": matchmaking_model._iso(obj["llamada_abierta_at"])}
    return obj