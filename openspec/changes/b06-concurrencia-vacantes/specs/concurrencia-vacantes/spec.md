# Purpose

Define la carrera por la última vacante en `mesas-api` (criterio AE2 7): dos jugadores que solicitan a la vez el último cupo de una mesa deben quedar con exactamente un ganador y el otro con `409`, el conteo de jugadores nunca debe superar `jugadores_max`, y repetir la misma solicitud con la misma `Idempotency-Key` no debe duplicar efecto (idempotencia visible).

## ADDED Requirements

### Requirement: Registro de solicitudes y conteo de ocupación
La base de `mesas_db` DEBE contar jugadores por mesa (`jugadores_actuales`, default 0) y DEBE persistir cada solicitud de unión en la tabla `solicitudes_uniones` con `mesa_id`, `usuario_id`, `estado` (`pendiente|aceptada|rechazada`) e `idem_key`, con migración aditiva e idempotente (no recalcula datos existentes).

#### Scenario: Mesa sin ocupación previa
- **WHEN** se consulta una mesa recién creada
- **THEN** `jugadores_actuales` es `0` y el campo aparece en la respuesta de la mesa

#### Scenario: Solicitud persistida
- **WHEN** un usuario solicita unirse
- **THEN** queda una fila en `solicitudes_uniones` con su `mesa_id`, `usuario_id` y `idem_key`

### Requirement: Control de concurrencia con doble barrera
`mesas-api` DEBE usar dos barreras contra la carrera por la última vacante: un lock distribuido en Redis (`SET NX EX 60` sobre `reserva:vacante:{mesa_id}`) para descartar solicitudes simultáneas, y un check-and-set atómico en PostgreSQL (`UPDATE mesas SET jugadores_actuales = jugadores_actuales + 1 WHERE id = %s AND jugadores_actuales < jugadores_max RETURNING id`) que solo devuelve fila a la transacción ganadora.

#### Scenario: Único cupo, dos solicitudes concurrentes
- **WHEN** dos usuarios autenticados envían `POST /api/v1/mesas/{id}/solicitudes` a la vez sobre el último cupo
- **THEN** exactamente uno recibe `201` con la solicitud aceptada y el otro recibe `409`, y `jugadores_actuales` queda en `jugadores_max` (nunca por encima)

### Requirement: Idempotencia por Idempotency-Key
El endpoint DEBE aceptar el header `Idempotency-Key` y, si esa clave ya fue procesada (cache en Redis `idem:solicitud:{key}` TTL 24 h o fila existente en `solicitudes_uniones`), DEBE devolver el mismo resultado que la primera vez sin volver a ocupar vacante ni duplicar la solicitud.

#### Scenario: Reenvío con la misma clave ganadora
- **WHEN** se repite `POST /api/v1/mesas/{id}/solicitudes` con la misma `Idempotency-Key` que ganó antes
- **THEN** se devuelve el mismo `201`/respuesta original y `jugadores_actuales` no vuelve a incrementarse

#### Scenario: Reintento de la clave ganadora en carrera
- **WHEN** la clave perdedora del primer intento se reenvía
- **THEN** si el cupo se agotó devuelve `409` con el mismo criterio (sin estado inconsistente)

### Requirement: Notificación al ganador del cupo
Tras ocupar la vacante, `mesas-api` DEBE publicar el evento `mesa.aceptada` (RabbitMQ, flujo B05) para que `notif-api` notifique al jugador aceptado.

#### Scenario: Evento de aceptación
- **WHEN** el controlador de B06 acepta una solicitud
- **THEN** se publica `mesa.aceptada` con `mesa_id` y `usuario_id` y el consumidor de notificaciones crea la notificación correspondiente