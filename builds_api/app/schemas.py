from typing import Any, Optional

from pydantic import BaseModel


class BuildOut(BaseModel):
    id: int
    mesaId: Optional[int] = None
    persona: str
    handle: Optional[str] = None
    autor: Optional[str] = None
    categoria: Optional[str] = "mio"
    nombre: Optional[str] = None
    display: Optional[str] = None
    clase: Optional[str] = None
    raza: Optional[str] = None
    arquetipo: Optional[str] = None
    nivel: Optional[int] = None
    rol: Optional[str] = None
    alineamiento: Optional[str] = None
    alineamientoColor: Optional[str] = None
    privacidad: Optional[str] = "publico"
    actualizado: Optional[str] = None
    protagonista: bool = False
    detalle: Optional[str] = None
    favoritos: int = 0
    historial: list = []
    ficha: Optional[Any] = None


class TagOut(BaseModel):
    nombre: str