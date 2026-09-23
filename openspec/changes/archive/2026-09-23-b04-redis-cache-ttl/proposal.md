# Proposal: Redis — caché, TTL de llamado abierto y reserva de vacante

## Why

B03 demostró Redis para sesiones; este issue agrega dos casos más de uso pertinente (criterio AE2 6): cache-aside del listado público de mesas (alta lectura) y estado efímero con TTL para el matchmaking ("llamado abierto") y para la reserva de vacante durante una solicitud de unión. Todo en `mesas-api`.

## What Changes

- **Cache-Aside del listado de mesas**: `GET /api/v1/mesas` sirve desde la clave Redis `cache:mesas:list` (TTL 60 s) cuando hay hit; un miss lee `mesas_db`, guarda y devuelve. Crear/actualizar/eliminar mesa **invalida** la clave (write-through coherente).
- **"Llamado abierto" del matchmaking**: `POST /api/v1/matchmaking/{mm_id}/abrir` (rol `gm`) crea `llamado:{mm_id}` con TTL 120 s; `GET /api/v1/matchmaking/{mm_id}/estado` reporta `abierto`/`cerrado` con `ttl_restante`. El TTL cierra el llamado sin jobs.
- **Reserva de vacante**: helper `reservar(mesa_id)` / `liberar(mesa_id)` sobre `reserva:vacante:{mesa_id}` (`SET NX EX 60`) listo para la carrera de B06 (aquí solo existe y se documenta).
- **Tabla `matchmaking`** en `mesas_db` (DDL idempotente): `id, mesa_id, estado, llamada_abierta_at` — el "llamado abierto" se persiste y su vigencia se controla por TTL en Redis.
- **Evidencia de TTL**: salida de `redis-cli TTL` capturable para el Portafolio.

## Capabilities

- **New Capabilities**: `redis-cache-ttl` — caché con invalidación y estado efímero (TTL) en Redis para `mesas-api`.
- **Modified Capabilities**: ninguna.

## Impact

- `mesas_api/app/services/cache.py`, `services/llamado.py`, `services/vacante.py` (nuevo).
- `mesas_api/app/models/matchmaking.py`, `controllers/matchmaking_controller.py`, `routes/v1/matchmaking.py`.
- `mesas_api/app/controllers/mesas.py`: listar cachea; writes invalidan.
- `mesas_api/app/schema.sql`: tabla `matchmaking`.
- `mesas_api/main.py`: router matchmaking (protegido: `/abrir` requiere `gm`).
- Reusa `app/infra/redis.py` (B01) y auth de B03.