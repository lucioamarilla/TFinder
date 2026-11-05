from fastapi import APIRouter, Depends, Request

from feed_api.app.controllers.diario import publicar_diario_controller
from feed_api.app.middleware.auth import usuario_actual
from feed_api.app.schemas import DiarioCreate
from feed_api.app.services.eventos import publicar_diario_pdf

router = APIRouter(prefix="/api/v1/mesas", tags=["diario"])


@router.post(
    "/{mesa_id}/sesiones/{sesion_id}/diario",
    status_code=201,
)
def publicar_diario(
    mesa_id: str,
    sesion_id: int,
    payload: DiarioCreate,
    request: Request,
    usuario: dict = Depends(usuario_actual),
):
    """Publica el contenido del diario de la sesión y emite sesion.diario_publicado."""
    return publicar_diario_controller(
        mesa_id,
        sesion_id,
        int(usuario["sub"]),
        usuario.get("email") or f"usuario {usuario['sub']}",
        payload.titulo,
        payload.cuerpo,
        correlation_id=request.scope.get("correlation_id"),
    )


@router.post(
    "/{mesa_id}/sesiones/{sesion_id}/diario/pdf",
    status_code=202,
    dependencies=[Depends(usuario_actual)],
    tags=["diario-pdf"],
)
def solicitar_diario_pdf(mesa_id: str, sesion_id: int, request: Request):
    doc_id = publicar_diario_pdf(mesa_id, sesion_id, request.scope.get("correlation_id"))
    return {
        "estado": "aceptado",
        "documento_id": doc_id,
        "detalle": "turno_enviado",
    }