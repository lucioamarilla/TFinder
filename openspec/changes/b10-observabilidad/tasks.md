## 1. Logger y middleware compartidos (raíz)

- [x] 1.1 Crear `app/infra/logge.py`: `JsonFormatter`, `configurar_logger`, `logger` singleton, `nuevo_correlation_id`, `correlation_id_var` (ContextVar) y `log_record_factory` que inyecta el CID
- [x] 1.2 Crear `app/middleware/log_context.py` (ASGI): lee/genera `X-Correlation-Id`, setea ContextVar, loguea entrada/salida del request y devuelve el CID en el header de respuesta
- [x] 1.3 Agregar `app/middleware/__init__.py`

## 2. Propagación de correlación

- [x] 2.1 Agregar `publicar(routing_key, payload)` en `app/infra/rabbitmq.py` que inyecta `correlation_id` desde el ContextVar
- [x] 2.2 Verificar que el payload del mensaje lleva el CID del request

## 3. /live y /ready + middleware en los 4 servicios

- [x] 3.1 `mesas_api/main.py`: middleware, `/live`, `/ready` (Postgres/Redis/RabbitMQ)
- [x] 3.2 `builds_api/main.py`: ídem
- [x] 3.3 `feed_api/main.py`: ídem
- [x] 3.4 `notif_api/main.py`: ídem
- [x] 3.5 Logues de verificación en contenedor: `docker compose logs` con salida JSON

## 4. Verificación (done)

- [x] 4.1 `/live` 200 y `/ready` 200 con las 3 dependencias en true en los 4 servicios
- [x] 4.2 `docker stop` postgres → `/ready` 503 (`postgres:false`); restart → 200
- [x] 4.3 Correlación: request con `X-Correlation-Id: cid-test-42` a dos servicios → logs JSON de ambos con ese CID y header de respuesta idéntico
- [x] 4.4 Sin secretos en logs (grep de token/password/QR en consolas)
- [x] 4.5 `openspec validate b10-observabilidad`

## 5. Cierre de la tarea

- [x] 5.1 Rama `f/B10_observabilidad`, commit `feat(observabilidad): logs JSON con correlation_id, /live y /ready (#23)`, merge y archivar
- [x] 5.2 Cerrar issue GitHub #23