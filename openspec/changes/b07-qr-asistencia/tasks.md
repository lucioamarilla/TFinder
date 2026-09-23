## 1. DDL y servicio de QR

- [x] 1.1 `mesas_api/app/schema.sql`: tablas `sesiones` (id, mesa_id FK, fecha, estado) y `asistencias` (id, sesion_id FK, usuario_id, fecha, unique (sesion_id, usuario_id))
- [x] 1.2 `mesas_api/app/services/qr_asistencia.py`: `generar_sesion_qr` (HMAC + qrcode PNG + SETEX TTL 600) y `validar_sesion_qr` (GETDEL + re-check firma/exp)

## 2. Modelo, controlador y rutas

- [x] 2.1 `mesas_api/app/models/sesiones.py`: `obtener_sesion`, `registrar_asistencia` (ON CONFLICT DO NOTHING)
- [x] 2.2 `mesas_api/app/controllers/sesiones_controller.py`: emitir (404 si no existe sesión) y validar (400/409)
- [x] 2.3 `mesas_api/app/routes/v1/sesiones.py`: `POST /{sesion_id}/qr` (auth, 201) y `POST /{sesion_id}/qr/validar` (gm); schemas `QROut`/`QrValidate`; registrar router en `main.py`

## 3. Verificación (done)

- [x] 3.1 Emitir QR → `201`; `qr_data` decodificado = solo `sesion`/`u`/`exp`/`firma` (sin email ni nombre)
- [x] 3.2 Validar 1ª vez → `200` + fila en `asistencias`; 2ª vez mismo `qr_data` → `409`; asistencia no duplicada
- [x] 3.3 Firma alterada → `400`; `exp` pasado → `409`; sesión inexistente → `404`
- [x] 3.4 Clave Redis `qr:sesion:*` con TTL y que desaparece tras validar
- [x] 3.5 `openspec validate b07-qr-asistencia`

## 4. Cierre de la tarea

- [x] 4.1 Rama `f/B07_qr_asistencia`, commit `feat(sesiones): QR de asistencia temporal single-use con firma HMAC (#20)`, merge y archivar
- [ ] 4.2 Cerrar issue GitHub #20