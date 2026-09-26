from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from app.infra.errors import registrar_manejadores
from app.infra.logge import logger
from app.infra.ready import evaluar_ready
from app.middleware.error_envelope import ErrorEnvelopeMiddleware
from app.middleware.log_context import CorrelationMiddleware
from mesas_api.app.controllers.mesas import MesaNotFoundError
from mesas_api.app.controllers.sesiones_controller import SesionNotFoundError
from mesas_api.app.controllers.solicitudes_controller import (
    CupoAgotadoError,
    MesaNoExisteError,
    SolicitudEnProcesoError,
)
from mesas_api.app.db import abrir_pool, cerrar_pool, get_pool
from mesas_api.app.errors import (
    manejar_conflicto,
    manejar_mesa_inexistente,
    manejar_no_encontrado,
    manejar_qr_conflicto,
    manejar_qr_invalido,
    manejar_sesion_inexistente,
)
from mesas_api.app.init_db import init_db
from mesas_api.app.routes.auth_routes import router as auth_router
from mesas_api.app.routes.v1.matchmaking import router as matchmaking_router
from mesas_api.app.routes.v1.mesas import router as mesas_router
from mesas_api.app.routes.v1.sesiones import router as sesiones_router
from mesas_api.app.seed_demo import seed_demo_if_enabled as seed_demo_mesas
from mesas_api.app.routes.v1.solicitudes import router as solicitudes_router
from mesas_api.app.services.qr_asistencia import _Conflict, _Invalid

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    abrir_pool()
    init_db()
    seed_demo_mesas()
    logger.info("servicio iniciado")
    yield
    cerrar_pool()


app = FastAPI(title="TFinder · Mesas API", version="0.5.0", lifespan=lifespan)
app.add_middleware(ErrorEnvelopeMiddleware)
app.add_middleware(CorrelationMiddleware)
registrar_manejadores(
    app,
    "mesas",
    adicionales={
        MesaNotFoundError: manejar_no_encontrado,
        CupoAgotadoError: manejar_conflicto,
        SolicitudEnProcesoError: manejar_conflicto,
        MesaNoExisteError: manejar_mesa_inexistente,
        SesionNotFoundError: manejar_sesion_inexistente,
        _Conflict: manejar_qr_conflicto,
        _Invalid: manejar_qr_invalido,
    },
)
app.include_router(mesas_router)
app.include_router(auth_router)
app.include_router(matchmaking_router)
app.include_router(solicitudes_router)
app.include_router(sesiones_router)


def psql_disponible():
    abrir_pool()
    return get_pool().connection()


@app.get("/health")
def health():
    abrir_pool()
    with get_pool().connection() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok", "servicio": "mesas-api"}


@app.get("/live")
def live():
    return {"estado": "vivo"}


@app.get("/ready")
def ready():
    return evaluar_ready(psql_disponible)