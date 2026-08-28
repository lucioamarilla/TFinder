from app.models.mesas_model import (
    MesaCreate,
    MesaOut,
    MesaUpdate,
    actualizar_mesa,
    crear_mesa,
    eliminar_mesa,
    listar_mesas,
    obtener_mesa_por_id,
)


class MesaNotFoundError(Exception):
    def __init__(self, mesa_id):
        self.mesa_id = mesa_id
        super().__init__(f"Mesa {mesa_id} no encontrada")


def listar_mesas_controller():
    filas = listar_mesas()
    return [MesaOut(**fila) for fila in filas]


def obtener_mesa_controller(mesa_id):
    fila = obtener_mesa_por_id(mesa_id)
    if fila is None:
        raise MesaNotFoundError(mesa_id)
    return MesaOut(**fila)


def crear_mesa_controller(data: MesaCreate):
    fila = crear_mesa(data)
    return MesaOut(**fila)


def actualizar_mesa_controller(mesa_id, data: MesaUpdate):
    obtener_mesa_controller(mesa_id)
    fila = actualizar_mesa(mesa_id, data)
    return MesaOut(**fila)


def eliminar_mesa_controller(mesa_id):
    obtener_mesa_controller(mesa_id)
    eliminar_mesa(mesa_id)