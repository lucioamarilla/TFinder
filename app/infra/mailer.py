"""Envío real de correos por SMTP (sustituye al sandbox B09).

Configuración 100 % por variables de entorno (.env), mismo criterio que el
resto de la infraestructura:

    SMTP_HOST        host del servidor (Gmail: smtp.gmail.com, Brevo:
                     smtp-relay.brevo.com, etc.)
    SMTP_PORT        puerto (465 SSL, 587 STARTTLS, 25 sin cifrar)
    SMTP_USER        usuario (opcional si el relay no exige autenticación)
    SMTP_PASSWORD    contraseña (Gmail: contraseña de aplicación de 16 dígitos)
    MAIL_FROM        remitente, ej. noreply@tfinder-dev.com
    MAIL_FROM_NAME   nombre visible (opcional, default "TFinder")
    MAIL_SECURE      "ssl" | "tls" (default) | "none"

La configuración NO valida en el arranque (no es un secreto de seguridad como
JWT_SECRET: que falte el SMTP no tumba el resto del MVP). Se valida al primer
envío con un error claro y accionable, y el arranque firma una advertencia.
"""

import os
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr

from app.infra.logge import logger

_OBLIGATORIAS = ("SMTP_HOST", "SMTP_PORT", "MAIL_FROM")

__all__ = [
    "MailNoConfigurado",
    "MailRechazado",
    "enviar_email",
    "enviar_codigo",
    "sin_configurar",
]


class MailNoConfigurado(RuntimeError):
    """Faltan variables SMTP_* en .env: no se puede enviar."""


class MailRechazado(RuntimeError):
    """El servidor SMTP rechazó la casilla destino (mail inexistente, mejor
    esfuerzo: sólo el MX autoritativo la rechaza al vuelo)."""


def sin_configurar():
    """Lista de variables SMTP faltantes, o [] si la configuración está completa.

    Usada por la fábrica de servicios para firmar una advertencia al arrancar.
    """
    return [v for v in _OBLIGATORIAS if not (os.getenv(v) or "").strip()]


def _config():
    faltantes = sin_configurar()
    if faltantes:
        raise MailNoConfigurado(
            "SMTP sin configurar: faltan " + ", ".join(faltantes) + " en .env. "
            "Ejemplo para Gmail: SMTP_HOST=smtp.gmail.com, SMTP_PORT=465, "
            "SMTP_USER=tu.usuario@gmail.com, SMTP_PASSWORD=<contraseña de "
            "aplicación de 16 dígitos>, MAIL_FROM=tu.usuario@gmail.com, "
            "MAIL_SECURE=ssl"
        )

    # El remitente visible (MAIL_FROM) es configuración de contenido, no un
    # secreto: va por .env como el resto, sin defaults silenciosos.
    port = int(os.getenv("SMTP_PORT").strip())
    seguro = (os.getenv("MAIL_SECURE") or "tls").strip().lower()
    if seguro not in ("ssl", "tls", "none"):
        raise MailNoConfigurado(
            f"MAIL_SECURE={seguro!r} no es válido: usar ssl | tls | none."
        )
    return {
        "host": os.getenv("SMTP_HOST").strip(),
        "port": port,
        "user": (os.getenv("SMTP_USER") or "").strip(),
        "password": os.getenv("SMTP_PASSWORD") or "",
        "from": os.getenv("MAIL_FROM").strip(),
        "nombre": (os.getenv("MAIL_FROM_NAME") or "TFinder").strip(),
        "secure": seguro,
    }


# ---------------------------------------------------------------------------
# Plantillas (asunto + texto + HTML) para los códigos de registro/recupero.
# ---------------------------------------------------------------------------

def _plantilla_codigo(titulo: str, codigo: str, valido_min: int) -> tuple[str, str, str]:
    """Devuelve (asunto, texto, html) del mail de código de 6 dígitos."""
    asunto = f"{titulo} · código {codigo}"
    pie = "Si no fuiste vos, ignorá este mail: ninguna cuenta cambia sin el código."
    texto = (
        "TFinder\n"
        "\n"
        f"{titulo}\n"
        "\n"
        "Tu código de verificación es:\n"
        f"    {codigo}\n"
        "\n"
        f"Vence en {valido_min} minutos. Cada envío invalida el código anterior.\n"
        f"{pie}"
    )
    html = (
        '<div style="font-family:Georgia,serif;max-width:520px;margin:0 auto;'
        'padding:24px;border:1px solid #d8c9a3;border-radius:12px;">'
        f'<p style="letter-spacing:.12em;text-transform:uppercase;color:#8a7a55;'
        f'size:12px;margin:0 0 12px;">TFinder</p>'
        f'<h1 style="font-size:20px;margin:0 0 16px;color:#3a2f1b;">{titulo}</h1>'
        '<p style="color:#3a2f1b;margin:0 0 16px;">Tu código de verificación es:</p>'
        '<p style="font-size:34px;letter-spacing:.35em;font-weight:700;margin:0 0 16px;'
        f'color:#3a2f1b;">{codigo}</p>'
        f'<p style="color:#5c4f33;margin:0 0 8px;">Vence en {valido_min} minutos.'
        " Cada envío invalida el código anterior.</p>"
        f'<p style="color:#8a7a55;font-size:13px;margin:0;">{pie}</p>'
        "</div>"
    )
    return asunto, texto, html


def enviar_email(destino: str, asunto: str, texto: str, html: str) -> None:
    """Envía por el SMTP configurado. Levanta MailRechazado si el servidor
    rechaza la casilla destino, y MailNoConfigurado si falta configuración."""
    cfg = _config()
    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = formataddr((cfg["nombre"], cfg["from"]))
    msg["To"] = destino
    msg.set_content(texto)
    msg.add_alternative(html, subtype="html")

    try:
        if cfg["secure"] == "ssl":
            contexto = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                cfg["host"], cfg["port"], timeout=15, context=contexto
            ) as server:
                if cfg["user"]:
                    server.login(cfg["user"], cfg["password"])
                server.send_message(msg)
        else:
            with smtplib.SMTP(cfg["host"], cfg["port"], timeout=15) as server:
                if cfg["secure"] == "tls":
                    server.starttls(context=ssl.create_default_context())
                if cfg["user"]:
                    server.login(cfg["user"], cfg["password"])
                server.send_message(msg)
    except smtplib.SMTPRecipientsRefused as exc:
        logger.warning("SMTP rechazó la casilla %s", destino)
        raise MailRechazado(f"El servidor de correo rechazó la dirección {destino}.") from exc
    except (smtplib.SMTPAuthenticationError, smtplib.SMTPException, OSError, ssl.SSLError) as exc:
        logger.warning("Fallo de envío SMTP a %s: %s", destino, exc.__class__.__name__)
        raise RuntimeError(
            "No se pudo enviar el correo: revisá SMTP_HOST/SMTP_PORT/SMTP_USER/"
            "SMTP_PASSWORD/MAIL_SECURE en .env."
        ) from exc


def enviar_codigo(destino: str, codigo: str, registro: bool, valido_min: int = 15) -> None:
    """Mail de un código de 6 dígitos del flujo (registro | recuperación)."""
    titulo = "Verificá tu correo" if registro else "Recuperación de contraseña"
    asunto, texto, html = _plantilla_codigo(titulo, codigo, valido_min)
    enviar_email(destino, asunto, texto, html)
