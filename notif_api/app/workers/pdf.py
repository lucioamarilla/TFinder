from notif_api.app.consumers._base import consumir
from notif_api.app.infra.amqp import COLA_PDF
from notif_api.app.models.notif import (
    actualizar_documento,
    crear_documento,
    evento_ya_procesado,
    registrar_evento,
)
from notif_api.app.services.pdf_service import generar_pdf_build, generar_pdf_diario

TIPOS = ("doc.pdf.build", "doc.pdf.diario")


def _procesar(mensaje: dict) -> bool:
    if evento_ya_procesado(mensaje["event_id"]):
        return True
    tipo = mensaje.get("tipo")
    doc_id = mensaje.get("doc_id")
    id_origen = mensaje.get("id_origen")
    if tipo not in TIPOS or not doc_id or id_origen is None:
        return False
    crear_documento(doc_id, tipo.rsplit(".", 1)[1], id_origen)
    datos = mensaje.get("datos") or {}
    if tipo == "doc.pdf.build":
        ruta = generar_pdf_build(id_origen, datos)
    else:
        ruta = generar_pdf_diario(id_origen, datos)
    actualizar_documento(doc_id, ruta)
    registrar_evento(
        mensaje["event_id"], tipo, {"doc_id": doc_id, "id_origen": id_origen},
        correlation_id=mensaje.get("correlation_id", "-"),
    )
    return True


def run():
    consumir(COLA_PDF, _procesar)