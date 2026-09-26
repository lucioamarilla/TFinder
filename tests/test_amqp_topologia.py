"""Topologia AMQP: el DLX debe tener destino.

Las colas de consumo declaran `x-dead-letter-exchange: tfinder.dlx`. Si
`dlq.general` no esta vinculada a ese exchange, cualquier rechazo con
`requeue=False` enruta el mensaje a un exchange sin bindings y RabbitMQ lo
descarta en silencio: el evento se pierde sin rastro.

La introspeccion usa la management API de RabbitMQ porque el cliente AMQP
(pika) no expone los bindings declarados.
"""

import base64
import json
import time
import urllib.error
import urllib.request

import pika
import pytest

from app.infra.rabbitmq import get_params
from notif_api.app.infra.amqp import (
    COLA_DLQ,
    COLA_MESA,
    COLA_PDF,
    COLA_SESION,
    DLX,
    EXCHANGE,
    declarar,
)

pytestmark = pytest.mark.integration

MGMT = "http://localhost:15673/api"
CRED = base64.b64encode(b"tfinder:tfinder").decode()


def _mgmt(ruta):
    req = urllib.request.Request(f"{MGMT}{ruta}")
    req.add_header("Authorization", f"Basic {CRED}")
    with urllib.request.urlopen(req, timeout=5) as respuesta:
        return json.loads(respuesta.read())


def _bindings_entre(exchange, cola):
    """Routing keys con los que `exchange` enruta a `cola`."""
    return {
        binding["routing_key"]
        for binding in _mgmt(f"/bindings/%2F/e/{exchange}/q/{cola}")
    }


def test_declarar_vincula_la_dlq_al_dlx():
    """Contrato de declarar(): dlq.general debe quedar alcanzable desde el DLX."""
    declarar()
    assert "#" in _bindings_entre(DLX, COLA_DLQ), (
        "declarar() no vincula dlq.general al DLX: un nack(requeue=False) "
        "descartaria el mensaje en silencio"
    )


def test_un_evento_muerto_llega_a_la_dlq():
    """Prueba de ida y vuelta: publicar al DLX debe encolar en dlq.general."""
    declarar()
    conn = pika.BlockingConnection(get_params())
    try:
        canal = conn.channel()
        canal.queue_purge(queue=COLA_DLQ)
        marca = f"probe-dlx-{time.time()}"
        canal.basic_publish(exchange=DLX, routing_key="mesa.probe", body=marca.encode())
        time.sleep(0.5)
        frame = canal.basic_get(queue=COLA_DLQ, auto_ack=True)
        assert frame is not None and frame[2] is not None, "el DLX no enruta a dlq.general"
        assert frame[2].decode() == marca
    finally:
        conn.close()


def test_las_tres_colas_de_consumo_declaran_dlx():
    declarar()
    for cola in (COLA_MESA, COLA_SESION, COLA_PDF):
        argumentos = _mgmt(f"/queues/%2F/{cola}").get("arguments") or {}
        assert argumentos.get("x-dead-letter-exchange") == DLX, (
            f"{cola} no declara x-dead-letter-exchange"
        )


def test_las_tres_colas_siguen_bound_al_exchange_de_eventos():
    """El fix del DLX no debe romper el ruteo normal de eventos."""
    declarar()
    esperado = {COLA_MESA: "mesa.*", COLA_SESION: "sesion.*", COLA_PDF: "doc.pdf.*"}
    for cola, routing in esperado.items():
        assert routing in _bindings_entre(EXCHANGE, cola), (
            f"{cola} perdio el binding {routing} desde {EXCHANGE}"
        )


def test_el_dlx_ya_no_esta_uerto():
    """El fallo original: el exchange existia sin ningun binding."""
    declarar()
    destinos = [b for b in _mgmt("/bindings/%2F") if b.get("source") == DLX]
    assert destinos, "tfinder.dlx sigue sin bindings: es un exchange muerto"
    assert any(b.get("destination") == COLA_DLQ for b in destinos)
