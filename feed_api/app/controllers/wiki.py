import json

from feed_api.app.db import get_connection
from feed_api.app.schemas import PaginaOut

TIPOS_VALIDOS = ("NPC", "Lugar", "Criatura", "Nota", "Sesión")
VISIBILIDADES = ("privada", "jugadores", "publica")


class WikiError(Exception):
    """403/408 de visibilidad — el mensaje repite VAL/RN de la wiki."""


def _serializar_pagina(fila, include_mesa=False):
    f = dict(fila)
    if include_mesa:
        f["mesaId"] = f.pop("mesa_id", None)
    else:
        f.pop("mesa_id", None)
    f.pop("creado_en", None)
    return PaginaOut(**f)


def obtener_wiki(mesa_id):
    with get_connection() as conn:
        if mesa_id:
            filas = conn.execute(
                "SELECT * FROM wiki_paginas WHERE mesa_id = %s ORDER BY id",
                (mesa_id,),
            ).fetchall()
        else:
            filas = conn.execute("SELECT * FROM wiki_paginas ORDER BY id").fetchall()
    paginas = [_serializar_pagina(f) for f in filas]
    carpetas = {}
    for pagina in paginas:
        clave = pagina.carpeta or "notas"
        carpetas.setdefault(clave, {"count": 0})
        carpetas[clave]["count"] += 1
    carpetas_out = [
        {
            "id": clave,
            "nombre": clave,
            "icono": "scroll",
            "abierta": True,
            **datos,
        }
        for clave, datos in carpetas.items()
    ]
    return {"carpetas": carpetas_out, "paginas": paginas, "total": len(paginas)}

# ---- P1.6: CRUD con visibilidad (RF-08/RF-09, RN-05) -------------------------

from fastapi import HTTPException

from feed_api.app.services.mesas import es_gm_mesa, es_miembro_aceptado


def _propiedad_o_403(mesa_id, usuario, token):
    if mesa_id is None or mesa_id == "" or str(mesa_id).lstrip("-").isdigit() is False:
        raise HTTPException(status_code=400, detail="mesa_id inválido.")
    try:
        gmid, mesa = es_gm_mesa(int(mesa_id), usuario, token=token)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from None
    if not gmid:
        raise HTTPException(
            status_code=403,
            detail="La wiki es privada del GM propietario para escribir (RN-02).",
        )
    return mesa


def crear_pagina_controller(mesa_id, usuario, datos, token=None):
    _propiedad_o_403(mesa_id, usuario, token)
    titulo = (datos.get("titulo") or "").strip()
    if not titulo:
        raise HTTPException(status_code=400, detail="El título de la página es obligatorio.")
    tipo = datos.get("tipo") or "Nota"
    if tipo not in TIPOS_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail="El tipo de página debe ser uno de: " + ", ".join(TIPOS_VALIDOS) + ".",
        )
    visibilidad = datos.get("visibilidad") or "jugadores"
    if visibilidad not in VISIBILIDADES:
        raise HTTPException(
            status_code=400,
            detail="La visibilidad debe ser privada, jugadores o publica.",
        )
    with get_connection() as conn:
        fila = conn.execute(
            "INSERT INTO wiki_paginas (mesa_id, carpeta, titulo, tipo, fecha, resumen,"
            " contenido, visibilidad) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *",
            (
                str(mesa_id),
                datos.get("carpeta") or "notas",
                titulo,
                tipo,
                datos.get("fecha"),
                datos.get("resumen"),
                _contenido_json(datos),
                visibilidad,
            ),
        ).fetchone()
    return _serializar_pagina(fila, include_mesa=True)


def _contenido_json(datos):
    cuerpo = datos.get("cuerpo")
    if cuerpo:
        return json.dumps([{"kind": "parrafo", "texto": cuerpo}])
    return json.dumps(datos.get("contenido") or [])


def obtener_pagina_controller(mesa_id, pagina_id, usuario, token):
    """RF-09/RN-05: lectura solo con permisos según visibilidad."""
    with get_connection() as conn:
        fila = conn.execute("SELECT * FROM wiki_paginas WHERE id = %s", (pagina_id,)).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="La página de wiki no existe.")
    visibilidad = fila["visibilidad"] or "jugadores"
    if visibilidad == "publica":
        return _serializar_pagina(fila, include_mesa=True)
    if visibilidad == "privada":
        try:
            gmid, _ = es_gm_mesa(int(mesa_id or fila["mesa_id"]), usuario, token=token)
        except (LookupError, RuntimeError):
            raise HTTPException(status_code=403, detail="No tienes permisos para ver esta página.") from None
        if not gmid:
            raise HTTPException(status_code=403, detail="No tienes permisos para ver esta página.")
    else:  # 'jugadores'
        if usuario is None:
            raise HTTPException(status_code=403, detail="No tienes permisos para ver esta página.")
        try:
            miembro = es_miembro_aceptado(int(fila["mesa_id"]), usuario, token)
        except (LookupError, RuntimeError, PermissionError):
            raise HTTPException(status_code=403, detail="No tienes permisos para ver esta página.") from None
        if not miembro:
            raise HTTPException(status_code=403, detail="No tienes permisos para ver esta página.")
    return _serializar_pagina(fila, include_mesa=True)


def actualizar_pagina_controller(mesa_id, pagina_id, usuario, datos, token=None):
    with get_connection() as conn:
        fil = conn.execute(
            "SELECT mesa_id FROM wiki_paginas WHERE id = %s", (pagina_id,)
        ).fetchone()
    if fil is None:
        raise HTTPException(status_code=404, detail="La página de wiki no existe.")
    _propiedad_o_403(fil["mesa_id"], usuario, token)
    cambios, params = [], []
    for campo in ("titulo", "carpeta", "tipo", "fecha", "resumen", "visibilidad"):
        if campo in datos and datos[campo] is not None:
            if campo == "tipo" and datos[campo] not in TIPOS_VALIDOS:
                raise HTTPException(
                    status_code=400,
                    detail="El tipo de página debe ser uno de: " + ", ".join(TIPOS_VALIDOS) + ".",
                )
            if campo == "visibilidad" and datos[campo] not in VISIBILIDADES:
                raise HTTPException(
                    status_code=400,
                    detail="La visibilidad debe ser privada, jugadores o publica.",
                )
            cambios.append(f"{campo} = %s")
            params.append(datos[campo])
    if "cuerpo" in datos or "contenido" in datos:
        cambios.append("contenido = %s")
        params.append(_contenido_json(datos))
    if not cambios:
        raise HTTPException(status_code=400, detail="Nada para actualizar.")
    params.append(pagina_id)
    with get_connection() as conn:
        fila = conn.execute(
            f"UPDATE wiki_paginas SET {', '.join(cambios)} WHERE id = %s RETURNING *", params
        ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="La página de wiki no existe.")
    return _serializar_pagina(fila, include_mesa=True)


def eliminar_pagina_controller(mesa_id, pagina_id, usuario, token=None):
    with get_connection() as conn:
        fil = conn.execute(
            "SELECT mesa_id FROM wiki_paginas WHERE id = %s", (pagina_id,)
        ).fetchone()
    if fil is None:
        raise HTTPException(status_code=404, detail="La página de wiki no existe.")
    _propiedad_o_403(fil["mesa_id"], usuario, token)
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM wiki_paginas WHERE id = %s", (pagina_id,))
    return None
