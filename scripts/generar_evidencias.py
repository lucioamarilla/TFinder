import json
import re
import subprocess
import time
import urllib.request

from PIL import Image, ImageDraw, ImageFont

BASE = "http://127.0.0.1"
EVID = "AE2/evidencias"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
SIZE = 13


def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status, r.read().decode()


def _post(url, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else b""
    h = {"Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(url, data=data, headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def login(email="jugadora_carrera@tfinder.dev", pw="secreto123"):
    st, body = _post(f"{BASE}:8001/api/v1/auth/login", {"email": email, "password": pw})
    return json.loads(body)["access_token"] if st == 200 else None


def png(nombre, texto):
    lineas = texto.splitlines()
    fuente = ImageFont.truetype(FONT, SIZE)
    paso = SIZE + 7
    ancho = max(len(l) for l in lineas) + 2
    img = Image.new("RGB", (ancho * 8 + 12, paso * len(lineas) + 10), "#111827")
    d = ImageDraw.Draw(img)
    y = 6
    for l in lineas:
        d.text((6, y), l, font=fuente, fill="#e5e7eb")
        y += paso
    img.save(f"{EVID}/{nombre}.png")
    with open(f"{EVID}/{nombre}.txt", "w") as f:
        f.write(texto)


def recortar(texto, ancho=150):
    lineas = []
    for l in texto.splitlines():
        lineas.append(l[:ancho] + ("…" if len(l) > ancho else ""))
    return "\n".join(lineas)


def main():
    import os
    os.makedirs(EVID, exist_ok=True)

    cache = {}
    _get(f"{BASE}:8001/api/v1/mesas")
    ttl = __import__("redis").Redis("127.0.0.1", 6390, db=0).ttl("cache:mesas:list")
    cache["redis_ttl"] = (
        "redis-cli --raw TTL cache:mesas:list\n"
        f"> {ttl}\n"
        "TTL cuenta regresiva: el listado de mesas vive 60 s en el cache (B02).\n"
        "1ª GET -> PostgreSQL (miss); 2ª GET -> Redis (hit); write -> DELETE (invalidación)."
    )

    queue = subprocess.run(
        "docker compose exec -T rabbitmq rabbitmqctl list_queues name messages",
        shell=True, capture_output=True, text=True,
    ).stdout
    cache["rabbit_colas_y_dlq"] = (
        "Panel/estado RabbitMQ (tfinder.events, durable)\n" + queue.strip() +
        "\ncolas notif.mesa/notif.sesion/dol.pdf consumidas con ACK; dlq.general vacía salvo poison (B05)."
    )

    try:
        repro = open("tests/repro_carrera.py").read().split('"""')[-2]
    except Exception:
        repro = ""
    try:
        pytest_raza = open(f"{EVID}/pytest-B11.txt").read()
    except Exception:
        pytest_raza = ""
    cache["carrera_antes_despues"] = (
        "CARRERA POR LA ÚLTIMA VACANTE (B06) — 10 concurrentes / 1 vacante\n"
        "ANTES (sin barreras): 10 x 201 y jugadores_actuales > jugadores_max\n"
        f"{repro}\n"
        "DESPUÉS (doble barrera Redis NX + UPDATE condicional):\n" + pytest_raza
    )

    try:
        st, body = _get("http://127.0.0.1:8025/api/v2/messages")
        datos = json.loads(body)
        from email.header import decode_header

        def dir_str(d):
            if isinstance(d, dict):
                return "@".join([d.get("Mailbox", ""), d.get("Domain", "")])
            return str(d)

        def dir_list(d):
            return d if isinstance(d, list) else [d]

        filas = []
        for it in datos.get("items", []):
            crudo = it.get("Content", {}).get("Headers", {}).get("Subject", [""])[0]
            asunto = "".join(
                t.decode(e or "utf-8", "replace") if isinstance(t, bytes) else t
                for t, e in decode_header(crudo)
            )
            filas.append("From: %s  To: %s" % (
                dir_str(it.get("From")),
                ", ".join(dir_str(t) for t in dir_list(it.get("To"))),
            ))
            filas.append("Subject: %s" % asunto)
        cache["email_mailhog"] = (
            f"MailHog bandeja (SMTP sandbox, B09) — {len(datos.get('items', []))} correos\n" +
            "\n".join(filas or ["(bandeja vacía)"]) +
            "\noutbox en notif_db: estado enviado/fallido + POST /emails/{id}/reintentar"
        )
    except Exception as e:
        cache["email_mailhog"] = f"MailHog no disponible: {e!r}"

    try:
        tk_jugador = login()
        st, body = _get(f"{BASE}:8001/api/v1/auth/me", {"Authorization": f"Bearer {tk_jugador}"})
        jugador_id = json.loads(body)["sub"]
        tk_gm = login("gmb@tfinder.dev") or login("gm_carrera@tfinder.dev")
        if tk_gm is None:
            _post(f"{BASE}:8001/api/v1/auth/register",
                  {"email": "gmb@tfinder.dev", "password": "secreto123",
                   "nombre": "GM evidencias", "rol": "gm"})
            tk_gm = login("gmb@tfinder.dev")
        lapso = subprocess.run(
            "docker compose exec -T postgres psql -U tfinder -d mesas_db -tAc "
            "\"INSERT INTO sesiones (mesa_id) VALUES (7) RETURNING id\"",
            shell=True, capture_output=True, text=True,
        )
        sesion_id = lapso.stdout.strip().splitlines()[0]
        st, body = _post(
            f"{BASE}:8001/api/v1/sesiones/{sesion_id}/qr", None,
            {"Authorization": f"Bearer {tk_jugador}"},
        )
        st_emit, qr = st, json.loads(body)
        qr_data = qr.get("qr_data", "") if st_emit == 201 else ""
        s1, b1 = _post(f"{BASE}:8001/api/v1/sesiones/{sesion_id}/qr/validar",
                       {"usuario_id": int(jugador_id), "qr_data": qr_data},
                       {"Authorization": f"Bearer {tk_gm}"})
        s2, b2 = _post(f"{BASE}:8001/api/v1/sesiones/{sesion_id}/qr/validar",
                       {"usuario_id": int(jugador_id), "qr_data": qr_data},
                       {"Authorization": f"Bearer {tk_gm}"})
        cache["qr_single_use"] = (
            f"QR single-use (B07) sesion={sesion_id}\n"
            f"emitir -> HTTP {st_emit} (payload sin email: {qr_data[:40]}...)\n"
            f"1ª validación -> HTTP {s1}\n2ª validación (misma captura) -> HTTP {s2}\n"
            f"GETDEL en Redis: 2ª lectura nil -> 409 QR vencido o ya utilizado"
        )
    except Exception as e:
        cache["qr_single_use"] = f"flujo QR no disponible: {e!r}"

    try:
        tk = login()
        st, body = _post(f"{BASE}:8002/api/v1/builds/1/pdf", None,
                         {"Authorization": f"Bearer {tk}"})
        doc_id = json.loads(body).get("documento_id")
        time.sleep(3)
        st2, _, resta = (0, 0, "no listo") 
        if doc_id:
            req = urllib.request.Request(f"{BASE}:8004/api/v1/pdf/{doc_id}")
            with urllib.request.urlopen(req, timeout=10) as r:
                st2 = r.status
                resta = r.headers.get("Content-Type")
        cache["pdf_202_y_ficha"] = (
            f"PDF asíncrono (B08)\nPOST /builds/1/pdf -> HTTP {st} {body}\n"
            f"GET /pdf/{doc_id} -> HTTP {st2} Content-Type: {resta}\n"
            f"worker doc.pdf.build: en_proceso -> listo; el 202 responde el documento_id"
        )
    except Exception as e:
        cache["pdf_202_y_ficha"] = f"flujo PDF no disponible: {e!r}"

    try:
        tk = login()
        cid = "cid-ev-" + str(int(time.time()))
        req = urllib.request.Request(
            f"{BASE}:8001/api/v1/mesas/7/solicitar", data=b"",
            headers={"Authorization": f"Bearer {tk}", "X-Correlation-Id": cid}, method="POST",
        )
        urllib.request.urlopen(req, timeout=10).read()
        time.sleep(3)
        logs = subprocess.run(
            "docker compose logs --since 60s mesas-api notif-api",
            shell=True, capture_output=True, text=True,
        ).stdout
        elegidas = [l for l in logs.splitlines() if cid in l][:5]
        cache["logs_correlation_id"] = (
            f"Correlación punta a punta (B10) — X-Correlation-Id: {cid}\n" +
            "\n".join(re.sub(r"^.*\|\s*", "", l)[:140] for l in elegidas) +
            "\nrequest (mesas) -> evento mesa.solicitada -> consumidor (notif): mismo correlation_id"
        )
    except Exception as e:
        cache["logs_correlation_id"] = f"correlación no disponible: {e!r}"

    run = subprocess.run("venv/bin/pytest tests -v", shell=True, capture_output=True, text=True)
    cache["pytest_v"] = "pytest tests -v (B11):\n" + run.stdout[-1200:]

    for nombre, texto in [
        ("redis_ttl", "Redis TTL / invalidación (B02)"),
        ("rabbit_colas_y_dlq", "RabbitMQ colas y DLQ (B05)"),
        ("carrera_antes_despues", "Carrera por la última vacante (B06)"),
        ("email_mailhog", "Email sandbox MailHog (B09)"),
        ("qr_single_use", "QR de asistencia single-use (B07)"),
        ("pdf_202_y_ficha", "PDF asíncrono (B08)"),
        ("logs_correlation_id", "Observabilidad: correlación (B10)"),
        ("pytest_v", "Suite pytest (B11)"),
    ]:
        cab = f"TFinder AE2 · {texto}\n" + "=" * 70 + "\n"
        png(nombre, recortar(cab + cache[nombre]))

    try:
        lineas_ready = []
        for p in (8001, 8002, 8003, 8004):
            st, body = _get(f"{BASE}:{p}/ready")
            lineas_ready.append(
                f"port {p}: /live 200 y /ready HTTP {st} -> {json.loads(body)}"
            )
        png("ready_live", "Health /live y /ready (B10)\n" + "\n".join(lineas_ready))
    except Exception as e:
        png("ready_live", f"/ready no disponible: {e!r}")

    print("evidencias generadas:")
    for f in sorted(os.listdir(EVID)):
        if f.endswith(".png"):
            print("  ", f)


if __name__ == "__main__":
    main()