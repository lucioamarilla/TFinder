"""Fábrica de servicios FastAPI (ADR-006: servicios por dominio).

Los cuatro main.py repetían a mano la misma estructura: dotenv, lifespan con
pool + init_ddl + seed (+ hilos de consumidores en notif), middlewares de
envelope y correlación, manejo de errores, routers ordenados y /health /live
/ready. La fábrica absorbe esa estructura; cada main declara solo lo que hace
distinto a los demás (routers, errores de dominio, seed, hilos).

Los cuerpos exactos de /health, /live y /ready (y los títulos OpenAPI) están
congelados en tests/test_congelado_salud.py: cualquier cambio es una decisión
explícita, no un efecto lateral del refactor.
"""

from contextlib import asynccontextmanager
from threading import Thread
from types import ModuleType

from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.openapi.utils import get_openapi

from app.infra import metrics
from app.infra.errors import registrar_manejadores
from app.infra.logge import logger
from app.infra.ready import evaluar_ready
from app.middleware.error_envelope import ErrorEnvelopeMiddleware
from app.middleware.log_context import CorrelationMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

import os
from app.infra import metrics


def crear_app(
    *,
    titulo: str,
    version: str,
    servicio: str,  # nombre corto del dominio: "mesas" | "builds" | "feed" | "notif"
    db: ModuleType,  # db.py del servicio dueño (abrir_pool/cerrar_pool/get_pool)
    init_db,  # callable: aplica el DDL del dueño
    routers,  # orden de include_router, tal como quedó en el main original
    adicionales: dict | None = None,  # errores de dominio -> manejadores
    seed=None,  # seed_demo_if_enabled del servicio (opcional)
    hilos=(),  # en notif: run() de consumidores y workers que arrancan daemon
) -> FastAPI:
    load_dotenv()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        db.abrir_pool()
        init_db()
        if seed:
            seed()
        logger.info("servicio iniciado")
        for objetivo in hilos:
            Thread(target=objetivo, daemon=True).start()
        yield
        db.cerrar_pool()

    app = FastAPI(title=titulo, version=version, lifespan=lifespan)
    app.add_middleware(ErrorEnvelopeMiddleware)
    app.add_middleware(CorrelationMiddleware)
    app.add_middleware(RateLimitMiddleware, limite=int(os.getenv("RATE_LIMIT_PER_MIN", "100")))

    @app.middleware("http")
    async def _medir(request, call_next):
        respuesta = await call_next(request)
        metrics.contar(servicio, respuesta.status_code)
        return respuesta

    @app.get("/metrics")
    def metrics_endpoint():
        return Response(
            content=metrics.exposicion(servicio),
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )

    def _openapi_con_bearer():
        """OpenAPI con securitySchemes (BearerAuth) — audit 'Que le falta' 7.3."""
        documento = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        )
        documento.setdefault("components", {}).setdefault("securitySchemes", {})
        documento["components"]["securitySchemes"]["BearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Access token JWT emitido por mesas-api (POST /api/v1/auth/login).",
        }
        return documento

    app.openapi = _openapi_con_bearer

    registrar_manejadores(app, servicio, adicionales=adicionales)
    for router in routers:
        app.include_router(router)

    def _psql_disponible():
        db.abrir_pool()
        return db.get_pool().connection()

    @app.get("/health")
    def health():
        db.abrir_pool()
        with db.get_pool().connection() as conn:
            conn.execute("SELECT 1")
        return {"status": "ok", "servicio": f"{servicio}-api"}

    @app.get("/live")
    def live():
        return {"estado": "vivo"}

    @app.get("/ready")
    def ready():
        return evaluar_ready(_psql_disponible)

    return app
