from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

EstadoMesa = Literal["abierta", "cerrada"]


class MesaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1)
    sistema: str = Field(min_length=1)
    descripcion: Optional[str] = None
    tono: Optional[str] = None
    horario: Optional[str] = None
    estado: EstadoMesa = "abierta"
    nivel_inicial: Optional[int] = Field(default=None, ge=0)
    jugadores_max: Optional[int] = Field(default=None, gt=0)


class MesaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: Optional[str] = Field(default=None, min_length=1)
    sistema: Optional[str] = Field(default=None, min_length=1)
    descripcion: Optional[str] = None
    tono: Optional[str] = None
    horario: Optional[str] = None
    estado: Optional[EstadoMesa] = None
    nivel_inicial: Optional[int] = Field(default=None, ge=0)
    jugadores_max: Optional[int] = Field(default=None, gt=0)


class MesaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    sistema: str
    descripcion: Optional[str] = None
    tono: Optional[str] = None
    horario: Optional[str] = None
    estado: EstadoMesa
    nivel_inicial: Optional[int] = None
    jugadores_max: Optional[int] = None
    fecha_creacion: str