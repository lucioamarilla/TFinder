from contextlib import asynccontextmanager
from threading import Thread

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.infra.logge import logger
from app.infra.ready import evaluar_ready
from app.middleware.log_context import CorrelationMiddleware
from notif_api.app.consumers import mesa as mesa_consumer
from notif_api.app.consumers import sesion as sesion_consumer
from notif_api.app.db import abrir_pool, cerrar_pool, get_pool
from notif_api.app.errors import manejar_error_interno, manejar_validacion
from notif_api.app.init_db import init_db
from notif_api.app.models.notif import listar_dlq
from notif_api.app.routes.v1.auth import router as auth_router
from notif_api.app.routes.v1.emails import router as emails_router
from notif_api.app.routes.v1.event_log import router as event_log_router
from notif_api.app.routes.v1.notificaciones import router as notificaciones_router
from notif_api.app.routes.v1.pdf import router as pdf_router
from notif_api.app.workers import pdf as pdf_worker

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    abrir_pool()
    init_db()
    logger.info("servicio iniciado")
    Thread(target=mesa_consumer.run, daemon=True).start()
    Thread(target=sesion_consumer.run, daemon=True).start()
    Thread(target=pdf_worker.run, daemon=True).start()
    yield
    cerrar_pool()


app = FastAPI(title="TFinder · Notif API", version="0.6.0", lifespan=lifespan)
app.add_middleware(CorrelationMiddleware)
app.add_exception_handler(RequestValidationError, manejar_validacion)
app.add_exception_handler(Exception, manejar_error_interno)
app.include_router(notificaciones_router)
app.include_router(auth_router)
app.include_router(event_log_router)
app.include_router(emails_router)
app.include_router(pdf_router)


@app.get("/api/v1/dlq")
def dlq(limite: int = 50):
    return listar_dlq(limite)


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