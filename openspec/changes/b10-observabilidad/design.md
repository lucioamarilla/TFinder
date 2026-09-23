# Design: Observabilidad base

## Context

B02/B05 ya proveyeron `app/infra/logge.py` (JSON + ContextVar), `app/middleware/log_context.py` (header → ContextVar → respuesta) y `app/infra/ready.py` (postgres+redis+rabbitmq). B05 propagó `correlation_id` en los mensajes (`publicar`) y en el consumidor. B10 formaliza y verifica, sin rediseñar.

## Decisions

**D1 — Logger JSON compartido (ya existe).**
`JsonFormatter.format()` arma `{ts, nivel, servicio, mensaje, correlation_id}` usando primer el `extra` del record y, si falta, el `ContextVar`. Un `StreamHandler` único por servicio (helper `configurar_logger`).

**D2 — Middleware ASGI (ya existe).**
`CorrelationMiddleware` lee `x-correlation-id` (o genera `uuid4().hex[:16]`), setea el `ContextVar` (así `publicar()` toma el CID del request), loguea "request iniciado/finalizado" y replica el header en la respuesta. `log_record_factory` no hace falta: los logs dentro del request caen en el ContextVar.

**D3 — Propagación vía eventos (ya existe).**
`app/infra/rabbitmq.publicar()` usa `correlation_id or correlation_id_var.get()`. `_base.consumir()/_manejar()` de notif hace `correlation_id_var.set(cid)` y loguea "evento procesado" con `extra={"correlation_id": cid}` → correlación request→evento→consumidor.

**D4 — `/ready` multi-dependencia (ya existe).**
`evaluar_ready(conectarse_db)`: postgres (pool propio de cada `*_db`), redis (`ping()`), rabbitmq (conexión pika) → `200 listo` o `503 degradado`. `/live` responde `{"estado": "vivo"}` sin chequear nada.

**D5 — No imprimir secretos.**
Los logs loguean structuretas/IDs; nunca el body del request, tokens ni `qr_data` completo (B07/B09 ya respetan esto). Este change lo confirma en spec.

## Risks

- **Ambiente degradado**: si un servicio de dependencia cae, `/ready` 503 puede hacer que healthchecks externos lo marquen caído; es el comportamiento deseado (degradado ≠ muerto, `/live` sigue 200).

## Migration Plan

1. Confirmar presencia de logge/middleware/ready en los 4 mains (+ `/live`/`/ready`).
2. Verificación punta a punta con `X-Correlation-Id` (solicitud → mesas → notif).
3. Verificación `/ready` 200 y 503 (detener postgres transitoriamente).
4. Rama, commit, merge, archivar, cerrar #23.

## Verification

- `curl -H "X-Correlation-Id: cid-test-42" localhost:8001/api/v1/mesas` → logs mesas con cid-test-42, header replicado.
- `POST /mesas/7/solicitar` con CID → `publicar` con ese CID; consumidor notif "evento procesado" con el mismo CID (≥3 logs, 2 servicios).
- `/live` 200 y `/ready` 200 en los 4 (8001–8004) con todo sano; `/ready` 503 con postgres detenido; `/live` sigue 200.
- Salida de logs en JSON (captura para Portafolio).