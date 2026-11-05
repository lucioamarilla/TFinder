from datetime import datetime

from fastapi import HTTPException

from mesas_api.app.controllers.mesas import obtener_mesa_controller
from mesas_api.app.models.sesiones import (
    cerrar_sesion_db,
    confirmar_sesion_db,
    crear_sesion_db,
    listar_sesiones_db,
    obtener_sesion,
    obtener_sesion_de_mesa,
    registrar_asistencia,
)
from mesas_api.app.schemas import SesionOut, QrValidate
from mesas_api.app.services.eventos import publicar_sesion_confirmada
from mesas_api.app.services.qr_asistencia import (
    _Conflict,
    _Invalid,
    generar_sesion_qr,
    validar_sesion_qr,
)


class SesionNotFoundError(Exception):
    pass


class SesionCerradaError(Exception):
    """Operación no válida: la sesión ya está cerrada."""


def _formatear_sesion(fila):
    if not fila:
        return fila
    salida = dict(fila)
    for clave in ("fecha", "confirmada_at"):
        valor = salida.get(clave)
        if isinstance(valor, datetime):
            salida[clave] = valor.isoformat()
    return salida


def emitir_qr(sesion_id: int, usuario_id: int):
    if obtener_sesion(sesion_id) is None:
        raise SesionNotFoundError(f"Sesión {sesion_id} no encontrada")
    return generar_sesion_qr(sesion_id, usuario_id)


def validar_qr(sesion_id: int, body: QrValidate, usuario: dict | None = None):
    if obtener_sesion(sesion_id) is None:
        raise SesionNotFoundError(f"Sesión {sesion_id} no encontrada")
    if usuario is not None:
        fila = obtener_sesion(sesion_id)
        from mesas_api.app.models.mesa import obtener_mesa_por_id

        mesa = obtener_mesa_por_id(fila["mesa_id"])
        if mesa is None:
            raise SesionNotFoundError(f"La mesa de la sesión no existe")
        gmid = mesa.get("gm_id")
        # ÚNICAMENTE el GM propietario registra asistencia (incluso admin fuera).
        if gmid is None or int(usuario["sub"]) != gmid:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para registrar asistencia de esta mesa (solo su GM).",
            )
    try:
        validar_sesion_qr(sesion_id, body.usuario_id, body.qr_data)
    except _Conflict:
        raise
    except _Invalid:
        raise
    registrar_asistencia(sesion_id, body.usuario_id)
    return {"asistencia": "registrada"}


# ---- Gestión de sesiones (cierre AE2) ---------------------------------------

def crear_sesion_controller(mesa_id: int) -> SesionOut:
    obtener_mesa_controller(mesa_id)  # MesaNotFoundError -> 404
    return SesionOut(**(_formatear_sesion(crear_sesion_db(mesa_id))))


def listar_sesiones_controller(mesa_id: int) -> list[SesionOut]:
    obtener_mesa_controller(mesa_id)
    return [SesionOut(**_formatear_sesion(f)) for f in listar_sesiones_db(mesa_id)]


def confirmar_sesion_controller(
    mesa_id: int, sesion_id: int, usuario_id: int, correlation_id: str = "-"
) -> dict:
    fila = obtener_sesion_de_mesa(sesion_id, mesa_id)
    if fila is None:
        raise SesionNotFoundError(
            f"Sesión {sesion_id} de la mesa {mesa_id} no encontrada"
        )
    if fila["estado"] == "cerrada":
        raise SesionCerradaError(
            f"La sesión {sesion_id} ya está cerrada; no se puede confirmar"
        )
    if fila.get("confirmada_at") is not None:
        return {
            "sesion_id": sesion_id,
            "mesa_id": mesa_id,
            "estado": "confirmada",
            "evento": "ya_estaba_confirmada",
        }
    confirmar_sesion_db(sesion_id)
    publicar_sesion_confirmada(
        mesa_id, sesion_id, usuario_id, correlation_id=correlation_id
    )
    return {
        "sesion_id": sesion_id,
        "mesa_id": mesa_id,
        "estado": "confirmada",
        "evento": "publicado",
    }


def cerrar_sesion_controller(mesa_id: int, sesion_id: int) -> dict:
    fila = obtener_sesion_de_mesa(sesion_id, mesa_id)
    if fila is None:
        raise SesionNotFoundError(
            f"Sesión {sesion_id} de la mesa {mesa_id} no encontrada"
        )
    if fila["estado"] == "cerrada":
        raise SesionCerradaError(f"La sesión {sesion_id} ya está cerrada")
    if cerrar_sesion_db(sesion_id) is None:
        # Carrera: entre la lectura y el UPDATE alguien la cerró.
        raise SesionCerradaError(f"La sesión {sesion_id} ya está cerrada")
    return {"sesion_id": sesion_id, "mesa_id": mesa_id, "estado": "cerrada"}
