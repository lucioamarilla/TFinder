"""Puente REST feed-api → mesas-api (contrato B09, igual que notif-api).

Las reglas de permiso viven en mesas-api:
  - GET /api/v1/mesas/{id}          → datos de la mesa (con gm_id)
  - GET /api/v1/mesas/{id}/miembros → miembros aceptados (requiere sesión)

MESA_URL no se congela en import: los tests apuntan el ambiente al puerto del
mesas-api real cuando se levanta.
"""

import json
import os
import urllib.error
import urllib.request

_MESAS_URL = lambda: os.getenv("MESA_URL") or os.getenv("MESAS_URL", "http://localhost:8001")

_TIMEOUT = 3


def _pedir(ruta: str, token=None, metodo="GET", cuerpo=None):
    url = f"{_MESAS_URL()}{ruta}"
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    peticion = urllib.request.Request(url, data=datos, method=metodo)
    peticion.add_header("Content-Type", "application/json")
    if token:
        peticion.add_header("Authorization", token)
    with urllib.request.urlopen(peticion, timeout=_TIMEOUT) as respuesta:
        return json.loads(respuesta.read().decode())


def obtener_mesa(mesa_id: int, token=None):
    try:
        return _pedir(f"/api/v1/mesas/{mesa_id}", token=token)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise LookupError("La mesa solicitada no existe.") from None
        raise RuntimeError(f"mesas-api respondió {e.code}.") from None
    except (urllib.error.URLError, TimeoutError):
        raise RuntimeError("No se pudo contactar a mesas-api.") from None


def listar_miembros(mesa_id: int, token):
    try:
        return _pedir(f"/api/v1/mesas/{mesa_id}/miembros", token=token)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise PermissionError("Sesión inválida para verificar membresía.") from None
        raise RuntimeError(f"mesas-api respondió {e.code}.") from None
    except (urllib.error.URLError, TimeoutError):
        raise RuntimeError("No se pudo contactar a mesas-api.") from None


def es_gm_mesa(mesa_id: int, usuario: dict, token=None) -> tuple[bool, dict]:
    """admin siempre está autorizado; el resto solo si es el gm_id de la mesa."""
    mesa = obtener_mesa(mesa_id, token=token)
    gm_id = mesa.get("gm_id")
    if (usuario or {}).get("rol") == "admin":
        return True, mesa
    return gm_id == int(usuario["sub"]), mesa


def es_miembro_aceptado(mesa_id: int, usuario, token) -> bool:
    if (usuario or {}).get("rol") in ("admin", "gm"):
        return True
    respuesta = listar_miembros(mesa_id, token=token)
    sub = str(usuario["sub"])
    return any(str(m.get("id")) == sub for m in respuesta.get("miembros", []))
