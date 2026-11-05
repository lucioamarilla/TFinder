import json
import time

import pika

from app.infra.logge import logger
from app.infra.rabbitmq import EXCHANGE, get_params
from feed_api.app.db import get_connection


COLA = "mesa.eliminada.feed"
ROUTING = "mesa.eliminada"


def _procesar(mensaje: dict) -> bool:
    if mensaje.get("tipo") != "mesa.eliminada":
        return False
    mesa_id = mensaje.get("mesa_id")
    if mesa_id is None:
        return False
    try:
        with get_connection() as conn:
            conn.execute(
                "UPDATE publicaciones SET oculto = TRUE "
                "WHERE embed->>'mesa_id' = %s",
                (str(mesa_id),),
            )
    except Exception as exc:
        logger.error(f"b6: error ocultando posts de mesa {mesa_id}: {exc!r}")
        return False
    return True


def run():
    while True:
        try:
            conn = pika.BlockingConnection(get_params())
            canal = conn.channel()
            canal.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
            canal.queue_declare(queue=COLA, durable=True)
            canal.queue_bind(queue=COLA, exchange=EXCHANGE, routing_key=ROUTING)
            canal.basic_qos(prefetch_count=1)

            def callback(ch, method, properties, body):
                try:
                    mensaje = json.loads(body)
                except Exception:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return
                if _procesar(mensaje):
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            canal.basic_consume(queue=COLA, on_message_callback=callback, auto_ack=False)
            canal.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            logger.warning("rabbitmq no disponible; consumer feed reintenta en 3s")
            time.sleep(3)
        except Exception as exc:
            logger.error(f"consumer feed reinicia tras error: {exc!r}")
            time.sleep(3)
