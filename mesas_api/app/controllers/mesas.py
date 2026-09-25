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


def _formatear_fila(fila):
    if fila and isinstance(fila.get("fecha_creacion"), datetime):
        fila = {**fila, "fecha_creacion": fila["fecha_creacion"].isoformat()}
    return fila


def listar_mesas_controller():
    cache = obtener_listado_cachead()
    if cache is not None:
        return cache
    listado = [
        MesaOut(**fila).model_dump()
        for fila in (_formatear_fila(f) for f in listar_mesas())
        if fila
    ]
    guardar_listado(listado)
    return listado


def obtener_mesa_controller(mesa_id):
    fila = _formatear_fila(obtener_mesa_por_id(mesa_id))
    if fila is None:
        raise MesaNotFoundError(mesa_id)
    return MesaOut(**fila)


def crear_mesa_controller(data: MesaCreate):
    mesa = MesaOut(**(_formatear_fila(crear_mesa(data))))
    invalidar_listado()
    return mesa


def actualizar_mesa_controller(mesa_id, data: MesaUpdate):
    fila = _formatear_fila(obtener_mesa_por_id(mesa_id))
    if fila is None:
        raise MesaNotFoundError(mesa_id)
    mesa = MesaOut(**(_formatear_fila(actualizar_mesa(mesa_id, data))))
    invalidar_listado()
    return mesa


def eliminar_mesa_controller(mesa_id):
    fila = _formatear_fila(obtener_mesa_por_id(mesa_id))
    if fila is None:
        raise MesaNotFoundError(mesa_id)
    eliminar_mesa(mesa_id)
    invalidar_listado()