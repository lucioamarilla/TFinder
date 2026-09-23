import os
import uuid

import pika

from app.infra.logge import correlation_id_var


def get_params() -> pika.ConnectionParameters:
    """Devuelve los parametros de conexion a RabbitMQ desde RABBITMQ_URL.

    Default local alineado con docker-compose.yml (AMQP publicado en 5673).
    """
    url = os.getenv("RABBITMQ_URL", "amqp://tfinder:tfinder@localhost:5673/")
    return pika.URLParameters(url)


def publicar(routing_key: str, payload: dict, correlation_id: str = "-"):
    """Publica un mensaje en RabbitMQ con su correlation_id.

    Si el caller no provee correlation_id, se toma el del contexto del
    request actual (ContextVar de app.infra.logge), propagando el CID
    punta a punta: request -> evento -> consumer.
    """
    cuerpo = {
        "event_id": uuid.uuid4().hex,
        "correlation_id": correlation_id or correlation_id_var.get(),
        **payload,
    }
    conn = pika.BlockingConnection(get_params())
    try:
        channel = conn.channel()
        channel.basic_publish(
            exchange="",
            routing_key=routing_key,
            body=__import__("json").dumps(cuerpo, ensure_ascii=False),
            properties=pika.BasicProperties(content_type="application/json"),
        )
    finally:
        conn.close()
    return cuerpo