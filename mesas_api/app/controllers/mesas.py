from datetime import datetime

from mesas_api.app.models.mesa import (
    actualizar_mesa,
    crear_mesa,
    eliminar_mesa,
    listar_mesas,
    obtener_mesa_por_id,
)
from mesas_api.app.schemas import MesaCreate, MesaOut, MesaUpdate


class MesaNotFoundError(Exception):
    def __init__(self, mesa_id):
        self.mesa_id = mesa_id
        super().__init__(f"Mesa {mesa_id} no encontrada")


def _formatear_fila(fila):
    if fila and isinstance(fila.get("fecha_creacion"), datetime):
        fila = {**fila, "fecha_creacion": fila["fecha_creacion"].isoformat()}
    return fila


def listar_mesas_controller():
    return [MesaOut(**fila) for fila in (_formatear_fila(f) for f in listar_mesas()) if fila]


def obtener_mesa_controller(mesa_id):
    fila = _formatear_fila(obtener_mesa_por_id(mesa_id))
    if fila is None:
        raise MesaNotFoundError(mesa_id)
    return MesaOut(**fila)


def crear_mesa_controller(data: MesaCreate):
    return MesaOut(**(_formatear_fila(crear_mesa(data))))


def actualizar_mesa_controller(mesa_id, data: MesaUpdate):
    fila = _formatear_fila(obtener_mesa_por_id(mesa_id))
    if fila is None:
        raise MesaNotFoundError(mesa_id)
    return MesaOut(**(_formatear_fila(actualizar_mesa(mesa_id, data))))


def eliminar_mesa_controller(mesa_id):
    fila = _formatear_fila(obtener_mesa_por_id(mesa_id))
    if fila is None:
        raise MesaNotFoundError(mesa_id)
    eliminar_mesa(mesa_id)