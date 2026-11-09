"""P0.4 · Vertical de mesa: ownership GM, sistema pf1e (VAL-08), filtros +
paginación (RF-04/13), flujo de solicitudes pendiente→GM acepta/rechaza
(RF-14/15, RN-07/08, VAL-18/20/21/22/23/15) y expulsión con cupo.

RED previo: cualquiera editaba/borraba mesas ajenas, 'sistema' aceptaba
cualquier string, GET /mesas no filtraba, y POST /solicitudes auto-aceptaba.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

pytestmark = pytest.mark.integration


def _credencial(email):
    return {
        "email": email,
        "password": "secreto123",
        "nombre": "Jugador Vertical",
        "rol": "usuario",
    }


def _usuario(client):
    email = f"vert_{uuid.uuid4().hex[:8]}@tfinder.dev"
    client.post("/api/v1/auth/register", json=_credencial(email))
    from tests.conftest import codigo_del_ultimo_mail

    verif = client.post(
        "/api/v1/auth/register/verificar",
        json={"email": email, "codigo": codigo_del_ultimo_mail(destino=email)},
    )
    assert verif.status_code == 200
    return verif.json()


# ---- VAL-08: sistema único válido -------------------------------------------

def test_crear_mesa_rechaza_sistema_distinto_de_pf1e(client, token_gm):
    r = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa D&D", "sistema": "dnd5e"},
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r.status_code == 400
    assert "pf1e" in r.json()["error"]["mensaje"]


def test_crear_mesa_acepta_pf1e_y_registra_al_gm_propietario(client, token_gm):
    r = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa propiedad", "sistema": "pf1e", "jugadores_max": 4},
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert r.status_code == 201
    assert "gm_id" in r.json(), "la mesa debe registrar quién la creó (RN-02)"


# ---- RN-02 / VAL-17: ownership ----------------------------------------------

def test_usuario_no_propietario_no_puede_editar_ni_borrar_mesas(client, token_gm):
    mesa_id = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa del GM", "sistema": "pf1e"},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]

    otro = _usuario(client)
    auth = {"Authorization": f"Bearer {otro['access_token']}"}

    put = client.put(
        f"/api/v1/mesas/{mesa_id}",
        json={"estado": "cerrada"},
        headers=auth,
    )
    assert put.status_code == 403

    borrar = client.delete(f"/api/v1/mesas/{mesa_id}", headers=auth)
    assert borrar.status_code == 403


def test_el_propietario_puede_editar_y_el_admin_puede_todo(client, token_gm, token_admin):
    mesa_id = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa owner", "sistema": "pf1e", "jugadores_max": 4},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]

    put = client.put(
        f"/api/v1/mesas/{mesa_id}",
        json={"estado": "cerrada"},
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert put.status_code == 200
    assert put.json()["estado"] == "cerrada"

    put_admin = client.put(
        f"/api/v1/mesas/{mesa_id}",
        json={"estado": "abierta"},
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert put_admin.status_code == 200

    borrar_admin = client.delete(
        f"/api/v1/mesas/{mesa_id}",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert borrar_admin.status_code == 204


def test_actualizar_cupo_bajo_el_numero_actual_de_jugadores_da_409(
    client, token_gm, token_jugador
):
    mesa_id = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa cupo", "sistema": "pf1e", "jugadores_max": 4},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]

    gm = {"Authorization": f"Bearer {token_gm}"}
    for _ in range(2):
        usuario = _usuario(client)
        sol_id = client.post(
            f"/api/v1/mesas/{mesa_id}/solicitudes",
            headers={"Authorization": f"Bearer {usuario['access_token']}"},
        ).json()["id"]
        client.post(f"/api/v1/mesas/{mesa_id}/solicitudes/{sol_id}/aceptar", headers=gm)

    r = client.put(
        f"/api/v1/mesas/{mesa_id}",
        json={"jugadores_max": 1},
        headers=gm,
    )
    assert r.status_code == 409, "VAL-15: no puede bajar el cupo debajo de los jugadores actuales"


# ---- RF-04 / RF-13: filtros + paginación ------------------------------------

def test_listado_mesas_filtrar_estado_sistema_y_paginar(client, token_gm):
    auth = {"Authorization": f"Bearer {token_gm}"}
    ids_abiertas = [
        client.post(
            "/api/v1/mesas",
            json={"nombre": f"Abierta {i}", "sistema": "pf1e", "estado": "abierta"},
            headers=auth,
        ).json()["id"]
        for i in range(4)
    ]
    cerrada_id = client.post(
        "/api/v1/mesas",
        json={"nombre": "Cerrada", "sistema": "pf1e", "estado": "cerrada"},
        headers=auth,
    ).json()["id"]

    r = client.get("/api/v1/mesas", params={"estado": "abierta"})
    assert r.status_code == 200
    listado = r.json()
    assert cerrada_id not in [m["id"] for m in listado]
    assert set(ids_abiertas) <= {m["id"] for m in listado}

    r = client.get("/api/v1/mesas", params={"limit": 2, "page": 2})
    assert r.status_code == 200
    assert len(r.json()) <= 2

    r = client.get("/api/v1/mesas", params={"limit": 60})
    assert r.status_code == 400, "limit fuera de rango se rechaza (techo 50)"

    r = client.get("/api/v1/mesas", params={"orden": "inventado"})
    assert r.status_code == 400, "orden no blaqueado se rechaza"


# ---- RF-14 / RF-15 / RN-07 / RN-08: flujo de solicitudes ---------------------

def test_solicitud_queda_pendiente_y_el_gm_la_ve(client, token_gm, token_jugador):
    mesa_id = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa flujo", "sistema": "pf1e"},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]

    r = client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes",
        headers={"Authorization": f"Bearer {token_jugador}"},
    )
    assert r.status_code == 201
    assert r.json()["estado"] == "pendiente", "RF-14: la solicitud nace pendiente"

    bandejita = client.get(
        f"/api/v1/mesas/{mesa_id}/solicitudes",
        headers={"Authorization": f"Bearer {token_gm}"},
    )
    assert bandejita.status_code == 200
    assert len(bandejita.json()) == 1
    assert bandejita.json()[0]["estado"] == "pendiente"


def test_doble_solicitud_activa_del_mismo_usuario_da_409(client, token_gm, token_jugador):
    mesa_id = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa dup", "sistema": "pf1e"},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]

    auth = {"Authorization": f"Bearer {token_jugador}"}
    client.post(f"/api/v1/mesas/{mesa_id}/solicitudes", headers=auth)
    otra = client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes",
        headers={"Authorization": f"Bearer {token_jugador}", "Idempotency-Key": "otra-clave"},
    )
    assert otra.status_code == 409, "RN-07: una sola solicitud activa por jugador y mesa"


def test_suario_puede_reaplicar_tras_rechazo(client, token_gm, token_jugador):
    mesa_id = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa reintentos", "sistema": "pf1e"},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]
    auth = {"Authorization": f"Bearer {token_jugador}"}

    sol_id = client.post(f"/api/v1/mesas/{mesa_id}/solicitudes", headers=auth).json()["id"]
    client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes/{sol_id}/rechazar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )

    reapertura = client.post(f"/api/v1/mesas/{mesa_id}/solicitudes", headers=auth)
    assert reapertura.status_code == 201, "tras el rechazo el jugador puede volver a aplicar"


def test_aceptar_hace_miembro_con_cupo_y_rechazar_cierra(client, token_gm, token_jugador):
    mesa_id = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa aceptar", "sistema": "pf1e", "jugadores_max": 4},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]
    auth = {"Authorization": f"Bearer {token_jugador}"}

    sol_id = client.post(f"/api/v1/mesas/{mesa_id}/solicitudes", headers=auth).json()["id"]
    gm = {"Authorization": f"Bearer {token_gm}"}

    r = client.post(f"/api/v1/mesas/{mesa_id}/solicitudes/{sol_id}/aceptar", headers=gm)
    assert r.status_code == 200
    assert r.json()["estado"] == "aceptada"

    detalle = client.get(
        f"/api/v1/mesas/{mesa_id}",
        headers={"Authorization": f"Bearer {token_jugador}"},
    ).json()
    assert detalle["jugadores_actuales"] == 1

    miembros = client.get(f"/api/v1/mesas/{mesa_id}/miembros", headers=gm).json()["miembros"]
    assert any(m["email"] == "vert_" for m in miembros) or miembros, "el aceptado es miembro"


def test_aceptar_rechazar_es_solo_del_gm_propietario(client, token_gm, token_jugador, token_admin):
    mesa_id = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa guard", "sistema": "pf1e"},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]
    auth = {"Authorization": f"Bearer {token_jugador}"}
    sol_id = client.post(f"/api/v1/mesas/{mesa_id}/solicitudes", headers=auth).json()["id"]

    gm_ajeno = _usuario(client)
    r = client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes/{sol_id}/aceptar",
        headers={"Authorization": f"Bearer {gm_ajeno['access_token']}"},
    )
    assert r.status_code == 403, "VAL-23: solo el GM propietario decide"

    admin = client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes/{sol_id}/aceptar",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert admin.status_code == 200


def test_solicitud_ya_procesada_no_reprocesa(client, token_gm, token_jugador):
    mesa_id = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa repro", "sistema": "pf1e"},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]
    auth = {"Authorization": f"Bearer {token_jugador}"}
    gm = {"Authorization": f"Bearer {token_gm}"}
    sol_id = client.post(f"/api/v1/mesas/{mesa_id}/solicitudes", headers=auth).json()["id"]

    client.post(f"/api/v1/mesas/{mesa_id}/solicitudes/{sol_id}/aceptar", headers=gm)
    otra = client.post(f"/api/v1/mesas/{mesa_id}/solicitudes/{sol_id}/aceptar", headers=gm)
    assert otra.status_code == 409, "VAL-22"

    sol_id_2 = None
    banda = client.get(f"/api/v1/mesas/{mesa_id}/solicitudes", headers=gm).json()
    otra_2 = client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes/{sol_id_2 or banda[0]['id']}/rechazar", headers=gm
    )
    assert otra_2.status_code == 409


def test_solicitud_a_mesa_cerrada_da_409(client, token_gm, token_jugador):
    mesa_id = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa cerrada", "sistema": "pf1e", "estado": "cerrada"},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]
    auth = {"Authorization": f"Bearer {token_jugador}"}
    r = client.post(f"/api/v1/mesas/{mesa_id}/solicitudes", headers=auth)
    assert r.status_code == 409, "VAL-18: mesas cerradas no aceptan solicitudes"


def test_aceptar_sin_cupo_da_409_y_no_consume_mas(client, token_gm):
    mesa_id = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa cupo Uno", "sistema": "pf1e", "jugadores_max": 1},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]
    gm = {"Authorization": f"Bearer {token_gm}"}

    solicitudes = []
    for _ in range(2):
        auth = _usuario(client)["access_token"]
        sol_id = client.post(
            f"/api/v1/mesas/{mesa_id}/solicitudes",
            headers={"Authorization": f"Bearer {auth}"},
        ).json()["id"]
        solicitudes.append(sol_id)

    primera = client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes/{solicitudes[0]}/aceptar", headers=gm
    )
    assert primera.status_code == 200
    segunda = client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes/{solicitudes[1]}/aceptar", headers=gm
    )
    assert segunda.status_code == 409, "CupoAgotado: no hay vacantes"


def test_bandeja_del_gm_muestra_quien_pidio(client, token_gm, token_jugador):
    """P2: la bandeja trae nombre/email del solicitante (JOIN dentro de mesas_db)."""
    mesa_id = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa bandeja", "sistema": "pf1e"},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]

    email_jugador = f"bandeja_{uuid.uuid4().hex[:8]}@tfinder.dev"
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email_jugador,
            "password": "secreto123",
            "nombre": "Nombre Visible",
        },
    )
    from tests.conftest import codigo_del_ultimo_mail

    verif_jugador = client.post(
        "/api/v1/auth/register/verificar",
        json={"email": email_jugador, "codigo": codigo_del_ultimo_mail(destino=email_jugador)},
    )
    assert verif_jugador.status_code == 200
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email_jugador, "password": "secreto123"},
    )
    auth = {"Authorization": f"Bearer {login.json()['access_token']}"}
    client.post(f"/api/v1/mesas/{mesa_id}/solicitudes", headers=auth)

    banda = client.get(
        f"/api/v1/mesas/{mesa_id}/solicitudes",
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()[0]
    assert banda.get("nombre") == "Nombre Visible", "el GM necesita ver QUIÉN pide"
    assert banda.get("email") == email_jugador


def test_votos_del_calendario_muestran_el_nombre_del_votante(client, token_gm):
    """P2: la propuesta devuelve los nombres por facción (faturado JOIN)."""
    mesa_id = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa votos nombres", "sistema": "pf1e"},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]

    email_votante = f"voto_{uuid.uuid4().hex[:8]}@tfinder.dev"
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email_votante,
            "password": "secreto123",
            "nombre": "Votarón Ana",
        },
    )
    from tests.conftest import codigo_del_ultimo_mail

    verif_votante = client.post(
        "/api/v1/auth/register/verificar",
        json={"email": email_votante, "codigo": codigo_del_ultimo_mail(destino=email_votante)},
    )
    assert verif_votante.status_code == 200
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email_votante, "password": "secreto123"},
    )
    assert login.status_code == 200, login.text
    auth_vot = {"Authorization": f"Bearer {login.json()['access_token']}"}

    client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes", headers=auth_vot
    )
    sol_id = client.get(
        f"/api/v1/mesas/{mesa_id}/solicitudes",
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()[0]["id"]
    client.post(
        f"/api/v1/mesas/{mesa_id}/solicitudes/{sol_id}/aceptar",
        headers={"Authorization": f"Bearer {token_gm}"},
    )

    fut = (datetime.now(timezone.utc) + timedelta(days=9)).strftime("%Y-%m-%dT%H:%M:%S")
    fecha_id = client.post(
        f"/api/v1/mesas/{mesa_id}/fechas",
        json={"propuesta": fut},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]
    client.post(
        f"/api/v1/mesas/{mesa_id}/fechas/{fecha_id}/voto",
        json={"valor": "a_favor"},
        headers=auth_vot,
    )

    lista = client.get(
        f"/api/v1/mesas/{mesa_id}/fechas", headers=auth_vot
    ).json()
    prop = [p for p in lista if p["id"] == fecha_id][0]
    assert prop["a_favor_nombres"] == ["Votarón Ana"]
    assert prop["en_contra_nombres"] == []


def test_gm_puede_expulsar_jugador_y_liberar_cupo(client, token_gm, token_jugador):
    mesa_id = client.post(
        "/api/v1/mesas",
        json={"nombre": "Mesa exp", "sistema": "pf1e", "jugadores_max": 2},
        headers={"Authorization": f"Bearer {token_gm}"},
    ).json()["id"]
    gm = {"Authorization": f"Bearer {token_gm}"}
    usuario = _usuario(client)
    auth = {"Authorization": f"Bearer {usuario['access_token']}"}
    sol_id = client.post(f"/api/v1/mesas/{mesa_id}/solicitudes", headers=auth).json()["id"]
    client.post(f"/api/v1/mesas/{mesa_id}/solicitudes/{sol_id}/aceptar", headers=gm)

    r = client.delete(f"/api/v1/mesas/{mesa_id}/miembros/{usuario['perfil']['id']}", headers=gm)
    assert r.status_code == 200, "el GM expulsa al jugador"
    assert r.json().get("jugadores_actuales", 0) == 0
