"""Publicación del diario de sesión (cierre AE2).

RNF-04: feed-api nunca consulta por SQL a mesas_db; validar la existencia de
la mesa es responsabilidad de mesas-api (contrato REST/evento). Feed-api
propietario del dominio del diario en feed_db: el contenido se persiste en
publicaciones (con referencia a la sesión en embed) y luego se emite el
evento sesion.diario_publicado.
"""

import json

from feed_api.app.db import get_connection
from feed_api.app.services.eventos import publicar_sesion_diario


def publicar_diario_controller(
    mesa_id,
    sesion_id: int,
    usuario_id: int,
    autor: str,
    titulo: str,
    cuerpo: str,
    correlation_id: str = "-",
) -> dict:
    """Persiste la publicación del diario y emite sesion.diario_publicado.

    Idempotente por (mesa, sesión): si ya existe una publicación de diario
    para esa sesión, se devuelve la existente sin duplicar ni reemitir el evento.
    """
    with get_connection() as conn:
        existente = conn.execute(
            "SELECT id FROM publicaciones WHERE embed->>'sesion_id' = %s "
            "AND embed->>'es_diario' = 'true' AND autor_id = %s",
            (str(sesion_id), str(mesa_id)),
        ).fetchone()
        if existente is not None:
            return {
                "id": existente["id"],
                "mesa_id": str(mesa_id),
                "sesion_id": sesion_id,
                "titulo": titulo,
                "estado": "ya_publicado",
            }

        fila = conn.execute(
            "INSERT INTO publicaciones (tipo, autor, autor_id, autor_nombre, titulo, cuerpo, embed)"
            " VALUES ('post', %s, %s, %s, %s, %s, %s::jsonb)"
            " RETURNING id",
            (
                autor,
                str(mesa_id),
                autor,
                titulo,
                cuerpo,
                json.dumps({"sesion_id": sesion_id, "es_diario": True}),
            ),
        ).fetchone()

    publicar_sesion_diario(
        mesa_id, sesion_id, usuario_id, titulo, correlation_id=correlation_id
    )
    return {
        "id": fila["id"],
        "mesa_id": str(mesa_id),
        "sesion_id": sesion_id,
        "titulo": titulo,
        "estado": "publicado",
    }
