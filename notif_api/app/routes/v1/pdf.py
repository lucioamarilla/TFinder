from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from notif_api.app.models.notif import obtener_documento

router = APIRouter(prefix="/api/v1/pdf", tags=["pdf"])


def _serializar_documento(doc: dict) -> dict:
    return {
        "documento_id": doc["id"],
        "tipo": doc["tipo"],
        "id_origen": doc["id_origen"],
        "estado": doc["estado"],
        "fecha": doc["fecha"].isoformat() if doc.get("fecha") else None,
    }


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


@router.get("/{documento_id}/estado")
def estado(documento_id: str):
    doc = obtener_documento(documento_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Documento no existe")
    return _serializar_documento(doc)