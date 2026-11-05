"""Puente REST feed-api → builds-api (contrato B09): validación de builds adjuntas."""

import json
import os
import urllib.error
import urllib.request

_BUILDS_URL = lambda: os.getenv("BUILDS_URL") or os.getenv("BUILDS_API_URL", "http://localhost:8002")

_TIMEOUT = 3


def obtener_build(build_id, token=None):
    url = f"{_BUILDS_URL()}/api/v1/builds/{build_id}"
    peticion = urllib.request.Request(url, method="GET")
    if token:
        peticion.add_header("Authorization", token)
    try:
        with urllib.request.urlopen(peticion, timeout=_TIMEOUT) as respuesta:
            return json.loads(respuesta.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise LookupError("El build adjunto no existe.") from None
        raise RuntimeError(f"builds-api respondió {e.code}.") from None
    except (urllib.error.URLError, TimeoutError):
        raise RuntimeError("No se pudo contactar a builds-api.") from None
