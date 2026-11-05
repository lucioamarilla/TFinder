import json
import time

import pika

from app.infra.logge import logger
from app.infra.rabbitmq import EXCHANGE, get_params
from builds_api.app.controllers.builds import desvincular_builds_de_mesa


COLA = "mesa.eliminada.builds"
ROUTING = "mesa.eliminada"


def _procesar(mensaje: dict) -> bool:
    if mensaje.get("tipo") != "mesa.eliminada":
        return False
    mesa_id = mensaje.get("mesa_id")
    if mesa_id is None:
        return False
    try:
        desvincular_builds_de_mesa(int(mesa_id))
    except Exception as exc:
        logger.error(f"b6: error desvinculando builds de mesa {mesa_id}: {exc!r}")
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
            logger.warning("rabbitmq no disponible; consumer builds reintenta en 3s")
            time.sleep(3)
        except Exception as exc:
            logger.error(f"consumer builds reinicia tras error: {exc!r}")
            time.sleep(3)
