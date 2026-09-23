# ADR-007 · QR de asistencia single-use en Redis con firma HMAC

- Estado: **Aceptado**
- Fecha: 2026-09-23

## Contexto

Un gm debe validar la asistencia a una sesión presentando un código QR que (a) no pueda ser forjado por el alumno, (b) expire a los pocos minutos, (c) no pueda reutilizarse la misma captura dos veces y (d) no exponga datos personales del portador (RNF-23 básico).

## Decisión

**QR emitido por mesas-api con firma HMAC + single-use en Redis con GETDEL** (`mesas_api/app/services/qr_asistencia.py`):

- **Token**: payload mínimo `{sesion, u, exp}` firmado con **HMAC-SHA256** (truncado a 32 hex) usando `QR_SECRET`, serializado en base64url JSON — sin JWT para el QR: ahorra headers/claims y el `GETDEL` valida por clave, no por firma.
- **Single-use exacto**: emitir hace `SETEX qr:{sesion}:{usuario} 600`; validar hace **`GETDEL`** → la segunda lectura de la misma captures devuelve `nil` → `409 "QR vencido o ya utilizado"` (sin ventana de reintento).
- **Destino de la firma**: `emitir_qr` devuelve `qr_data`, `png_base64`, `expira_en_seg` y `sesion_id`; el payload no incluye el email.
- **Tiempo de vida**: `TTL_QR = 600` s (10 min), suficiente para una clase.
- Endpoints: `POST /api/v1/sesiones/{id}/qr` (jugador) y `POST /api/v1/sesiones/{id}/qr/validar` (rol gm, `requerir_roles("gm")`).

## Consecuencias

- **Positivas**: imposible de reutilizar (GETDEL atómico), imposible de forjar sin `QR_SECRET`, sin PII en el QR, TTL automático sin tareas de limpieza; evidenciable con `pytest` (1ª validación 200, 2ª 409).
- **Negativas**: firma no-verificable por el gm sin llamar al servicio (el QR solo "existe" si la clave vive en Redis, de modo que un gm necesitaría una clave distinta; en la práctica el gm presenta el dispositivo donde fue emitido); un Redis caído impide tanto emitir como validar; rotación del `QR_SECRET` invalida QRs emitidos antes de la rotación.