"""DLQ (B05): un mensaje cuyo procesamiento falla termina en dlq.general."""

import pytest

import json
import types
from unittest.mock import patch

import pika

from app.infra.rabbitmq import get_params
from notif_api.app.consumers import _base
from notif_api.app.infra.amqp import COLA_DLQ

pytestmark = pytest.mark.integration


class CanalFake:
    def __init__(self):
        self.acks = []

    def basic_ack(self, delivery_tag=None):
        self.acks.append(delivery_tag)


# Tope de iteraciones del drain. Sin este techo el helper se cuelga en un
# bucle infinito: ante un mensaje ajeno al event_id buscado, el nack con
# requeue=True lo devuelve a la MISMA cola y el basic_get siguiente devuelve
# el mismo mensaje otra vez. El techo convierte un cuelgue indefinite en un
# fallo de test con un mensaje util.
MAX_DRAIN = 200


def _mensaje_dlgs_por_event(event_id):
    """Drena dlq.general y devuelve los mensajes del event_id indicado.

    Drenar en vez de requeuear es intencional: la cola es compartida con el
    notif-api real, y dejar mensajes requeueados hace que este test dependa
    del estado previo de la cola. El fixture dlq_general_vacia purga antes y
    despues, asi que drenar no pierde evidencia de otros tests.
    """
    conn = pika.BlockingConnection(get_params())
    try:
        ch = conn.channel()
        ch.queue_declare(queue=COLA_DLQ, durable=True)
        encontrados = []
        for _ in range(MAX_DRAIN):
            frame = ch.basic_get(queue=COLA_DLQ, auto_ack=False)
            if frame is None or frame[2] is None:
                break
            method, props, body = frame
            try:
                datos = json.loads(body)
            except ValueError:
                ch.basic_ack(method.delivery_tag)
                continue
            if datos.get("event_id") == event_id:
                encontrados.append(datos)
            ch.basic_ack(method.delivery_tag)
        return encontrados
    finally:
        conn.close()


def test_fallo_repetido_termina_en_dlq(dlq_general_vacia):
    event_id = "t11-dlq-" + "x" * 16
    canal = CanalFake()
    method = types.SimpleNamespace(delivery_tag=1)

    def procesar_siempre_falla(mensaje):
        raise RuntimeError("fallo simulado en el consumidor")

    def cuerpo(intentos):
        return json.dumps(
            {
                "event_id": event_id,
                "tipo": "test.poison",
                "correlation_id": "-",
                "datos": {"clave": "maligno"},
                "_intentos": intentos,
            }
        ).encode()

    with patch.object(_base.time, "sleep", lambda s: None):
        for intentos in (0, 1, 2):
            _base._manejar(canal, method, cuerpo(intentos), "notif.mesa",
                           procesar_siempre_falla)

    mensajes = _mensaje_dlgs_por_event(event_id)
    assert len(mensajes) == 1
    assert mensajes[0]["ultimo_error"].startswith("fallo tras 3 reintentos")
    assert mensajes[0]["cola_origen"] == "notif.mesa"
    assert mensajes[0]["_intentos"] == 2
    assert canal.acks == [1, 1, 1]