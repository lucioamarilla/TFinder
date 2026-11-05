from fastapi import APIRouter, Depends, Header, Query, Request
from typing import Optional

from feed_api.app.controllers.wiki_contribuciones import (
    crear_contribucion_controller,
    decidir_contribucion_controller,
    listar_contribuciones_controller,
)
from feed_api.app.controllers.wiki import (
    actualizar_pagina_controller,
    crear_pagina_controller,
    eliminar_pagina_controller,
    obtener_pagina_controller,
    obtener_wiki,
)
from feed_api.app.middleware.auth import auth_opcional, usuario_actual

router = APIRouter(prefix="/api/v1")


@router.get("/wiki")
def listar_wiki(
    request: Request,
    mesa_id: Optional[str] = Query(default=None, alias="mesa_id"),
    authorization: Optional[str] = Header(default=None),
):
    """F2: listado con visibilidad según llamante (privadas solo master)."""
    try:
        usuario = auth_opcional(request)
    except Exception:
        usuario = None
    token = authorization or request.headers.get("Authorization")
    return obtener_wiki(mesa_id, token=token, usuario=usuario)


def _token_de(request: Request, autorizacion_raw):
    fwd = autorizacion_raw or request.headers.get("Authorization")
    return fwd or None


@router.post("/mesas/{mesa_id}/wiki", status_code=201)
def crear_pagina(
    mesa_id: str,
    payload: dict,
    request: Request,
    _: dict = Depends(usuario_actual),
    authorization: Optional[str] = Header(default=None),
):
    """RF-08: crear página (firma de GM propietario, verificada vía REST B09)."""
    return crear_pagina_controller(mesa_id, _, payload, token=_token_de(request, authorization))


@router.get("/wiki/{pagina_id}")
def detallar_pagina(
    pagina_id: int,
    request: Request,
    mesa_id: Optional[str] = Query(default=None),
    authorization: Optional[str] = Header(default=None),
):
    """RF-09/RN-05: lectura según visibilidad (pública no exige sesión)."""
    try:
        usuario = auth_opcional(request)
    except Exception:
        usuario = None
    token = _token_de(request, authorization)
    return obtener_pagina_controller(mesa_id, pagina_id, usuario, token)


@router.put("/wiki/{pagina_id}")
def actualizar_pagina(
    pagina_id: int,
    payload: dict,
    request: Request,
    mesa_id: Optional[str] = Query(default=None),
    _: dict = Depends(usuario_actual),
    authorization: Optional[str] = Header(default=None),
):
    return actualizar_pagina_controller(
        mesa_id, pagina_id, _, payload, token=_token_de(request, authorization)
    )


@router.delete("/wiki/{pagina_id}", status_code=204)
def eliminar_pagina(
    pagina_id: int,
    request: Request,
    mesa_id: Optional[str] = Query(default=None),
    _: dict = Depends(usuario_actual),
    authorization: Optional[str] = Header(default=None),
):
    eliminar_pagina_controller(mesa_id, pagina_id, _, token=_token_de(request, authorization))
    return None

# ---- F4: contribuciones con estados -----------------------------------------

@router.post("/mesas/{mesa_id}/wiki/{pagina_id}/contribuciones", status_code=201)
def agregar_contribucion(
    mesa_id: str,
    pagina_id: int,
    payload: dict,
    request: Request,
    _: dict = Depends(usuario_actual),
    authorization: Optional[str] = Header(default=None),
):
    """Pliego F4: un integrante propone una edición (nace 'pendiente')."""
    return crear_contribucion_controller(mesa_id, pagina_id, _, payload, token=_token_de(request, authorization))


@router.get("/mesas/{mesa_id}/wiki/contribuciones")
def bandeja_contribuciones(
    mesa_id: str,
    request: Request,
    estado: str = Query(default='pendiente', pattern='^(pendiente|aprobada|rechazada)$'),
    _: dict = Depends(usuario_actual),
    authorization: Optional[str] = Header(default=None),
):
    """Solo el master ve la bandeja (2.4)."""
    return listar_contribuciones_controller(mesa_id, _, token=_token_de(request, authorization), estado=estado)


@router.post("/mesas/{mesa_id}/wiki/{pagina_id}/publicar-feed", status_code=201)
def publicar_wiki_en_feed(mesa_id: str, pagina_id: int, usuario: dict = Depends(usuario_actual)):
    from feed_api.app.controllers.feed import crear_publicacion
    from feed_api.app.controllers.wiki import obtener_pagina_controller

    pagina = obtener_pagina_controller(mesa_id, pagina_id, usuario, token=None)
    datos = {
        "titulo": pagina.titulo,
        "cuerpo": pagina.resumen or "Página de wiki publicada en el feed.",
        "tipo": "wiki",
        "embed": {"wiki_id": pagina_id},
    }
    return crear_publicacion(usuario, datos)


@router.post("/mesas/{mesa_id}/wiki/contribuciones/{contribucion_id}/aprobar")
def aprobar_contribucion(
    mesa_id: str,
    contribucion_id: int,
    request: Request,
    _: dict = Depends(usuario_actual),
    authorization: Optional[str] = Header(default=None),
):
    return decidir_contribucion_controller(mesa_id, contribucion_id, _, 'aprobada', token=_token_de(request, authorization))


@router.post("/mesas/{mesa_id}/wiki/contribuciones/{contribucion_id}/rechazar")
def rechazar_contribucion(
    mesa_id: str,
    contribucion_id: int,
    request: Request,
    _: dict = Depends(usuario_actual),
    authorization: Optional[str] = Header(default=None),
):
    return decidir_contribucion_controller(mesa_id, contribucion_id, _, 'rechazada', token=_token_de(request, authorization))
