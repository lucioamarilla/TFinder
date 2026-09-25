# Purpose

Define la integración de `notif-api` con un proveedor de email SMTP en sandbox (MailHog): los eventos `sesion.confirmada` y `sesion.diario_publicado` generan un email a cada jugador de la mesa (destinos obtenidos por REST desde `mesas-api`), con timeout, registro en outbox y reintento manual ante fallo; el SMTP caído no rompe el flujo asíncrono.

## Requirements

### Requirement: Emails al confirmar sesión o publicar diario
Al recibir `sesion.confirmada` o `sesion.diario_publicado`, el consumidor `sesion.*` DEBE obtener los emails de los jugadores aceptados de la mesa vía `GET /api/v1/mesas/{mesa_id}/miembros` (mesas-api) y DEBE enviar un email a cada uno con asunto y cuerpo simples, sin datos personales extra.

#### Scenario: Sesión confirmada
- **WHEN** llega el evento `sesion.confirmada` (idempotente por `event_id`)
- **THEN** se envía un email a cada miembro de la mesa con asunto "TFinder · Sesión confirmada", registrándose en la tabla `emails`

#### Scenario: Diario publicado
- **WHEN** llega el evento `sesion.diario_publicado`
- **THEN** se envía un email de "TFinder · Diario de sesión publicado" a cada miembro

### Requirement: Timeout y outbox con reintento
El envío DEBE usar un timeout de 3 s (configurable); si el SMTP falla (timeout/conexión), el email DEBE quedar en `emails` con estado `fallido` y `error`, sin propagar la excepción al consumidor (el evento se procesa igual). `POST /api/v1/emails/{id}/reintentar` DEBE reintentarlo y actualizar su estado.

#### Scenario: SMTP caído
- **WHEN** el envío falla (p. ej. puerto cerrado)
- **THEN** la fila en `emails` queda `fallido` con el error, el evento sigue procesado (ACK) y el email no se pierde (outbox)

#### Scenario: Reintento manual
- **WHEN** se llama `POST /api/v1/emails/{id}/reintentar` con el SMTP disponible
- **THEN** el email se vuelve a enviar y la fila pasa a `enviado`

### Requirement: Contrato REST de miembros de mesa
`mesas-api` DEBE exponer `GET /api/v1/mesas/{mesa_id}/miembros` (autenticado) que devuelve los jugadores con solicitud `aceptada` de esa mesa (id, nombre, email). `notif-api` DEBE consumirlo por la red interna sin leer `mesas_db`.

#### Scenario: Consulta de destinatarios
- **WHEN** `notif-api` consulta `GET /api/v1/mesas/{mesa_id}/miembros`
- **THEN** recibe la lista de jugadores aceptados con sus emails (404 si la mesa no existe)

### Requirement: Privacidad del email
El cuerpo y asunto del email NO DEBEN incluir secreto/contraseña/QR ni información personal superflua; solo texto de aviso simple (MIMEText plan, utf-8).

#### Scenario: Contenido mínimo
- **WHEN** se inspecciona el mensaje en MailHog (API v2)
- **THEN** aparece el asunto esperado y un cuerpo plano sin datos sensibles