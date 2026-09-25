import uuid

from app.infra.rabbitmq import publicar
from builds_api.app.controllers.builds import obtener_build


def publicar_doc_pdf(build_id: int, correlation_id: str = "-") -> str:
    """Publica doc.pdf.build en el exchange tfinder.events y devuelve el doc_id.

    El doc_id lo genera el emisor: el 202 sincronico responde con el mismo id
    que luego servira para GET /pdf/{documento_id}.
    """
    build = obtener_build(build_id)
    doc_id = uuid.uuid4().hex
    datos = {
        "id": build.id,
        "persona": build.persona,
        "clase": build.clase,
        "nivel": build.nivel,
        "handle": build.handle,
    }
    publicar(
        "doc.pdf.build",
        {"doc_id": doc_id, "id_origen": int(build_id), "datos": datos},
        correlation_id=correlation_id,
    )
    return doc_id