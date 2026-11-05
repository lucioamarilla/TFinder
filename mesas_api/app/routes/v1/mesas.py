from typing import Literal

from fastapi import APIRouter, Depends, Query, Request, Response
from starlette.responses import JSONResponse

from mesas_api.app.controllers.mesas import (
    actualizar_mesa_controller,
    crear_mesa_controller,
    eliminar_mesa_controller,
    listar_mesas_controller,
    obtener_mesa_controller,
    _formatear_fila,
)
from mesas_api.app.models.mesa import listar_con_rol
from mesas_api.app.models.sesiones import listar_miembros
from mesas_api.app.schemas import MesaOut


def _con_mi_rol(filas):
    return [
        {**MesaOut(**(_formatear_fila(fila))).model_dump(), "mi_rol": fila.get("mi_rol")}
        for fila in filas
    ]
from mesas_api.app.controllers.sesiones_controller import (
    SesionNotFoundError,
    cerrar_sesion_controller,
    confirmar_sesion_controller,
    crear_sesion_controller,
    listar_sesiones_controller,
)
from mesas_api.app.controllers.solicitudes_controller import (
    crear_solicitud_controller,
    expulsar_miembro_controller,
    salir_controller,
)
from mesas_api.app.middleware.auth import requerir_roles, usuario_actual
from mesas_api.app.middleware.membresia import requerir_miembro, requerir_master
from mesas_api.app.models.sesiones import listar_miembros
from mesas_api.app.schemas import MesaCreate, MesaMiaOut, MesaOut, MesaUpdate, SesionOut

router = APIRouter(prefix="/api/v1/mesas")


@router.get("/mias", response_model=list[MesaMiaOut])
def mis_mesas(usuario: dict = Depends(usuario_actual)):
    """F1: mesas donde el usuario es master o jugador (fuente del header)."""
    return _con_mi_rol(listar_con_rol(int(usuario["sub"])))


@router.get("/{mesa_id}/miembros")
def miembros_mesa(mesa_id: int, _=Depends(requerir_miembro)):
    """F2 (2.4): solo integrantes (o servicio B09) leen los miembros."""
    obtener_mesa_controller(mesa_id)
    return {"mesa_id": mesa_id, "miembros": listar_miembros(mesa_id)}


@router.delete("/{mesa_id}/miembros/mi")
def salir_de_mesa_mia(
    mesa_id: int,
    usuario: dict = Depends(requerir_miembro),
):
    """F2: baja voluntaria del jugador (el master no sale por esta vía)."""
    return salir_controller(mesa_id, usuario)


@router.delete("/{mesa_id}/miembros/{usuario_id}")
def expulsar_miembro_mesa(
    mesa_id: int,
    usuario_id: int,
    request: Request,
    usuario: dict = Depends(requerir_master),
):
    """El master expulsa a un miembro (libera cupo y notifica)."""
    return expulsar_miembro_controller(
        mesa_id,
        usuario_id,
        usuario,
        correlation_id=request.scope.get("correlation_id"),
    )


@router.get("", response_model=list[MesaOut])
def listar_mesas(
    estado: Literal["abierta", "cerrada"] | None = None,
    sistema: str | None = Query(default=None, max_length=32),
    tono: str | None = Query(default=None, max_length=64),
    orden: Literal["id", "recientes", "nombre"] = "id",
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=50),
):
    """Listado con filtros RF-04/13: estado, sistema, tono, orden y pagina."""
    listado, tier = listar_mesas_controller(estado, sistema, tono, orden, page, limit)
    return JSONResponse(content=listado, headers={"X-Cache": tier})


@router.get("/{mesa_id}", response_model=MesaOut)
def obtener_mesa(mesa_id: int):
    return obtener_mesa_controller(mesa_id)


@router.post("", response_model=MesaOut, status_code=201)
def crear_mesa(payload: MesaCreate, usuario: dict = Depends(usuario_actual)):
    return crear_mesa_controller(payload, usuario)


@router.put("/{mesa_id}", response_model=MesaOut)
def actualizar_mesa(
    mesa_id: int,
    payload: MesaUpdate,
    usuario: dict = Depends(usuario_actual),
):
    return actualizar_mesa_controller(mesa_id, payload, usuario)


@router.delete("/{mesa_id}", status_code=204)
def eliminar_mesa(mesa_id: int, usuario: dict = Depends(usuario_actual)):
    eliminar_mesa_controller(mesa_id, usuario)
    return Response(status_code=204)


@router.post("/{mesa_id}/solicitar", status_code=201)
def solicitar_union(
    mesa_id: int,
    request: Request,
    usuario: dict = Depends(usuario_actual),
):
    """Alias legado de POST /solicitudes: crea la solicitud 'pendiente'."""
    return crear_solicitud_controller(
        mesa_id,
        int(usuario["sub"]),
        correlation_id=request.scope.get("correlation_id"),
        idem_key=None,
    )


# ---- Sesiones de juego (cierre AE2) -----------------------------------------

@router.get("/{mesa_id}/sesiones", response_model=list[SesionOut])
def listar_sesiones_mesa(mesa_id: int, _=Depends(requerir_miembro)):
    """F2 (2.4): sesiones solo para integrantes de la mesa."""
    return listar_sesiones_controller(mesa_id)


@router.post("/{mesa_id}/sesiones", status_code=201, response_model=SesionOut)
def crear_sesion_mesa(mesa_id: int, _=Depends(requerir_master)):
    """El master de la mesa crea la sesión (principio 2.1)."""
    return crear_sesion_controller(mesa_id)


@router.post("/{mesa_id}/sesiones/{sesion_id}/confirmar")
def confirmar_sesion_mesa(
    mesa_id: int,
    sesion_id: int,
    request: Request,
    usuario: dict = Depends(requerir_master),
):
    """Confirma la sesión y emite sesion.confirmada (notif + emails)."""
    return confirmar_sesion_controller(
        mesa_id,
        sesion_id,
        int(usuario["sub"]),
        correlation_id=request.scope.get("correlation_id"),
    )


@router.post("/{mesa_id}/sesiones/{sesion_id}/cerrar")
def cerrar_sesion_mesa(
    mesa_id: int,
    sesion_id: int,
    _=Depends(requerir_master),
):
    return cerrar_sesion_controller(mesa_id, sesion_id)

# ---- F3: bitácora de la sesión (pliego 2.3) ----------------------------------

from mesas_api.app.controllers.sesiones_controller import (
    AnotacionInvalidaError,
    anotacion_controller,
    anotaciones_controller,
)
from app.infra.errors import body_error as _body_error


def _anotacion_resp(code, mensaje):
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=code, content=_body_error(code, mensaje))


@router.post("/{mesa_id}/sesiones/{sesion_id}/anotaciones", status_code=201)
def anotar_sesion(
    mesa_id: int,
    sesion_id: int,
    payload: dict,
    usuario: dict = Depends(requerir_miembro),
):
    """F3: anotación cronológica de un integrante (autor y fecha del server)."""
    try:
        return anotacion_controller(mesa_id, sesion_id, usuario, (payload or {}).get("texto"))
    except AnotacionInvalidaError as exc:
        return _anotacion_resp(400, str(exc))


@router.get("/{mesa_id}/sesiones/{sesion_id}/anotaciones")
def historial_sesion(
    mesa_id: int,
    sesion_id: int,
    _=Depends(requerir_miembro),
):
    """F3: historial cronológico (autor, fecha-hora, texto)."""
    return anotaciones_controller(mesa_id, sesion_id)
