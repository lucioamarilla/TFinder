# Design: RabbitMQ — productores, consumidores, ACK, reintentos y DLQ

## Context

B01 dejó RabbitMQ levantado (host 5673 / interno `rabbitmq:5672`, `get_params()`). B10 agregó `app.infra.rabbitmq.publicar()` con `correlation_id` pero publishing a exchange default. `notif_api` ya tiene rutas/consultas a `notificaciones` y `event_log` con el shape AE1 de B02. Este change arma la mensajería real de extremo a extremo.

## Decisions

**D1 — Publisher genérico en `app/infra/rabbitmq.py`.**
`publicar(routing_key, payload)` declara (idempotente) el exchange topic durable `tfinder.events`, arma `{event_id: uuid4().hex, tipo: routing_key, correlation_id, **payload}` y publica con `delivery_mode=2`. Un solo productor compartido sirve a los 4 servicios (mesas hoy, feed/builds en B08/B09).

**D2 — Helpers de dominio y trigger en `mesas-api`.**
`mesas_api/app/services/eventos.py` envuelve al publicador con `publicar_solicitud/aceptacion/expulsion`. `POST /api/v1/mesas/{id}/solicitar` (401 sin token, 404 si la mesa no existe) publica `mesa.solicitada` y responde `202`. La **carrera por la última vacante y la reserva** (B04 ya deja el helper `reservar`) se integran en B06; aquí el endpoint solo encola.

**D3 — Colas, DLX y bindings en `notif-api/app/infra/amqp.py`.**
Una cola durable por flujo, cada una con `x-dead-letter-exchange=tfinder.dlx` (dead-letter nativa como respaldo) y bind en el topic: `notif.mesa←mesa.*`, `notif.sesion←sesion.*`, `doc.pdf←doc.pdf.*`. `dlq.general` durable consumible desde el panel (15673) para evidencia. `declarar()` es idempotente (los consumers y los producers lo llaman sin riesgo).

**D4 — Reintentos modelados en el payload (no TTL-por-mensaje).**
El callback lleva `_intentos` en el mensaje: suma 1, procesa; en excepción, si `_intentos >= 3` → `ack(requeue=False)` + publica a `dlq.general` + guarda en `mensaje_dlq`; si no → `nack(requeue=True)` tras `time.sleep(2**n)`. Backoff exponencial sencillo de explicar (mismo criterio del issue). El broker no duplica: solo re-entrega el mismo mensaje.

**D5 — Idempotencia por `event_id` con índice único parcial.**
`event_log` (tabla existente) suma columna `event_id VARCHAR(64)` y un índice único parcial `WHERE event_id IS NOT NULL`. `registrar_evento` inserta el `event_id`; `evento_ya_procesado` lo consulta antes de crear la notificación. Si ya existe → ACK y no se duplica (B06 extiende este patrón en `mesas_db`).

**D6 — Adaptación aditiva del DDL B02 (no reemplazo).**
`schema.sql` de notif agrega `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` (`notificaciones.usuario_id BIGINT`, `event_log.event_id VARCHAR`) y `CREATE TABLE IF NOT EXISTS mensaje_dlq`. `init_db` divide por `;` y ejecuta; el DDL es idempotente para revisar en reinicios.

**D7 — Consumers en threads daemon del lifespan.**
`notif_api/main.py` arranca un thread daemon por consumer (mesa, sesion). `prefetch_count=1`, ACK manual (`basic_consume` sin auto_ack → `callback` con `ch.basic_ack`). Si el broker cae, el thread muere con el proceso; los mensajes quedan encolados en el broker (durables) y se consumen al reiniciar el servicio.

**D8 — Notificaciones mapeadas al shape existente.**
`guardar_notificacion(usuario_id, titulo, detalle, entidad, enlace)` inserta en las columnas AE1: `mensaje=titulo`, `usuario_id`, `entidad`, `detalle`, `enlace` (JSONB). Mantiene compatibilidad con `NotificacionOut` y la UI.

## Risks

- **Mensajes de los flows que no tienen consumer aún** (`sesion.*`, `doc.pdf.*` se procesan en B08/B09): la cola los acumula (durable), sin pérdida.
- **Backoff dentro del callback bloquea el hilo**: aceptable en un solo consumer por cola; `prefetch=1` evita re-prefetch.
- **Duplicados entre reintento y DLQ**: el envío a DLQ ocurre solo en el último intento (3), con `ack` previo de la clave de entrega.
- **`event_id` nulo en filas históricas**: el índice parcial lo excluye; los consumos nuevos siempre llevan `event_id`.

## Migration Plan

1. `app/infra/rabbitmq.py`: exchange topic durable + publish persistente con `event_id`.
2. `mesas_api/app/services/eventos.py` + ruta `POST /mesas/{id}/solicitar`.
3. `notif_api/app/infra/amqp.py` (exchanges/colas/DLX), `models/notif.py` (DB helpers), `consumers/mesa.py` + `consumers/sesion.py`, threads en lifespan, ruta `GET /api/v1/dlq`, DDL aditivo.
4. Verificación: notificación creada + event-log, idempotencia (re-publicar mismo event_id), DLQ (matando Postgres), panel RabbitMQ, `openspec validate`.
5. Rama `f/B05_rabbitmq_eventos`, commit, merge, archivar, cerrar #18.

## Verification

- `POST /api/v1/mesas/{id}/solicitar` → `202`; `GET /api/v1/notificaciones` muestra la notificación (mesas-api + notif-api).
- `GET /api/v1/event-log` registra el `event_id` consumido.
- Re-publicar el mismo `event_id` (cliente de prueba) → sin duplicados.
- Con Postgres detenido, el consumidor falla → reintenta 3 veces → mensaje en `dlq.general` (panel 15673) y en `GET /api/v1/dlq`.
- Panel RabbitMQ con colas `notif.mesa`, `notif.sesion`, `doc.pdf`, `dlq.general` (colas vacías/procesadas).
- `openspec validate b05-rabbitmq-eventos` válido.