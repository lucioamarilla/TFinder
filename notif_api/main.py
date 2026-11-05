"""notif-api: notificaciones vivas, emails, PDF, event-log y DLQ (f08/f09/B05).

Además del andamiaje estándar, arranca en hilos daemon los consumidores de
RabbitMQ (mesas, sesiones) y el worker de PDF — era la única diferencia de su
lifespan respecto a los otros tres servicios.
"""

from notif_api.app import db as notif_db
from notif_api.app.consumers import mesa as mesa_consumer
from notif_api.app.consumers import sesion as sesion_consumer
from notif_api.app.init_db import init_db as notif_init_db
from notif_api.app.routes.v1.auth import router as auth_router
from notif_api.app.routes.v1.dlq import router as dlq_router
from notif_api.app.routes.v1.emails import router as emails_router
from notif_api.app.routes.v1.event_log import router as event_log_router
from notif_api.app.routes.v1.notificaciones import router as notificaciones_router
from notif_api.app.routes.v1.pdf import router as pdf_router
from notif_api.app.workers import pdf as pdf_worker
from app.servicio import crear_app

app = crear_app(
    titulo="TFinder · Notif API",
    version="0.6.0",
    servicio="notif",
    db=notif_db,
    init_db=notif_init_db,
    routers=[
        notificaciones_router,
        auth_router,
        event_log_router,
        emails_router,
        pdf_router,
        dlq_router,
    ],
    hilos=(
        mesa_consumer.run,
        sesion_consumer.run,
        pdf_worker.run,
    ),
)