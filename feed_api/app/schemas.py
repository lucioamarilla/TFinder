from typing import Any, Optional

from pydantic import BaseModel, Field

class DiarioCreate(BaseModel):
    """Contenido de la publicación del diario de sesión."""

    titulo: str = Field(min_length=1)
    cuerpo: str = Field(min_length=1)


class PostOut(BaseModel):
    id: int
    tipo: Optional[str] = "post"
    autor: Optional[str] = None
    autorId: Optional[str] = None
    autorNombre: Optional[str] = None
    iniciales: Optional[str] = None
    tono: Optional[str] = None
    tiempo: Optional[str] = None
    horas: int = 0
    etiqueta: Optional[str] = None
    comunidad: Optional[str] = None
    titulo: str
    cuerpo: Optional[str] = None
    votos: int = 0
    totalComentarios: int = 0
    embed: Optional[Any] = None
    comentarios: list = []


class PaginaOut(BaseModel):
    id: int
    mesaId: Optional[str] = None
    carpeta: Optional[str] = "notas"
    titulo: str
    tipo: Optional[str] = "NOTA"
    fecha: Optional[str] = None
    resumen: Optional[str] = None
    visibilidad: Optional[str] = "jugadores"
    contenido: list = []
    parentId: Optional[int] = None
    markdown: Optional[str] = None