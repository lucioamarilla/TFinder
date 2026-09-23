from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.infra.logge import logger
from app.infra.ready import evaluar_ready
from app.middleware.log_context import CorrelationMiddleware
from mesas_api.app.controllers.mesas import MesaNotFoundError
from mesas_api.app.controllers.solicitudes_controller import (
    CupoAgotadoError,
    MesaNoExisteError,
    SolicitudEnProcesoError,
)
from mesas_api.app.db import abrir_pool, cerrar_pool, get_pool
from mesas_api.app.errors import (
    manejar_conflicto,
    manejar_error_interno,
    manejar_http,
    manejar_mesa_inexistente,
    manejar_no_encontrado,
    manejar_validacion,
)
from mesas_api.app.init_db import init_db
from mesas_api.app.routes.auth_routes import router as auth_router
from mesas_api.app.routes.v1.matchmaking import router as matchmaking_router
from mesas_api.app.routes.v1.mesas import router as mesas_router
from mesas_api.app.routes.v1.solicitudes import router as solicitudes_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    abrir_pool()
    init_db()
    logger.info("servicio iniciado")
    yield
    cerrar_pool()


app = FastAPI(title="TFinder · Mesas API", version="0.5.0", lifespan=lifespan)
app.add_middleware(CorrelationMiddleware)
app.add_exception_handler(MesaNotFoundError, manejar_no_encontrado)
app.add_exception_handler(CupoAgotadoError, manejar_conflicto)
app.add_exception_handler(SolicitudEnProcesoError, manejar_conflicto)
app.add_exception_handler(MesaNoExisteError, manejar_mesa_inexistente)
app.add_exception_handler(RequestValidationError, manejar_validacion)
app.add_exception_handler(HTTPException, manejar_http)
app.add_exception_handler(Exception, manejar_error_interno)
app.include_router(mesas_router)
app.include_router(auth_router)
app.include_router(matchmaking_router)
app.include_router(solicitudes_router)


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