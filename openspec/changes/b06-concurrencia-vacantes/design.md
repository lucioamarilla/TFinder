# Design: Concurrencia e idempotencia — carrera por la última vacante

## Context

B04 dejó el lock distribuido (`reservar/liberar` en `vacante.py`) y B05 un endpoint async (`POST /mesas/{id}/solicitar` → `202`) que solo encolaba `mesa.solicitada`. El issue B06 pide resolver la carrera real: dos jugadores por el último cupo, con idempotencia por `Idempotency-Key`. El tutorial del issue usa helpers genéricos (`app.models.*`, `app.services.*`) que este repo ya tiene con naming propio; se respeta el patrón real (`mesas_api.app.*`, `app.infra.redis`).

## Decisions

**D1 — Migración aditiva, no destructiva.**
`schema.sql` de mesas agrega `jugadores_actuales INT NOT NULL DEFAULT 0` a `mesas` (la columna participa del `WHERE` del UPDATE atómico) y crea `solicitudes_uniones` con índice por `(mesa_id, usuario_id)`. `init_db` ya ejecuta el DDL por sentencia (idempotente gracias a `IF NOT EXISTS`).

**D2 — Segunda barrera: `UPDATE ... RETURNING` como check-and-set.**
`ocupar_vacante(mesa_id)` ejecuta `UPDATE mesas SET jugadores_actuales = jugadores_actuales + 1 WHERE id = %s AND jugadores_actuales < jugadores_max RETURNING id`; devuelve `True` si `fetchone()` trae fila. En PostgreSQL el UPDATE toma lock de fila hasta el commit, serializando las transacciones concurrentes. `RETURNING id` (no `rowcount`) es la señal de "ganaste el cupo".

**D3 — Primera barrera: lock distribuido.**
`vacante.reservar(mesa_id)` (B04, `SET reserva:vacante:{mesa_id} NX EX 60`) es la barrera 1: descarta doble clic simultáneo. Se libera en `finally` (bloquea la misma solicitud mientras procesa).

**D4 — Idempotencia por `Idempotency-Key` en Redis + fila en `solicitudes_uniones`.**
`idem.py` (prefijo `idem:solicitud:`, TTL 24 h) guarda el JSON de la respuesta y lo redevuelve si se repite la clave (sin repetir el UPDATE). `obtener_solicitud_por_key` cubre el caso en que la respuesta venció pero la solicitud ya existía.

**D5 — Orden del controlador.**
```
1) idem (¿key ya procesada?)  -> devolver respuesta cacheada
2) existente por key          -> devolver solicitud guardada
3) reservar()                 -> si False, 409 "procesándose"
4) ocupar_vacante()           -> si False, 409 "cupo agotado"
5) crear_solicitud(aceptada)  -> guardar idem + publicar mesa.aceptada -> 201
finally: liberar()
```
El `409` por lock (3) y el `409` por cupo (4) son distinguibles en el mensaje para el front.

**D6 — Publicar `mesa.aceptada`** (helper B05 `publicar_aceptacion`) tras aceptar: la notificación "Solicitud aceptada" corresponde al flujo real del ganador. El endpoint B05 `POST /mesas/{id}/solicitar` (202, async) se mantiene como demo de encolamiento; el flujo autoritativo de la carrera es `POST /mesas/{id}/solicitudes`.

## Risks

- **Doble endpoint de "solicitar"**: B06 usa `solicitudes` (síncrono 201/409); B05 `solicitar` (202) queda documentado como async de notificación. No entran en conflicto funcional pero conviene no duplicar llamadas desde el front (F04 usará `solicitudes`).
- **Redis no es la fuente de verdad del cupo**: solo descarta solapamiento inmediato; el cupo lo decide el UPDATE atómico. Si Redis cae, el UPDATE sigue garantizando integridad (con menos descarte de doble clic).
- **TTL de idempotencia (24 h) vs click duplicado**: un reenvío de la misma key después de 24 h volvería a crear solicitud; aceptable para el alcance (la fila `solicitudes_uniones` mitiga si el estado ya quedó).
- **`jugadores_actuales` arranca en 0 para mesas históricas (B01 en adelante)**: las mesas de prueba locales ya tienen participantes ficticios en el front pero no en `mesas_db`; el conteo es por diseño desde B06.

## Migration Plan

1. `mesas_api/app/schema.sql`: columna + tabla nuevas (idempotentes).
2. `mesas_api/app/models/mesa.py`: `ocupar_vacante`.
3. `mesas_api/app/models/solicitudes.py`: `crear_solicitud`, `obtener_solicitud_por_key`.
4. `mesas_api/app/services/idem.py`: cache Redis de respuestas.
5. `mesas_api/app/controllers/solicitudes_controller.py` + `mesas_api/app/routes/v1/solicitudes.py` (+ registro en `main.py`).
6. Verificación en contenedor: carrera (201/409), límite de conteo, replay de key, evento `mesa.aceptada` en notif.
7. Rama `f/B06_concurrencia_vacantes`, commit, merge, archivar, cerrar #19.

## Verification

- `POST /api/v1/mesas/{id}/solicitudes` concurrentes (dos tokens, una mesa `jugadores_max=1`): un `201` + un `409`.
- `SELECT jugadores_actuales, jugadores_max FROM mesas` → `1 ≤ 1` tras N intentos.
- Replay de la key ganadora → mismo `201`, `jugadores_actuales` sin cambios; `solicitudes_uniones` con 1 sola fila de esa key.
- Notificación "Solicitud aceptada" en `notif-api` (evento `mesa.aceptada`).
- `openspec validate b06-concurrencia-vacantes`.