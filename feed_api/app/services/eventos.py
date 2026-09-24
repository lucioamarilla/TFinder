import uuid

from app.infra.rabbitmq import publicar
from feed_api.app.controllers.wiki import obtener_wiki


def _armar_datos_diario(mesa_id: str) -> dict:
    """Arma titulo/cuerpo del diario desde las paginas wiki de la mesa."""
    wiki = obtener_wiki(mesa_id)
    paginas = wiki.get("paginas", [])
    titulo = f"Diario de la mesa {mesa_id}"
    bloques = []

    def _texto(contenido):
        if isinstance(contenido, str):
            return contenido
        if isinstance(contenido, list):
            return "\n".join(
                item.get("texto", "") if isinstance(item, dict) else str(item)
                for item in contenido
            )
        return ""

    for pagina in paginas:
        texto = _texto(pagina.contenido)
        if texto:
            bloques.append(f"# {pagina.titulo}\n{texto}")
    return {"titulo": titulo, "cuerpo": "\n\n".join(bloques) or "Sin contenido por el momento."}


def publicar_diario_pdf(mesa_id, sesion_id: int, correlation_id: str = "-") -> str:
    """Publica doc.pdf.diario en tfinder.events y devuelve el documento_id.

    El doc_id lo genera el emisor: el 202 sincronico responde con el mismo id
    que luego servira para GET /pdf/{documento_id}.
    """
    doc_id = uuid.uuid4().hex
    publicar(
        "doc.pdf.diario",
        {
            "doc_id": doc_id,
            "id_origen": int(sesion_id),
            "datos": _armar_datos_diario(str(mesa_id)),
        },
        correlation_id=correlation_id,
    )
    return doc_id