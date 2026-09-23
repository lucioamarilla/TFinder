from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from notif_api.app.models.notif import obtener_documento

router = APIRouter(prefix="/api/v1/pdf", tags=["pdf"])


@router.get("/{documento_id}")
def descargar(documento_id: str):
    doc = obtener_documento(documento_id)
    if doc is None or doc["estado"] != "listo" or not doc.get("ruta"):
        raise HTTPException(status_code=404, detail="Documento no disponible aún o no existe")
    return FileResponse(
        doc["ruta"],
        media_type="application/pdf",
        filename=f"tfinder_{doc['tipo']}_{doc['id_origen']}.pdf",
    )