from fastapi import APIRouter, Depends, UploadFile

from feed_api.app.controllers.uploads import (
    guardar_imagen_controller,
    obtener_archivo_controller,
)
from feed_api.app.middleware.auth import usuario_actual

router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])


@router.post("", status_code=201)
def subir_imagen(upload: UploadFile, usuario: dict = Depends(usuario_actual)):
    """F5: PNG/JPG/WEBP, máx 5 MB. Devuelve la URL pública del archivo."""
    return guardar_imagen_controller(usuario, upload)


@router.get("/{ident}")
def bajar_imagen(ident: str):
    """Archivo visual público (el id es uuid no ceremonioso)."""
    return obtener_archivo_controller(ident)
