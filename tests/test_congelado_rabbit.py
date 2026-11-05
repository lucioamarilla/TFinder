"""CONGELADO: infra de eventos RabbitMQ (constantes y forma de los mensajes).

Aferra nombres de exchange/colas, la constante de reintentos del engine y el
cuerpo exacto que produce publicar(): si el refactor cambia alguno, hay que
decidirlo de forma explícita.
"""

import json

import pika
import pytest

from app.infra.rabbitmq import EXCHANGE as RABBIT_EXCHANGE
from app.infra.rabbitmq import get_params, publicar
from notif_api.app.consumers._base import MAX_REINTENTOS
from notif_api.app.infra.amqp import (
    COLA_DLQ,
    COLA_MESA,
    COLA_PDF,
    COLA_SESION,
    DLX,
    EXCHANGE,
)


@pytest.fixture()
def canal_pika():
    conn = pika.BlockingConnection(get_params())
    canal = conn.channel()
    yield canal
    conn.close()


def test_nombres_de_exchanges_y_colas_congelados():
    assert RABBIT_EXCHANGE == "tfinder.events"
    assert EXCHANGE == RABBIT_EXCHANGE
    assert DLX == "tfinder.dlx"
    assert COLA_MESA == "notif.mesa"
    assert COLA_SESION == "notif.sesion"
    assert COLA_PDF == "doc.pdf"
    assert COLA_DLQ == "dlq.general"


def test_reintentos_congelados():
    assert MAX_REINTENTOS == 3
    # El backoff es 2^n: reintento 1 duerme 2s, el 2 duerme 4s (ver _manejar).


def test_publicar_construye_el_cuerpo_exacto(canal_pika):
    # La cola probe se declara y bindea ANTES de publicar (un topic exchange
    # descarta lo publicado sin binding).
    canal_pika.exchange_declare(
        exchange="tfinder.events", exchange_type="topic", durable=True
    )
    canal_pika.queue_declare(queue="congelado.probe", durable=True)
    canal_pika.queue_bind(
        queue="congelado.probe", exchange="tfinder.events", routing_key="prueba.congelada"
    )

    cuerpo = publicar("prueba.congelada", {"x": 1}, correlation_id="cid-xyz")
    assert set(cuerpo) >= {"event_id", "tipo", "correlation_id", "x"}
    assert cuerpo["tipo"] == "prueba.congelada"
    assert cuerpo["correlation_id"] == "cid-xyz"

    frame = canal_pika.basic_get(queue="congelado.probe", auto_ack=True)
    assert frame[0] is not None

    mensaje = json.loads(frame[2])
    assert set(mensaje) >= {"event_id", "tipo", "correlation_id", "x"}
    assert mensaje["tipo"] == "prueba.congelada"
    assert mensaje["correlation_id"] == "cid-xyz"
    assert mensaje["x"] == 1

    canal_pika.queue_delete(queue="congelado.probe")
