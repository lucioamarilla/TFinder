# Proposal: Concurrencia e idempotencia — carrera por la última vacante

## Why

Demostrar y resolver un caso real de carrera (criterio AE2 7): dos jugadores solicitan a la vez la única vacante de una mesa con `jugadores_max` cubierto tras aceptar a uno. Sin control, ambos superan `vacantes > 0` y la mesa queda con overbooking. Además, reintentar la misma solicitud (misma `Idempotency-Key`) no debe duplicar la solicitud ni la ocupación.

## What Changes

- **Migración aditiva en `mesas_db`**: `ALTER TABLE mesas ADD COLUMN IF NOT EXISTS jugadores_actuales INT NOT NULL DEFAULT 0`; nueva tabla `solicitudes_uniones` (id, mesa_id, usuario_id, estado `pendiente|aceptada|rechazada`, idem_key, fecha). Verificación de cupo por conteo real y registro de solicitudes con su clave de idempotencia.
- **Doble barrera**:
  1. Lock distribuido en Redis (`reserva:vacante:{mesa_id}`, `SET NX EX 60` — helper B04) descarta doble clic simultáneo.
  2. Check-and-set atómico en Postgres: `UPDATE mesas SET jugadores_actuales = jugadores_actuales + 1 WHERE id = %s AND jugadores_actuales < jugadores_max RETURNING id` → `fetchone()` `None` = cupo agotado (`409`). El `WHERE` + `RETURNING` serializa por lock de fila hasta commit.
- **Idempotencia por `Idempotency-Key`**: `mesas_api/app/services/idem.py` cachea en Redis (`idem:solicitud:{key}`, TTL 24 h) la respuesta de una solicitud ya procesada; un reenvío devuelve el resultado original sin repetir efecto. Además `obtener_solicitud_por_key` evita duplicados por la misma clave de idempotencia.
- **Endpoint**: `POST /api/v1/mesas/{mesa_id}/solicitudes` (autenticado, header `Idempotency-Key`) → `201` con la solicitud (estado `aceptada`) o `409` "cupo agotado". Tras aceptar, publica `mesa.aceptada` (RabbitMQ, B05) para notificar al jugador.
- **Rutas/controlador**: `solicitudes_controller.py` + `solicitudes_routes.py` (nuevos, siguiendo el patrón del config actual de `mesas-api`).

## Capabilities

- **New Capabilities**: `concurrencia-vacantes` — doble barrera (Redis + `UPDATE ... RETURNING`) e idempotencia por `Idempotency-Key` para la carrera por la última vacante.
- **Modified Capabilities**: `eventos-rabbitmq` — el productor de B05 (`mesa.solicitada`, encolaba sin validar cupo) ahora se dispara desde el controlador ganador de B06 con `mesa.aceptada`; el endpoint B05 `POST /mesas/{id}/solicitar` (202) queda como flujo async de notificación y `POST /mesas/{id}/solicitudes` es el flujo síncrono de la carrera.

## Impact

- `mesas_db`: DDL aditivo (`jugadores_actuales` con default 0, tabla nueva) — no rompe lecturas B04 (`MesaOut` expone el campo nuevo).
- `mesas-api`: nuevo endpoint con idempotencia; `reservar/liberar` (B04) se reutilizan; sin cambios en notif-api.
- Evidencia para portafolio: dos requests concurrentes sobre el último cupo → una `201` y una `409`; conteo final ≤ `jugadores_max`; replay de la misma key devuelve el mismo `201` sin duplicar ocupación (la carrera automatizada en `tests` queda para B11).