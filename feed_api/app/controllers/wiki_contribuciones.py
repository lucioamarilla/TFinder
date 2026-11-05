"""F4: contribuciones de wiki con estados (pliego F4 — 2.4 permisos back)."""

import json

from fastapi import HTTPException

from feed_api.app.db import get_connection
from feed_api.app.schemas import PaginaOut


class ContribucionNoProcesableError(Exception):
    """La contribución ya fue resuelta (aprobada/rechazada)."""


def _serializar_c(fila):
    f = dict(fila)
    f["autorNombre"] = f.pop("autor_nome", None)
    f["revisadoPor"] = f.pop("revisado_por", None)
    f["revisadoEn"] = f.pop("revisado_en", None)
    f["creadoEn"] = f.pop("creado_en", None)
    return f


def _pag_y_acceso(mesa_id, pagina_id, usuario, token, solo_master=False):
    """Verifica que la página exista y pertenezca a esa mesa + permisos (2.4)."""
    from fastapi import HTTPException

    from app.infra.mesas import es_gm_mesa

    with get_connection() as conn:
        pag = conn.execute("SELECT * FROM wiki_paginas WHERE id = %s", (pagina_id,)).fetchone()
    if pag is None or str(pag["mesa_id"]) != str(mesa_id):
        raise HTTPException(status_code=404, detail="La página de wiki no existe.")
    try:
        es_master, _ = es_gm_mesa(int(mesa_id), usuario, token=token)
    except (LookupError, RuntimeError):
        raise HTTPException(status_code=403, detail="No tienes permisos sobre esta página.") from None
    if solo_master and not es_master:
        raise HTTPException(status_code=403, detail="Esta acción es exclusiva del master de la mesa.")
    return pag, es_master


def crear_contribucion_controller(mesa_id, pagina_id, usuario, datos, token=None):
    """Cualquier integrante propone; nace 'pendiente' (pliego F4)."""
    from app.infra.mesas import es_miembro_aceptado

    usuario_id = str(usuario["sub"])
    try:
        es_miembro_aceptado(int(mesa_id), usuario, token=token)
    except (LookupError, RuntimeError, PermissionError):
        raise HTTPException(status_code=403, detail="No eres miembro de esta mesa.") from None
    _pag_y_acceso(mesa_id, pagina_id, usuario, token)

    cuerpo = datos.get("cuerpo") or datos.get("contenido")
    textos = ""
    if isinstance(cuerpo, list):
        textos = " ".join(str(b.get("texto") or "") for b in cuerpo if isinstance(b, dict))
    elif isinstance(cuerpo, dict):
        textos = str(cuerpo.get("texto") or "")
    elif isinstance(cuerpo, str):
        textos = cuerpo
    if not textos.strip():
        raise HTTPException(status_code=400, detail="La contribución está vacía.")

    with get_connection() as conn:
        fila = conn.execute(
            """
            INSERT INTO wiki_contribuciones (pagina_id, mesa_id, autor_id, autor_nome, cuerpo)
            VALUES (%s, %s, %s, %s, %s) RETURNING *""",
            (pagina_id, str(mesa_id), usuario_id, usuario.get("email", "").split("@")[0], json.dumps(datos.get("cuerpo") or {})),
        ).fetchone()
    return _serializar_c(fila)


def listar_contribuciones_controller(mesa_id, usuario, token=None, estado="pendiente"):
    """Bandeja del master (solo master ve/resuelve, 2.4)."""
    from app.infra.mesas import es_gm_mesa

    try:
        es_master, _ = es_gm_mesa(int(mesa_id), usuario, token=token)
    except (LookupError, RuntimeError):
        raise HTTPException(status_code=502, detail="No se pudo verificar la membresía.") from None
    if not es_master:
        raise HTTPException(status_code=403, detail="Esta bandeja es del master de la mesa.")
    with get_connection() as conn:
        filas = conn.execute(
            "SELECT * FROM wiki_contribuciones WHERE mesa_id = %s AND estado = %s ORDER BY creado_en",
            (str(mesa_id), estado),
        ).fetchall()
    return [_serializar_c(f) for f in filas]


def decidir_contribucion_controller(mesa_id, contribucion_id, usuario, decision, token=None):
    """El master aplica (aprobada) o rechaza; VAL-22-estilo: una decisión sola."""
    from app.infra.mesas import es_gm_mesa

    try:
        pag_es, _ = es_gm_mesa(int(mesa_id), usuario, token=token)
    except (LookupError, RuntimeError):
        raise HTTPException(status_code=502, detail="No se pudo verificar la membresía.") from None
    if not pag_es:
        raise HTTPException(status_code=403, detail="Esta acción es exclusiva del master.")

    import json as _json

    with get_connection() as conn, conn.transaction():
        fila = conn.execute(
            "UPDATE wiki_contribuciones SET estado = %s, revisado_por = %s, revisado_en = now()"
            " WHERE id = %s AND mesa_id = %s AND estado = 'pendiente' RETURNING *",
            (decision, str(usuario["sub"]), contribucion_id, str(mesa_id)),
        ).fetchone()
        if fila is None:
            raise ContribucionNoProcesableError("La contribución ya fue resuelta.")

        if decision == "aprobada":
            cuerpo = fila["cuerpo"] or []
            # F4: el cuerpo ya es una bolsa de bloques; NO lo re-envuelva
            # (el bug era [[{texto}]] por el dumps+loads extra).
            pag = conn.execute(
                "SELECT contenido FROM wiki_paginas WHERE id = %s", (fila["pagina_id"],)
            ).fetchone()
            contenido_actual = pag["contenido"] or []
            nuevos = cuerpo
            conn.execute(
                "UPDATE wiki_paginas SET contenido = %s WHERE id = %s",
                (_json.dumps(contenido_actual + list(nuevos)), fila["pagina_id"]),
            )
    return _serializar_c(fila)
