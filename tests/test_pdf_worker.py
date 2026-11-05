from unittest.mock import patch

import pytest

from notif_api.app.workers import pdf as pdf_worker


def _mensaje(tipo="doc.pdf.build", doc_id="abc123", id_origen=1, event_id="ev-1"):
    return {
        "event_id": event_id,
        "tipo": tipo,
        "doc_id": doc_id,
        "id_origen": id_origen,
        "datos": {"titulo": "T", "cuerpo": "C"},
        "correlation_id": "-",
    }


def test_procesar_tipo_invalido_devuelve_false():
    msg = _mensaje(tipo="doc.pdf.otro")
    assert pdf_worker._procesar(msg) is False


def test_procesar_sin_doc_id_devuelve_false():
    msg = _mensaje(doc_id=None)
    assert pdf_worker._procesar(msg) is False


def test_procesar_sin_id_origen_devuelve_false():
    msg = _mensaje(id_origen=None)
    assert pdf_worker._procesar(msg) is False


def test_procesar_evento_ya_procesado_devuelve_true():
    with patch("notif_api.app.workers.pdf.evento_ya_procesado", return_value=True):
        assert pdf_worker._procesar(_mensaje()) is True


def test_procesar_build_ok():
    with patch("notif_api.app.workers.pdf.evento_ya_procesado", return_value=False), \
         patch("notif_api.app.workers.pdf.crear_documento") as crear, \
         patch("notif_api.app.workers.pdf.generar_pdf_build", return_value="/tmp/x.pdf") as gen, \
         patch("notif_api.app.workers.pdf.actualizar_documento") as upd, \
         patch("notif_api.app.workers.pdf.registrar_evento") as reg:
        assert pdf_worker._procesar(_mensaje()) is True
        crear.assert_called_once()
        gen.assert_called_once()
        upd.assert_called_once()
        reg.assert_called_once()


def test_procesar_diario_ok():
    with patch("notif_api.app.workers.pdf.evento_ya_procesado", return_value=False), \
         patch("notif_api.app.workers.pdf.crear_documento"), \
         patch("notif_api.app.workers.pdf.generar_pdf_diario", return_value="/tmp/d.pdf") as gen, \
         patch("notif_api.app.workers.pdf.actualizar_documento"), \
         patch("notif_api.app.workers.pdf.registrar_evento"):
        msg = _mensaje(tipo="doc.pdf.diario")
        assert pdf_worker._procesar(msg) is True
        gen.assert_called_once()


def test_procesar_error_marca_documento_y_relanza():
    with patch("notif_api.app.workers.pdf.evento_ya_procesado", return_value=False), \
         patch("notif_api.app.workers.pdf.crear_documento"), \
         patch("notif_api.app.workers.pdf.generar_pdf_build", side_effect=RuntimeError("boom")) as gen, \
         patch("notif_api.app.workers.pdf.marcar_documento_error") as marca, \
         patch("notif_api.app.workers.pdf.actualizar_documento"), \
         patch("notif_api.app.workers.pdf.registrar_evento"):
        with pytest.raises(RuntimeError):
            pdf_worker._procesar(_mensaje())
        marca.assert_called_once()