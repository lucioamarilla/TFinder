from fastapi import APIRouter, Depends, Header, Query, Request
from typing import Optional

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
def listar_wiki(mesa_id: Optional[str] = Query(default=None, alias="mesa_id")):
    """Listado público (carpetas agregadas); la visibilidad filtra el DETALLE."""
    return obtener_wiki(mesa_id)


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
