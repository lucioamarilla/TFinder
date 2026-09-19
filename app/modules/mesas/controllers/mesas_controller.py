from app.modules.mesas.models.mesas_model import (
    actualizar_mesa,
    crear_mesa,
    eliminar_mesa,
    listar_mesas,
    obtener_mesa_por_id,
)
from app.modules.mesas.schemas.mesas_schema import MesaCreate, MesaOut, MesaUpdate


class MesaNotFoundError(Exception):
    def __init__(self, mesa_id):
        self.mesa_id = mesa_id
        super().__init__(f"Mesa {mesa_id} no encontrada")


def listar_mesas_controller():
    return [MesaOut(**fila) for fila in listar_mesas()]


def obtener_mesa_controller(mesa_id):
    fila = obtener_mesa_por_id(mesa_id)
    if fila is None:
        raise MesaNotFoundError(mesa_id)
    return MesaOut(**fila)


def crear_mesa_controller(data: MesaCreate):
    return MesaOut(**crear_mesa(data))


def actualizar_mesa_controller(mesa_id, data: MesaUpdate):
    fila = obtener_mesa_por_id(mesa_id)
    if fila is None:
        raise MesaNotFoundError(mesa_id)
    return MesaOut(**actualizar_mesa(mesa_id, data))


def eliminar_mesa_controller(mesa_id):
    fila = obtener_mesa_por_id(mesa_id)
    if fila is None:
        raise MesaNotFoundError(mesa_id)
    eliminar_mesa(mesa_id)
