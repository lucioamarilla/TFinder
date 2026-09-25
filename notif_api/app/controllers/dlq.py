import json

import pika

from app.infra.rabbitmq import get_params
from notif_api.app.infra.amqp import EXCHANGE
from notif_api.app.models.notif import descartar_dlq, reintentar_dlq


def reintentar_mensaje(id: int):
    fila = reintentar_dlq(id)
    if fila is None:
        return None
    payload = fila["payload"]
    if isinstance(payload, str):
        payload = json.loads(payload)
    conn = pika.BlockingConnection(get_params())
    try:
        canal = conn.channel()
        canal.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
        canal.basic_publish(
            exchange=EXCHANGE,
            routing_key=payload.get("tipo"),
            body=json.dumps(payload, ensure_ascii=False),
            properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
        )
    finally:
        conn.close()
    return fila


def descartar_mensaje(id: int):
    return descartar_dlq(id)