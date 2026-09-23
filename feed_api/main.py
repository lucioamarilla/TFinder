from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.infra.logge import logger
from app.infra.ready import evaluar_ready
from app.middleware.log_context import CorrelationMiddleware
from feed_api.app.db import abrir_pool, cerrar_pool, get_pool
from feed_api.app.errors import manejar_error_interno, manejar_validacion
from feed_api.app.init_db import init_db
from feed_api.app.routes.v1.feed import router as feed_router
from feed_api.app.routes.v1.wiki import router as wiki_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    abrir_pool()
    init_db()
    logger.info("servicio iniciado")
    yield
    cerrar_pool()


app = FastAPI(title="TFinder · Feed API", version="0.3.0", lifespan=lifespan)
app.add_middleware(CorrelationMiddleware)
app.add_exception_handler(RequestValidationError, manejar_validacion)
app.add_exception_handler(Exception, manejar_error_interno)
app.include_router(feed_router)
app.include_router(wiki_router)


def psql_disponible():
    abrir_pool()
    return get_pool().connection()


@app.get("/health")
def health():
    abrir_pool()
    with get_pool().connection() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok", "servicio": "feed-api"}


@app.get("/live")
def live():
    return {"estado": "vivo"}


@app.get("/ready")
def ready():
    return evaluar_ready(psql_disponible)