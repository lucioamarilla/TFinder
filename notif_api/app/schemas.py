from typing import Any, Optional

from pydantic import BaseModel


class NotificacionOut(BaseModel):
    id: int
    grupo: Optional[str] = "mesas"
    icono: Optional[str] = "solicitud"
    leida: bool = False
    autor: Optional[str] = None
    mensaje: str
    entidad: Optional[str] = None
    detalle: Optional[str] = None
    enlace: Optional[Any] = None
    fecha: Optional[str] = None


class EventOut(BaseModel):
    id: int
    entidadTipo: str
    entidadId: Optional[str] = None
    accion: str
    usuarioId: Optional[str] = None
    metadata: Optional[Any] = None
    ocurridoEn: Optional[str] = None