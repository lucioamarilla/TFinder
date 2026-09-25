# Proposal: QR de asistencia temporal y de un solo uso

## Why

Criterio AE2 9: cada sesión necesita un mecanismo de asistencia que sea temporal (TTL corto), de un solo uso y sin datos personales en el payload. El QR incluye solo `sesion`, `exp` y una firma HMAC-SHA256; el estado de validez vive en Redis (`getdel` = consumo atómico) y el GM lo valida marcando `asistencias`.

## What Changes

- **DDL en `mesas_db`**: tablas `sesiones` (id, mesa_id FK, fecha, estado) y `asistencias` (id, sesion_id FK, usuario_id, fecha, unique `(sesion_id, usuario_id)`) — base para F06 y B11 (double-use → 409).
- **Servicio `mesas_api/app/services/qr_asistencia.py`**: emisión con `qrcode` (PNG base64 + `qr_data` compacto) y firma HMAC (`QR_SECRET`, `exp = now + 600 s`); single-use vía `SETEX qr:sesion:{id}:{user} TTL qr_data` y validación con `GETDEL` (atómico) + re-verificación de firma y `exp` (defensa en profundidad, no confía solo en Redis).
- **Controlador/modelo de sesiones**: `sesiones_controller.py` (emitir/validar, 404 si la sesión no existe, `registrar_asistencia` idempotente por unique) + `models/sesiones.py`.
- **Rutas**: `POST /api/v1/sesiones/{sesion_id}/qr` (rol `auth`) → `201` con `qr_data`, `png_base64` y `expira_en_seg`; `POST /api/v1/sesiones/{sesion_id}/qr/validar` (rol `gm`, body `{usuario_id, qr_data}`) → `200 {"asistencia":"registrada"}` o `409` (vencido/usado) / `400` (firma inválida).
- **Privacidad**: el payload solo lleva ids numéricos y `exp`; nunca email ni nombre (verificación decodificando `qr_data`). Logs no imprimen el contenido del QR.

## Capabilities

- **New Capabilities**: `qr-asistencia` — emisión y validación de QR de asistencia con firma HMAC, expiración y single-use atómico (Redis `GETDEL`).
- **Modified Capabilities**: `eventos-rabbitmq`/`concurrencia-vacantes` — sin cambios; las rutas `sesiones/*` son nuevas y conviven con mesas/matchmaking/solicitudes.

## Impact

- `mesas_db`: DDL aditivo (tablas nuevas), no destructivo.
- `mesas-api`: endpoint nuevo; reutiliza auth (Bearer) y el manejo de errores existente (`manejar_http` para 400/409/404).
- Disponible para F06 (frontend muestra QR y el GM lo valida) y B11 (prueba de double-use).