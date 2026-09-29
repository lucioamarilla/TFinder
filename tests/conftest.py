import os

os.environ.setdefault(
    "MESAS_DATABASE_URL",
    "postgresql://tfinder:tfinder@localhost:5432/mesas_db_test",
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6390/15")
os.environ.setdefault("JWT_SECRET", "dev-secret")
# Los cuatro servicios deben apuntar a sus bases de test. Sin esto, builds_api y
# feed_api caen en su default (builds_db / feed_db) y la suite trunca y escribe
# sobre los datos de desarrollo.
os.environ.setdefault(
    "NOTIF_DATABASE_URL",
    "postgresql://tfinder:tfinder@localhost:5432/notif_db_test",
)
os.environ.setdefault(
    "BUILDS_DATABASE_URL",
    "postgresql://tfinder:tfinder@localhost:5432/builds_db_test",
)
os.environ.setdefault(
    "FEED_DATABASE_URL",
    "postgresql://tfinder:tfinder@localhost:5432/feed_db_test",
)

# ---- Aislamiento de RabbitMQ -------------------------------------------------
# Los tests de integración publican eventos de dominio. Si usan el vhost "/",
# los consumen los consumidores del notif-api que corren en Docker, rebotan y
# dejan residuo permanente en dlq.general del ambiente de desarrollo. Ademas
# los tests leen esa cola, asi que el resultado depende de mensajes ajenos.
#
# Solución: apuntar RABBITMQ_URL a un vhost propio. El vhost "/" queda intacto
# para el ambiente y la suite no puede tocarlo.
VHOST_PRUEBAS = os.environ.get("RABBITMQ_VHOST_TEST", "tfinder_test")
AMQP_BASE = os.environ.get("RABBITMQ_URL", "amqp://tfinder:tfinder@localhost:5673/")
os.environ["RABBITMQ_URL"] = AMQP_BASE.rstrip("/") + f"/{VHOST_PRUEBAS}"

import base64
import json
import urllib.error
import urllib.request
import uuid
import warnings

import pytest
from fastapi.testclient import TestClient

from app.infra.redis import get_redis
from mesas_api.app.db import abrir_pool, cerrar_pool, get_connection
from mesas_api.app.init_db import init_db
from mesas_api.main import app

TABLAS = (
    "mesas, usuarios, matchmaking, solicitudes_uniones, sesiones, asistencias"
)

# Puertos donde puede estar la management API segun se exponga el compose (15673)
# o el service container de CI (15672).
_MGMT_CANDIDATOS = [
    os.environ.get("RABBITMQ_MGMT_URL", ""),
    "http://localhost:15673/api",
    "http://localhost:15672/api",
]
_CRED = base64.b64encode(b"tfinder:tfinder").decode()


def _mgmt_disponible():
    """Devuelve la base de la management API, o None si no responde."""
    for base in _MGMT_CANDIDATOS:
        if not base:
            continue
        req = urllib.request.Request(f"{base}/overview", method="GET")
        req.add_header("Authorization", f"Basic {_CRED}")
        try:
            with urllib.request.urlopen(req, timeout=3):
                return base.rstrip("/")
        except (urllib.error.URLError, OSError):
            continue
    return None


def _asegurar_vhost(base, nombre):
    """Crea el vhost y le da permisos completos al usuario de los tests."""
    def _pedir(ruta, metodo, cuerpo=None):
        datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
        req = urllib.request.Request(f"{base}{ruta}", data=datos, method=metodo)
        req.add_header("Authorization", f"Basic {_CRED}")
        req.add_header("content-type", "application/json")
        with urllib.request.urlopen(req, timeout=5):
            return True

    try:
        _pedir(f"/vhosts/{nombre}", "PUT", {"description": "TFinder suite de tests"})
    except urllib.error.HTTPError as exc:
        # 400 = ya existe con esos parametros; 201/todo lo demas tambien es ok
        if exc.code not in (400, 201):
            raise
    _pedir(
        f"/permissions/{nombre}/tfinder",
        "PUT",
        {"configure": ".*", "write": ".*", "read": ".*"},
    )


def _purgar_vhost_de_pruebas():
    """Vacía las colas del vhost de tests al terminar la sesión."""
    try:
        import pika

        from app.infra.rabbitmq import get_params

        conn = pika.BlockingConnection(get_params())
        try:
            canal = conn.channel()
            for cola in ("notif.mesa", "notif.sesion", "doc.pdf", "dlq.general"):
                try:
                    canal.queue_purge(queue=cola)
                except Exception:
                    pass
        finally:
            conn.close()
    except Exception:
        pass


@pytest.fixture(scope="session", autouse=True)
def vhost_de_pruebas():
    """Deja RABBITMQ_URL apuntando a un vhost aislado y lo crea si falta.

    Si la management API no responde (broker sin plugin de management), cae al
    vhost por defecto con un warning: la suite sigue siendo ejecutable, pero
    pierde el aislamiento y puede volver a dejar residuo en dlq.general.
    """
    base = _mgmt_disponible()
    if base is None:
        warnings.warn(
            "RabbitMQ management API no disponible: los tests usan el vhost '/' "
            "y pueden dejar residuo en dlq.general del ambiente de desarrollo",
            RuntimeWarning,
            stacklevel=1,
        )
        os.environ["RABBITMQ_URL"] = AMQP_BASE
        yield None
        return

    _asegurar_vhost(base, VHOST_PRUEBAS)
    os.environ["RABBITMQ_URL"] = AMQP_BASE.rstrip("/") + f"/{VHOST_PRUEBAS}"
    yield VHOST_PRUEBAS

    # Los tests publican eventos que nadie consume en el vhost de pruebas (los
    # consumidores viven en el vhost "/"). Purgar al terminar evita que el
    # vhost crezca sin limite entre corridas.
    _purgar_vhost_de_pruebas()


@pytest.fixture(scope="session")
def bd_pruebas():
    abrir_pool()
    init_db()
    yield
    cerrar_pool()


@pytest.fixture(scope="session")
def dlq_general_vacia(request, vhost_de_pruebas):
    """Purgar dlq.general del vhost de tests para que test_dlq sea determinista.

    Con el vhost aislado (ver vhost_de_pruebas) nadie externo escribe en esta
    cola, asi que el purgado es solo defensivo. El problema original era que el
    notif-api de Docker consumia los mensajes de la suite y los rebotaba a la
    DLQ del vhost "/" DESPUES del purgado de fin de sesion.
    """
    import pika

    from app.infra.rabbitmq import get_params

    def _purgar():
        try:
            conn = pika.BlockingConnection(get_params())
            ch = conn.channel()
            ch.queue_declare(queue="dlq.general", durable=True)
            ch.queue_purge(queue="dlq.general")
            conn.close()
        except Exception:
            pass

    _purgar()
    yield
    _purgar()


@pytest.fixture(autouse=True)
def sin_publicar_en_broker_real(request):
    """Impide que un test unitario escriba en el broker de desarrollo.

    `_base._manejar` publica en la cola real `dlq.general` cuando un consumidor
    agota los reintentos. Un test unitario que exercise esa rama por accidente
    deja mensajes en el broker del ambiente, y esa cola es compartida con el
    notif-api de Docker. Los tests de integración sí necesitan el broker real,
    por eso el marcador decide.
    """
    if request.node.get_closest_marker("integration"):
        yield
        return

    import notif_api.app.consumers._base as base

    original = base._dlq_final

    def _interceptado(*args, **kwargs):
        raise AssertionError(
            "un test unitario no debe publicar en dlq.general; "
            "mockea el consumidor o marcalo como integration"
        )

    base._dlq_final = _interceptado
    yield
    base._dlq_final = original


@pytest.fixture(autouse=True)
def estado_limpio(request):
    if not request.node.get_closest_marker("integration"):
        yield
        return
    request.getfixturevalue("bd_pruebas")
    with get_connection() as conn:
        conn.execute(f"TRUNCATE {TABLAS} RESTART IDENTITY CASCADE")
    get_redis().flushdb()
    yield
    with get_connection() as conn:
        conn.execute(f"TRUNCATE {TABLAS} RESTART IDENTITY CASCADE")
    get_redis().flushdb()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def client_aislado():
    return TestClient(app)


def _registrar(client, rol):
    email = f"test_{uuid.uuid4().hex[:10]}@{rol}.tfinder"
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secreto123",
            "nombre": f"Test {rol}",
            "rol": rol,
        },
    )
    assert resp.status_code == 201
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "secreto123"},
    )
    return login.json()["access_token"]


def _crear_con_rol(rol):
    """El registro publico ya no asigna roles: los roles se crean por SQL."""
    from mesas_api.app.controllers.auth_controller import _emitir_tokens
    from mesas_api.app.models.auth_model import crear_usuario

    email = f"test_{rol}_{uuid.uuid4().hex[:10]}@tfinder.dev"
    usuario = crear_usuario(email, "secreto123", f"Test {rol}", rol)
    return _emitir_tokens(usuario)["access_token"]


@pytest.fixture
def token_gm(client):
    return _crear_con_rol("gm")


@pytest.fixture
def token_jugador(client):
    return _registrar(client, "usuario")


@pytest.fixture
def token_admin(client):
    return _crear_con_rol("admin")


@pytest.fixture
def headers_admin(token_admin):
    return {"Authorization": f"Bearer {token_admin}"}


def _token_de_usuario(usuario):
    from mesas_api.app.controllers.auth_controller import _emitir_tokens

    return _emitir_tokens(usuario)["access_token"]


def crear_mesa(client, token, nombre="Mesa test", jugadores_max=4):
    resp = client.post(
        "/api/v1/mesas",
        json={
            "nombre": nombre,
            "sistema": "PF1e",
            "jugadores_max": jugadores_max,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def crear_sesion(mesa_id):
    with get_connection() as conn:
        fila = conn.execute(
            "INSERT INTO sesiones (mesa_id) VALUES (%s) RETURNING id",
            (mesa_id,),
        ).fetchone()
    return fila["id"]