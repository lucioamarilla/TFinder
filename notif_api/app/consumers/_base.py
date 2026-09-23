import json
import time

import pika

from app.infra.logge import correlation_id_var, logger
from app.infra.rabbitmq import get_params
from notif_api.app.infra.amqp import COLA_DLQ, EXCHANGE, declarar
from notif_api.app.models.notif import registro_dlq

MAX_REINTENTOS = 3


def _enviar_a(cola_routing: str, mensaje: dict, propiedades=None):
    conn = pika.BlockingConnection(get_params())
    try:
        canal = conn.channel()
        canal.queue_declare(queue=COLA_DLQ, durable=True)
        canal.basic_publish(
            exchange="",
            routing_key=cola_routing,
            body=json.dumps(mensaje, ensure_ascii=False),
            properties=propiedades or pika.BasicProperties(delivery_mode=2),
        )
    finally:
        conn.close()


def _republicar(mensaje: dict):
    """Re-encola el mismo mensaje con _intentos incrementado (persistido)."""
    conn = pika.BlockingConnection(get_params())
    try:
        canal = conn.channel()
        canal.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
        canal.basic_publish(
            exchange=EXCHANGE,
            routing_key=mensaje["tipo"],
            body=json.dumps(mensaje, ensure_ascii=False),
            properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
        )
    finally:
        conn.close()


def _enviar_dlq(mensaje: dict, ultimo_error: str, cola: str):
    _enviar_a(
        COLA_DLQ,
        {**mensaje, "ultimo_error": ultimo_error, "cola_origen": cola},
    )


def consumir(cola: str, procesar):
    """Lazo de consumo con ACK explícito, reintentos (backoff 2^n) y DLQ."""
    declarar()
    while True:
        try:
            conn = pika.BlockingConnection(get_params())
            canal = conn.channel()
            canal.basic_qos(prefetch_count=1)

            def callback(ch, method, properties, body, _cola=cola, _procesar=procesar):
                _manejar(ch, method, body, _cola, _procesar)

            canal.basic_consume(
                queue=cola,
                on_message_callback=callback,
                auto_ack=False,
            )
            canal.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            logger.warning("rabbitmq no disponible; consumidor reintenta en 3s")
            time.sleep(3)
        except Exception as exc:
            logger.error(f"consumidor {cola} reinicia tras error: {exc!r}")
            try:
                canal.stop_consuming()
            except Exception:
                pass
            time.sleep(3)


def _dlq_final(ch, method, mensaje, cid, cola, exc):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    error = f"fallo tras {MAX_REINTENTOS} reintentos: {exc}"
    _enviar_dlq(mensaje, error, cola)
    try:
        registro_dlq(cola, mensaje, str(exc))
    except Exception:
        logger.error("no se pudo persistir en mensaje_dlq (db caida?)")
    logger.error(
        "evento a dlq",
        extra={
            "correlation_id": cid,
            "event_id": mensaje.get("event_id", "-"),
            "tipo": mensaje.get("tipo", "-"),
            "error": str(exc),
        },
    )


def _manejar(ch, method, body, cola, procesar):
    mensaje = json.loads(body)
    cid = mensaje.get("correlation_id", "-")
    token = correlation_id_var.set(cid)
    try:
        if procesar(mensaje):
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(
                "evento procesado",
                extra={
                    "correlation_id": cid,
                    "event_id": mensaje.get("event_id", "-"),
                    "tipo": mensaje.get("tipo", "-"),
                },
            )
            return
        raise ValueError(f"tipo no soportado: {mensaje.get('tipo')}")
    except Exception as exc:
        intentos = int(mensaje.get("_intentos", 0)) + 1
        if intentos >= MAX_REINTENTOS:
            try:
                _dlq_final(ch, method, mensaje, cid, cola, exc)
            except Exception as exc2:
                logger.error(f"dlq final fallo: {exc2!r}")
        else:
            mensaje["_intentos"] = intentos
            logger.warning(
                f"evento fallido, reintento {intentos}: {exc}",
                extra={
                    "correlation_id": cid,
                    "event_id": mensaje.get("event_id", "-"),
                    "tipo": mensaje.get("tipo", "-"),
                    "error": str(exc),
                },
            )
            time.sleep(2 ** intentos)
            _republicar(mensaje)
            ch.basic_ack(delivery_tag=method.delivery_tag)
    finally:
        correlation_id_var.reset(token)