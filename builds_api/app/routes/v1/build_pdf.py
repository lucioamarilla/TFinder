from fastapi import APIRouter, Depends, Request

from builds_api.app.middleware.auth import usuario_actual
from builds_api.app.services.eventos import publicar_doc_pdf

router = APIRouter(prefix="/api/v1/builds", tags=["build-pdf"])


@router.post("/{build_id}/pdf", status_code=202)
def solicitar_pdf(build_id: int, request: Request, _=Depends(usuario_actual)):
    doc_id = publicar_doc_pdf(build_id, request.scope.get("correlation_id"))
    return {
        "estado": "aceptado",
        "documento_id": doc_id,
        "detalle": "turno_enviado",
    }