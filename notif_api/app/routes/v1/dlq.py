from fastapi import APIRouter, Depends, HTTPException

from notif_api.app.controllers.dlq import descartar_mensaje, reintentar_mensaje
from notif_api.app.middleware.auth import requerir_roles
from notif_api.app.models.notif import listar_dlq

router = APIRouter(prefix="/api/v1")
_admin = Depends(requerir_roles("admin"))


@router.get("/dlq", dependencies=[_admin])
def listar_dlq_endpoint(limite: int = 50):
    return listar_dlq(limite)


@router.post("/dlq/{id}/reintentar", dependencies=[_admin])
def reintentar_dlq_endpoint(id: int):
    fila = reintentar_mensaje(id)
    if fila is None:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado en DLQ")
    return {"ok": True, "id": fila["id"], "cola": fila["cola"]}


@router.delete("/dlq/{id}", dependencies=[_admin])
def descartar_dlq_endpoint(id: int):
    fila = descartar_mensaje(id)
    if fila is None:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado en DLQ")
    return {"ok": True, "id": fila["id"]}
