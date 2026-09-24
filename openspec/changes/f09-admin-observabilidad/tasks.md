## 1. Implementación

- [x] 1.1 Backend: rutas DLQ (GET/POST reintentar/DELETE), event-log con correlation_id, columna + índice aditivos
- [x] 1.2 Consumers/workers pasan correlation_id a `registrar_evento`
- [x] 1.3 `endpoints.js`: `adminApi` (live/ready/dlq/eventLog/reintentarDlq/descartarDlq)
- [x] 1.4 `services/admin.js`: getObservabilidad/getDlq/getResiliencia reales
- [x] 1.5 `AdminObservabilidadView.vue`: panel por servicio + filtro por CID
- [x] 1.6 `AdminDlqView.vue`: tabla real + reintentar/descartar + inspección de payload
- [x] 1.7 `AdminResilienciaView.vue`: estado real broker + verificar
- [x] 1.8 `npm run build` compila sin errores

## 2. Verificación

- [x] 2.1 DLQ real: evento `mesa.desconocido` → dlq.general; reintentar → 200 + reencola; descartar → borra; 404 si no existe
- [x] 2.2 Observabilidad: redis detenido → mesas `/ready` degradado; restaurado → listo
- [x] 2.3 CID punta a punta: recorrido de solicitud → event-log con correlationId real, filtro devuelve el evento
- [x] 2.4 `openspec validate f09-admin-observabilidad`

## 3. Cierre de la tarea

- [ ] 3.1 Rama `f/F09_admin_observabilidad`, commit, merge y archivar
- [ ] 3.2 Cerrar issue GitHub #34