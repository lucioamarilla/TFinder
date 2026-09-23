import os

os.environ.setdefault(
    "MESAS_DATABASE_URL",
    "postgresql://tfinder:tfinder@localhost:5432/mesas_db_test",
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6390/15")
os.environ.setdefault("JWT_SECRET", "dev-secret")
os.environ.setdefault(
    "NOTIF_DATABASE_URL",
    "postgresql://tfinder:tfinder@localhost:5432/notif_db_test",
)

import uuid

import pytest
from fastapi.testclient import TestClient

from app.infra.redis import get_redis
from mesas_api.app.db import abrir_pool, cerrar_pool, get_connection
from mesas_api.app.init_db import init_db
from mesas_api.main import app

TABLAS = (
    "mesas, usuarios, matchmaking, solicitudes_uniones, sesiones, asistencias"
)


@pytest.fixture(scope="session", autouse=True)
def bd_pruebas():
    abrir_pool()
    init_db()
    yield
    cerrar_pool()


@pytest.fixture(autouse=True)
def estado_limpio(bd_pruebas):
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


@pytest.fixture
def token_gm(client):
    return _registrar(client, "gm")


@pytest.fixture
def token_jugador(client):
    return _registrar(client, "usuario")


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