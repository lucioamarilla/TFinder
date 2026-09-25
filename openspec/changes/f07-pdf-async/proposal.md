# Proposal: Exportar PDF async con estado 202 → en cola → descargar

## Why

"Exportar PDF" era un mock. Ahora el botón solicita el PDF a `builds-api` (`POST /api/v1/builds/{id}/pdf`), que responde 202 con `documento_id` (turno en cola RabbitMQ), y la UI entra en "Generando…" consultando a `notif-api` (`GET /api/v1/pdf/{doc_id}`): 404 = aún en proceso, 200 = `application/pdf` listo para descargar. El estado no bloquea la pantalla (badge async) y los errores muestran "Falló la generación: <motivo>".

## What Changed

- **`src/api/endpoints.js`**: `pdfApi.solicitarBuild(buildId)` (202 hacia builds-api) y `pdfApi.estado(docId)` (404/200 hacia notif-api).
- **`src/composables/usePdfDescarga.js`** (nuevo): máquina `inactivo → enviando → en_cola → listo/error`, polling de 2 s del estado y `abrirDescarga()` que abre el endpoint real de PDF.
- **`src/views/BuildDetailView.vue`**: botón "Exportar PDF" con los 4 estados + badge "en cola (async)" + error visible.
- **`src/views/BuildHistorialView.vue`**: mismo patrón reemplazando el mock `exportarHistorial`.

## Impact

- Descarga real `application/pdf` desde `notif-api` (verificado: 1263 bytes, PDF 1 página para build 1).
- Sin cambios de backend (B08 ya expone los endpoints de builds y PDF). DiarioEditorView conserva su flujo (no existe endpoint `diario/pdf` en feed-api).