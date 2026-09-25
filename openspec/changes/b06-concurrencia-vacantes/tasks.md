## 1. Modelo y migración

- [x] 1.1 `mesas_api/app/schema.sql`: `ALTER TABLE mesas ADD COLUMN IF NOT EXISTS jugadores_actuales INT NOT NULL DEFAULT 0` + tabla `solicitudes_uniones` (id, mesa_id FK, usuario_id, estado, idem_key, fecha) e índice
- [x] 1.2 `mesas_api/app/models/mesa.py`: `ocupar_vacante(mesa_id) -> bool` con `UPDATE ... WHERE jugadores_actuales < jugadores_max RETURNING id`
- [x] 1.3 `mesas_api/app/models/solicitudes.py`: `crear_solicitud(mesa_id, usuario_id, estado, idem_key)` y `obtener_solicitud_por_key(mesa_id, usuario_id, idem_key)` con fila y listado simple

## 2. Servicios y controlador

- [x] 2.1 `mesas_api/app/services/idem.py`: `obtener_resultado(key)` / `guardar_resultado(key, resultado)` en Redis (prefijo `idem:solicitud:`, TTL 86400)
- [x] 2.2 `mesas_api/app/controllers/solicitudes_controller.py`: `solicitar_union(mesa_id, usuario_id, idem_key)` con idem → reserva (409 procesándose) → ocupar_vacante (409 cupo agotado) → crear_solicitud → publicar `mesa.aceptada` → liberar (finally)

## 3. Ruta y registro

- [x] 3.1 `mesas_api/app/routes/v1/solicitudes.py`: `POST /api/v1/mesas/{mesa_id}/solicitudes` con header `Idempotency-Key` (201/409) y `GET` de solicitudes de la mesa
- [x] 3.2 Registrar router en `mesas_api/main.py`

## 4. Verificación (done)

- [x] 4.1 Mesa `jugadores_max=1`: dos requests concurrentes → un `201` y un `409`
- [x] 4.2 `jugadores_actuales` nunca supera `jugadores_max` tras varios intentos
- [x] 4.3 Replay de la key ganadora → mismo resultado, sin doble ocupación ni fila duplicada
- [x] 4.4 Evento `mesa.aceptada` publicado y notificación visible en `notif-api`
- [x] 4.5 `openspec validate b06-concurrencia-vacantes`

## 5. Cierre de la tarea

- [x] 5.1 Rama `f/B06_concurrencia_vacantes`, commit `feat(concurrencia): doble barrera contra la carrera por la última vacante e idempotencia por key (#19)`, merge y archivar
- [x] 5.2 Cerrar issue GitHub #19