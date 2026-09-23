from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from mesas_api.app.controllers.mesas import MesaNotFoundError
from mesas_api.app.db import abrir_pool, cerrar_pool, get_pool
from mesas_api.app.errors import (
    manejar_error_interno,
    manejar_http,
    manejar_no_encontrado,
    manejar_validacion,
)
from mesas_api.app.init_db import init_db
from mesas_api.app.routes.auth_routes import router as auth_router
from mesas_api.app.routes.v1.mesas import router as mesas_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    abrir_pool()
    init_db()
    yield
    cerrar_pool()


app = FastAPI(title="TFinder · Mesas API", version="0.3.0", lifespan=lifespan)
app.add_exception_handler(MesaNotFoundError, manejar_no_encontrado)
app.add_exception_handler(RequestValidationError, manejar_validacion)
app.add_exception_handler(HTTPException, manejar_http)
app.add_exception_handler(Exception, manejar_error_interno)
app.include_router(mesas_router)
app.include_router(auth_router)


@app.get("/health")
def health():
    abrir_pool()
    with get_pool().connection() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok", "servicio": "mesas-api"}