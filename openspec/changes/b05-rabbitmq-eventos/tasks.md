## 1. Productor (root + mesas-api)

- [x] 1.1 `app/infra/rabbitmq.py`: `publicar` con exchange topic `tfinder.events` durable, `delivery_mode=2`, `event_id` + `tipo` + `correlation_id`
- [x] 1.2 `mesas_api/app/services/eventos.py`: `publicar_solicitud/aceptacion/expulsion`
- [x] 1.3 Ruta `POST /api/v1/mesas/{id}/solicitar` (auth; 404 si no existe; responde 202 y publica `mesa.solicitada`)

## 2. Colas, DLX y DDL (notif-api)

- [x] 2.1 `notif_api/app/infra/amqp.py`: exchange `tfinder.events`, DLX `tfinder.dlx`, colas `notif.mesa`(mesa.*), `notif.sesion`(sesion.*), `doc.pdf`(doc.pdf.*), `dlq.general`; `declarar()` idempotente
- [x] 2.2 DDL aditivo en `notif_api/app/schema.sql`: `notificaciones.usuario_id`, `event_log.event_id` + índice único parcial, tabla `mensaje_dlq`
- [x] 2.3 `notif_api/app/models/notif.py`: `evento_ya_procesado`, `registrar_evento`, `guardar_notificacion`, `guardar_dlq`

## 3. Consumidores

- [x] 3.1 `notif_api/app/consumers/mesa.py`: callback con ACK / reintento (3, backoff 2^n) / DLQ (ack requeue=False + `dlq.general` + `mensaje_dlq`)
- [x] 3.2 `notif_api/app/consumers/sesion.py`: procesa `sesion.confirmada` y `sesion.diario_publicado` (mismo patrón)
- [x] 3.3 Threads daemon de consumers en `notif_api/main.py` (lifespan) + ruta `GET /api/v1/dlq`

## 4. Verificación (done)

- [x] 4.1 `POST /mesas/1/solicitar` → 202; notificación creada y visible; `event-log` con el `event_id`
- [x] 4.2 Idempotencia: re-entregar el mismo `event_id` no duplica notificación ni event_log
- [x] 4.3 DLQ: parar Postgres → 3 reintentos → mensaje en `dlq.general` (panel) y en `GET /api/v1/dlq`; restart
- [x] 4.4 Panel RabbitMQ: colas `notif.mesa`, `notif.sesion`, `doc.pdf`, `dlq.general` visibles (evidencia)
- [x] 4.5 `openspec validate b05-rabbitmq-eventos`

## 5. Cierre de la tarea

- [x] 5.1 Rama `f/B05_rabbitmq_eventos`, commit `feat(eventos): RabbitMQ productores/consumidores con ACK, reintentos y DLQ (#18)`, merge y archivar
- [x] 5.2 Cerrar issue GitHub #18