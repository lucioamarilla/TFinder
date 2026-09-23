# Design: PDF de comprobante generado de forma asíncrona

## Context

B05 dejó el exchange `tfinder.events`, la cola `doc.pdf` (binding `doc.pdf.*`) con DLQ, y `app/infra/rabbitmq.publicar` compartida; B07 dejó `mesas_db` con `sesiones`/`asistencias`. `builds-api` todavía no publica eventos ni autoriza peticiones. El objetivo: responder `202` con `documento_id` y generar el PDF fuera del request.

## Decisions

**D1 — Cola y DDL sin cambios en RabbitMQ.**
La cola `doc.pdf` ya está declarada por `notif-api` (B05). El DDL nuevo es solo la tabla `documentos` en `notif_db` (aditivo, `IF NOT EXISTS`).

**D2 — `documentos.id` como UUID producido por el emisor.**
El `202` debe devolver un `documento_id` consultable luego (`GET /pdf/{documento_id}`), pero el documento todavía no existe. El productor (builds-api) genera `doc_id = uuid.hex` y lo lleva en el mensaje; `notif-api` usa ese mismo id como PK. Sin esto el `<documento_id>` del 202 no mapearía a nada hasta después de procesar.

**D3 — Emisor en `builds-api` con datos del build.**
`publicar_doc_pdf(build_id)` consulta el build (`obtener_build`) y publica `doc.pdf.build` con `{doc_id, id_origen, datos:{persona,clase,nivel,handle}}`. El PDF queda rico (ficha) sin que `notif-api` dependa de la DB de builds.

**D4 — Auth mínima idéntica a B03 en builds-api.**
`builds_api/app/middleware/auth.py` replica `usuario_actual` de mesas: `decodificar_token` (PyJWT HS256, `JWT_SECRET` compartido) + `sesion_valida` (Redis `sesion:{jti}`). Sin tocar mesas ni duplicar lógica de almacenamiento.

**D5 — Worker `doc.pdf` con el patrón B05.**
`notif_api/app/workers/pdf.py` usa `consumir(cola, procesar)` de `_base` (ACK explícito, `evento_ya_procesado`, reintentos con backoff `2^n`, `_republicar` y DLQ). `_procesar` valida tipo (`doc.pdf.build` | `doc.pdf.diario`) y `doc_id`; crea el documento, genera y actualiza a `listo`.

**D6 — `fpdf2` y carpeta compartida.**
`pdf_service.py` escribe en `os.getenv("PDF_DIR", "./storage/pdf")` (volume del container notif). `FileResponse` sirve el archivo con `media_type="application/pdf"` y filename `tfinder_{tipo}_{id_origen}.pdf`.

**D7 — Descarga con estado.**
`GET /api/v1/pdf/{documento_id}` devuelve `404` si no existe o si `estado != 'listo'` (el doc puede estar `en_proceso`; eso no es error de cliente). No se imprime el contenido del PDF en logs.

## Risks

- **PDF_DIR dentro del container**: para evidencia hay que `docker cp`; no se monta volume a propósito (ambiente efímero).
- **Auth duplicada (builds vs mesas)**: idéntica implementación (mismo secret compartido), aceptado para desacople de servicios; B11 podrá ejercitarla.
- **Documento queda `en_proceso` tras DLQ**: no se marca `error` para no acoplar el worker al manejo de DLQ; el DLQ y `mensaje_dlq` ya registran la causa.

## Migration Plan

1. `notif_api/app/schema.sql`: `documentos`.
2. `notif_api/app/models/notif.py`: `crear_documento`, `actualizar_documento`, `obtener_documento`.
3. `notif_api/app/services/pdf_service.py` (fpdf2) y `notif_api/app/workers/pdf.py`.
4. `notif_api` main: registrar worker `doc.pdf` en lifespan y router `/api/v1/pdf`.
5. `builds_api`: middleware auth, `services/eventos.py`, ruta `POST /builds/{id}/pdf`, registrar en main.
6. Verificación en contenedores; rama, commit, merge, archivar, cerrar #21.

## Verification

- `POST /api/v1/builds/{id}/pdf` (token) → `202` `< 300ms` con `documento_id`.
- tras unos segundos `GET /api/v1/pdf/{documento_id}` → `200` `application/pdf`; `file` lo confirma.
- Contenido del PDF con datos del build y sin datos sensibles.
- Fila `documentos` en `listo`; `event_log` con `event_id` (idempotencia).
- Replay del mismo `event_id` → no regenera (evento_ya_procesado).
- `openspec validate b08-pdf-async`.