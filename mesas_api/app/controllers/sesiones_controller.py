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
from mesas_api.app.schemas import SesionOut


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
    return {
        "sesion_id": sesion_id,
        "mesa_id": mesa_id,
        "estado": "confirmada",
        "evento": "confirmada",
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


def marcar_asistencia_controller(sesion_id: int, usuario: dict) -> dict:
    fila = obtener_sesion(sesion_id)
    if fila is None:
        raise SesionNotFoundError(f"Sesión {sesion_id} no encontrada")
    mesa_id = fila["mesa_id"]
    from mesas_api.app.models.mesa import obtener_mesa_por_id, rol_de

    mesa = obtener_mesa_por_id(mesa_id)
    if mesa is None:
        raise SesionNotFoundError(f"La mesa de la sesión no existe")
    if int(usuario["sub"]) != mesa.get("gm_id") and rol_de(int(usuario["sub"]), mesa_id) is None:
        raise HTTPException(status_code=403, detail="No eres miembro de esta mesa.")
    if fila["estado"] == "cerrada":
        raise SesionCerradaError(
            f"La sesión {sesion_id} está cerrada; no se puede registrar asistencia"
        )
    registrar_asistencia(sesion_id, int(usuario["sub"]))
    return {"asistencia": "registrada"}
