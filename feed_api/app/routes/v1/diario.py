from fastapi import APIRouter, Depends, Request

from feed_api.app.middleware.auth import usuario_actual
from feed_api.app.services.eventos import publicar_diario_pdf

router = APIRouter(prefix="/api/v1/mesas", tags=["diario-pdf"])


@router.post(
    "/{mesa_id}/sesiones/{sesion_id}/diario/pdf",
    status_code=202,
    dependencies=[Depends(usuario_actual)],
)
def solicitar_diario_pdf(mesa_id: str, sesion_id: int, request: Request):
    doc_id = publicar_diario_pdf(mesa_id, sesion_id, request.scope.get("correlation_id"))
    return {
        "estado": "aceptado",
        "documento_id": doc_id,
        "detalle": "turno_enviado",
    }