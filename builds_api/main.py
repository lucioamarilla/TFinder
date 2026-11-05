"""builds-api: catálogo de builds/tags + exportación PDF asíncrona (B05/B08)."""

from builds_api.app import db as builds_db
from builds_api.app.controllers.builds import (
    BuildNotFoundError,
    BuildProhibidoError,
    ValorInvalidoError,
)
from builds_api.app.errors import (
    manejar_no_encontrado,
    manejar_prohibido_build,
    manejar_valor_invalido_build,
)
from builds_api.app.init_db import init_db as builds_init_db
from builds_api.app.routes.v1.build_pdf import router as build_pdf_router
from builds_api.app.routes.v1.builds import router as builds_router
from builds_api.app.routes.v1.tags import router as tags_router
from builds_api.app.consumers.mesa import run as run_builds_consumer
from app.servicio import crear_app

app = crear_app(
    titulo="TFinder · Builds API",
    version="0.4.0",
    servicio="builds",
    db=builds_db,
    init_db=builds_init_db,
    routers=[builds_router, tags_router, build_pdf_router],
    adicionales={
        BuildNotFoundError: manejar_no_encontrado,
        BuildProhibidoError: manejar_prohibido_build,
        ValorInvalidoError: manejar_valor_invalido_build,
    },
    hilos=(run_builds_consumer,),
)