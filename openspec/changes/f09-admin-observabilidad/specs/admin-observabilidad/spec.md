# Purpose

Conectar las vistas admin de observabilidad, DLQ y resiliencia a datos reales de `notif-api` y de los `/live`/`/ready` de los 4 servicios, con reintento/descartes reales sobre `dlq.general` y trazabilidad por `correlation_id`.

## ADDED Requirements

### Requirement: Panel de salud real por servicio
`AdminObservabilidadView` DEBE consultar `/live` y `/ready` de los 4 servicios (`mesas`, `builds`, `feed`, `notif`) y mostrar un panel por servicio: verde si `live` y `ready.estado==='listo'`, ámbar si `degradado` (con las dependencias pg/redis/rabbitmq en falso), gris si no responde (sin romper la vista).

`/ready` responde 503 cuando hay una dependencia caída, pero con el detalle en el body; el cliente DEBE poder leer ese body sin convertirlo en error, y DEBE seguir tratándolo como error cuando no se pida explícitamente.

#### Scenario: servidor con Redis caído
- **GIVEN** `redis` detenido
- **WHEN** la vista consulta el `/ready` de `mesas-api`
- **THEN** el panel muestra `degradado` con `redis ✗` y las dependencias postgres/rabbitmq en verde
- **AND** al restaurar Redis, un nuevo `/ready` devuelve `listo`

#### Scenario: un 503 con el detalle de dependencias
- **GIVEN** un servicio que responde 503 en `/ready` con `{estado:'degradado', dependencias:{...}}`
- **WHEN** la vista pide ese `/ready`
- **THEN** el body se lee y el panel refleja la dependencia caída
- **AND** una petición sin esa opción sigue lanzando `ApiError`

### Requirement: Traza por correlation_id
La vista DEBE listar los últimos eventos del `event-log` mostrando su `correlationId`, y DEBE permitir filtrar por un CID para ver solo ese recorrido (backend: `GET /api/v1/event-log?correlation_id=`).

El `event-log` no expone un nivel de log, así que la tabla DEBE mostrar los campos reales del evento (ocurrido, entidad, acción y CID) y no una severidad inventada.

#### Scenario: filtrar un recorrido
- **GIVEN** un recorrido previo (ej. solicitud de unión) con CID `dc59...`
- **WHEN** el admin hace clic sobre ese CID en la tabla de logs
- **THEN** los logs se filtran a los eventos con ese `correlationId`

### Requirement: DLQ real con reintento y descarte
`AdminDlqView` DEBE listar los mensajes reales de la DLQ (`id`, `cola`, `payload`, `error`, `fecha`) con `GET /api/v1/dlq`. El nombre del mensaje DEBE derivarse de `payload.tipo`; no DEBE inventar una columna de reintentos porque el backend no la expone. "Reintentar" DEBE reencolar el mensaje a la cola original (`POST /dlq/{id}/reintentar`) y "Descartar" DEBE eliminarlo (`DELETE /dlq/{id}`).

#### Scenario: reintentar un mensaje DLQ
- **GIVEN** un mensaje en la DLQ (ej. `mesa.desconocido` tras 3 reintentos)
- **WHEN** el admin presiona "Reintentar"
- **THEN** el mensaje desaparece de la lista y el evento vuelve a ser publicado en `tfinder.events`
- **AND** si el mensaje no existe, la API responde 404 "Mensaje no encontrado en DLQ" y la vista muestra ese mensaje

#### Scenario: drenar la cola
- **GIVEN** varios mensajes en la DLQ
- **WHEN** el admin presiona "Drenar cola"
- **THEN** el frontend descarta uno por uno con `DELETE /dlq/{id}` y muestra el progreso
- **AND** si un descarte falla, el drenaje se detiene y la lista se recarga para no mostrar una cola que ya no coincide con la del backend

### Requirement: Resiliencia desde el estado real del broker
`AdminResilienciaView` DEBE derivar el breaker del `/ready` real de `mesas-api` (CERRADO si `listo`, ABIERTO si `degradado` o si el servicio no responde), mostrar chips pg/redis/rabbitmq y el conteo actual de la DLQ. El botón "Verificar broker" DEBE reconsultar el estado; no DEBE simular caídas.

Los parámetros de referencia del códice (umbral del breaker, reintentos, timeouts) no tienen endpoint que los persista: DEBEN mostrarse en solo lectura y rotulados como ajustes locales.

#### Scenario: verificar broker con Redis detenido
- **GIVEN** `redis` detenido en `mesas-api`
- **WHEN** el admin presiona "Verificar broker"
- **THEN** el breaker pasa a `ABIERTO`, redis ✗ en rojo, y `DLQ en cola` refleja el conteo real

#### Scenario: notif-api caído
- **GIVEN** `notif-api` no responde
- **WHEN** el admin abre el gestor de DLQ
- **THEN** la vista indica "sin datos del operador" y ofrece reintentar la carga, sin mostrar datos de ejemplo

### Requirement: Parámetros de resiliencia no editables
`AdminResilienciaView` NO DEBE ofrecer guardado ni simulación de caída: el backend no expone ninguno de los dos.

#### Scenario: revisar los sellos
- **GIVEN** el panel de resiliencia cargado
- **WHEN** el admin intenta modificar un parámetro
- **THEN** el campo es de solo lectura y el texto aclara que no hay backend que lo guarde
- **AND** no existe un botón "Simular caída"