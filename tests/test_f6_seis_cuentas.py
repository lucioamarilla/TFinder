"""F6 · Pruebas funcionales con 6 cuentas (1 master + 5 jugadores).

Recorre los 19 ítems del pliego de la FASE 6 sobre los 4 servicios reales
(contratos de permiso, persistencia y autorización), sin navegador. Complementa
a la suite unit/int (268/268) y al Playwright smoke que se intenta correr en
paralelo (ver docs/SEGUIMIENTO-REFACTOR.md).
"""

import os
import socket
import threading
import time
import uuid

import pytest
import uvicorn
from fastapi.testclient import TestClient

from builds_api.app.db import abrir_pool as abrir_pool_builds
from builds_api.app.init_db import init_db as init_db_builds
from builds_api.main import app as builds_app
from feed_api.app.db import abrir_pool as abrir_pool_feed
from feed_api.app.db import get_connection as feed_conn
from feed_api.app.init_db import init_db as init_db_feed
from feed_api.main import app as feed_app
from mesas_api.main import app as mesas_app

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module", autouse=True)
def _pools():
    abrir_pool_builds()
    init_db_builds()
    abrir_pool_feed()
    init_db_feed()
    yield


@pytest.fixture(scope="module", autouse=True)
def _mesas_real():
    puerto = 0
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        puerto = s.getsockname()[1]
    config = uvicorn.Config(
        mesas_app, host="127.0.0.1", port=puerto, log_level="warning", lifespan="off"
    )
    servidor = uvicorn.Server(config)
    hilo = threading.Thread(target=servidor.run, daemon=True)
    hilo.start()
    for _ in range(60):
        if getattr(servidor, "started", False):
            break
        time.sleep(0.2)
    url_previa = os.environ.get("MESA_URL")
    os.environ["MESA_URL"] = f"http://127.0.0.1:{puerto}"
    yield
    if url_previa is None:
        os.environ.pop("MESA_URL", None)
    else:
        os.environ["MESA_URL"] = url_previa
    servidor.should_exit = True
    hilo.join(timeout=5)


@pytest.fixture(scope="module", autouse=True)
def _builds_real():
    puerto = 0
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        puerto = s.getsockname()[1]
    config = uvicorn.Config(
        builds_app, host="127.0.0.1", port=puerto, log_level="warning", lifespan="off"
    )
    servidor = uvicorn.Server(config)
    hilo = threading.Thread(target=servidor.run, daemon=True)
    hilo.start()
    for _ in range(60):
        if getattr(servidor, "started", False):
            break
        time.sleep(0.2)
    url_previa = os.environ.get("BUILDS_URL")
    os.environ["BUILDS_URL"] = f"http://127.0.0.1:{puerto}"
    yield
    if url_previa is None:
        os.environ.pop("BUILDS_URL", None)
    else:
        os.environ["BUILDS_URL"] = url_previa
    servidor.should_exit = True
    hilo.join(timeout=5)


@pytest.fixture
def mesas_client():
    return TestClient(mesas_app)


@pytest.fixture
def builds_client():
    return TestClient(builds_app)


@pytest.fixture
def feed_client():
    with feed_conn() as conn:
        conn.execute("TRUNCATE publicaciones, likes_post, follows, uploads, wiki_paginas, wiki_contribuciones RESTART IDENTITY CASCADE")
    return TestClient(feed_app)


def _registrar(client, nombre, idx):
    email = f"f6_{idx}_{uuid.uuid4().hex[:8]}@tfinder.dev"
    r = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secreto123", "nombre": nombre},
    )
    assert r.status_code == 201, r.text
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "secreto123"})
    assert login.status_code == 200
    return login.json()


def test_f6_seis_cuentas_flujo_completo(client, token_gm, builds_client, feed_client):
    # ---- 1. Creación de mesa (master = cuenta 1) -------------------------------
    master = _registrar(client, "Master F6", 0)
    master_token = master["access_token"]
    master_id = int(master["perfil"]["id"])
    mesa = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa F6 (seis cuentas)", "sistema": "pf1e", "jugadores_max": 5, "estado": "abierta"},
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert mesa.status_code == 201, mesa.text
    mesa_id = mesa.json()["id"]
    assert mesa.json()["gm_id"] == master_id, "el creador es master automáticamente (principio 2.1)"
    assert mesa.json()["estado"] == "abierta"

    # ---- 2/3/4. Solicitudes, aceptación y rechazo ------------------------------
    jugadores = [_registrar(client, f"Jugador F6 {i}", i + 1) for i in range(5)]
    sol_ids = []
    for j in jugadores:
        sol = client.post(
            f"/api/v1/mesas/{mesa_id}/solicitudes",
            headers={"Authorization": f"Bearer {j['access_token']}"},
        )
        assert sol.status_code == 201
        assert sol.json()["estado"] == "pendiente", "RF-14: nace pendiente"
        sol_ids.append(sol.json()["id"])

    # master acepta 3, rechaza 1, deja 1 pendiente
    for sid in sol_ids[:3]:
        r = client.post(
            f"/api/v1/mesas/{mesa_id}/solicitudes/{sid}/aceptar",
            headers={"Authorization": f"Bearer {master_token}"},
        )
        assert r.status_code == 200, f"aceptar {sid}: {r.text}"
        assert r.json()["estado"] == "aceptada"
    r_rech = client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes/{sol_ids[3]}/rechazar",
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert r_rech.status_code == 200
    assert r_rech.json()["estado"] == "rechazada"

    detalle = client.get(f"/api/v1/mesas/{mesa_id}", headers={"Authorization": f"Bearer {master_token}"}).json()
    assert detalle["jugadores_actuales"] == 3, "cupo consumido solo por los aceptados"

    # ---- 5. Permisos del master vs jugadores ---------------------------------
    # jugador no master no edita la mesa (403)
    r_put = client.put(
        f"/api/v1/mesas/{mesa_id}",
        json={"estado": "cerrada"},
        headers={"Authorization": f"Bearer {jugadores[0]['access_token']}"},
    )
    assert r_put.status_code == 403, "VAL-17: solo el master edita"
    # master edita (200) y luego vuelve a abrir
    r_put_gm = client.put(
        f"/api/v1/mesas/{mesa_id}",
        json={"estado": "abierta"},
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert r_put_gm.status_code == 200

    # ---- 7/8/9. Wiki: master crea directo + contribuciones de jugadores ---------
    r_wiki = feed_client.post(
        f"/api/v1/mesas/{mesa_id}/wiki",
        json={"titulo": "El corredor", "tipo": "Lugar", "visibilidad": "jugadores"},
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert r_wiki.status_code == 201
    pagina_id = r_wiki.json()["id"]

    # jugador envía contribución (pendiente)
    contrib = feed_client.post(
        f"/api/v1/mesas/{mesa_id}/wiki/{pagina_id}/contribuciones",
        json={"cuerpo": [{"texto": "El corredor respira sal."}]},
        headers={"Authorization": f"Bearer {jugadores[0]['access_token']}"},
    )
    assert contrib.status_code == 201, contrib.text
    contrib_id = contrib.json()["id"]
    assert contrib.json()["estado"] == "pendiente"

    # el master la acepta → aprobada y el contenido se aplica a la página
    ok = feed_client.post(
        f"/api/v1/mesas/{mesa_id}/wiki/contribuciones/{contrib_id}/aprobar",
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert ok.status_code == 200
    assert ok.json()["estado"] == "aprobada"
    pagina = feed_client.get(f"/api/v1/wiki/{pagina_id}", headers={"Authorization": f"Bearer {jugadores[1]['access_token']}"}).json()
    textos = " ".join(
        (str(b.get("texto") or "") if isinstance(b, dict) else str(b)) for b in (pagina.get("contenido") or [])
    )
    assert "El corredor respira sal." in textos, "aprobación aplica el contenido"

    # rechazar otra contribución
    contrib2 = feed_client.post(
        f"/api/v1/mesas/{mesa_id}/wiki/{pagina_id}/contribuciones",
        json={"cuerpo": [{"texto": "La luna es de queso"}]},
        headers={"Authorization": f"Bearer {jugadores[1]['access_token']}"},
    ).json()
    r_rech = feed_client.post(
        f"/api/v1/mesas/{mesa_id}/wiki/contribuciones/{contrib2['id']}/rechazar",
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert r_rech.status_code == 200 and r_rech.json()["estado"] == "rechazada"

    # jugador (no master) intenta aprobar → 403
    r_forbidden = feed_client.post(
        f"/api/v1/mesas/{mesa_id}/wiki/contribuciones/{contrib_id}/aprobar",
        headers={"Authorization": f"Bearer {jugadores[0]['access_token']}"},
    )
    assert r_forbidden.status_code == 403

    # ---- 6. Creación de sesión + anotaciones de todos -------------------------
    r_ses = client.post(
        f"/api/v1/mesas/{mesa_id}/sesiones",
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert r_ses.status_code == 201
    sesion_id = r_ses.json()["id"]

    # jugador no master no crea sesión
    r_ses_forbidden = client.post(
        f"/api/v1/mesas/{mesa_id}/sesiones",
        headers={"Authorization": f"Bearer {jugadores[0]['access_token']}"},
    )
    assert r_ses_forbidden.status_code == 403

    anotaciones_texto = [
        "El master abre la sesión en la taberna.",
        "El jugador uno anota que entró el mensajero.",
        "El jugador dos suma que la carta era sangrada.",
    ]
    for idx, texto in enumerate(anotaciones_texto):
        tok = master_token if idx == 0 else jugadores[idx - 1]["access_token"]
        r_an = client.post(
            f"/api/v1/mesas/{mesa_id}/sesiones/{sesion_id}/anotaciones",
            json={"texto": texto},
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert r_an.status_code == 201, r_an.text

    # anotación vacía → 400
    r_vacia = client.post(
        f"/api/v1/mesas/{mesa_id}/sesiones/{sesion_id}/anotaciones",
        json={"texto": "   "},
        headers={"Authorization": f"Bearer {jugadores[0]['access_token']}"},
    )
    assert r_vacia.status_code == 400

    historial = client.get(
        f"/api/v1/mesas/{mesa_id}/sesiones/{sesion_id}/anotaciones",
        headers={"Authorization": f"Bearer {jugadores[0]['access_token']}"},
    ).json()
    assert len(historial) == 3, "persistencia del historial (3 anotaciones)"
    fechas = [a["creado_en"] for a in historial]
    assert fechas == sorted(fechas), "orden cronológico"
    autores = {a["autor_nombre"] for a in historial}
    assert len(autores) >= 2, "varios integrantes anotaron"
    assert all(a["autor_nombre"].strip() for a in historial)
    assert all(a["texto"].strip() for a in historial)

    # no-miembro no lee
    extrano = _registrar(client, "Ajeno F6", 99)
    assert client.get(
        f"/api/v1/mesas/{mesa_id}/sesiones/{sesion_id}/anotaciones",
        headers={"Authorization": f"Bearer {extrano['access_token']}"},
    ).status_code == 403

    # ---- 10. Publicaciones en el foro -----------------------------------------
    r_post = feed_client.post(
        "/api/v1/feed",
        json={"titulo": "Crónica de la sesión", "cuerpo": "La mesa mato al Drago sin caer.", "tipo": "post"},
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert r_post.status_code == 201, r_post.text

    # adjunto de build pública (RF-20): crear un build público y adjuntarlo
    build_token = master_token
    r_build = builds_client.post(
        "/api/v1/builds",
        json={"titulo": "Mago del Alba", "clase": "Mago", "privacidad": "publico", "atributos": {"fue": 10, "des": 14, "con": 12, "int": 18, "sab": 12, "car": 10}},
        headers={"Authorization": f"Bearer {build_token}"},
    )
    assert r_build.status_code == 201, r_build.text
    build_id = r_build.json()["id"]
    r_post_build = feed_client.post(
        "/api/v1/feed",
        json={"titulo": "Build compartida", "cuerpo": "Análisis", "tipo": "build", "embed": {"build_id": build_id}},
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert r_post_build.status_code == 201, r_post_build.text

    # adjunto de build privada → 409 (pliego F5)
    r_build_priv = builds_client.post(
        "/api/v1/builds",
        json={"titulo": "Sombra", "clase": "Pícaro", "privacidad": "privado", "atributos": {"fue": 10, "des": 18, "con": 12, "int": 10, "sab": 10, "car": 14}},
        headers={"Authorization": f"Bearer {master_token}"},
    ).json()
    r_post_priv = feed_client.post(
        "/api/v1/feed",
        json={"titulo": "x", "cuerpo": "y", "embed": {"build_id": r_build_priv["id"]}},
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert r_post_priv.status_code == 409

    # adjunto de imagen (upload real en feed-api)
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
    r_up = feed_client.post(
        "/api/v1/uploads",
        files={"upload": ("avatar.png", png, "image/png")},
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert r_up.status_code == 201
    upload_id = r_up.json()["id"]
    r_post_img = feed_client.post(
        "/api/v1/feed",
        json={"titulo": "Con imagen", "cuerpo": "Foto real", "embed": {"imagenes": [upload_id]}},
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert r_post_img.status_code == 201

    # like + follow
    post_id = r_post.json()["id"]
    assert feed_client.post(f"/api/v1/feed/{post_id}/like", headers={"Authorization": f"Bearer {jugadores[0]['access_token']}"}).status_code == 200
    assert feed_client.post(f"/api/v1/usuarios/{master_id}/seguir", headers={"Authorization": f"Bearer {jugadores[0]['access_token']}"}).status_code == 200
    auto = feed_client.post(f"/api/v1/usuarios/{master_id}/seguir", headers={"Authorization": f"Bearer {jugadores[0]['access_token']}"}).status_code
    assert auto == 409, "RN-10: no duplica"

    # ---- 11/17. Builds: múltiples personajes por usuario ---------------------
    for i in range(2):
        r_b = builds_client.post(
            "/api/v1/builds",
            json={"titulo": f"Personaje {i}", "clase": "Mago", "privacidad": "borrador", "atributos": {"fue": 10, "des": 14, "con": 12, "int": 18, "sab": 12, "car": 10}},
            headers={"Authorization": f"Bearer {master_token}"},
        )
        assert r_b.status_code == 201
    mios = builds_client.get("/api/v1/builds", params={"autor_id": str(master_id)}, headers={"Authorization": f"Bearer {master_token}"}).json()
    assert len(mios) >= 2, "múltiples builds por usuario"
    # privada no legible por tercero (L-04)
    privado_id = builds_client.post(
        "/api/v1/builds",
        json={"titulo": "Sombra", "clase": "Pícaro", "privacidad": "privado", "atributos": {"fue": 10, "des": 18, "con": 12, "int": 10, "sab": 10, "car": 14}},
        headers={"Authorization": f"Bearer {master_token}"},
    ).json()["id"]
    assert builds_client.get(f"/api/v1/builds/{privado_id}").status_code == 404
    # publicar lo vuelve público
    assert builds_client.post(f"/api/v1/builds/{privado_id}/publicar", headers={"Authorization": f"Bearer {master_token}"}).json()["privacidad"] == "publico"

    # ---- 12/18. Perfil: edición y avatar -------------------------------------
    r_perfil = client.patch(
        "/api/v1/auth/perfil",
        json={"nombre": "Master F6", "bio": "Dirijo campañas", "avatarUrl": f"/api/v1/uploads/{upload_id}"},
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert r_perfil.status_code == 200
    assert r_perfil.json()["avatarUrl"] == f"/api/v1/uploads/{upload_id}"
    r_perfil2 = client.get("/api/v1/auth/perfil", headers={"Authorization": f"Bearer {master_token}"})
    assert r_perfil2.json()["bio"] == "Dirijo campañas"

    # ---- 13/14/16. wiki: master crea + jugador contribuye + acepta/rechaza ----
    # (cubierto en test_f4; verificación mínima de estados aquí)
    r_wiki = feed_client.post(
        f"/api/v1/mesas/{mesa_id}/wiki",
        json={"titulo": "El corredor", "tipo": "Lugar", "visibilidad": "jugadores"},
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert r_wiki.status_code == 201
    pagina_id = r_wiki.json()["id"]
    contrib = feed_client.post(
        f"/api/v1/mesas/{mesa_id}/wiki/{pagina_id}/contribuciones",
        json={"cuerpo": [{"texto": "El corredor respira sal."}]},
        headers={"Authorization": f"Bearer {jugadores[0]['access_token']}"},
    )
    assert contrib.status_code == 201
    assert contrib.json()["estado"] == "pendiente"
    r_ok = feed_client.post(
        f"/api/v1/mesas/{mesa_id}/wiki/contribuciones/{contrib.json()['id']}/aprobar",
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert r_ok.status_code == 200 and r_ok.json()["estado"] == "aprobada"

    # ---- Expulsar (15) y salirse (voluntario) --------------------------------
    # expulsar al jugador 4 (master)
    sol_extra = client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes",
        headers={"Authorization": f"Bearer {jugadores[3]['access_token']}"},
    ).json()
    client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes/{sol_extra['id']}/aceptar",
        headers={"Authorization": f"Bearer {master_token}"},
    )
    import jwt as _jwt

    sub_j3 = int(_jwt.decode(jugadores[3]["access_token"], options={"verify_signature": False})["sub"])
    r_exp = client.delete(
        f"/api/v1/mesas/{mesa_id}/miembros/{sub_j3}",
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert r_exp.status_code == 200, r_exp.text
    assert r_exp.json()["jugadores_actuales"] == 3, "el cupo vuelve al expulsar"

    # jugador 5 (pendiente sin aceptar) se retira por su cuenta → 409 (no es miembro)
    sol_pend_id = sol_ids[4]  # ya estaba pendiente desde el inicio
    r_salir = client.delete(
        f"/api/v1/mesas/{mesa_id}/miembros/mi",
        headers={"Authorization": f"Bearer {jugadores[4]['access_token']}"},
    )
    assert r_salir.status_code == 403, "un pendiente no es miembro: no sale por esa vía (403)"

    # ---- 19. Cierre y expiración de sesiones de autenticación -----------------
    r_ref = client.post("/api/v1/auth/refresh", json={"refresh_token": master["refresh_token"]})
    assert r_ref.status_code == 200 and "access_token" in r_ref.json()
    r_logout = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {master_token}"})
    assert r_logout.status_code == 200
    assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {master_token}"}).status_code == 401
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": master["refresh_token"]}).status_code == 401
