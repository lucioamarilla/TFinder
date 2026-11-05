from psycopg import errors as pg_errors

from mesas_api.app.models.mesa import obtener_mesa_por_id
from mesas_api.app.models.mesa import rol_de
from mesas_api.app.models.solicitudes import (
    aceptar_solicitud,
    crear_solicitud,
    existe_solicitud_pendiente,
    expulsar_miembro,
    listar_solicitudes_con_estado,
    obtener_solicitud,
    rechazar_solicitud,
    salir_de_mesa,
)
from mesas_api.app.services.eventos import (
    publicar_aceptacion,
    publicar_expulsion,
    publicar_solicitud,
)
from mesas_api.app.services.idem import guardar_resultado, obtener_resultado

# Los manejadores de errores importan desde este módulo (ruta histórica).
from mesas_api.app.models.solicitudes import (  # noqa: F401
    CupoAgotadoError,
    SolicitudNoProcesableError,
)


class MesaNoExisteError(Exception):
    pass


class MesaCerradaError(Exception):
    pass


class SolicitudDuplicadaError(Exception):
    pass


class SolicitudNoExisteError(Exception):
    pass


class SolicitudProhibidaError(Exception):
    pass


class SalirDeMasterError(Exception):
    pass


class AccionInvalidaError(Exception):
    pass


def _es_admin(usuario) -> bool:
    return (usuario or {}).get("rol") == "admin"


def _es_propietario(usuario, mesa) -> bool:
    """RN-02: solo el GM propietario (o admin de plataforma)."""
    if mesa.get("gm_id") is not None and int(usuario["sub"]) == mesa["gm_id"]:
        return True
    return _es_admin(usuario)


def _asegurar_propietario(usuario, mesa):
    if not _es_propietario(usuario, mesa):
        raise SolicitudProhibidaError(
            "No tienes permisos sobre esta mesa: solo su GM propietario (RN-02)."
        )


def crear_solicitud_controller(mesa_id, usuario_id, correlation_id, idem_key=None):
    """Crea la solicitud 'pendiente' (RF-14) y publica el evento (RF-22)."""
    if idem_key:
        previo = obtener_resultado(idem_key)
        if previo is not None:
            return previo
        existente_db = obtener_solicitud_por_idem(
            mesa_id, usuario_id, idem_key
        )
        if existente_db:
            guardar_resultado(idem_key, existente_db)
            return existente_db

    if obtener_mesa_por_id(mesa_id) is None:
        raise MesaNoExisteError(f"Mesa {mesa_id} no encontrada")
    mesa = obtener_mesa_por_id(mesa_id)
    if mesa["estado"] == "cerrada":
        raise MesaCerradaError("La mesa no está abierta para solicitudes de unión.")
    if existe_solicitud_pendiente(mesa_id, usuario_id):
        raise SolicitudDuplicadaError(
            "Ya tenés una solicitud pendiente para esta mesa."
        )

    try:
        fila = crear_solicitud(mesa_id, usuario_id, estado="pendiente", idem_key=idem_key)
    except pg_errors.UniqueViolation:
        raise SolicitudDuplicadaError(
            "Ya tenés una solicitud pendiente para esta mesa."
        ) from None

    if idem_key:
        guardar_resultado(idem_key, fila)
    publicar_solicitud(
        mesa_id, usuario_id, gm_id=mesa.get("gm_id"), correlation_id=correlation_id
    )
    return fila


def obtener_solicitud_por_idem(mesa_id, usuario_id, idem_key):
    from mesas_api.app.models.solicitudes import obtener_solicitud_por_key

    return obtener_solicitud_por_key(mesa_id, usuario_id, idem_key)


def salir_controller(mesa_id, usuario):
    """F2: el jugador se va; el master no puede salir por esta vía (409)."""
    mesa = obtener_mesa_por_id(mesa_id)
    if mesa is None:
        raise MesaNoExisteError(f"Mesa {mesa_id} no encontrada")
    usuario_id = int(usuario["sub"])
    # El master de la mesa NO sale por esta vía: transfiere o elimina (futuro).
    if rol_de(mesa_id, usuario_id) == "master":
        raise SalirDeMasterError(
            "El master no puede salir de su mesa por esta vía: transferí la dirección o eliminá la mesa."
        )
    hubo, nuevo_cupo = salir_de_mesa(mesa_id, usuario_id)
    if not hubo:
        raise SolicitudNoExisteError(f"El usuario {usuario_id} no es jugador de la mesa {mesa_id}.")
    return {"mesa_id": mesa_id, "jugadores_actuales": nuevo_cupo}


def listar_solicitudes_controller(mesa_id, usuario, estado=None):
    """Bandeja pendientes/listado del GM (RF-15):Solo owner o admin."""
    mesa = obtener_mesa_por_id(mesa_id)
    if mesa is None:
        raise MesaNoExisteError(f"Mesa {mesa_id} no encontrada")
    _asegurar_propietario(usuario, mesa)
    return listar_solicitudes_con_estado(mesa_id, estado=estado)


def responder_solicitud_controller(mesa_id, solicitud_id, accion, usuario, correlation_id):
    """El GM propietario decide (RF-15/RN-08): aceptar ➜ miembro y cupo; rechazar ➜ cerrada."""
    if accion not in ("aceptar", "rechazar"):
        raise AccionInvalidaError("La acción debe ser 'aceptar' o 'rechazar'.")

    mesa = obtener_mesa_por_id(mesa_id)
    if mesa is None:
        raise MesaNoExisteError(f"Mesa {mesa_id} no encontrada")
    _asegurar_propietario(usuario, mesa)
    previa = obtener_solicitud(mesa_id, solicitud_id)
    if previa is None:
        raise SolicitudNoExisteError(f"La solicitud {solicitud_id} no existe")

    if accion == "aceptar":
        fila = aceptar_solicitud(solicitud_id, mesa_id)
        publicar_aceptacion(
            mesa_id, fila["usuario_id"], gm_id=mesa.get("gm_id"), correlation_id=correlation_id
        )
    else:
        fila = rechazar_solicitud(solicitud_id, mesa_id)
    return fila


def expulsar_miembro_controller(mesa_id, usuario_objetivo, usuario, correlation_id):
    """El GM expulsa a un miembro aceptado: vacante liberada + evento expulsada."""
    mesa = obtener_mesa_por_id(mesa_id)
    if mesa is None:
        raise MesaNoExisteError(f"Mesa {mesa_id} no encontrada")
    _asegurar_propietario(usuario, mesa)

    hubo, nuevo_cupo = expulsar_miembro(mesa_id, usuario_objetivo)
    if not hubo:
        raise SolicitudNoExisteError(
            f"El usuario {usuario_objetivo} no es miembro de la mesa {mesa_id}."
        )
    publicar_expulsion(
        mesa_id, usuario_objetivo, gm_id=mesa.get("gm_id"), correlation_id=correlation_id
    )
    return {"mesa_id": mesa_id, "usuario_id": usuario_objetivo, "jugadores_actuales": nuevo_cupo}
