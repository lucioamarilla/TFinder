from datetime import datetime

from mesas_api.app.models.mesa import (
    actualizar_mesa,
    crear_mesa,
    eliminar_mesa,
    listar_mesas,
    obtener_mesa_por_id,
)
from mesas_api.app.schemas import MesaCreate, MesaOut, MesaUpdate
from mesas_api.app.services.cache import (
    guardar_listado,
    invalidar_listado,
    obtener_listado_cachead,
)


class MesaNotFoundError(Exception):
    def __init__(self, mesa_id):
        self.mesa_id = mesa_id
        super().__init__(f"Mesa {mesa_id} no encontrada")


class MesaUsurpadoError(Exception):
    """403 (VAL-17): solo el GM propietario (o admin) habla por la mesa."""


class CupoMenorError(Exception):
    """409 (VAL-15): no se puede bajar el cupo debajo de los jugadores actuales."""


def _formatear_fila(fila):
    if fila and isinstance(fila.get("fecha_creacion"), datetime):
        fila = {**fila, "fecha_creacion": fila["fecha_creacion"].isoformat()}
    return fila


def _es_admin(usuario) -> bool:
    return (usuario or {}).get("rol") == "admin"


def _asegurar_propietario(usuario, mesa):
    """RN-02/VAL-17: solo el GM propietario (o admin de plataforma)."""
    sub = int((usuario or {}).get("sub", -1))
    if mesa.get("gm_id") is not None and sub == mesa["gm_id"]:
        return
    if _es_admin(usuario):
        return
    raise MesaUsurpadoError("No tienes permisos para modificar o eliminar esta mesa.")


def listar_mesas_controller(estado=None, sistema=None, tono=None, orden="id", page=1, limit=20):
    """RF-04/13. Con Redis sano usa caché (X-Cache: HIT); si falla, BD (MISS)."""
    import json as _json

    cacheada = (
        estado is None
        and sistema is None
        and tono is None
        and orden == "id"
        and page == 1
        and limit == 20
    )
    tier = "MISS"
    cache = None
    if cacheada:
        try:
            cache = obtener_listado_cachead()
            if cache is not None:
                tier = "HIT"
        except Exception:
            # CA-51: Redis caído → modo degradado: se responde desde la BD.
            cache = None
            tier = "MISS"
    if cache is not None:
        return cache, tier
    listado = [
        MesaOut(**fila).model_dump()
        for fila in (_formatear_fila(f) for f in listar_mesas(estado, sistema, tono, orden, page, limit))
        if fila
    ]
    if cacheada:
        try:
            guardar_listado(listado)
        except Exception:
            pass
    return listado, tier


def obtener_mesa_controller(mesa_id):
    fila = _formatear_fila(obtener_mesa_por_id(mesa_id))
    if fila is None:
        raise MesaNotFoundError(mesa_id)
    return MesaOut(**fila)


def crear_mesa_controller(data: MesaCreate, usuario):
    fila_bruta = crear_mesa(data, gm_id=int(usuario["sub"]))
    mesa = MesaOut(**(_formatear_fila(fila_bruta)))
    invalidar_listado()
    return mesa


def actualizar_mesa_controller(mesa_id, data: MesaUpdate, usuario):
    fila = _formatear_fila(obtener_mesa_por_id(mesa_id))
    if fila is None:
        raise MesaNotFoundError(mesa_id)
    _asegurar_propietario(usuario, fila)
    cambios = data.model_dump(exclude_unset=True)
    nuevo_cupo = cambios.get("jugadores_max")
    if nuevo_cupo is not None and fila["jugadores_actuales"] > nuevo_cupo:
        raise CupoMenorError(
            "El cupo máximo no puede ser menor que el número actual de jugadores en la mesa."
        )
    mesa = MesaOut(**(_formatear_fila(actualizar_mesa(mesa_id, data))))
    invalidar_listado()
    return mesa


def eliminar_mesa_controller(mesa_id, usuario):
    fila = _formatear_fila(obtener_mesa_por_id(mesa_id))
    if fila is None:
        raise MesaNotFoundError(mesa_id)
    _asegurar_propietario(usuario, fila)
    eliminar_mesa(mesa_id)
    invalidar_listado()
    try:
        from app.infra.rabbitmq import publicar

        publicar("mesa.eliminada", {"mesa_id": mesa_id}, correlation_id="-")
    except Exception:
        pass