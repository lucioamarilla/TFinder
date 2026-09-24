# Purpose

Completar el backend pendiente de los issues reabiertos #32, #33 y #34: PDF de diario con auth (feed-api), estado de documentos + fix de error (notif-api), notificaciones en vivo por SSE (notif-api), y tests/evidencias de la capa admin.

## ADDED Requirements

### Requirement: PDF de diario con auth (feed-api)
`feed-api` DEBE exponer `POST /api/v1/mesas/{mesa_id}/sesiones/{sesion_id}/diario/pdf` protegido con **autenticación JWT** (`Authorization: Bearer`, `JWT_SECRET` compartido, sesión activa en Redis). DEBE responder **202 Aceptado** con `{estado:"aceptado", documento_id, detalle:"turno_enviado"}` y publicar `doc.pdf.diario` en `tfinder.events` con `id_origen=sesion_id` y datos armados desde `wiki_paginas` de la mesa. Sin token válido DEBE responder 401.

#### Scenario: solicitar PDF de diario autenticado
- **GIVEN** un usuario autenticado (token vigente emitido por mesas-api, mismo JWT_SECRET)
- **WHEN** realiza `POST /api/v1/mesas/{mesa_id}/sesiones/{sesion_id}/diario/pdf` contra `feed-api`
- **THEN** responde 202 con `documento_id` y `estado:"aceptado"`
- **AND** un consumidor genera el PDF y `GET /api/v1/pdf/{documento_id}/estado` en `notif-api` llega a `listo`

#### Scenario: sin token
- **GIVEN** la petición sin `Authorization`
- **WHEN** se llama al endpoint del diario
- **THEN** responde 401 "Autenticación requerida"

### Requirement: Estado del documento consultable (notif-api)
`notif-api` DEBE exponer `GET /api/v1/pdf/{documento_id}/estado` devolviendo `{documento_id, tipo, id_origen, estado, fecha}` con `estado` en `en_proceso | listo | error`; 404 si el documento no existe.

#### Scenario: estado de un documento en proceso
- **GIVEN** un `documento_id` recién generado por un 202
- **WHEN** se consulta `/api/v1/pdf/{id}/estado` antes de terminar el worker
- **THEN** responde 200 con `estado:"en_proceso"`
- **AND** tras el procesamiento responde `estado:"listo"`

### Requirement: Fallo de generación marcado como error
Si el worker de PDF (`notif_api/app/workers/pdf.py`) no puede generar el archivo, DEBE marcar `documentos.estado = 'error'` en la base antes de reencolar/DLQ. El evento puede ir a DLQ, pero el documento queda consultable como `error`, no `en_proceso` para siempre.

#### Scenario: worker que falla
- **GIVEN** un `doc.pdf.build` cuyo payload es inválido (falla `generar_pdf_build`)
- **WHEN** el worker intenta generarlo y falla
- **THEN** `GET /api/v1/pdf/{id}/estado` responde `estado:"error"`
- **AND** el mensaje termina en `dlq.general` (política de reintentos intacta)

### Requirement: Notificaciones en vivo por SSE (notif-api)
`notif-api` DEBE exponer `GET /api/v1/notificaciones/stream` (`text/event-stream`) que emita en vivo cada notificación nueva que los consumers (`mesa.*`, `sesion.*`) persistan, filtrada por `usuario_id` cuando se pasa como query. El polling (`GET /notificaciones`) DEBE seguir funcionando.

#### Scenario: notificación emitida en vivo
- **GIVEN** un cliente conectado a `/notificaciones/stream?usuario_id=N`
- **WHEN** se genera una solicitud de unión (`mesa.solicitada`) para el usuario N
- **THEN** el consumer persiste la notificación y el stream emite `data: {…notificacion…}`
- **AND** `GET /notificaciones` sigue listando sin duplicados

### Requirement: Tests automatizados de la capa admin
El repo DEBE incluir tests que cubran: reintentar un mensaje DLQ (200, desaparece de `mensaje_dlq`), descartarlo (200, se borra), id DLQ inexistente (404), `/ready` degradado cuando una dependencia falla y `listo` cuando todas responden (parametrizado a los 4 servicios), y `GET /event-log?correlation_id=` devolviendo solo el recorrido buscado.

#### Scenario: reintentar un DLQ
- **GIVEN** una fila en `mensaje_dlq`
- **WHEN** se hace `POST /api/v1/dlq/{id}/reintentar`
- **THEN** responde 200 `{ok:true, id, cola}` y la fila desaparece de `mensaje_dlq`

#### Scenario: ready degradado
- **GIVEN** Redis no responde (`ping()` = False)
- **WHEN** se consulta `/ready` de un servicio
- **THEN** responde `estado:"degradado"` con `dependencias.redis=false`
- **AND** con todas las dependencias OK responde `estado:"listo"`

### Requirement: Evidencias nuevas en AE2
Se DEBEN agregar capturas (`.png` + `.txt`) y entradas en `AE2/evidencias/EVIDENCIAS.md` para: `ready_degradado`, `dlq_reintentar_y_descartar`, `event_log_correlation` (y diario/SSE si el flujo lo requiere), siguiendo el mismo formato de las evidencias existentes.

#### Scenario: evidencia regenerable
- **GIVEN** la infraestructura levantada con `docker compose` y el script `scripts/generar_evidencias.py`
- **WHEN** se ejecuta el script
- **THEN** genera `.png` y `.txt` para `ready_degradado`, `dlq_reintentar_y_descartar`, `event_log_correlation`, `diario_pdf_202` y `sse_notificaciones`
- **AND** `AE2/evidencias/EVIDENCIAS.md` referencia cada nuevo archivo con su criterio