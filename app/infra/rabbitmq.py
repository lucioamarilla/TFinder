import json
import os
import uuid

import pika

from app.infra.logge import correlation_id_var

EXCHANGE = "tfinder.events"


def get_params() -> pika.ConnectionParameters:
    """Devuelve los parametros de conexion a RabbitMQ desde RABBITMQ_URL.

    Default local alineado con docker-compose.yml (AMQP publicado en 5673).
    """
    url = os.getenv("RABBITMQ_URL", "amqp://tfinder:tfinder@localhost:5673/")
    return pika.URLParameters(url)


def publicar(routing_key: str, payload: dict, correlation_id: str = "-"):
    """Publica un evento de dominio en el exchange topic durable tfinder.events.

    - Mensajes persistentes (delivery_mode=2).
    - event_id: idempotencia del consumidor (B05/B06).
    - correlation_id: tomado del contexto del request (B10) o provisto.
    """
    cuerpo = {
        "event_id": uuid.uuid4().hex,
        "tipo": routing_key,
        "correlation_id": correlation_id or correlation_id_var.get(),
        **payload,
    }
    conn = pika.BlockingConnection(get_params())
    try:
        channel = conn.channel()
        channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
        channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=routing_key,
            body=json.dumps(cuerpo, ensure_ascii=False),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,
            ),
        )
    finally:
        conn.close()
    return cuerpo