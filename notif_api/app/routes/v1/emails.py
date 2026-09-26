from fastapi import APIRouter, Depends, HTTPException

from notif_api.app.middleware.auth import requerir_roles
from notif_api.app.models.notif import (
    actualizar_estado_email,
    listar_emails,
    obtener_email,
)
from notif_api.app.services.email_service import _enviar_por_smtp

router = APIRouter(prefix="/api/v1/emails", tags=["emails"])
_admin = Depends(requerir_roles("admin"))


@router.get("", dependencies=[_admin])
def emails(limite: int = 50):
    return listar_emails(limite)


@router.post("/{email_id}/reintentar", dependencies=[_admin])
def reintentar(email_id: int):
    email = obtener_email(email_id)
    if email is None:
        raise HTTPException(status_code=404, detail="Email no encontrado")
    error = _enviar_por_smtp(email["destino"], email["asunto"], email["cuerpo"])
    estado = "enviado" if error is None else "fallido"
    actualizar_estado_email(email_id, estado, error)
    return {"id": email_id, "estado": estado, "error": error}
