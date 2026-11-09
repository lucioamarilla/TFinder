"""Flujos de correo verificado: registro por código y recuperación de contraseña.

Objetivo de negocio (pedido del dueño): que no queden en la BD correos que no
se pueden confirmar. El registro sólo crea la fila de `usuarios` cuando el
usuario acredita leer el código enviado a su mail; la recupero sólo existe para
cuentas reales y nunca revela si el correo existe.
"""

import uuid

import pytest

from app.infra.redis import get_redis
from mesas_api.app.services import verificacion

pytestmark = pytest.mark.integration


def _pedir_registro(client, email=None, password="secreto123", nombre="Con Código", rol=None):
    email = email or f"cod_{uuid.uuid4().hex[:10]}@tfinder.dev"
    cuerpo = {"email": email, "password": password, "nombre": nombre}
    if rol:
        cuerpo["rol"] = rol
    r = client.post("/api/v1/auth/register", json=cuerpo)
    return r, email


def test_flujo_completo_registro_con_codigo(client):
    r, email = _pedir_registro(client)
    assert r.status_code == 202
    assert r.json() == {"pendiente": True, "email": email}

    from tests.mailbox import codigo_del_ultimo_mail

    codigo = codigo_del_ultimo_mail(destino=email)
    r = client.post("/api/v1/auth/register/verificar", json={"email": email, "codigo": codigo})
    assert r.status_code == 200, r.text
    tokens = r.json()
    assert tokens["perfil"]["email"] == email
    assert tokens["access_token"]

    # Sesión emitida por el verificar sirve en /me...
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert me.status_code == 200
    # ... y las credenciales quedan válidas para el login normal.
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "secreto123"})
    assert login.status_code == 200


def test_pendiente_expira_y_desaparece(client):
    """Un registro nunca confirmado no deja nada: expirar = no existe."""
    _, email = _pedir_registro(client)
    # Sin tocar Redis TTL: simulamos la expiración borrando la clave pendiente.
    get_redis().delete(verificacion.K_REGISTRO.format(email=email))
    r = client.post(
        "/api/v1/auth/register/verificar",
        json={"email": email, "codigo": "777777"},
    )
    assert r.status_code == 400
    assert "Registrate de nuevo" in r.json()["error"]["mensaje"]


def test_codigo_equivocado_banea_tras_el_maximo_de_intentos(client):
    r, email = _pedir_registro(client)
    assert r.status_code == 202

    equivocado = "000000"
    for n in range(verificacion.MAX_INTENTOS_REGISTRO - 1):
        r = client.post(
            "/api/v1/auth/register/verificar", json={"email": email, "codigo": equivocado}
        )
        assert r.status_code == 400
        assert r.json()["error"]["mensaje"] == verificacion.MSG["codigo"]

    # El último intento alcanza el tope: se banea y borra la solicitud.
    r = client.post(
        "/api/v1/auth/register/verificar", json={"email": email, "codigo": equivocado}
    )
    assert r.status_code == 400
    assert "Demasiados intentos" in r.json()["error"]["mensaje"]

    # Hasta el código correcto ya no sirve: la solicitud baneada expiró.
    from tests.mailbox import codigo_del_ultimo_mail

    r = client.post(
        "/api/v1/auth/register/verificar",
        json={"email": email, "codigo": codigo_del_ultimo_mail(destino=email)},
    )
    assert r.status_code == 400
    assert "Registrate de nuevo" in r.json()["error"]["mensaje"]


def test_reenviar_registro_genera_codigo_nuevo(client):
    _, email = _pedir_registro(client)
    from tests.mailbox import inbox as mails_capturados
    from tests.mailbox import codigo_del_ultimo_mail

    codigo1 = codigo_del_ultimo_mail()

    # El envío inicial también dejó cooldown: reenviar al instante da 409.
    r = client.post("/api/v1/auth/register/reenviar", json={"email": email})
    assert r.status_code == 409
    assert len(mails_capturados) == 1

    # Se venció el cooldown (lo simulamos limpiando la clave de Redis).
    get_redis().delete(verificacion.K_REGISTRO_COOL.format(email=email))
    r = client.post("/api/v1/auth/register/reenviar", json={"email": email})
    assert r.status_code == 202, r.text
    codigo2 = codigo_del_ultimo_mail(destino=email)
    assert codigo1 != codigo2

    # Dentro del cooldown no reenvía: mismo estado y cero mails nuevos.
    mails_antes = len(mails_capturados)
    r = client.post("/api/v1/auth/register/reenviar", json={"email": email})
    assert r.status_code == 409
    assert len(mails_capturados) == mails_antes

    # El código viejo quedó invalidado; el nuevo crea la cuenta.
    r = client.post("/api/v1/auth/register/verificar", json={"email": email, "codigo": codigo1})
    assert r.status_code == 400
    r = client.post("/api/v1/auth/register/verificar", json={"email": email, "codigo": codigo2})
    assert r.status_code == 200


def test_email_ya_registrado_rechaza_solicitud(client):
    from mesas_api.app.controllers.auth_controller import _emitir_tokens
    from mesas_api.app.models.auth_model import crear_usuario

    email = f"duplicate_{uuid.uuid4().hex[:8]}@tfinder.dev"
    crear_usuario(email, "secreto123", "Existente")
    r, _ = _pedir_registro(client, email=email)
    assert r.status_code == 400
    assert r.json()["error"]["mensaje"] == "El email ya está registrado"


def test_verificar_de_correo_mayuscula_igual_que_como_se_solicito(client):
    email_orig = f"Mayus_{uuid.uuid4().hex[:8]}@TFinder.dev"
    r, _ = _pedir_registro(client, email=email_orig)
    assert r.status_code == 202
    email = email_orig.lower()
    assert r.json()["email"] == email  # devuelto normalizado
    from tests.mailbox import codigo_del_ultimo_mail

    r = client.post(
        "/api/v1/auth/register/verificar",
        json={"email": email.upper(), "codigo": codigo_del_ultimo_mail(destino=email)},
    )
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# Recupero
# ---------------------------------------------------------------------------


def test_recupero_email_inexistente_generico_y_sin_mail(client):
    r = client.post("/api/v1/auth/recuperar", json={"email": "fantasma@tfinder.dev"})
    assert r.status_code == 202
    from tests.mailbox import inbox as mails_capturados

    assert r.json() == {"mensaje": verificacion.MENSAJE_RECUPERO}
    assert len(mails_capturados) == 0


def test_recupero_respuesta_identicas_no_revelan_existencia(client):
    from mesas_api.app.models.auth_model import crear_usuario

    email = f"recup_{uuid.uuid4().hex[:8]}@tfinder.dev"
    crear_usuario(email, "secreto123", "Real")
    real = client.post("/api/v1/auth/recuperar", json={"email": email}).json()
    fantasma = client.post("/api/v1/auth/recuperar", json={"email": "nada@tfinder.dev"}).json()
    assert real == fantasma == {"mensaje": verificacion.MENSAJE_RECUPERO}


def test_recupero_cambia_contraseña_y_revoca_sesiones(client):
    from tests.conftest import codigo_del_ultimo_mail
    from mesas_api.app.models.auth_model import crear_usuario

    email = f"recup_{uuid.uuid4().hex[:10]}@tfinder.dev"
    crear_usuario(email, "secreto123", "Recupero Real")

    # El usuario entra (sesión A) y después pide recupero.
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "secreto123"})
    assert login.status_code == 200
    access_previo = login.json()["access_token"]
    assert client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {access_previo}"}
    ).status_code == 200

    assert client.post("/api/v1/auth/recuperar", json={"email": email}).status_code == 202
    codigo = codigo_del_ultimo_mail(destino=email)

    r = client.post(
        "/api/v1/auth/recuperar/verificar",
        json={"email": email, "codigo": codigo, "nueva_password": "nuevaclave99"},
    )
    assert r.status_code == 200, r.text

    # La sesión previa quedó muerta y la clave vieja ya no entra.
    assert (
        client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_previo}"}).status_code
        == 401
    )
    assert (
        client.post("/api/v1/auth/login", json={"email": email, "password": "secreto123"}).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/auth/login", json={"email": email, "password": "nuevaclave99"}
        ).status_code
        == 200
    )

    # El código quedó quemado: reusarlo no cambia nada.
    r = client.post(
        "/api/v1/auth/recuperar/verificar",
        json={"email": email, "codigo": codigo, "nueva_password": "otraclave100"},
    )
    assert r.status_code == 400


def test_recupero_maximo_de_intentos_banea(client):
    from tests.conftest import codigo_del_ultimo_mail
    from mesas_api.app.models.auth_model import crear_usuario

    email = f"banco_{uuid.uuid4().hex[:8]}@tfinder.dev"
    crear_usuario(email, "secreto123", "Baneada")
    client.post("/api/v1/auth/recuperar", json={"email": email})
    codigo = codigo_del_ultimo_mail(destino=email)

    for _ in range(verificacion.MAX_INTENTOS_RECUPERO - 1):
        r = client.post(
            "/api/v1/auth/recuperar/verificar",
            json={"email": email, "codigo": "000000", "nueva_password": "nuevaclave99"},
        )
        assert r.status_code == 400
        assert r.json()["error"]["mensaje"] == verificacion.MSG["codigo"]

    # Tercer intento malo: banea y borra la solicitud.
    r = client.post(
        "/api/v1/auth/recuperar/verificar",
        json={"email": email, "codigo": "000000", "nueva_password": "nuevaclave99"},
    )
    assert r.status_code == 400
    assert "Demasiados intentos" in r.json()["error"]["mensaje"]

    # Aun con el código correcto, la solicitud baneada ya no existe.
    r = client.post(
        "/api/v1/auth/recuperar/verificar",
        json={"email": email, "codigo": codigo, "nueva_password": "nuevaclave99"},
    )
    assert r.status_code == 400
    assert "no es válido o venció" in r.json()["error"]["mensaje"]

    # La clave original sigue vigente: nada cambió.
    assert (
        client.post("/api/v1/auth/login", json={"email": email, "password": "secreto123"}).status_code
        == 200
    )


# ---------------------------------------------------------------------------
# Unit: config del mailer (sin SMTP real en la suite)
# ---------------------------------------------------------------------------


def test_mailer_config_incompleta_falla_con_mensaje_accionable(monkeypatch):
    from app.infra import mailer
    from app.infra.mailer import MailNoConfigurado

    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("MAIL_FROM", raising=False)
    with pytest.raises(MailNoConfigurado) as exc_info:
        mailer._config()
    mensaje = str(exc_info.value)
    assert "SMTP_HOST" in mensaje
    assert ".env" in mensaje


def test_mailer_sin_configurar_lista_faltantes(monkeypatch):
    from app.infra import mailer

    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("MAIL_FROM", raising=False)
    faltan = mailer.sin_configurar()
    assert set(faltan) == {"SMTP_HOST", "MAIL_FROM"}


def test_plantilla_de_codigo_menciona_el_codigo_y_vencimiento():
    from app.infra.mailer import _plantilla_codigo

    asunto, texto, html = _plantilla_codigo("Verificá tu correo", "123456", 15)
    assert "123456" in asunto and "123456" in texto and "123456" in html
    assert "15 minutos" in texto and "15 minutos" in html
    assert "TFinder" in texto
