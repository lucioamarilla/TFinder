from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from builds_api.app.controllers.builds import BuildNotFoundError
from builds_api.app.db import abrir_pool, cerrar_pool, get_pool
from builds_api.app.errors import (
    manejar_error_interno,
    manejar_no_encontrado,
    manejar_validacion,
)
from builds_api.app.init_db import init_db
from builds_api.app.routes.v1.builds import router as builds_router
from builds_api.app.routes.v1.tags import router as tags_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    abrir_pool()
    init_db()
    yield
    cerrar_pool()


app = FastAPI(title="TFinder · Builds API", version="0.2.0", lifespan=lifespan)
app.add_exception_handler(BuildNotFoundError, manejar_no_encontrado)
app.add_exception_handler(RequestValidationError, manejar_validacion)
app.add_exception_handler(Exception, manejar_error_interno)
app.include_router(builds_router)
app.include_router(tags_router)


@app.get("/health")
def health():
    abrir_pool()
    with get_pool().connection() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok", "servicio": "builds-api"}