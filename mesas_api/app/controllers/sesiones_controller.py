from datetime import datetime

from fastapi import HTTPException

from mesas_api.app.controllers.mesas import obtener_mesa_controller
from mesas_api.app.models.sesiones import (
    cerrar_sesion_db,
    confirmar_sesion_db,
    crear_sesion_db,
    listar_sesiones_db,
    listar_anotaciones,
    agregar_anotacion,
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


def resolver_sesion(sesion_id: int):
    """F3: obtiene la sesión (mesa_id incluido) o None."""
    return obtener_sesion(sesion_id)


def annotacion_para_controller(mesa_id, sesion_id, usuario, texto):
    """Alias solicitado por la ruta (transforma controller de igual nombre)."""
    return anotacion_controller(mesa_id, sesion_id, usuario, texto)


class AnotacionInvalidaError(Exception):
    """VAL-33 aplicado a la bitácora: el texto no puede estar vacío."""


def anotacion_controller(mesa_id: int, sesion_id: int, usuario, texto: str):
    """F3: agrega una anotación cronológica de un integrante."""
    texto_limpio = (texto or '').strip()
    if not texto_limpio:
        raise AnotacionInvalidaError('El texto de la anotación no puede estar vacío.')
    if len(texto_limpio) > 2000:
        raise AnotacionInvalidaError('La anotación no puede superar los 2000 caracteres.')
    if '<script' in texto_limpio.lower():
        raise AnotacionInvalidaError('La anotación no puede incluir scripts.')
    fila = obtener_sesion(sesion_id)
    if fila is None or fila["mesa_id"] != mesa_id:
        raise SesionNotFoundError(f'Sesión {sesion_id} no encontrada')
    modelo = agregar_anotacion(sesion_id, mesa_id, int(usuario['sub']), texto_limpio)
    import uuid as _uuid

    from mesas_api.app.models.usuarios_lookup import obtener_usuario_por_id

    autor = obtener_usuario_por_id(int(usuario['sub']))
    return {**modelo, 'autor_nombre': autor['nombre'] if autor else ''}


def anotaciones_controller(mesa_id: int, sesion_id: int):
    """F3: historial cronológico con autor y fecha-hora."""
    fila = obtener_sesion(sesion_id)
    if fila is None or fila["mesa_id"] != mesa_id:
        raise SesionNotFoundError(f'Sesión {sesion_id} no encontrada')
    salida = []
    for a in listar_anotaciones(sesion_id):
        creado = a['creado_en'].isoformat() if hasattr(a['creado_en'], 'isoformat') else str(a['creado_en'])
        salida.append({**a, 'creado_en': creado})
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
