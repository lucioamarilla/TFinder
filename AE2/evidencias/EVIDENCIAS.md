# Evidencias AE2

Índice: criterio del enunciado → archivo de captura. Cada `.png` tiene su `.txt` con el texto renderizado (para revisión rápida) y fue generada contra el sistema en ejecución (B12).

| Criterio | Archivo | Qué muestra |
| -------- | ------- | ----------- |
| 6 · Redis TTL / invalidación | `redis_ttl.png` | `TTL cache:mesas:list = 60` cuenta regresiva; 1ª GET→PostgreSQL, 2ª GET→Redis, write→DELETE |
| 5 · RabbitMQ colas y DLQ | `rabbit_colas_y_dlq.png` | Colas `notif.mesa`, `notif.sesion`, `doc.pdf`, `dlq.general` (0 mensajes), persistentes |
| 7 · Concurrencia carrera | `carrera_antes_despues.png` | Bug sin barreras vs `pytest test_carrera`: 10 concurrentes / 1 vacante → 1×201 y 9×409 |
| 9 · Email sandbox | `email_mailhog.png` | MailHog `8025`: `noreply@tfinder.local → jugadora_carrera@tfinder.dev`, asunto "TFinder · Sesión confirmada"; outbox con reintento |
| 9 · QR single-use | `qr_single_use.png` | Emitir 201 → 1ª validación 200 → 2ª validación 409 (GETDEL, sin email en payload) |
| 9 · PDF asíncrono | `pdf_202_y_ficha.png` | `POST /builds/1/pdf → 202` con `documento_id`; `GET /pdf/{id} → 200 application/pdf` |
| 8 · Observabilidad / correlación | `logs_correlation_id.png` | `X-Correlation-Id: cid-ev-…` en 3 logs de 2 servicios (request mesas → evento → consumidor notif) |
| 13 · Salud | `ready_live.png` | `/ready` 200 en los 4 servicios con postgres/redis/rabbitmq listos; `/live` 200 |
| 13 · Reproducibilidad | `pytest_v.png` | `pytest tests -v` → 5 passed (cache, carrera, idempotencia, QR, DLQ) |

## Cómo regenerar

```bash
venv/bin/python scripts/generar_evidencias.py   # requiere infra arriba (compose) y MailHog
```

El script genera todos los `.png`/`.txt` de esta carpeta contra los servicios en ejecución.