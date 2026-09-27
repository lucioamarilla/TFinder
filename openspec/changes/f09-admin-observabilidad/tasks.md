## 1. Implementación

> Nota: la implementación original de esta tarea (`4dcba75`) fue revertida, así que los `[x]` previos no describían el estado real del repo. La lista de abajo es la que quedó después de reimplementar F09.

- [x] 1.1 Backend (ya existía, sin cambios en esta tarea): `/live` y `/ready` en los 4 servicios, `GET /api/v1/dlq`, `POST /api/v1/dlq/{id}/reintentar`, `DELETE /api/v1/dlq/{id}` y `GET /api/v1/event-log?correlation_id=`
- [x] 1.2 `api/http.js`: opción aditiva `aceptarEstados` (default `null`) para leer el body de un 503; sin la opción el comportamiento de `ApiError` no cambia
- [x] 1.3 `endpoints.js`: `adminApi` (live/ready por servicio, dlq, reintentarDlq, descartarDlq); `eventLog` sigue en `notifApi` y ahora acepta filtros (`correlation_id`, `entidad_tipo`, `entidad_id`) con URL-encoding
- [x] 1.4 `services/admin.js`: `estadoDe()`/`getCanalesReales()` (verde/ocre/gris + chips pg/redis/rabbitmq) y `getEventosRecorridos()` reales; se borran `getObservabilidad()` y los JSON `data/admin/observabilidad.json` y `data/admin/dlq.json`
- [x] 1.5 `services/admin.js`: `getDlq()`/`reintentarMensaje()`/`descartarMensaje()` reales; el tipo del mensaje sale de `payload.tipo` (parseado si viene como texto JSON) y la fecha se formatea
- [x] 1.6 `services/admin.js`: `drenarCola()` encadena un `DELETE /dlq/{id}` por mensaje y reporta progreso con `alProgresar`
- [x] 1.7 `services/admin.js`: `getResiliencia()` deriva el breaker del `/ready` real de `mesas-api` + conteo de DLQ; se eliminan `guardarResiliencia()` y `simularCaida()` (no hay backend que los soporte)
- [x] 1.8 `AdminObservabilidadView.vue`: panel por servicio con live/ready y dependencias, tabla `EventOut` (ocurrido/entidad/acción/CID), clic en el CID filtra el recorrido y "Activar seguimiento" pasa a auto-refresco real de 60 s
- [x] 1.9 `AdminDlqView.vue`: columnas reales (tipo, cola, error, fecha), inspección del payload sin toast simulado, drenaje con barra de progreso y "Exportar" descarga el JSON con un Blob
- [x] 1.10 `AdminResilienciaView.vue`: breaker real + estado del operador + DLQ en cola + chips de dependencias; sliders en solo lectura rotulados como ajustes locales; sin "Guardar" ni "Simular caída"; botón "Verificar broker" y enlace a la DLQ
- [x] 1.11 Tests: `tests/unit/admin.spec.js` (19), 2 casos nuevos en `tests/integration/http.spec.js` y el test de admin de `tests/integration/services.spec.js` migrado al contrato real
- [x] 1.12 `npm run lint` y `npm run build` sin errores

## 2. Verificación

- [x] 2.1 `npm test` → 85/85 (63 previos + 22 nuevos)
- [x] 2.2 `/ready` responde 503 con el detalle de dependencias y el panel lo lee sin romperse; sin `aceptarEstados` el 503 sigue lanzando `ApiError`
- [x] 2.3 Servicio caído → panel gris con el detalle del error y la vista sigue navegable
- [x] 2.4 DLQ: normaliza id/cola/error/fecha, parsea el payload, reintenta, descarta y drena mensaje por mensaje
- [ ] 2.5 Recorrido manual end-to-end con los 4 servicios arriba y sesión admin (`admin@tfinder.dev` / `DemoTFinder123!`, con `DEMO_SEED_ENABLED`): Redis detenido → `mesas-api /ready` degradado, DLQ con un mensaje real → reintentar/descartar/drenar, y recorrido con CID filtrable. **Pendiente de verificación manual**
- [x] 2.6 `openspec validate f09-admin-observabilidad` — no se puede ejecutar: el CLI de `openspec` no está instalado en la máquina

## 3. Cierre de la tarea

- [ ] 3.1 Commit en `f/F07_pdf_async` (la entrega de F09 se apila sobre F07 y F08, un solo PR al final)
- [ ] 3.2 Push, pull y PR quedan para el final del proyecto, por decisión del usuario
- [ ] 3.3 Cerrar issue GitHub #34
