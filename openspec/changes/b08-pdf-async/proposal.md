# Proposal: PDF de comprobante generado de forma asíncrona

## Why

Criterio AE2 9 (portafolio): generar la ficha del build como PDF sin bloquear el request. El endpoint síncrono responde `202` con `documento_id` en <300 ms; RabbitMQ dispara el trabajo; `notif-api` compone el PDF con `fpdf2`, lo persiste en `documentos` y queda descargable por `GET /pdf/{documento_id}`. Un fallo del generador o del storage no quema la petición: el mensaje va a DLQ (barrera B05).

## What Changes

- **`notif_db` (B08)**: tabla `documentos` (id UUID/str PK, tipo `build|diario`, id_origen, ruta, estado `en_proceso|listo|error`, fecha). DDL aditivo idempotente.
- **`notif-api`**: worker `doc.pdf` (`workers/pdf.py`, patrón `consumir` de B05: idempotencia por `event_id`, ACK/reintentos/DLQ) + `services/pdf_service.py` (`fpdf2` genera ficha de build o diario de sesión en `PDF_DIR`) + ruta `GET /api/v1/pdf/{documento_id}` (`FileResponse` media_type `application/pdf`; 404 si no existe o aún no está listo).
- **`builds-api`** produce el pedido: `services/eventos.py::publicar_doc_pdf(build_id)` consulta el build y publica `doc.pdf.build` (con `doc_id` generado y `datos` del build) en el exchange `tfinder.events`. Ruta nueva `POST /api/v1/builds/{build_id}/pdf` (rol `auth`, middleware nuevo idéntico a B03) → `202` con `documento_id`.
- **Privacidad**: el PDF lleva solo datos del build/identificadores; el sistema no imprime `qr_data`/secrets.

## Capabilities

- **New Capabilities**: `pdf-async` — solicitud asíncrona de documento (202 + `documento_id`), worker generador y descarga del PDF.
- **Modified Capabilities**: `eventos-rabbitmq` — se agrega el emisor `doc.pdf.build` (exchange existente, cola `doc.pdf` ya declarada).

## Impact

- `mesas-api` no cambia. `notif_api` gana cola ya declarada `doc.pdf` (B05) y una tabla nueva en `notif_db`.
- `builds-api` gana dependencia a RabbitMQ (ya disponible en el container environment) y a `app.infra.rabbitmq` (ya compartida).