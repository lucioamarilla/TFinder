# Purpose

Nueva pantalla "Sesión en curso · QR" dentro de la gestión de una mesa. El jugador obtiene su QR de asistencia single-use (PNG + `qr_data` firmado con TTL de Redis), y el GM lo valida: la primera vez registra la asistencia (200) y cualquier reuso de la misma clave falla con 409. El payload del QR no contiene email ni nombre.

## ADDED Requirements

### Requirement: Generación del QR de asistencia con countdown
`SesionQrView` DEBE permitir a cualquier usuario autenticado generar el QR llamando a `sesionesApi.qr`. La vista DEBE mostrar el PNG (`data:image/png;base64,...`), los segundos restantes (countdown de UX iniciado desde `expira_en_seg`, con margen visual) y el botón "Generar otro QR" para reemplazar la clave cuando venza. El `qr_data` DEBE ser visible (para que el GM lo pegue) y NO DEBE contener email ni nombre del jugador.

#### Scenario: TTL del QR y regeneración
- **GIVEN** un jugador autenticado en el pase de asistencia
- **WHEN** genera su QR
- **THEN** el backend responde `png_base64`, `qr_data` y `expira_en_seg=600`
- **AND** la vista muestra el QR y el countdown
- **AND** al vencer, "Generar otro QR" re-emite una clave nueva

### Requirement: Validación single-use por el GM
Un usuario con rol `gm` DEBE poder pegar el `qr_data` y validarlo vía `sesionesApi.validarQr`. La primera validación DEBE mostrar "Asistencia registrada" (200). Validar de nuevo la misma clave DEBE mostrar el mensaje del backend de 409 ("QR vencido o ya utilizado") y marcar la UI como usado.

#### Scenario: Reuso del mismo QR
- **GIVEN** un GM con el `qr_data` de un jugador ya validado
- **WHEN** intenta validarlo una segunda vez
- **THEN** la respuesta del backend es 409 single-use
- **AND** la vista muestra el error del backend y no repite la asistencia