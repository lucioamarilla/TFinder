from unittest.mock import patch

import pytest

from notif_api.app.services import email_service, pdf_service

pytestmark = pytest.mark.unit


def test_email_registra_envio_exitoso():
    with patch.object(email_service, "_enviar_por_smtp", return_value=None), \
         patch.object(email_service, "registrar_email") as registrar:
        assert email_service.enviar_email("user@tfinder.dev", "Hola", "Cuerpo") is True
    registrar.assert_called_once()
    assert registrar.call_args.args[3] == "enviado"


def test_email_registra_fallo_sin_levantar_error():
    with patch.object(email_service, "_enviar_por_smtp", return_value="timeout"), \
         patch.object(email_service, "registrar_email") as registrar:
        assert email_service.enviar_email("user@tfinder.dev", "Hola", "Cuerpo") is False
    assert registrar.call_args.args[3] == "fallido"
    assert registrar.call_args.args[4] == "timeout"


def test_obtener_emails_filtra_miembros_sin_email():
    with patch.object(email_service, "_llamar_mesas", return_value={"miembros": [
        {"email": "a@tfinder.dev"}, {"nombre": "sin email"}
    ]}):
        assert email_service.obtener_emails_mesa(1) == ["a@tfinder.dev"]


def test_pdf_build_y_diario_generan_archivos(tmp_path, monkeypatch):
    monkeypatch.setattr(pdf_service, "CARPETA", str(tmp_path))
    build = pdf_service.generar_pdf_build(7, {"id": 7, "persona": "A", "clase": "Guerrero", "nivel": 3})
    diario = pdf_service.generar_pdf_diario(9, {"titulo": "Sesión", "cuerpo": "Notas"})
    assert build.endswith("build_7.pdf")
    assert diario.endswith("diario_9.pdf")
    assert (tmp_path / "build_7.pdf").read_bytes().startswith(b"%PDF")
    assert (tmp_path / "diario_9.pdf").read_bytes().startswith(b"%PDF")
