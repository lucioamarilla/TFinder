import json
import logging
import os
import time
import uuid
from contextvars import ContextVar

correlation_id_var = ContextVar("correlation_id", default="-")


def nuevo_correlation_id() -> str:
    return uuid.uuid4().hex[:16]


class JsonFormatter(logging.Formatter):
    def __init__(self, servicio=None):
        super().__init__()
        self._servicio = servicio or os.getenv("SERVICIO", "tfinder")

    def format(self, record: logging.LogRecord) -> str:
        cuerpo = {
            "ts": int(time.time() * 1000),
            "nivel": record.levelname,
            "servicio": self._servicio,
            "mensaje": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", None)
            or correlation_id_var.get(),
        }
        if record.exc_info:
            cuerpo["exc"] = self.formatException(record.exc_info)
        return json.dumps(cuerpo, ensure_ascii=False)


def configurar_logger(nombre="tfinder"):
    logger = logging.getLogger(nombre)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


logger = configurar_logger()