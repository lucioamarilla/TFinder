"""feed-api: feed/wiki/diario de campañas (lectura pública + PDF de diario)."""

from feed_api.app import db as feed_db
from feed_api.app.controllers.wiki_contribuciones import ContribucionNoProcesableError
from feed_api.app.init_db import init_db as feed_init_db
from feed_api.app.routes.v1.diario import router as diario_router
from feed_api.app.routes.v1.feed import router as feed_router
from feed_api.app.routes.v1.uploads import router as uploads_router
from feed_api.app.routes.v1.wiki import router as wiki_router
from feed_api.app.seed_demo import seed_demo_if_enabled as seed_demo_feed
from app.infra.errors import manejar_conflicto
from app.servicio import crear_app

app = crear_app(
    titulo="TFinder · Feed API",
    version="0.3.0",
    servicio="feed",
    db=feed_db,
    init_db=feed_init_db,
    routers=[feed_router, wiki_router, diario_router, uploads_router],
    adicionales={ContribucionNoProcesableError: manejar_conflicto},
    seed=seed_demo_feed,
)
