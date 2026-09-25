# ADR-003 · RabbitMQ topic con DLQ, ACK, reintentos con backoff e idempotencia del consumidor

- Estado: **Aceptado**
- Fecha: 2026-09-23

## Contexto

El matchmaking publica eventos (`mesa.solicitada`, `mesa.aceptada`, `mesa.expulsada`) que notif-api consume, y `doc.pdf.build` une builds-api con el worker de PDF. Se necesitaba un bus con entrega durable, acuse explícito, reintento ante fallos transitorios y protección contra duplicados (entrega at-least-once + problemas de conexión pueden entregar dos veces).

## Decisión

**RabbitMQ 3.13** con:

- **Exchange topic durable `tfinder.events`** + colas persistentes de routing específico (`mesa.*`/`sesion.*` → `notif.mesa`/`notif.sesion`, `doc.pdf.*` → `doc.pdf`).
- **Persistencia**: `delivery_mode=2` en los mensajes; **ACK explícito** (`basic_ack`; sin `auto_ack`).
- **Reintentos con backoff 2^n**: ante excepción, se `basic_ack` el original y se re-publica el mismo mensaje con `_intentos += 1` (persistido en el body, no en headers), hasta `MAX_REINTENTOS = 3`.
- **DLQ `dlq.general`**: tras agotar reintentos, `basic_ack` + reenvío a `dlq.general` con `ultimo_error` y `cola_origen`, más registro en tabla `mensaje_dlq` (B05).
- **Idempotencia del consumidor (B05/B06)**: cada evento lleva `event_id` único; el consumidor persiste `(cola, event_id)` en `event_log` y descarta duplicados ACK sin reprocesar.
- **_manejar** como función compartida: `json.loads`, contexto de `correlation_id` (B10), dispatch por `tipo`, fallo de tipo → ValueError → reintento/DLQ.

## Consecuencias

- **Positivas**: entrega durable y trazable; fallos transitorios no pierden eventos (se reponen con backoff); mensajes maliciosos/incompatibles quedan aislados en DLQ sin bloquear el consumidor; panel de gestión en `15673`.
- **Negativas**: los duplicados de reintento requieren ACK+republicado (el `nack(requeue=True)` de pika re-encola la copia original sin persistir cambios); el DLQ consume espacio si no se monitorea; exige mantener coherentes `event_log` y el routing por `tipo` al agregar eventos.