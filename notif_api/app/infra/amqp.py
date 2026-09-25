import pika

from app.infra.rabbitmq import get_params

EXCHANGE = "tfinder.events"
DLX = "tfinder.dlx"

COLA_MESA = "notif.mesa"
COLA_SESION = "notif.sesion"
COLA_PDF = "doc.pdf"
COLA_DLQ = "dlq.general"


def declarar(conn=None):
    """Declara (idempotente) exchanges y colas con DLQ y bindings de topic."""
    cerrar = conn is None
    conn = conn or pika.BlockingConnection(get_params())
    canal = conn.channel()
    canal.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    canal.exchange_declare(exchange=DLX, exchange_type="topic", durable=True)

    def cola(nombre, routing):
        canal.queue_declare(
            queue=nombre,
            durable=True,
            arguments={"x-dead-letter-exchange": DLX},
        )
        canal.queue_bind(queue=nombre, exchange=EXCHANGE, routing_key=routing)

    cola(COLA_MESA, "mesa.*")
    cola(COLA_SESION, "sesion.*")
    cola(COLA_PDF, "doc.pdf.*")
    canal.queue_declare(queue=COLA_DLQ, durable=True)
    if cerrar:
        conn.close()
    return conn