from mesas_api.app.models.sesiones import obtener_sesion, registrar_asistencia
from mesas_api.app.schemas import QrValidate
from mesas_api.app.services.qr_asistencia import (
    _Conflict,
    _Invalid,
    generar_sesion_qr,
    validar_sesion_qr,
)


class SesionNotFoundError(Exception):
    pass


def emitir_qr(sesion_id: int, usuario_id: int):
    if obtener_sesion(sesion_id) is None:
        raise SesionNotFoundError(f"Sesión {sesion_id} no encontrada")
    return generar_sesion_qr(sesion_id, usuario_id)


def validar_qr(sesion_id: int, body: QrValidate):
    if obtener_sesion(sesion_id) is None:
        raise SesionNotFoundError(f"Sesión {sesion_id} no encontrada")
    try:
        validar_sesion_qr(sesion_id, body.usuario_id, body.qr_data)
    except _Conflict:
        raise
    except _Invalid:
        raise
    registrar_asistencia(sesion_id, body.usuario_id)
    return {"asistencia": "registrada"}