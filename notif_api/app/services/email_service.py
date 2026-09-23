import json
import os
import smtplib
import socket
import urllib.error
import urllib.request
from email.mime.text import MIMEText

from notif_api.app.models.notif import (
    actualizar_estado_email,
    registrar_email,
)

SMTP_TIMEOUT = int(os.getenv("SMTP_TIMEOUT", "3"))
MESAS_URL = os.getenv("MESAS_URL", "http://localhost:8001")
MESAS_EMAIL = os.getenv("MESAS_EMAIL", "email_svc@tfinder.dev")
MESAS_PASSWORD = os.getenv("MESAS_PASSWORD", "cambiar-svc-password")

_token_cache = {"access": None}


def _config():
    return (
        os.getenv("SMTP_HOST", "localhost"),
        int(os.getenv("SMTP_PORT", "1025")),
        os.getenv("MAIL_FROM", "noreply@tfinder.local"),
    )


def _enviar_por_smtp(destino: str, asunto: str, cuerpo: str) -> str | None:
    """Envía por SMTP; devuelve None si OK o el error como string si falló."""
    host, port, desde = _config()
    msg = MIMEText(cuerpo, "plain", "utf-8")
    msg["Subject"] = asunto
    msg["From"] = desde
    msg["To"] = destino
    try:
        with smtplib.SMTP(host, port, timeout=SMTP_TIMEOUT) as conexion:
            conexion.sendmail(desde, [destino], msg.as_string())
        return None
    except (smtplib.SMTPException, socket.timeout, TimeoutError, OSError) as exc:
        return str(exc)


def enviar_email(destino: str, asunto: str, cuerpo: str, registrar: bool = True) -> bool:
    error = _enviar_por_smtp(destino, asunto, cuerpo)
    ok = error is None
    if registrar:
        registrar_email(
            destino,
            asunto,
            cuerpo,
            "enviado" if ok else "fallido",
            error,
        )
    return ok


def _obtener_token_mesas() -> str:
    if _token_cache["access"]:
        return _token_cache["access"]
    body = json.dumps({"email": MESAS_EMAIL, "password": MESAS_PASSWORD}).encode()
    req = urllib.request.Request(
        f"{MESAS_URL}/api/v1/auth/login",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=SMTP_TIMEOUT) as resp:
        datos = json.loads(resp.read().decode())
    _token_cache["access"] = datos["access_token"]
    return datos["access_token"]


def _llamar_mesas(path: str) -> dict:
    try:
        token = _obtener_token_mesas()
        req = urllib.request.Request(
            f"{MESAS_URL}{path}",
            headers={"Authorization": f"Bearer {token}"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=SMTP_TIMEOUT) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            _token_cache["access"] = None
        raise


def obtener_emails_mesa(mesa_id: int) -> list[str]:
    datos = _llamar_mesas(f"/api/v1/mesas/{mesa_id}/miembros")
    return [m["email"] for m in datos.get("miembros", []) if m.get("email")]