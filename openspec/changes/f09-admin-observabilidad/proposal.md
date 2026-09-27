# Proposal: Admin con evidencia real — observabilidad, DLQ y broker

## Why

Tres vistas admin estaban mockeadas. Ahora leen datos reales:
- `AdminObservabilidadView`: `/live` y `/ready` de los 4 servicios (verde/ocre/gris) + el `event-log` con `correlation_id` filtrando por recorrido.
- `AdminDlqView`: `GET /api/v1/dlq` real (payload + error + fecha), "Reintentar" reencola a la cola original y "Descartar" elimina.
- `AdminResilienciaView`: breaker derivado del `/ready` real (pg/redis/rabbitmq) + conteo de DLQ; "Simular caída" → "Verificar broker".

## What Changed

- **Backend**: sin cambios en esta tarea. `/live` y `/ready` ya existían en los 4 servicios, y `notif-api` ya exponía `GET /api/v1/dlq`, `POST /api/v1/dlq/{id}/reintentar`, `DELETE /api/v1/dlq/{id}` y `GET /api/v1/event-log`.
- **`src/api/http.js`**: opción aditiva `aceptarEstados` (default `null`). `/ready` responde 503 con el detalle de dependencias en el body, y sin esta opción `api()` lo convertiría en `ApiError` y tiraría la información.
- **`src/api/endpoints.js`**: `adminApi` (live/ready por servicio, dlq, reintentarDlq, descartarDlq). `eventLog` no se duplica: se queda en `notifApi` y ahora acepta filtros (`correlation_id`, `entidad_tipo`, `entidad_id`).
- **`src/services/admin.js`**: `estadoDe()`/`getCanalesReales()`, `getEventosRecorridos()`, `getDlq()`/`reintentarMensaje()`/`descartarMensaje()`/`drenarCola()` y `getResiliencia()` reales. Se eliminan `getObservabilidad()`, `guardarResiliencia()`, `simularCaida()` y los JSON `data/admin/observabilidad.json` y `data/admin/dlq.json`.
- **Vistas**: `AdminObservabilidadView` (tono gris, chips de dependencias, filtro por CID y auto-refresco real), `AdminDlqView` (columnas reales, inspección sin toast, drenaje con progreso, export JSON real), `AdminResilienciaView` (breaker + chips + DLQ en cola, parámetros en solo lectura).

## Desviaciones respecto del enunciado

- **No hay columna de nivel de log.** `EventOut` no expone severidad, así que la tabla muestra ocurrido/entidad/acción/CID en lugar de INFO/WARN/ERROR inventados.
- **No existe `reintentos` en la DLQ.** La tabla real es `id, cola, payload, error, fecha`; la columna "Reintentos" del mock se eliminó y el nombre del mensaje se deriva de `payload.tipo`.
- **`drenarCola` es un bucle de `DELETE`, no un endpoint.** El backend no expone drenaje masivo, así que el servicio descarta mensaje por mensaje y la vista muestra el progreso.
- **Los parámetros de resiliencia no se guardan.** No hay endpoint que los persista, así que los sliders quedan en solo lectura y rotulados como ajustes locales del códice.

## Impact

- El panel de salud tolera respuestas mixtas: un 503 en `/ready` se lee, un servicio caído se marca gris y la vista no se rompe.
- DLQ real: listar, inspeccionar el payload, reintentar (republica y borra el registro), descartar y drenar.
- El breaker se deriva del estado real de `mesas-api`, no de un toggle simulado.
- Pendiente de verificación manual: recorrido con los 4 servicios arriba y sesión admin.

## Hallazgo de seguridad (fuera de alcance)

`AuthRegistro.rol` acepta `admin`, así que un usuario puede auto-registrarse con rol administrador. No se toca el backend en esta tarea; queda documentado para corregirlo por separado.
