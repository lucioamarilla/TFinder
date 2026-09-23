from mesas_api.app.models.mesa import obtener_mesa_por_id, ocupar_vacante
from mesas_api.app.models.solicitudes import (
    crear_solicitud,
    obtener_solicitud_por_key,
)
from mesas_api.app.services.eventos import publicar_aceptacion
from mesas_api.app.services.idem import guardar_resultado, obtener_resultado
from mesas_api.app.services.vacante import liberar, reservar


class CupoAgotadoError(Exception):
    pass


class SolicitudEnProcesoError(Exception):
    pass


class MesaNoExisteError(Exception):
    pass


def solicitar_union(mesa_id: int, usuario_id: int, idem_key: str = None):
    if idem_key:
        previo = obtener_resultado(idem_key)
        if previo is not None:
            return previo

        existente = obtener_solicitud_por_key(mesa_id, usuario_id, idem_key)
        if existente:
            guardar_resultado(idem_key, existente)
            return existente

    if obtener_mesa_por_id(mesa_id) is None:
        raise MesaNoExisteError(f"Mesa {mesa_id} no encontrada")

    if not reservar(mesa_id):
        raise SolicitudEnProcesoError(
            "Otra solicitud se está procesando para esta mesa, reintentá"
        )

    try:
        if not ocupar_vacante(mesa_id):
            raise CupoAgotadoError("Cupo agotado: no quedan vacantes")

        solicitud = crear_solicitud(
            mesa_id, usuario_id, estado="aceptada", idem_key=idem_key
        )
        if idem_key:
            guardar_resultado(idem_key, solicitud)
        publicar_aceptacion(mesa_id, usuario_id)
        return solicitud
    finally:
        liberar(mesa_id)