from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.infra.logge import logger
from app.infra.ready import evaluar_ready
from app.middleware.log_context import CorrelationMiddleware
from notif_api.app.db import abrir_pool, cerrar_pool, get_pool
from notif_api.app.errors import manejar_error_interno, manejar_validacion
from notif_api.app.init_db import init_db
from notif_api.app.routes.v1.event_log import router as event_log_router
from notif_api.app.routes.v1.notificaciones import router as notificaciones_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    abrir_pool()
    init_db()
    logger.info("servicio iniciado")
    yield
    cerrar_pool()


app = FastAPI(title="TFinder · Notif API", version="0.3.0", lifespan=lifespan)
app.add_middleware(CorrelationMiddleware)
app.add_exception_handler(RequestValidationError, manejar_validacion)
app.add_exception_handler(Exception, manejar_error_interno)
app.include_router(notificaciones_router)
app.include_router(event_log_router)


def psql_disponible():
    abrir_pool()
    return get_pool().connection()


@app.get("/health")
def health():
    abrir_pool()
    with get_pool().connection() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok", "servicio": "notif-api"}


@app.get("/live")
def live():
    return {"estado": "vivo"}


@app.get("/ready")
def ready():
    return evaluar_ready(psql_disponible)