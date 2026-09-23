from fastapi import APIRouter

from notif_api.app.schemas import AuthRecuperar
from notif_api.app.services.email_service import enviar_email

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/recuperar", status_code=202)
def recuperar(data: AuthRecuperar):
    destinatario = data.email.strip().lower()
    enviar_email(
        destinatario,
        "TFinder · Recuperar contraseña",
        "Recibimos tu solicitud para restablecer tu contraseña. "
        "Si la cuenta existe, se te envía el enlace para continuar.",
    )
    return {"ok": True}