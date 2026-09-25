# Proposal: RabbitMQ — productores, consumidores, ACK, reintentos y DLQ

## Why

Desacoplar procesos del requerimiento síncrono (criterio AE2 5): `mesas-api` publica eventos de dominio y `notif-api` los consume para notificaciones in-app, con ACK explícito, reintentos con backoff exponencial, DLQ y idempotencia por `event_id`.

## What Changes

- **Productor (root `app/infra/rabbitmq.py`)**: declara el exchange topic `tfinder.events` (durable) y publica mensajes persistentes (`delivery_mode=2`) con `event_id`, `tipo` y `correlation_id` (B10). `mesas_api/app/services/eventos.py` agrega helpers de dominio (`mesa.solicitada|aceptada|expulsada`) y `POST /api/v1/mesas/{id}/solicitar` (autenticado) dispara `mesa.solicitada` → `202` (la carrera de B06 suma la reserva de vacante después).
- **Consumidor (`notif-api`)**: `app/infra/amqp.py` declara colas `notif.mesa` (bind `mesa.*`), `notif.sesion` (`sesion.*`), `doc.pdf` (`doc.pdf.*`) con `x-dead-letter-exchange=tfinder.dlx` y la cola `dlq.general`. Consumers en threads daemon (lifespan), `prefetch_count=1`, ACK en éxito, reintento `_intentos` con backoff `2^n` hasta 3, y al agotar → `ack(requeue=False)` + mensaje a `dlq.general` + fila en `mensaje_dlq`.
- **Idempotencia**: `event_log.event_id` (índice único parcial) — un `event_id` ya procesado se ACKea sin duplicar la notificación (base de B06).
- **Adaptación del schema B02 de `notif_db`** (no se reemplazan tablas existentes): ALTER idempotente agrega `notificaciones.usuario_id` y `event_log.event_id`; nueva tabla `mensaje_dlq`. Notif expone `GET /api/v1/notificaciones`, `GET /api/v1/event-log` (ya existentes) y `GET /api/v1/dlq` (nuevo).

## Capabilities

- **New Capabilities**: `eventos-rabbitmq` — mensajería asíncrona con entrega confiable, reintentos, DLQ e idempotencia.
- **Modified Capabilities**: `observabilidad` (el producer ya inyectaba `correlation_id`; ahora el mensaje completo viaja con él al consumer).

## Impact

- `mesas-api`: se agrega endpoint `POST /mesas/{id}/solicitar` (202, encolamiento); no rompe contratos.
- `notif-api`: consumidores levantan en el mismo proceso (threads daemon); toleran broker caído con reconexión entre mensajes.
- `notif_db`: DDL aditivo (columnas nuevas opcionales), no destructivo.
- El productor raíz pasa de publish por exchange default a exchange topic durable (B05): observado solo por contenedores con el nuevo código.