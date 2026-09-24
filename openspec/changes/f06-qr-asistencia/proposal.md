# Proposal: Sesión en curso con QR de asistencia (single-use) y validación del GM

## Why

Los jugadores no tenían un pase de asistencia real a las sesiones. Nueva pantalla `SesionQrView` conectada al contrato B07 de `mesas-api`: el jugador genera su QR single-use (`POST /sesiones/{id}/qr`), que llega como PNG + `qr_data` firmado + TTL (600 s) y se muestra con cuenta regresiva. El GM valida pegando el `qr_data` (`POST /sesiones/{id}/qr/validar`): primera vez 200 "Asistencia registrada", la misma clave da 409 single-use. El payload del QR no expone email ni nombre (solo `sesion`, `u`, `exp`, `firma`).

## What Changed

- **`src/api/endpoints.js`**: `sesionesApi.qr(sesionId)` y `sesionesApi.validarQr(sesionId, {usuario_id, qr_data})`.
- **`src/views/gestion/SesionQrView.vue`** (nuevo): generación del QR jugador con countdown, botón "Generar otro QR" al vencer, `details` con el `qr_data`; y panel del GM (según rol del token de F02) para pegar/validar, decodificando el `u` del payload para armar la validación.
- **`src/router/index.js`**: ruta `/mesas/:id/sesiones/:sesionId/qr` (`mesa-sesion-qr`), solo `auth/admin`.
- **`src/views/gestion/SesionesView.vue`**: enlace "Asistencia (QR)" por sesión en estados abierta/confirmada/ejecutada.

## Impact

- Requiere sesión; "Validar asistencia" solo con rol `gm` (el backend devuelve 403 de lo contrario).
- Sin cambios de backend: los endpoints B07 ya existían en `mesas-api` (verificados por curl: PNG + TTL 600, 200 → 409 single-use).