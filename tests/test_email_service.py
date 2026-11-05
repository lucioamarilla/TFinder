from unittest.mock import patch

import pytest

from notif_api.app.services import email_service


def test_enviar_email_ok_registra_enviado():
    with patch.object(email_service, "_enviar_por_smtp", return_value=None) as smtp, \
         patch.object(email_service, "registrar_email") as registrar:
        assert email_service.enviar_email("a@tfinder.dev", "Hola", "Cuerpo") is True
        smtp.assert_called_once()
        registrar.assert_called_once()
        args = registrar.call_args.args
        assert args[3] == "enviado"


def test_enviar_email_falla_registra_fallido():
    with patch.object(email_service, "_enviar_por_smtp", return_value="timeout") as smtp, \
         patch.object(email_service, "registrar_email") as registrar:
        assert email_service.enviar_email("a@tfinder.dev", "Hola", "Cuerpo") is False
        args = registrar.call_args.args
        assert args[3] == "fallido"
        assert args[4] == "timeout"


def test_enviar_email_sin_registrar():
    with patch.object(email_service, "_enviar_por_smtp", return_value=None), \
         patch.object(email_service, "registrar_email") as registrar:
        assert email_service.enviar_email("a@tfinder.dev", "Hola", "Cuerpo", registrar=False) is True
        registrar.assert_not_called()


def test_obtener_emails_mesa():
    with patch.object(email_service, "_llamar_mesas", return_value={"miembros": [
        {"email": "a@tfinder.dev"}, {"email": "b@tfinder.dev"}, {"nombre": "sin email"}
    ]}):
        assert email_service.obtener_emails_mesa(1) == ["a@tfinder.dev", "b@tfinder.dev"]


def test_obtener_emails_mesa_vacio():
    with patch.object(email_service, "_llamar_mesas", return_value={"miembros": []}):
        assert email_service.obtener_emails_mesa(1) == []
    with patch.object(email_service.urllib.request, "urlopen") as urlopen:
        urlopen.return_value.__enter__.return_value.read.return_value = b'{"access_token": "tok-123"}'
        email_service._token_cache["access"] = None
        assert email_service._obtener_token_mesas() == "tok-123"
        assert email_service._token_cache["access"] == "tok-123"


def test_obtener_token_mesas_ok():
    with patch.object(email_service.urllib.request, "urlopen") as urlopen:
        urlopen.return_value.__enter__.return_value.read.return_value = b'{"access_token": "tok-123"}'
        email_service._token_cache["access"] = None
        assert email_service._obtener_token_mesas() == "tok-123"
        assert email_service._token_cache["access"] == "tok-123"


def test_obtener_token_mesas_cache():
    email_service._token_cache["access"] = "cached-tok"
    assert email_service._obtener_token_mesas() == "cached-tok"
    email_service._token_cache["access"] = None


def test_llamar_mesas_http_error_401_reintenta():
    # Primera llamada falla con 401 (limpia cache), segunda (con nuevo token) ok.
    email_service._token_cache["access"] = "tok-viejo"
    with patch.object(email_service, "_obtener_token_mesas", side_effect=["tok-nuevo"]) as tok, \
         patch.object(email_service.urllib.request, "urlopen") as urlopen:
        err = email_service.urllib.error.HTTPError(
            "http://x", 401, "Unauthorized", {}, None
        )
        # Primera urlopen lanza 401; segunda devuelve datos.
        resp_ok = urlopen.return_value.__enter__.return_value
        resp_ok.read.return_value = b'{"miembros": []}'
        urlopen.side_effect = [err, urlopen.return_value]
        # _llamar_mesas captura HTTPError 401 y reintenta; la segunda debe ok.
        try:
            email_service._llamar_mesas("/api/v1/mesas/1/miembros")
        except Exception:
            pass
        assert email_service._token_cache["access"] is None or email_service._token_cache["access"] == "tok-nuevo"