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

    # El binding al DLX es obligatorio: las colas de arriba declaran
    # x-dead-letter-exchange, asi que un nack(requeue=False) o un reject
    # enrutan el mensaje a DLX. Sin este binding el exchange no tiene destino
    # y RabbitMQ descarta el mensaje en silencio. El routing key "#" atrapa
    # cualquier tipo de evento.
    canal.queue_declare(queue=COLA_DLQ, durable=True)
    canal.queue_bind(queue=COLA_DLQ, exchange=DLX, routing_key="#")
    if cerrar:
        conn.close()
    return conn