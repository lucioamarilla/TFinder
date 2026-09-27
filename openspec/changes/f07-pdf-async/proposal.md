# Proposal: Exportar PDF async con estado 202 → en cola → descargar

## Why

"Exportar PDF" era un mock. Ahora el botón solicita el PDF a `builds-api` (`POST /api/v1/builds/{id}/pdf`), que responde 202 con `documento_id` (turno en cola RabbitMQ), y la UI entra en "Generando…" consultando a `notif-api` (`GET /api/v1/pdf/{doc_id}/estado`): `en_proceso` sigue esperando, `listo` habilita la descarga y `error` muestra "Falló la generación: <motivo>". El estado no bloquea la pantalla y la descarga real (`application/pdf`) se pide con el token de sesión, no abriendo la URL en una pestaña.

## What Changed

- **`src/api/endpoints.js`**: `pdfApi.solicitarBuild(buildId)` (202 hacia builds-api), `pdfApi.estado(docId)` contra `GET /api/v1/pdf/{id}/estado` (JSON con `estado ∈ {en_proceso, listo, error}`; 404 si el worker todavía no registró el documento) y `pdfApi.descargar(docId)`.
- **`src/api/http.js`**: nuevo `apiBlob()` hermano de `api()`, que devuelve `{status, blob, encabezados}`. Comparte token, `X-Correlation-Id`, timeout y rama 401 con `api()`, cuya forma de retorno no cambia. `notif_api/app/routes/v1/pdf.py` declara `Depends(usuario_actual)`, así que la descarga necesita el token: `window.open` no lo envía y siempre recibía 401.
- **`src/composables/usePdfDescarga.js`** (nuevo): máquina `inactivo → enviando → en_cola → descargando → listo/error/cancelado`, polling de 2 s del estado con techo de 30 intentos, y `descargar()` que trae el PDF como blob y lo guarda con `URL.createObjectURL` + `<a download>`, tomando el nombre de `content-disposition`.
- **`src/views/BuildDetailView.vue`**: botón "Exportar PDF" con los 4 estados, botón "Cancelar" mientras está en cola y aviso por toast cuando queda listo o falla.
- **`src/views/BuildHistorialView.vue`**: mismo patrón reemplazando el mock `exportarHistorial`.
- **`src/config/features.js`**: `builds` y `admin` pasan a `available: true`; sin esto el guard redirige las 5 rutas `/builds/*` y las 10 `/admin/*` a `ComingSoonView` y el flujo no es alcanzable.

## Impact

- Descarga real `application/pdf` desde `notif-api` con el token de sesión (verificado en su momento con curl: 1263 bytes, PDF 1 página para build 1).
- Sin cambios de backend (B08 ya expone los endpoints de builds y PDF). DiarioEditorView conserva su flujo (no existe endpoint `diario/pdf` en feed-api).
- Pendiente de verificación manual en navegador: el catálogo de `services/builds.js` sigue mock, así que el `id` de la ruta puede no existir en builds-api y el POST devuelva 404 (la UI lo muestra como error).