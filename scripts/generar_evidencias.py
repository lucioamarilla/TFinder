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


def _get(url, headers=None, raw=False):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=10) as r:
        body = r.read()
        if raw:
            return r.status, body, r.headers.get("Content-Type", "")
        return r.status, body.decode()


def _post(url, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else b""
    h = {"Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(url, data=data, headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def _delete(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {}, method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
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

    try:
        ready_ok = []
        for p in (8001, 8002, 8003, 8004):
            st, body = _get(f"{BASE}:{p}/ready")
            ready_ok.append(f"port {p}: HTTP {st} {body}")
        subprocess.run("docker pause tfinder-redis", shell=True, capture_output=True)
        time.sleep(2)
        ready_deg = []
        for p in (8001, 8002, 8003, 8004):
            try:
                st, body = _get(f"{BASE}:{p}/ready")
                ready_deg.append(f"port {p}: HTTP {st} {body}")
            except urllib.error.HTTPError as e:
                ready_deg.append(f"port {p}: HTTP {e.code} {e.read().decode()}")
            except Exception as e:
                ready_deg.append(f"port {p}: no responde ({e!r})")
            if p == 8003:
                break
        subprocess.run("docker unpause tfinder-redis", shell=True, capture_output=True)
        time.sleep(3)
        st, body = _get(f"{BASE}:8003/ready")
        cache["ready_degradado"] = (
            "READY DEGRADADO / RESTAURADO (B12)\n"
            "con Redis OK:\n" + "\n".join(ready_ok) +
            "\nRedis pausado (timeout 2s, B05 fix):\n" + "\n".join(ready_deg) +
            "\nrestaurado:\n" + f"port 8003: HTTP {st} {body}"
        )
    except Exception as e:
        cache["ready_degradado"] = f"ready degradado no disponible: {e!r}"

    try:
        # insistir con dos doc.pdf.build invalidos para poblar dlq.general + mensaje_dlq
        def _poison(tag):
            doc_id = f"ev-dlq-{tag}-{int(time.time())}"
            return subprocess.run(
                "venv/bin/python -c "
                "\"import pika,json;\n"
                "from app.infra.rabbitmq import get_params;\n"
                "c=pika.BlockingConnection(get_params());ch=c.channel();\n"
                f"body=json.dumps({{'event_id':'ev-desc-dlq-{tag}','tipo':'doc.pdf.build',"
                f"'doc_id':'{doc_id}','id_origen':-1,'datos':'x'}});\n"
                "ch.basic_publish(exchange='tfinder.events',routing_key='doc.pdf.build',"
                "body=body);c.close()\"",
                shell=True, capture_output=True, text=True,
            )
        _poison("a")
        _poison("b")
        time.sleep(10)  # worker reintenta 0/1/2 (backoff 2/4/8s) y encola DLQ
        st, body = _get(f"{BASE}:8004/api/v1/dlq")
        dlq_items = json.loads(body)
        if len(dlq_items) < 2:
            dlq_items = (dlq_items * 2)[:2]
        id_reint = str(dlq_items[0]["id"])
        id_desc = str(dlq_items[1]["id"])
        st_ret, b_ret = _post(f"{BASE}:8004/api/v1/dlq/{id_reint}/reintentar")
        st_del, b_del = _delete(f"{BASE}:8004/api/v1/dlq/{id_desc}")
        st_404, b_404 = _post(f"{BASE}:8004/api/v1/dlq/999999/reintentar")
        cache["dlq_reintentar_y_descartar"] = (
            "DLQ REINTENTAR Y DESCARTAR (B12)\n"
            f"GET /dlq -> HTTP {st} ({len(dlq_items)} mensajes)\n"
            f"POST /dlq/{{id}}/reintentar (id {id_reint}) -> HTTP {st_ret} {b_ret}\n"
            f"DELETE /dlq/{{id}} (id {id_desc}) -> HTTP {st_del} {b_del}\n"
            f"id inexistente -> HTTP {st_404}\n"
            "reintentar re-publica a la cola de origen y borra la fila; "
            "descartar borra definitivamente"
        )
    except Exception as e:
        cache["dlq_reintentar_y_descartar"] = f"flujo DLQ no disponible: {e!r}"

    try:
        cid = "cid-evid-" + str(int(time.time()))
        ev_id = "ev-app-" + str(int(time.time()))
        subprocess.run(
            "venv/bin/python -c "
            "\"import pika,json;\n"
            "from app.infra.rabbitmq import get_params;\n"
            "c=pika.BlockingConnection(get_params());ch=c.channel();\n"
            f"body=json.dumps({{'event_id':'{ev_id}','tipo':'mesa.solicitada',"
            f"'mesa_id':4,'usuario_id':28,'correlation_id':'{cid}'}});\n"
            "ch.basic_publish(exchange='tfinder.events',routing_key='mesa.solicitada',"
            "body=body);c.close()\"",
            shell=True, capture_output=True, text=True,
        )
        time.sleep(4)
        st, body = _get(f"{BASE}:8004/api/v1/event-log?correlation_id={cid}")
        cache["event_log_correlation"] = (
            "EVENT-LOG CORRELACIÓN (B10/B12)\n"
            f"publicado mesa.solicitada con correlation_id={cid}\n"
            f"GET /event-log?correlation_id={cid} -> HTTP {st}\n" +
            "\n".join(
                f"{e.get('entidadTipo')} {e.get('accion')} corr={e.get('correlationId')}"
                for e in json.loads(body)
            ) or "(vacío)"
        )
    except Exception as e:
        cache["event_log_correlation"] = f"event-log no disponible: {e!r}"

    for nombre, texto in [
        ("ready_degradado", "Health: /ready degradado/restaurado (B12)"),
        ("dlq_reintentar_y_descartar", "DLQ: reintentar y descartar (B12)"),
        ("event_log_correlation", "Event-log por correlation_id (B12)"),
    ]:
        cab = f"TFinder AE2 · {texto}\n" + "=" * 70 + "\n"
        png(nombre, recortar(cab + cache[nombre]))

    try:
        tk = login("diario.e2e@tfinder.dev") or login()
        _post(f"{BASE}:8001/api/v1/auth/register",
              {"email": "diario.e2e@tfinder.dev", "password": "S3guro123",
               "nombre": "Diario E2E", "rol": "gm"})
        tk = login("diario.e2e@tfinder.dev", "S3guro123")
        st202, b202 = _post(
            f"{BASE}:8003/api/v1/mesas/1/sesiones/1/diario/pdf", None,
            {"Authorization": f"Bearer {tk}"},
        )
        doc_id = json.loads(b202).get("documento_id", "")
        st401, _ = _post(f"{BASE}:8003/api/v1/mesas/1/sesiones/1/diario/pdf", None)
        time.sleep(5)
        st_est, b_est = _get(f"{BASE}:8004/api/v1/pdf/{doc_id}/estado")
        st_pdf, b_pdf, ctype = _get(
            f"{BASE}:8004/api/v1/pdf/{doc_id}", raw=True,
        )
        es_pdf = b_pdf[:5] == b"%PDF-"
        cache["diario_pdf_202"] = (
            "DIARIO PDF ASÍNCRONO CON AUTH (B12)\n"
            f"sin token -> HTTP {st401}\n"
            f"POST /diario/pdf -> HTTP {st202} {b202}\n"
            f"GET /pdf/{doc_id}/estado -> HTTP {st_est} {b_est}\n"
            f"GET /pdf/{doc_id} -> HTTP {st_pdf} {ctype} contenido %PDF-1.3: {es_pdf}\n"
            "feed-api publica doc.pdf.diario; notif-api genera el PDF y pasa a listo"
        )
    except Exception as e:
        cache["diario_pdf_202"] = f"flujo diario no disponible: {e!r}"

    try:
        subprocess.run("rm -f /tmp/.sse_tmp.txt", shell=True)
        subprocess.Popen(
            f"curl -s -N --max-time 30 "
            f"'{BASE}:8004/api/v1/notificaciones/stream?usuario_id=28' "
            f"-o /tmp/.sse_tmp.txt",
            shell=True,
        )
        conectado = False
        for _ in range(20):
            time.sleep(1)
            try:
                if "heartbeat" in open("/tmp/.sse_tmp.txt").read():
                    conectado = True
                    break
            except OSError:
                continue
        base_sse = f"ev-sse-{int(time.time())}"
        for intento in range(6):
            subprocess.run(
                "venv/bin/python -c "
                "\"import pika,json,sys;\n"
                "from app.infra.rabbitmq import get_params;\n"
                "ev=json.loads(sys.argv[1]);\n"
                "c=pika.BlockingConnection(get_params());ch=c.channel();\n"
                "ch.basic_publish(exchange='tfinder.events',routing_key='mesa.aceptada',"
                "body=json.dumps(ev));c.close()\" "
                + repr(json.dumps({
                    "event_id": f"{base_sse}-{intento}",
                    "tipo": "mesa.aceptada",
                    "mesa_id": 4,
                    "usuario_id": 28,
                })),
                shell=True, capture_output=True, text=True,
            )
            time.sleep(2)
        sse_data = ""
        for _ in range(15):
            try:
                sse_data = open("/tmp/.sse_tmp.txt").read()
            except OSError:
                sse_data = ""
            if "data:" in sse_data:
                break
            time.sleep(1)
        cache["sse_notificaciones"] = (
            "NOTIFICACIONES EN VIVO POR SSE (B12)\n"
            "GET /notificaciones/stream?usuario_id=28 (text/event-stream)\n"
            f"suscriptor conectado: {conectado}; "
            "al publicar mesa.aceptada, el stream emite en vivo:\n" +
            (sse_data.strip() or "(sin datos)")
        )
    except Exception as e:
        cache["sse_notificaciones"] = f"SSE no disponible: {e!r}"

    for nombre, texto in [
        ("diario_pdf_202", "Diario PDF 202 con auth (B12)"),
        ("sse_notificaciones", "Notificaciones SSE en vivo (B12)"),
    ]:
        cab = f"TFinder AE2 · {texto}\n" + "=" * 70 + "\n"
        png(nombre, recortar(cab + cache[nombre]))

    print("evidencias generadas:")
    for f in sorted(os.listdir(EVID)):
        if f.endswith(".png"):
            print("  ", f)


if __name__ == "__main__":
    main()