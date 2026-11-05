"""Permss de membresía por mesa (pliego 2.1 y 2.4).

El rol ya no es un atributo de la cuenta: 'master' y 'jugador' viven en
miembros_mesa y SON validados en el backend en cada peligro/no-peligroso.
El rol global `admin` de usuarios queda SOLO para plataforma (bypass por
diseño, documentado en la auditoría F0 §7 D1).

Puente B09: la cuenta de servicio de notif-api (MESAS_EMAIL) puede listar
miembros de cualquier mesa para enviar emails de sesiones confirmadas.
"""

import os

from fastapi import Depends, HTTPException

from mesas_api.app.middleware.auth import usuario_actual
from mesas_api.app.models.mesa import rol_de

_SERVICIO_EMAIL = os.getenv("MESAS_EMAIL", "email_svc@tfinder.dev")


def _es_servicio_email(usuario: dict) -> bool:
    return (usuario or {}).get("email") == _SERVICIO_EMAIL or \
           ((usuario or {}).get("rol") == "usuario" and (usuario or {}).get("email", "").startswith("email_svc"))


def _rol_o_lanzar(usuario: dict, mesa_id: int, esperado: str | None, codigo: int = 403):
    """La mesa inexistente es 404 (semántica preservada); el resto 403."""
    from mesas_api.app.models.mesa import obtener_mesa_por_id, rol_de

    if obtener_mesa_por_id(mesa_id) is None:
        raise HTTPException(status_code=404, detail=f"Mesa {mesa_id} no encontrada")
    if (usuario or {}).get("rol") == "admin":
        return usuario
    rol = rol_de(int(usuario["sub"]), mesa_id)
    if rol is None:
        raise HTTPException(status_code=codigo, detail="No eres miembro de esta mesa.")
    if esperado and rol != esperado:
        raise HTTPException(
            status_code=403,
            detail="Esta acción es exclusiva del master de la mesa.",
        )
    return usuario


def requerir_miembro(mesa_id: int, usuario: dict = Depends(usuario_actual)):
    """Lectura de contenido de mesa: miembros de ESA mesa (o servicio/admin).

    FastAPI inyecta el path param `mesa_id` automáticamente.
    """
    if (usuario or {}).get("rol") == "admin" or _es_servicio_email(usuario):
        return usuario
    return _rol_o_lanzar(usuario, mesa_id, None)


def requerir_master(mesa_id: int, usuario: dict = Depends(usuario_actual)):
    """Administración de LA mesa: su master (o admin de plataforma)."""
    return _rol_o_lanzar(usuario, mesa_id, "master")
