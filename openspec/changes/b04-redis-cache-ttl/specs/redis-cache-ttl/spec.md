## Purpose

Define el uso pertinente de Redis en `mesas-api` (criterio AE2 6): caché de alto rendimiento con invalidación al escribir (cache-aside) para el listado público de mesas, y estado efímero con TTL para el matchmaking ("llamado abierto") y la reserva de vacante durante una solicitud de unión, manteniendo PostgreSQL como fuente de verdad.

## ADDED Requirements

### Requirement: Caché de listado de mesas con invalidación al escribir
`mesas-api` DEBE cachear la respuesta de `GET /api/v1/mesas` en la clave Redis `cache:mesas:list` (cache-aside, TTL 60 s), sirviendo desde Redis cuando hay hit, y DEBE invalidar esa clave tras crear, actualizar o eliminar una mesa, de modo que el siguiente GET devuelva datos actuales de `mesas_db`.

#### Scenario: Lectura cacheada
- **WHEN** se consulta `GET /api/v1/mesas` una vez y se repite la consulta
- **THEN** la segunda respuesta se sirve desde la clave `cache:mesas:list` (el listado no cambia) y la clave existe con TTL restante

#### Scenario: Invalidación tras escritura
- **WHEN** se crea, actualiza o elimina una mesa autenticada
- **THEN** la clave `cache:mesas:list` se elimina y un GET posterior refleja la escritura

#### Scenario: Miss con re-llenado
- **WHEN** la clave de caché no existe (o expiró)
- **THEN** el GET lee `mesas_db`, re-puebla `cache:mesas:list` con TTL 60 s y devuelve los datos

### Requirement: Llamado abierto del matchmaking con TTL
`mesas-api` DEBE exponer `POST /api/v1/matchmaking/{mm_id}/abrir` (requiere rol `gm`) que persista el matchmaking y cree la clave `llamado:{mm_id}` en Redis con TTL 120 s, y `GET /api/v1/matchmaking/{mm_id}/estado` que reporte `abierto` (con `ttl_restante`) o `cerrado` (TTL 0) sin necesidad de jobs de expiración.

#### Scenario: Apertura del llamado
- **WHEN** un `gm` envía `POST /api/v1/matchmaking/1/abrir`
- **THEN** se crea/actualiza el registro `matchmaking` y la clave `llamado:1` existe con TTL ~120 s decreciente

#### Scenario: Estado abierto y cierre por expiración
- **WHEN** se consulta `GET /api/v1/matchmaking/1/estado` durante la vigencia del TTL y luego tras su expiración
- **THEN** durante la vigencia responde `{"estado":"abierto","ttl_restante":N}`, y tras expirar responde `{"estado":"cerrado","ttl_restante":0}` sin intervención externa

#### Scenario: Acceso no permitido sin rol gm
- **WHEN** un usuario sin rol `gm` intenta `POST /api/v1/matchmaking/1/abrir`
- **THEN** la API responde `403` con el formato de error AE1

### Requirement: Reserva de vacante con TTL
`mesas-api` DEBE proveer helper de reserva de vacante (`reserva:vacante:{mesa_id}`) con `SET NX EX 60` (un solo creador, expira sola), de modo que el matchmaking pueda bloquear transitoriamente una vacante mientras procesa una solicitud, y `liberar` pueda quitarla explícitamente.

#### Scenario: Reserva atómica y expirable
- **WHEN** se ejecuta el helper `reservar(mesa_id)` sobre la clave
- **THEN** la primera reserva responde que adquirió la clave (otra reserva simultánea no la obtiene), la clave existe con TTL 60 s, y tras expirar o llamar `liberar` ya no existe

### Requirement: Persistencia del matchmaking en mesas_db
`mesas-api` DEBE exponer la tabla `matchmaking` (id, mesa_id, estado, llamada_abierta_at) como registro persistente del llamado, con DDL idempotente en su `schema.sql`, de modo que el estado del matchmaking sobreviva aun cuando el TTL efímero ya expiró.

#### Scenario: Registro persistente tras apertura
- **WHEN** se abre un llamado vía el endpoint
- **THEN** existe una fila en `mesas_db.matchmaking` con su `mesa_id`, `estado` y `llamada_abierta_at` coincidentes