"""mesas-api: CRUD de mesas + auth (B03) + matchmaking (f05/B04) + sesiones (B07).

El andamiaje (lifespan, middlewares, salud, errores) lo aporta crear_app
(app/servicio.py); acá queda solo lo propio del servicio.
"""

from mesas_api.app import db as mesas_db
from mesas_api.app.controllers.mesas import (
    CupoMenorError,
    MesaNotFoundError,
    MesaUsurpadoError,
)
from mesas_api.app.controllers.sesiones_controller import (
    SesionCerradaError,
    SesionNotFoundError,
)
from mesas_api.app.controllers.solicitudes_controller import (
    AccionInvalidaError,
    SalirDeMasterError,
    CupoAgotadoError,
    MesaCerradaError,
    MesaNoExisteError,
    SolicitudDuplicadaError,
    SolicitudNoExisteError,
    SolicitudNoProcesableError,
    SolicitudProhibidaError,
)
from mesas_api.app.errors import (
    manejar_accion_invalida,
    manejar_conflicto,
    manejar_mesa_inexistente,
    manejar_no_encontrado,
    manejar_prohibido,
    manejar_qr_conflicto,
    manejar_qr_invalido,
    manejar_sesion_inexistente,
    manejar_solicitud_inexistente,
)
from mesas_api.app.init_db import init_db as mesas_init_db
from mesas_api.app.routes.auth_routes import router as auth_router
from mesas_api.app.routes.v1.fechas import router as fechas_router
from mesas_api.app.routes.v1.matchmaking import router as matchmaking_router
from mesas_api.app.routes.v1.mesas import router as mesas_router
from mesas_api.app.routes.v1.sesiones import router as sesiones_router
from mesas_api.app.routes.v1.solicitudes import router as solicitudes_router
from mesas_api.app.services.qr_asistencia import _Conflict, _Invalid
from app.servicio import crear_app

app = crear_app(
    titulo="TFinder · Mesas API",
    version="0.5.0",
    servicio="mesas",
    db=mesas_db,
    init_db=mesas_init_db,
    routers=[
        mesas_router,
        auth_router,
        matchmaking_router,
        solicitudes_router,
        fechas_router,
        sesiones_router,
    ],
    adicionales={
        MesaNotFoundError: manejar_no_encontrado,
        CupoAgotadoError: manejar_conflicto,
        SolicitudNoProcesableError: manejar_conflicto,
        MesaNoExisteError: manejar_mesa_inexistente,
        MesaCerradaError: manejar_conflicto,
        MesaUsurpadoError: manejar_prohibido,
        CupoMenorError: manejar_conflicto,
        SolicitudDuplicadaError: manejar_conflicto,
        SolicitudNoExisteError: manejar_solicitud_inexistente,
        SolicitudProhibidaError: manejar_prohibido,
        SalirDeMasterError: manejar_conflicto,
        AccionInvalidaError: manejar_accion_invalida,
        SesionNotFoundError: manejar_sesion_inexistente,
        SesionCerradaError: manejar_conflicto,
        _Conflict: manejar_qr_conflicto,
        _Invalid: manejar_qr_invalido,
    },
)