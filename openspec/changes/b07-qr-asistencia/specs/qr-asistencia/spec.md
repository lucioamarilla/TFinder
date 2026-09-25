# Purpose

Define la emisión y validación del QR de asistencia a una sesión (criterio AE2 9): generado por un usuario autenticado, temporal (expiración TTL), de un solo uso (consumo atómico en Redis) y sin datos personales en su payload (solo ids numéricos y `exp`, con firma HMAC).

## ADDED Requirements

### Requirement: Emisión de QR con firma y expiración
`mesas-api` DEBE emitir, en `POST /api/v1/sesiones/{sesion_id}/qr` (rol auth, 404 si la sesión no existe), un código QR con payload que DEBE contener únicamente `sesion` (id), `u` (usuario id), `exp` (epoch) y `firma` (HMAC-SHA256 truncada), y DEBE guardar en Redis la clave `qr:sesion:{sesion_id}:{usuario_id}` con TTL (10 min) para el control de expiración y single-use.

#### Scenario: Usuario autenticado emite el QR de su sesión
- **WHEN** un usuario autenticado llama a `POST /api/v1/sesiones/3/qr`
- **THEN** obtiene `201` con `qr_data`, `png_base64` y `expira_en_seg`, la clave Redis queda con ese TTL y el payload decodificado no contiene email ni nombre

### Requirement: Validación del QR por el GM (single-use)
`POST /api/v1/sesiones/{sesion_id}/qr/validar` (rol gm) DEBE consumir la clave Redis de forma atómica (`GETDEL`) y, si no existe o no coincide, DEBE responder `409` (QR vencido o ya utilizado); además DEBE re-verificar la firma HMAC y `exp` del payload (defensa en profundidad) y, si pasa, DEBE registrar la asistencia del jugador en `asistencias`.

#### Scenario: Primera validación exitosa
- **WHEN** el GM valida un QR emitido recientemente (`usuario_id` y `qr_data` correctos)
- **THEN** la asistencia se registra en `asistencias` y se responde `200 {"asistencia": "registrada"}`, y la clave Redis desaparece

#### Scenario: Reintento con el mismo QR (double-use)
- **WHEN** el GM intenta validar el mismo `qr_data` por segunda vez
- **THEN** devuelve `409` y no se duplica la fila en `asistencias` (unique `(sesion_id, usuario_id)`)

#### Scenario: QR vencido
- **WHEN** se valida un QR cuyo `exp` ya pasó
- **THEN** devuelve `409` aunque la clave Redis aún exista

### Requirement: Privacidad del payload
El `qr_data` NO DEBE contener email, nombre ni otra información personal; únicamente ids numéricos (`sesion`, `u`) y `exp`. Los logs del servicio NO deben imprimir el contenido completo del QR.

#### Scenario: Decodificación del QR
- **WHEN** se decodifica `qr_data` (base64url + JSON)
- **THEN** las claves presentes son `sesion`, `u`, `exp` y `firma`, y ninguna contiene correo o nombre de persona