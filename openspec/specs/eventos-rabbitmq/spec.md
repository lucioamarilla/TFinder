## Purpose

Define la mensajería asíncrona de TFinder AE2 con RabbitMQ (criterio AE2 5): productores que publican eventos de dominio en un exchange topic durable y consumidores en `notif-api` que materializan notificaciones, con ACK explícito, reintentos con backoff exponencial, dead-letter queue e idempotencia por `event_id`, manteniendo la correlación del recorrido (B10).

## Requirements

### Requirement: Publicación de eventos de dominio en exchange topic
El módulo compartido DEBE publicar mensajes en el exchange topic durable `tfinder.events` con `delivery_mode=2` (persistentes) y cuerpo con `event_id` (uuid), `tipo` (routing key) y `correlation_id`; `mesas-api` DEBE exponer helpers de dominio y un endpoint que publique `mesa.solicitada` respondiendo `202`.

#### Scenario: Evento de solicitud de unión
- **WHEN** un usuario autenticado solicita unirse a una mesa existente vía `POST /api/v1/mesas/{id}/solicitar`
- **THEN** el servicio responde `202 {"estado":"pendiente"}` y el mensaje `mesa.solicitada` queda en la cola `notif.mesa` con `event_id`, `mesa_id`, `usuario_id` y `correlation_id`

#### Scenario: Mensaje persistente
- **WHEN** se publica un evento y RabbitMQ recibió el publish
- **THEN** el mensaje sobrevive reinicios del broker (durable exchange/cola + `delivery_mode=2`)

### Requirement: Consumo con ACK y notificación persistida
`notif-api` DEBE consumir los eventos del exchange (colas `notif.mesa`, `notif.sesion`, `doc.pdf`) con `prefetch_count=1`, ACK explícito en éxito y, para eventos de mesa, crear una fila en `notificaciones` visible por `GET /api/v1/notificaciones`.

#### Scenario: Consumo exitoso
- **WHEN** un mensaje `mesa.solicitada` se procesa con éxito
- **THEN** se ACKea, se registra en `event_log` y `GET /api/v1/notificaciones` muestra una notificación nueva con el `usuario_id` del mensaje

#### Scenario: Reconexión y prefetch
- **WHEN** el consumidor arranca o el broker cae y vuelve
- **THEN** consume de a un mensaje por vez (`prefetch_count=1`) y continúa tras reconectar

### Requirement: Reintentos con backoff y dead-letter
El consumidor DEBE reintentar los mensajes que fallan hasta 3 intentos con backoff exponencial (`2^n` s, usando `nack + requeue`), y al agotar reintentos DEBE enrutar el mensaje a la cola `dlq.general` (y persistirlo en `mensaje_dlq` con el error), sin perder el mensaje original ni las notificaciones ya creadas.

#### Scenario: Retry con backoff
- **WHEN** el procesamiento lanza excepción en el primer intento
- **THEN** el mensaje se reintenta con contador `_intentos` creciente y espera `2^n` segundos entre reintentos, hasta 3

#### Scenario: DLQ tras agotar reintentos
- **WHEN** los 3 intentos fallan
- **THEN** el mensaje se niega con `requeue=False`, aparece en la cola `dlq.general` del panel de RabbitMQ y se persiste una fila en `mensaje_dlq` con `cola`, `payload` y `error`, visible por `GET /api/v1/dlq`

### Requirement: Idempotencia por event_id
El consumidor DEBE evitar duplicar efectos cuando un mismo `event_id` se entrega más de una vez: si `event_log` ya tiene ese `event_id`, DEBE ACKear sin crear otra notificación.

#### Scenario: Reentrega del mismo evento
- **WHEN** un mensaje con un `event_id` ya procesado se consume de nuevo
- **THEN** se ACKea y no se inserta una segunda notificación ni un segundo registro en `event_log`

### Requirement: Trazabilidad operacional de eventos
`notif-api` DEBE exponer `GET /api/v1/event-log` (eventos consumidos) y `GET /api/v1/dlq` (mensajes en dead-letter), además de `GET /api/v1/notificaciones`, como evidencia consultable del criterio 5.

#### Scenario: Auditoría del consumo
- **WHEN** se consultan los endpoints de event-log y dlq tras un flujo con reintento fallido
- **THEN** el event-log lista los eventos procesados con su `event_id`/`tipo`, y el dlq lista el mensaje fallido con su error