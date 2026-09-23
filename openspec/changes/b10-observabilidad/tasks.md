## 1. Base de observabilidad (ya presente desde B02/B05)

- [x] 1.1 `app/infra/logge.py`: JsonFormatter con `ts/nivel/servicio/mensaje/correlation_id` + ContextVar
- [x] 1.2 `app/middleware/log_context.py`: header `X-Correlation-Id` → ContextVar → respuesta
- [x] 1.3 `app/infra/ready.py`: check postgres + redis + rabbitmq (200/503)
- [x] 1.4 `/live` y `/ready` en mesas/builds/feed/notif main

## 2. Verificación (done)

- [x] 2.1 `GET /live` 200 y `GET /ready` 200 en los 4 servicios (8001–8004)
- [x] 2.2 `/ready` 503 con postgres detenido; `/live` sigue 200 (restaurar postgres)
- [x] 2.3 Recorrido punta a punta con `X-Correlation-Id`: request → `mesa.solicitada` → consumidor notif, mismo CID en ≥3 logs de 2 servicios
- [x] 2.4 Logs en JSON y sin tokens/passwords/`qr_data` completos
- [x] 2.5 `openspec validate b10-observabilidad`

## 3. Cierre de la tarea

- [ ] 3.1 Rama `f/B10_observabilidad`, commit, merge y archivar
- [ ] 3.2 Cerrar issue GitHub #23