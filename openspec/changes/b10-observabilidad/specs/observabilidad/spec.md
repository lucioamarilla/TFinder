# Purpose

Define la observabilidad base de los 4 servicios AE2: logs estructurados JSON con `correlation_id` (propagado por header y por los mensajes RabbitMQ), y endpoints de salud `/live` (proceso) y `/ready` (dependencias) que F09 consultará.

## ADDED Requirements

### Requirement: Logs JSON con correlación
Cada evento de log de los 4 servicios DEBE emitirse en JSON con al menos `ts`, `nivel`, `servicio`, `mensaje` y `correlation_id` (default `-` si no hay traza); el `correlation_id` DEBE configurarse a partir del header `X-Correlation-Id` de cada request y quedar disponible para los logs del recorrido.

#### Scenario: Request con header de correlación
- **WHEN** llega un request con `X-Correlation-Id: abc123`
- **THEN** todos los logs de ese request contienen `"correlation_id": "abc123"` y la respuesta incluye el mismo header

### Requirement: Propagación de correlación a eventos
Cuando un request publica un evento RabbitMQ (p. ej. `mesa.solicitada`), el mensaje DEBE incluir el `correlation_id` del request, y el consumidor DEBE loguear el procesamiento con ese mismo id.

#### Scenario: Recorrido request → evento → consumidor
- **WHEN** un request con `X-Correlation-Id: cid-x` origina `mesa.solicitada` y `notif-api` la consume
- **THEN** aparecen ≥3 logs (request iniciado/finalizado en mesas, consumido en notif) con `"correlation_id": "cid-x"`

### Requirement: `/live` y `/ready`
Cada servicio DEBE exponer `GET /live` → `200` si el proceso responde, y `GET /ready` → `200` solo si PostgreSQL, Redis y RabbitMQ responden; si alguna falla, `/ready` DEBE responder `503` con el detalle de dependencias.

#### Scenario: Todo sano
- **WHEN** `GET /ready` con postgres, redis y rabbitmq arriba
- **THEN** responde `200` con `{"estado":"listo","dependencias":{...}}`

#### Scenario: Dependencia caída (postgres)
- **WHEN** `GET /ready` con PostgreSQL fuera
- **THEN** responde `503` con `{"estado":"degradado","dependencias":{"postgres":false,...}}` y los otros servicios siguen dando `/live` `200`

### Requirement: No imprimir secretos
Los logs NO DEBEN imprimir tokens, passwords ni el contenido completo de QRs (solo IDs/resultados).

#### Scenario: Log de autenticación sin token
- **WHEN** un request autenticado se registra en logs
- **THEN** ninguna línea de log contiene el `access_token`, el password ni el campo `qr_data` completo; a lo sumo se referencian IDs o resultados