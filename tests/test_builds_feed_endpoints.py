"""Endpoints de builds-api y feed-api con base de datos real.

Cubre la brecha de cobertura endpoint por endpoint: hasta ahora estos dos
servicios solo tenian verificacion manual via curl.

Las tablas se truncan por test (no se tocan los seeds de desarrollo) y se
insertan filas minimas para poder ejercitar filtros y 404.
"""

import pytest
from fastapi.testclient import TestClient

from builds_api.app.db import abrir_pool as abrir_pool_builds
from builds_api.app.db import get_connection as builds_conn
from builds_api.app.init_db import init_db as init_db_builds
from builds_api.main import app as builds_app
from feed_api.app.db import abrir_pool as abrir_pool_feed
from feed_api.app.db import get_connection as feed_conn
from feed_api.app.init_db import init_db as init_db_feed
from feed_api.main import app as feed_app

pytestmark = pytest.mark.integration

BUILDS_TABLAS = "builds, tags"
FEED_TABLAS = "wiki_paginas, publicaciones"

BUILDS_FIXTURE = [
    {
        "persona": "Mago Test", "handle": "@mago", "nombre": "Mago Test",
        "clase": "Mago", "raza": "Humano", "nivel": 3, "rol": "Soporte",
        "privacidad": "publico", "mesa_id": 1, "favoritos": 5,
    },
    {
        "persona": "Guerrera Test", "handle": "@guerrera", "nombre": "Guerrera Test",
        "clase": "Guerrero", "raza": "Humana", "nivel": 4, "rol": "Defensa",
        "privacidad": "privado", "mesa_id": 2, "favoritos": 12,
    },
]

POSTS_FIXTURE = [
    {
        "tipo": "post", "autor": "Admin", "autor_id": "1", "titulo": "Post uno",
        "etiqueta": "alfa", "votos": 1,
    },
    {
        "tipo": "build", "autor": "Jugador", "autor_id": "3", "titulo": "Build de mago",
        "etiqueta": "beta", "votos": 9,
    },
    {
        "tipo": "wiki", "autor": "GM", "autor_id": "2", "titulo": "Guia de campana",
        "etiqueta": "alfa", "votos": 4,
    },
]


def _truncar_y_sembrar_builds():
    with builds_conn() as conn:
        conn.execute(f"TRUNCATE {BUILDS_TABLAS} RESTART IDENTITY CASCADE")
        for fila in BUILDS_FIXTURE:
            columnas = ", ".join(fila)
            marcas = ", ".join(["%s"] * len(fila))
            conn.execute(f"INSERT INTO builds ({columnas}) VALUES ({marcas})", tuple(fila.values()))
        conn.execute("INSERT INTO tags (nombre) VALUES ('PF1e'), ('Mago'), ('Combate')")


def _truncar_y_sembrar_feed():
    with feed_conn() as conn:
        conn.execute(f"TRUNCATE {FEED_TABLAS} RESTART IDENTITY CASCADE")
        for fila in POSTS_FIXTURE:
            columnas = ", ".join(fila)
            marcas = ", ".join(["%s"] * len(fila))
            conn.execute(
                f"INSERT INTO publicaciones ({columnas}) VALUES ({marcas})", tuple(fila.values())
            )
        conn.execute(
            "INSERT INTO wiki_paginas (mesa_id, carpeta, titulo, tipo) "
            "VALUES ('demo-mesa', 'notas', 'Bienvenida', 'NOTA'),"
            "       ('otra-mesa', 'reglas', 'Reglas', 'NOTA')"
        )


@pytest.fixture(scope="module", autouse=True)
def _pools():
    """Abre los pools una vez por modulo y NO los cierra.

    Mismo criterio que test_dlq_operativo.py: el pool es global y se reutiliza
    entre modulos. Por eso el TestClient se usa sin `with`, para que corra el
    lifespan que cerraria el pool.
    """
    abrir_pool_builds()
    abrir_pool_feed()
    init_db_builds()
    init_db_feed()
    yield


@pytest.fixture
def builds_client(_pools):
    _truncar_y_sembrar_builds()
    return TestClient(builds_app)


@pytest.fixture
def feed_client(_pools):
    _truncar_y_sembrar_feed()
    return TestClient(feed_app)


# ---------------------------------------------------------------- builds-api

def test_listar_builds_devuelve_todos(builds_client):
    r = builds_client.get("/api/v1/builds")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_filtrar_builds_por_mesa(builds_client):
    r = builds_client.get("/api/v1/builds?mesa_id=1")
    assert r.status_code == 200
    cuerpo = r.json()
    assert [b["persona"] for b in cuerpo] == ["Mago Test"]


def test_filtrar_builds_por_mesa_sin_resultados_no_es_error(builds_client):
    r = builds_client.get("/api/v1/builds?mesa_id=99999")
    assert r.status_code == 200
    assert r.json() == []


def test_detalle_de_build(builds_client):
    r = builds_client.get("/api/v1/builds/1")
    assert r.status_code == 200
    assert r.json()["persona"] == "Mago Test"
    assert r.json()["nivel"] == 3


def test_build_inexistente_devuelve_404(builds_client):
    r = builds_client.get("/api/v1/builds/99999")
    assert r.status_code == 404
    assert r.json()["error"]["codigo"] == 404


def test_build_id_no_numerico_devuelve_422(builds_client):
    """FastAPI no puede coercionar a int: debe fallar, no devolver un build."""
    r = builds_client.get("/api/v1/builds/abc")
    assert r.status_code in (400, 422)


def test_listar_tags(builds_client):
    r = builds_client.get("/api/v1/tags")
    assert r.status_code == 200
    assert {t["nombre"] for t in r.json()} == {"PF1e", "Mago", "Combate"}


def test_pdf_de_build_exige_token(builds_client, headers_admin):
    r = builds_client.post("/api/v1/builds/1/pdf", json={})
    assert r.status_code == 401
    assert r.json() == {"error": {"codigo": 401, "mensaje": "Autenticación requerida"}}

    con_token = builds_client.post(
        "/api/v1/builds/1/pdf", json={}, headers=headers_admin
    )
    assert con_token.status_code == 202
    assert con_token.json()["documento_id"]


def test_pdf_de_build_inexistente_devuelve_404(builds_client, headers_admin):
    r = builds_client.post("/api/v1/builds/99999/pdf", json={}, headers=headers_admin)
    assert r.status_code == 404


# ------------------------------------------------------------------ feed-api

def test_feed_sin_filtros_devuelve_todo(feed_client):
    r = feed_client.get("/api/v1/feed")
    assert r.status_code == 200
    assert len(r.json()) == 3


@pytest.mark.parametrize("tipo,esperado", [("post", 1), ("build", 1), ("wiki", 1)])
def test_feed_filtrado_por_tipo(feed_client, tipo, esperado):
    r = feed_client.get(f"/api/v1/feed?tipo={tipo}")
    assert r.status_code == 200
    cuerpo = r.json()
    assert len(cuerpo) == esperado
    assert all(p["tipo"] == tipo for p in cuerpo)


def test_feed_tipo_invalido_devuelve_400(feed_client):
    """Un tipo desconocido no debe filtrar en silencio: se rechaza."""
    r = feed_client.get("/api/v1/feed?tipo=inventado")
    assert r.status_code == 400
    assert r.json()["error"]["codigo"] == 400


def test_feed_filtrado_por_autor(feed_client):
    r = feed_client.get("/api/v1/feed?autor_id=3")
    assert r.status_code == 200
    assert [p["titulo"] for p in r.json()] == ["Build de mago"]


def test_feed_filtrado_por_etiqueta(feed_client):
    r = feed_client.get("/api/v1/feed?etiqueta=alfa")
    assert r.status_code == 200
    assert {p["titulo"] for p in r.json()} == {"Post uno", "Guia de campana"}


def test_feed_ordenado_por_votos(feed_client):
    r = feed_client.get("/api/v1/feed?orden=votos")
    assert r.status_code == 200
    assert [p["titulo"] for p in r.json()] == ["Build de mago", "Guia de campana", "Post uno"]


def test_feed_orden_invalido_devuelve_400(feed_client):
    r = feed_client.get("/api/v1/feed?orden=cualquiera")
    assert r.status_code == 400
    assert r.json()["error"]["codigo"] == 400


def test_feed_paginacion_limit_y_offset(feed_client):
    primera = feed_client.get("/api/v1/feed?limit=2&offset=0").json()
    segunda = feed_client.get("/api/v1/feed?limit=2&offset=2").json()
    assert len(primera) == 2 and len(segunda) == 1
    assert not {p["id"] for p in primera} & {p["id"] for p in segunda}


@pytest.mark.parametrize("query", ["limit=0", "limit=101", "offset=-1"])
def test_feed_paginacion_invalida_devuelve_400(feed_client, query):
    r = feed_client.get(f"/api/v1/feed?{query}")
    assert r.status_code == 400


def test_wiki_sin_filtro_devuelve_todas_las_carpetas(feed_client):
    r = feed_client.get("/api/v1/wiki")
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["total"] == 2
    assert {c["id"] for c in cuerpo["carpetas"]} == {"notas", "reglas"}


def test_wiki_filtrada_por_mesa(feed_client):
    r = feed_client.get("/api/v1/wiki?mesa_id=demo-mesa")
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["total"] == 1
    assert cuerpo["paginas"][0]["titulo"] == "Bienvenida"


def test_wiki_de_mesa_inexistente_devuelve_estructura_vacia(feed_client):
    r = feed_client.get("/api/v1/wiki?mesa_id=99999")
    assert r.status_code == 200
    assert r.json() == {"carpetas": [], "paginas": [], "total": 0}


def test_diario_pdf_acepta_y_exige_token(feed_client, headers_admin):
    sin_token = feed_client.post("/api/v1/mesas/1/sesiones/1/diario/pdf", json={})
    assert sin_token.status_code == 401
    assert sin_token.json()["error"]["codigo"] == 401

    con_token = feed_client.post(
        "/api/v1/mesas/1/sesiones/1/diario/pdf", json={}, headers=headers_admin
    )
    assert con_token.status_code == 202
    assert con_token.json()["estado"] == "aceptado"
    assert con_token.json()["documento_id"]
