## 1. Servicios Redis

- [x] 1.1 Crear `mesas_api/app/services/cache.py`: `obtener_listado_cachead`/`guardar_listado`/`invalidar_listado` sobre `cache:mesas:list` (TTL 60 s) y verificar `redis-cli GET cache:mesas:list` tras una lectura
- [x] 1.2 Crear `mesas_api/app/services/llamado.py` con `abrir_llamado` (TTL 120 s) y `estado_llamado` (abierto/cerrado + ttl_restante)
- [x] 1.3 Crear `mesas_api/app/services/vacante.py` con `reservar` (`SET NX EX 60`) y `liberar`

## 2. Persistencia y controlador

- [x] 2.1 Agregar tabla `matchmaking` a `mesas_api/app/schema.sql` (id, mesa_id, estado, llamada_abierta_at) y verificar que `init_db` la aplica
- [x] 2.2 Inyectar caché en `mesas_api/app/controllers/mesas.py`: `listar_mesas_controller` usa el cache-aside y `crear/actualizar/eliminar` invalidan la clave

## 3. Endpoints de matchmaking

- [x] 3.1 Crear `mesas_api/app/models/matchmaking.py` y `controllers/matchmaking_controller.py` (upsert del registro + llamado)
- [x] 3.2 Crear `mesas_api/app/routes/v1/matchmaking.py` con `POST /api/v1/matchmaking/{mm_id}/abrir` (gm) y `GET /api/v1/matchmaking/{mm_id}/estado`; registrar en `main.py`

## 4. Verificación (done)

- [x] 4.1 Verificar caché: doble GET de mesas, `redis-cli TTL cache:mesas:list` en descenso; tras crear/editar/borrar mesa `EXISTS` → 0 y nuevo GET refleja el cambio
- [x] 4.2 Verificar llamado: `abrir` (gm) → `llamado:1` con TTL ~120; `/estado` abierto → cerrado tras expirar; `abrir` sin gm → 403
- [x] 4.3 Verificar reserva: `reservar` (NX) primer acceso True, re-intento False, `liberar` la borra
- [x] 4.4 Actualizar `docs/PROPIEDAD_DE_DATOS.md` con `matchmaking` (dueño `mesas-api`)

## 5. Cierre de la tarea

- [x] 5.1 `openspec validate` del change `b04-redis-cache-ttl`
- [x] 5.2 Rama `f/B04_redis_cache_ttl`, commit `feat(mesas-api): cache y estado efimero en Redis (llamado abierto, reserva de vacante) (#17)`, merge y archivar
- [x] 5.3 Cerrar issue GitHub #17