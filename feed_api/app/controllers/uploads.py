"""F5: uploads (imágenes de perfil y adjuntos del foro).

Reglas del pliego F5:
  - whitelist de tipo y tamaño (png/jpeg/webp, 5 MB máx);
  - servidas por feed-api en /api/v1/uploads/{id} (GET público, FileResponse);
  - el archivo de disco vive en UPLOAD_FILES_DIR (./storage/uploads).
"""

import os
import uuid

from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse

from feed_api.app.db import get_connection

_DIR = os.getenv("UPLOAD_FILES_DIR", "./storage/uploads")

_MIME_A_EXT = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp"}
_TAMANO_MAX = 5 * 1024 * 1024


class UploadInvalidoError(Exception):
    pass


def guardar_imagen_controller(usuario, upload: UploadFile):
    """F5: guarda una imagen y registra el archivo en la tabla uploads."""
    contenido = upload.file.read()
    tipo = upload.content_type or ""
    if tipo not in _MIME_A_EXT:
        raise HTTPException(status_code=400, detail="Solo se aceptan imágenes PNG, JPG o WEBP.")
    if len(contenido) > _TAMANO_MAX:
        raise HTTPException(status_code=400, detail="La imagen supera el límite de 5 MB.")

    ident = uuid.uuid4().hex
    ext = _MIME_A_EXT[tipo]
    os.makedirs(_DIR, exist_ok=True)
    ruta = os.path.join(_DIR, f"{ident}.{ext}")
    with open(ruta, "wb") as fh:
        fh.write(contenido)

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO uploads (id, tipo, contenido, tamano, owner_id, ruta)"
            " VALUES (%s, 'imagen', %s, %s, %s, %s)",
            (ident, tipo, len(contenido), str(usuario["sub"]), ruta),
        )
    return {"id": ident, "mime": tipo, "tamano": len(contenido), "url": f"/api/v1/uploads/{ident}"}


def obtener_archivo_controller(ident: str):
    from feed_api.app.db import get_connection as _c

    with get_connection() as conn:
        fila = conn.execute("SELECT * FROM uploads WHERE id = %s", (ident,)).fetchone()
    if fila is None:
        from app.infra.errors import body_error
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=404, content=body_error(404, "El archivo no existe."))
    if not os.path.exists(fila["ruta"]):
        raise HTTPException(status_code=404, detail="El archivo no existe más en el disco.")
    return FileResponse(fila["ruta"], media_type=fila["contenido"])
