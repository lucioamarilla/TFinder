# Purpose

Conectar las vistas admin de observabilidad, DLQ y resiliencia a datos reales de `notif-api` y de los `/live`/`/ready` de los 4 servicios, con reintento/descartes reales sobre `dlq.general` y trazabilidad por `correlation_id`.

## ADDED Requirements

### Requirement: Panel de salud real por servicio
`AdminObservabilidadView` DEBE consultar `/live` y `/ready` de los 4 servicios (`mesas`, `builds`, `feed`, `notif`) y mostrar un panel por servicio: verde si `live` y `ready.estado==='listo'`, ámbar si `degradado` (con las dependencias pg/redis/rabbitmq en falso), gris si no responde (sin romper la vista).

#### Scenario: servidor con Redis caído
- **GIVEN** `redis` detenido
- **WHEN** la vista consulta el `/ready` de `mesas-api`
- **THEN** el panel muestra `degradado` con `redis ✗` y las dependencias postgres/rabbitmq en verde
- **AND** al restaurar Redis, un nuevo `/ready` devuelve `listo`

### Requirement: Traza por correlation_id
La vista DEBE listar los últimos eventos del `event-log` mostrando su `correlationId`, y DEBE permitir filtrar por un CID para ver solo ese recorrido (backend: `GET /api/v1/event-log?correlation_id=`).

#### Scenario: filtrar un recorrido
- **GIVEN** un recorrido previo (ej. solicitud de unión) con CID `dc59...`
- **WHEN** el admin hace clic sobre ese CID en la tabla de logs
- **THEN** los logs se filtran a los eventos con ese `correlationId`

### Requirement: DLQ real con reintento y descarte
`AdminDlqView` DEBE listar los mensajes de `dlq.general` reales (payload JSON, `cola`, `error`, `reintentos`) con `GET /api/v1/dlq`. "Reintentar" DEBE reencolar el mensaje a la cola original (`POST /dlq/{id}/reintentar`, idempotente por `event_id` y elimina el registro) y "Descartar" DEBE eliminarlo (`DELETE /dlq/{id}`).

#### Scenario: reintentar un mensaje DLQ
- **GIVEN** un mensaje en `dlq.general` (ej. `mesa.desconocido` tras 3 reintentos)
- **WHEN** el admin presiona "Reintentar"
- **THEN** el mensaje desaparece de la lista y el evento vuelve a ser publicado en `tfinder.events`
- **AND** si el mensaje no existe, la API responde 404 "Mensaje no encontrado en DLQ"

### Requirement: Resiliencia desde el estado real del broker
`AdminResilienciaView` DEBE derivar el breaker del `/ready` real de `mesas-api` (CERRADO si `listo`, ABIERTO si `degradado`), mostrar chips pg/redis/rabbitmq y el conteo actual de `dlq.general`. El botón "Verificar broker" DEBE reconsultar el estado; no DEBE simular caídas.

#### Scenario: verificar broker con Redis detenido
- **GIVEN** `redis` detenido en `mesas-api`
- **WHEN** el admin presiona "Verificar broker"
- **THEN** el breaker pasa a `ABIERTO`, redis ✗ en rojo, y `DLQ en cola` refleja el conteo real