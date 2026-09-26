"""Contrato del campo `enlace` entre notif-api y el frontend.

Regresion: los consumidores de notif-api emitian `enlace` como mapa
{"/mesas/9": "ver mesa"} (URL como clave), mientras que NotificacionesView.vue
consume `notificacion.enlace.label` para el texto del boton y
`notificacion.enlace.to` para navegar. Con la forma vieja el boton se
renderizaba sin texto y router.push(undefined) no llevaba a ningun lado.
"""

import json

import pytest

from notif_api.app.consumers import mesa as consumer_mesa
from notif_api.app.consumers import sesion as consumer_sesion

pytestmark = pytest.mark.unit

MENSAJE_MESA = {
    "event_id": "ev-enlace-1",
    "tipo": "mesa.aceptada",
    "correlation_id": "cid-enlace-1",
    "mesa_id": 9,
    "usuario_id": 3,
}
MENSAJE_SESION = {
    "event_id": "ev-enlace-2",
    "tipo": "sesion.confirmada",
    "correlation_id": "cid-enlace-2",
    "mesa_id": 9,
    "usuario_id": 3,
}


def _correr(monkeypatch, modulo, mensaje):
    """Ejecuta el consumidor aislado de DB, RabbitMQ, SSE y HTTP.

    Devuelve (enlace_guardado, payload_sse).

    Se llama a `_procesar` directo y no a `_base._manejar` a proposito: la
    rama de fallo de `_manejar` publica en la cola real `dlq.general` via
    `_dlq_final`, y un test unitario no debe escribir en el broker de dev.
    """
    guardados = []
    por_sse = []

    monkeypatch.setattr(modulo, "evento_ya_procesado", lambda event_id: False)
    monkeypatch.setattr(
        modulo,
        "guardar_notificacion",
        lambda **kw: (guardados.append(kw), 42)[1],
    )
    monkeypatch.setattr(modulo, "registrar_evento", lambda *a, **k: None)
    monkeypatch.setattr(modulo.hub, "publicar", lambda usuario, payload: por_sse.append(payload))
    if hasattr(modulo, "enviar_email"):
        monkeypatch.setattr(modulo, "enviar_email", lambda *a, **k: None)
    if hasattr(modulo, "obtener_emails_mesa"):
        # sin esto el consumidor consulta mesas-api por HTTP y revienta
        monkeypatch.setattr(modulo, "obtener_emails_mesa", lambda mesa_id: [])

    assert modulo._procesar(mensaje) is True, "el consumidor no proceso el mensaje"
    return guardados, por_sse


@pytest.mark.parametrize(
    "modulo,mensaje",
    [
        (consumer_mesa, MENSAJE_MESA),
        (consumer_sesion, MENSAJE_SESION),
    ],
)
def test_notificacion_guardada_usa_label_y_to(modulo, mensaje, monkeypatch):
    guardados, _ = _correr(monkeypatch, modulo, mensaje)
    assert guardados, "el consumidor no guardo ninguna notificacion"
    enlace = guardados[0]["enlace"]
    assert set(enlace) == {"label", "to"}, f"el frontend espera label/to, vino {enlace}"
    assert enlace["to"] == "/mesas/9"
    assert isinstance(enlace["label"], str) and enlace["label"]


@pytest.mark.parametrize(
    "modulo,mensaje",
    [
        (consumer_mesa, MENSAJE_MESA),
        (consumer_sesion, MENSAJE_SESION),
    ],
)
def test_payload_sse_usa_el_mismo_contrato(modulo, mensaje, monkeypatch):
    _, por_sse = _correr(monkeypatch, modulo, mensaje)
    assert por_sse, "el consumidor no publico nada por SSE"
    enlace = por_sse[0]["enlace"]
    assert set(enlace) == {"label", "to"}
    assert enlace["to"] == "/mesas/9"
