# Proposal: Admin con evidencia real — observabilidad, DLQ y broker

## Why

Tres vistas admin estaban mockeadas. Ahora leen datos reales:
- `AdminObservabilidadView`: `/live` y `/ready` de los 4 servicios (verde/ocre/gris) + logs del `event-log` con `correlation_id` filtrando por recorrido.
- `AdminDlqView`: `GET /api/v1/dlq` real (payload + error + reintentos); "Reintentar" reencola a la cola original (publish con mismo event_id → idempotente) y "Descartar" elimina.
- `AdminResilienciaView`: breaker derivado del `/ready` real (pg/redis/rabbitmq) + conteo de DLQ; "Simular caída" → "Verificar broker".

## What Changed

- **Backend `notif-api`** (aditivo):
  - `PATCH /api/v1/notificaciones/{id}/leida` (F08) y ahora rutas DLQ: `GET /api/v1/dlq` (router), `POST /api/v1/dlq/{id}/reintentar` (republica en `tfinder.events` con routing por `tipo` y elimina el registro; idempotente por `event_id`), `DELETE /api/v1/dlq/{id}`.
  - `event-log` acepta `?correlation_id=` y expone `correlationId` en `EventOut`; columna `correlation_id` aditiva con índice; todos los consumers/workers pasan el CID del mensaje.
- **`src/api/endpoints.js`**: `adminApi` (live/ready por servicio, dlq, eventLog con cid, reintentarDlq, descartarDlq).
- **`src/services/admin.js`**: `getObservabilidad()`, `getDlq()`/`reintentarMensaje`/`descartarMensaje`/`drenarCola`, `getResiliencia()`/`simularCaida()` reales; `getResiliencia` suma `estadoBroker`, `broker`, `dlqTotal`.
- **Vistas**: `AdminObservabilidadView` (tono gris, detalle de dependencias, filtrar logs por CID), `AdminDlqView` (columna motivo, payload real con cid, inspección sin toast simulado, colspan 5), `AdminResilienciaView` (breaker + chips pg/redis/rabbitmq + DLQ en cola + botón "Verificar broker").

## Impact

- DLQ real verificado: evento `mesa.desconocido` → 3 reintentos (backoff 2s/4s/8s) → `dlq.general`; reintentar devuelve 200 `{ok,id,cola}` (reencola); descartar borra; 404 si no existe.
- Observabilidad: con Redis detenido, `mesas-api /ready` → `{estado:'degradado', dependencias:{redis:false}}` (panel ámbar); al restaurar vuelve a `listo`.
- CID punta a punta: recorrido de solicitud → `event-log` con `correlationId` real de 16 hex; filtro `?correlation_id=` devuelve ese evento.
- Sin cambios de esquema disruptivos: migraciones aditivas/idempotentes (`ALTER TABLE ... ADD COLUMN IF NOT EXISTS`).