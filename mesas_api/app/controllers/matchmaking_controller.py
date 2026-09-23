from mesas_api.app.models import matchmaking as matchmaking_model
from mesas_api.app.services import llamado as llamado_service


def abrir(mesa_id: int) -> dict:
    registro = matchmaking_model.crear_o_reabrir(mesa_id)
    efimero = llamado_service.abrir_llamado(registro["id"])
    return {**_iso(registro), **efimero}


def estado(mm_id: int) -> dict:
    return llamado_service.estado_llamado(mm_id)


def _iso(obj):
    if "llamada_abierta_at" in obj:
        obj = {**obj, "llamada_abierta_at": matchmaking_model._iso(obj["llamada_abierta_at"])}
    return obj