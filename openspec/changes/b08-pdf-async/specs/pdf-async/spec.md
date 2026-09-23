# Purpose

Define la generación asíncrona de PDFs de comprobante (ficha de build) en `notif-api`, pedida por `builds-api` vía `doc.pdf.build`: respuesta sincrónica `202` con `documento_id`, procesamiento por worker (idempotente, con reintentos y DLQ) y descarga por `GET /api/v1/pdf/{documento_id}`.

## ADDED Requirements

### Requirement: Solicitud asíncrona de PDF del build
`builds-api` DEBE exponer `POST /api/v1/builds/{build_id}/pdf` (autenticado) que publica `doc.pdf.build` en el exchange `tfinder.events` (con `doc_id` único, `id_origen` y `datos` del build) y DEBE responder `202` con `documento_id` sin generar el archivo en el camino síncrono.

#### Scenario: Solicitud de ficha de build
- **WHEN** un usuario autenticado llama a `POST /api/v1/builds/1/pdf`
- **THEN** obtiene `202` con `documento_id` en el cuerpo y el pedido queda en RabbitMQ (cola `doc.pdf`), sin bloquear el request

### Requirement: Generación del PDF en `notif-api`
`notif-api` DEBE consumir `doc.pdf.build`/`doc.pdf.diario` con idempotencia por `event_id` (patrón B05), generar el PDF con `fpdf2` en `PDF_DIR`, guardar la ruta en `documentos` con estado `listo` y registrar el evento; si el mensaje ya fue procesado DEBE ignorarlo (respuesta exitosa).

#### Scenario: Worker genera el PDF
- **WHEN** llega un evento `doc.pdf.build` procesable
- **THEN** se crea la fila en `documentos` (estado `en_proceso`), se genera el archivo PDF y la fila queda `listo` con `ruta`

#### Scenario: Evento repetido (idempotencia)
- **WHEN** llega un `event_id` ya procesado
- **THEN** el worker lo reconoce y lo ACK sin regenerar el documento

### Requirement: Descarga del documento
`GET /api/v1/pdf/{documento_id}` DEBE responder `application/pdf` (download) cuando el documento existe y está `listo`, y `404` si no existe o aún no está listo.

#### Scenario: Descarga de un documento listo
- **WHEN** se solicita `GET /api/v1/pdf/{doc}` con un documento en estado `listo`
- **THEN** responde `200` con `Content-Type: application/pdf` y el cuerpo del archivo

#### Scenario: Documento no disponible
- **WHEN** el documento no existe o está `en_proceso`
- **THEN** responde `404`

### Requirement: Falla del generador no rompe el flujo síncrono
Si el procesamiento del evento falla (p. ej. storage no disponible), el mensaje DEBE encolarse en `dlq.general` tras los reintentos de B05, y la petición síncrona ya respondió `202` (no se ve afectada).

#### Scenario: Error de generación
- **WHEN** el worker lanza una excepción al generar el PDF
- **THEN** tras `MAX_REINTENTOS` reintentos el mensaje viaja a `dlq.general` (con error registrado) y el `documento` queda en estado `en_proceso`, mientras el response sincrónico ya fue `202`