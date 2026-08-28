import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.controllers.mesas_controller import MesaNotFoundError
from app.db import init_db
from app.middleware.error_handler import manejar_no_encontrado, manejar_validacion
from app.routes.mesas_routes import router as mesas_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="TFinder", version="0.1.0", lifespan=lifespan)
app.add_exception_handler(MesaNotFoundError, manejar_no_encontrado)
app.add_exception_handler(RequestValidationError, manejar_validacion)
app.include_router(mesas_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )