## 1. Implementación

- [x] 1.1 `feed_api`: `services/eventos.py` + `routes/v1/diario.py` (POST diario/pdf → 202) con auth JWT
- [x] 1.2 `notif_api`: `GET /pdf/{id}/estado` + `marcar_documento_error` + worker marca `error`
- [x] 1.3 `notif_api`: SSE `/notificaciones/stream` + hub alimentado por consumers
- [x] 1.4 Tests: dlq operativo, ready degradado, event-log correlation
- [x] 1.5 Evidencias nuevas en AE2/evidencias + EVIDENCIAS.md

## 2. Verificación

- [x] 2.1 202 diario → estado listo → `application/pdf` real; 401 sin token
- [x] 2.2 Fallo de generación → `estado:error` + DLQ
- [x] 2.3 SSE emite notificación en vivo (curl -N) y polling intacto
- [x] 2.4 pytest pasa (nuevos + existentes)
- [x] 2.5 `openspec validate f-backend-32-34`

## 3. Cierre

- [ ] 3.1 Rama `f/B_pendiente_32_34`, commits, merge, archivo de spec
- [ ] 3.2 `gh issue close` #32, #33, #34