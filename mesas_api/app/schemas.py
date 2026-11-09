from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

EstadoMesa = Literal["abierta", "cerrada"]

ROLES = Literal["usuario", "gm", "admin"]

# VAL-08: en el MVP el único sistema válido es Pathfinder 1e.
SistemaMesa = Literal["pf1e"]

EDITABLE_FIELDS = {
    "nombre",
    "sistema",
    "descripcion",
    "tono",
    "horario",
    "estado",
    "nivel_inicial",
    "jugadores_max",
}


class MesaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1)
    sistema: SistemaMesa
    descripcion: Optional[str] = None
    tono: Optional[str] = None
    horario: Optional[str] = None
    estado: EstadoMesa = "abierta"
    nivel_inicial: Optional[int] = Field(default=None, ge=0, strict=True)
    jugadores_max: Optional[int] = Field(default=None, gt=0, strict=True)


class MesaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: Optional[str] = Field(default=None, min_length=1)
    sistema: Optional[SistemaMesa] = None
    descripcion: Optional[str] = None
    tono: Optional[str] = None
    horario: Optional[str] = None
    estado: Optional[EstadoMesa] = None
    nivel_inicial: Optional[int] = Field(default=None, ge=0, strict=True)
    jugadores_max: Optional[int] = Field(default=None, gt=0, strict=True)


class MesaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    sistema: str
    gm_id: Optional[int] = None
    gm_nombre: Optional[str] = None
    descripcion: Optional[str] = None
    tono: Optional[str] = None
    horario: Optional[str] = None
    estado: EstadoMesa
    nivel_inicial: Optional[int] = None
    jugadores_actuales: int = 0
    jugadores_max: Optional[int] = None
    fecha_creacion: str


class MesaMiaOut(MesaOut):
    """F1: la misma mesa + el rol del usuario peticionante (master | jugador)."""

    mi_rol: str = "jugador"


class PerfilUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: Optional[str] = Field(default=None, min_length=1)
    bio: Optional[str] = None
    avatarUrl: Optional[str] = Field(default=None, alias="avatarUrl")
    avatar_url: Optional[str] = None


class AuthRegistro(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=8)
    nombre: str = Field(min_length=1)
    rol: ROLES = "usuario"


class SolicitudEmail(BaseModel):
    """Sólo un email: pedidos públicos (reenvío de código / solicita recupero)."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr


class VerificarCodigo(BaseModel):
    """Código de 6 dígitos enviado por mail (registro | recupero)."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    codigo: str = Field(pattern=r"^\d{6}$")


class ConfirmarRecupero(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    codigo: str = Field(pattern=r"^\d{6}$")
    nueva_password: str = Field(min_length=8)


class SesionOut(BaseModel):
    """Sesión de juego de una mesa (B07)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    mesa_id: int
    estado: EstadoMesa  # mismas reglas del CHECK de la tabla: abierta | cerrada
    fecha: str
    confirmada_at: Optional[str] = None


class AuthLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class AuthRefresh(BaseModel):
    refresh_token: str