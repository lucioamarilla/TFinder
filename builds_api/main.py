from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from app.infra.errors import registrar_manejadores
from app.infra.logge import logger
from app.infra.ready import evaluar_ready
from app.middleware.error_envelope import ErrorEnvelopeMiddleware
from app.middleware.log_context import CorrelationMiddleware
from builds_api.app.controllers.builds import BuildNotFoundError
from builds_api.app.db import abrir_pool, cerrar_pool, get_pool
from builds_api.app.errors import manejar_no_encontrado
from builds_api.app.init_db import init_db
from builds_api.app.routes.v1.build_pdf import router as build_pdf_router
from builds_api.app.routes.v1.builds import router as builds_router
from builds_api.app.routes.v1.tags import router as tags_router
from builds_api.app.seed_demo import seed_demo_if_enabled as seed_demo_builds

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    abrir_pool()
    init_db()
    seed_demo_builds()
    logger.info("servicio iniciado")
    yield
    cerrar_pool()


app = FastAPI(title="TFinder · Builds API", version="0.4.0", lifespan=lifespan)
app.add_middleware(ErrorEnvelopeMiddleware)
app.add_middleware(CorrelationMiddleware)
registrar_manejadores(
    app,
    "builds",
    adicionales={BuildNotFoundError: manejar_no_encontrado},
)
app.include_router(builds_router)
app.include_router(tags_router)
app.include_router(build_pdf_router)


def psql_disponible():
    abrir_pool()
    return get_pool().connection()


@app.get("/health")
def health():
    abrir_pool()
    with get_pool().connection() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok", "servicio": "builds-api"}


@app.get("/live")
def live():
    return {"estado": "vivo"}


@app.get("/ready")
def ready():
    return evaluar_ready(psql_disponible)