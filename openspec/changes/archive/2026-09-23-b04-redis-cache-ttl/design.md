# Design: Redis — caché, TTL de llamado abierto y reserva de vacante

## Context

`mesas-api` ya usa Redis para sesiones JWT (B03) vía `app/infra/redis.py` (B01). Este issue agrega dos usos más (criterio AE2 6) manteniendo PostgreSQL (`mesas_db`) como fuente de verdad: cache-aside del listado de mesas y estado efímero del matchmaking.

## Decisions

**D1 — Cache-aside con invalidación explícita.**
`GET /api/v1/mesas` consulta `cache:mesas:list`; hit → devuelve el JSON cacheado; miss → lee `mesas_db`, `SETEX` 60 s y devuelve. Toda mutación de mesa llama `invalidar_listado()`. TTL 60 s acota el staleness ante fallos de invalidación; la invalidación evita servir datos viejos tras un write (write-through coherente).

**D2 — La caché guarda la lista serializada, no objetos.**
Se almacena `json.dumps` de la lista de mesas (la misma estructura del contrato). Al deserializar en hit se devuelve tal cual; no participa de la serialización de FastAPI (sin `response_model` en ese path de cache).

**D3 — El TTL del llamado cierra el estado sin jobs.**
`llamado:{mm_id}` con `SETEX` 120 s. `estado_llamado` lee `EXISTS`/`TTL`. La expiración nativa de Redis produce el estado `cerrado` automáticamente. Nada de CRON ni workers.

**D4 — El llamado se persiste en `mesas_db.matchmaking`.**
En `/abrir` se upsert un registro `matchmaking` (id, mesa_id, estado, llamada_abierta_at) y a la vez se setea el TTL. Redis gobierna la *vigencia*; Postgres guarda la *historia* (insumo para B05/B06/B10).

**D5 — Reserva de vacante como lock atómico (inicio de B06).**
`SET NX EX 60` sobre `reserva:vacante:{mesa_id}`: un solo ganador, expira sola (evita deadlock si el proceso cae). B06 usa este lock para la carrera por la última vacante; aquí queda el helper y su evidencia.

**D6 — Protección por rol.**
`/matchmaking/{mm_id}/abrir` requiere `requerir_roles("gm")` (403 para otros roles, formato AE1). `/estado` es público (lectura efímera).

## Risks

- **Caché staleness si falla la invalidación**: mitigado por TTL 60 s (staleness máximo acotado) y por invalidación sincrónica tras cada write.
- **Claves huérfanas**: todas con TTL (60/120/60 s); ninguna clave efímera sin expiración.
- **Redis caído**: la caché falla open y se resuelve con miss→DB (gracias al patrón `if data is not None`), el estado de matchmaking degrada a `cerrado` — coherente para un estado efímero.

## Migration Plan

1. `schema.sql`: tabla `matchmaking` (idempotente).
2. `app/services/cache.py`, `services/llamado.py`, `services/vacante.py`.
3. `app/models/matchmaking.py` + `controllers/matchmaking_controller.py` + `routes/v1/matchmaking.py` (registrar en `main.py`).
4. Inyectar caché en `controllers/mesas.py` (listar cachea; writes invalidan).
5. Verificación live + evidencia `redis-cli TTL`.

## Verification

- `GET /api/v1/mesas` dos veces → la segunda sale de `cache:mesas:list`; `docker exec tfinder-redis redis-cli TTL cache:mesas:list` muestra cuenta regresiva.
- Post/put/delete mesa autenticado → `redis-cli EXISTS cache:mesas:list` → 0; nuevo GET refleja el cambio.
- `POST /api/v1/matchmaking/1/abrir` con gm → `llamado:1` TTL ~120; `/estado` → abierto; tras expirar → cerrado.
- `abrir` sin rol gm → 403.
- Helper `reservar`/`liberar` sobre `reserva:vacante:{mesa_id}` (NX) → primera True, segunda False; liberar la borra.
- `users`/`matchmaking` en `docs/PROPIEDAD_DE_DATOS.md`.
- `openspec validate b04-redis-cache-ttl` válido.