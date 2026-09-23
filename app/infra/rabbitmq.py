import os

import pika


def get_params() -> pika.ConnectionParameters:
    """Devuelve los parametros de conexion a RabbitMQ desde RABBITMQ_URL.

    Default local alineado con docker-compose.yml (AMQP publicado en 5673).
    """
    url = os.getenv("RABBITMQ_URL", "amqp://tfinder:tfinder@localhost:5673/")
    return pika.URLParameters(url)