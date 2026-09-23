# Design: QR de asistencia temporal y de un solo uso

## Context

B06 dejó `mesas_db` con `mesas`, `usuarios`, `matchmaking`, `solicitudes_uniones` y `jugadores_actuales`. B07 agrega las sesiones de juego y su QR de asistencia: temporal (TTL), single-use y privado. Se reutilizan auth (B03), Redis (B01/B04) y el manejo de errores (`manejar_http` formatea 400/409/404).

## Decisions

**D1 — DDL aditivo en `mesas_db`.**
`schema.sql` agrega `sesiones(id, mesa_id FK, fecha, estado CHECK abierta/cerrada)` y `asistencias(id, sesion_id FK, usuario_id, fecha)` con unique `(sesion_id, usuario_id)` (idempotente para double-use en B11). Migración por `IF NOT EXISTS`, igual que B06.

**D2 — Payload mínimo y firma HMAC.**
`qr_data` = base64url JSON `{sesion, u, exp, firma}` con `firma = HMAC-SHA256[QR_SECRET](cuerpo)` truncada a 32 hex. Solo ids numéricos + `exp`; NUNCA email ni nombre (privacidad AE2 9). `QR_SECRET` por env con default de desarrollo; `exp = now + TTL_QR (600 s)`.

**D3 — Single-use atómico en Redis (GETDEL).**
Emisión: `SETEX qr:sesion:{sesion_id}:{usuario_id} 600 qr_data`. Validación: `GETDEL` consume la clave atómicamente → si no existe o difiere → `409`. El `GETDEL` garantiza que aunque dos validaciones lleguen juntas, solo una lee la clave (single-use real, verificado en B11).

**D4 — Defensa en profundidad: re-verificar firma y exp.**
Después del `GETDEL`, se re-valida `firma` (HMAC `compare_digest`) → `400` si inválida, y `exp` → `409` si vencido, incluso si la clave Redis aún existiera (p. ej. reloj corrido del cliente). No se confía solo en Redis.

**D5 — Asistencia registrada de forma idempotente.**
`registrar_asistencia(sesion_id, usuario_id)` con `INSERT ... ON CONFLICT (sesion_id, usuario_id) DO NOTHING` y retorno de si hubo fila nueva; el GM no puede duplicar asistencias aunque re-envíe la petición (doble barrera con B11).

**D6 — Rutas y errores.**
`POST /api/v1/sesiones/{sesion_id}/qr` (auth) → `201` con `QROut{qr_data, png_base64, expira_en_seg, sesion_id}`; 404 si la sesión no existe. `POST /api/v1/sesiones/{sesion_id}/qr/validar` (gm, body `{usuario_id, qr_data}`) → `200 {"asistencia":"registrada"}` o `400/409`. Se obtiene `usuario`, se valida la sesión con un helper de modelo (404), se emite. Logs (B10) no imprimen el QR.

## Risks

- **QR_SECRET default de desarrollo**: en producción el env debe fijarse; el default solo sirve local (mismo criterio que pwd del compose).
- **`exp` en cliente como única confianza**: la clave Redis TTL es la fuente primaria; `exp` es defensa extra. Si Redis cae, emisión falla (mejor que emitir sin control).
- **QR con `u` (id numérico)**: es un identificador, no dato personal; cumple el criterio de no exponer email/nombre.
- **Front F06**: el `png_base64` permite mostrar el QR sin librerías extra.

## Migration Plan

1. `mesas_api/app/schema.sql`: tablas `sesiones` y `asistencias`.
2. `mesas_api/app/services/qr_asistencia.py`: emisión + validación (HMAC, `GETDEL`, exp).
3. `mesas_api/app/models/sesiones.py`: `obtener_sesion`, `registrar_asistencia` (ON CONFLICT).
4. `mesas_api/app/controllers/sesiones_controller.py` + `mesas_api/app/routes/v1/sesiones.py` + schemas (`QROut`, `QrValidate`) + registro en `main.py`.
5. Verificación en contenedor: emitir → decodificar payload (sin email) → validar (200) → segunda validación (409) → expiración; `asistencias` con 1 fila.
6. Rama `f/B07_qr_asistencia`, commit, merge, archivar, cerrar #20.

## Verification

- `POST /api/v1/sesiones/3/qr` (auth) → `201`; `qr_data` decodificado: `sesion`, `u`, `exp`, `firma` y sin email/nombre.
- Clave Redis `qr:sesion:3:{u}` existe con TTL ~600.
- `POST .../qr/validar` (gm) 1ª vez → `200` + fila en `asistencias`; 2ª vez (mismo `qr_data`) → `409`; re-envío tras validar → no duplica asistencia.
- QR con firma alterada → `400`; con `exp` pasado → `409`.
- `openspec validate b07-qr-asistencia`.