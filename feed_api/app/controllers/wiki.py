from feed_api.app.db import get_connection
from feed_api.app.schemas import PaginaOut


def _serializar_pagina(fila):
    f = dict(fila)
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