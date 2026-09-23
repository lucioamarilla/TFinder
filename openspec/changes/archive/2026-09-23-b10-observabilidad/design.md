# Design: Observabilidad base — logs JSON + correlación + /live /ready

## Context

B02 dejó 4 servicios con `app/infra` compartido (raíz, copiado a cada imagen) y pools de Postgres propios por servicio (`{SVC}_DATABASE_URL`, fallback `DEFAULT_DATABASE_URL`). Los logs hoy son texto plano de uvicorn/logging por defecto, sin correlación.

## Decisions

**D1 — Logger compartido en `app/infra/logge.py`.**
Mismo patrón de `redis.py`/`rabbitmq.py` (módulo raíz importado como `app.infra.*`, un proceso por servicio → singleton válido). `JsonFormatter` serializa `ts` (ms epoch), `nivel`, `servicio` (de `SERVICIO`, default `tfinder`), `mensaje` y `correlation_id`.

**D2 — Correlación con `ContextVar` + `log_record_factory`.**
En vez de esparcir `extra={...}` en cada call-site, `correlation_id_var` vive en `logge.py` y el factory del `logging` inyecta el CID en todo record de forma acopladística. El logger general (`app.infra.logge.logger`) y los de dominio emiten con el CID automáticamente.

**D3 — Middleware ASGI en `app/middleware/log_context.py`.**
Lee `X-Correlation-Id`, genera uno (16 hex) si falta, setea el `ContextVar`, loguea entrada (`request {método} {path}`) y salida, y deja el CID en el header de respuesta (mismo nombre). Respeta scopes no-HTTP.

**D4 — Propagación a mensajes en `app/infra/rabbitmq.py`.**
Se agrega `publicar(routing_key, payload)` que arma el cuerpo con `correlation_id` tomado del `ContextVar` (típicamente el del request que dispara el evento). B05 agrega ACK/DLQ/reintentos; aquí queda la semántica de correlación del evento.

**D5 — `/live` y `/ready` en cada `main.py`.**
`/live`: `200 {"estado":"vivo"}` sin tocar dependencias. `/ready`: chequea (a) pool Postgres propio (`get_pool().connection()`, `SELECT 1`), (b) `get_redis().ping()`, (c) conexión `pika.BlockingConnection(get_params())` con cierre inmediato. `200` solo si las tres OK; `503` si alguna falla, con el detalle por dependencia. Excepciones por dependencia capturadas individualmente.

**D6 — Sin datos sensibles.**
El middleware/usuario solo loguea método/path/status/CID. No se loguean bodies de auth ni tokens (B03 ya no los imprime; se mantiene).

## Risks

- **Factory global del logging**: se setea una vez por proceso (un servicio por proceso); impacto bajo y acotado.
- **Chequeos de `/ready`**: abren conexiones a 3 sistemas por consulta; es por demanda y sin TTL destructivo.
- **Cambio de formato de logs**: visible solo para el operador; no toca API ni clientes.
- **B05 completa el recorrido evento→consumer**: en B10 la propagación (request→evento) queda lista; el consumo con CID en `event-log` se evidencia en B05.

## Migration Plan

1. `app/infra/logge.py` + `app/middleware/log_context.py` (raíz compartida).
2. `publicar` con CID en `app/infra/rabbitmq.py`.
3. En cada `main.py`: importar middleware (`app.add_middleware` o wrapper), registrar `/live` y `/ready`, loguear startup.
4. Verificar: `/live`/`/ready` (200; parando `postgres` → 503), logs JSON con CID propagado entre 2 servicios, sin secretos.
5. `git`: rama `f/B10_observabilidad`, commit, merge AE2-Backend, archivar change, cerrar #23.

## Verification

- `curl localhost:800X/live` → 200; `/ready` → `{"estado":"listo",...,postgres/redis/rabbitmq:true}`.
- `docker stop tfinder-postgres` → `/ready` 503 con `postgres:false`; `docker start` → 200.
- `curl -H "X-Correlation-Id: cid-test-42" <servicio>/api/...` → logs JSON con `"correlation_id":"cid-test-42"` en ≥2 servicios y header de respuesta con el mismo CID.
- Revisar consola: líneas JSON, sin token/password/QR.
- `openspec validate b10-observabilidad` válido.