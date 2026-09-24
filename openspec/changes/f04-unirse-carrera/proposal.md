# Proposal: Unirse a una mesa con carrera y idempotencia visible (B06)

## Why

El botón "Quiero unirme" simulado no ejercía la doble barrera de B06 (reserva de vacante en Redis + idempotencia). F04 dispara la solicitud real (`POST /api/v1/mesas/{id}/solicitudes`), persiste la `Idempotency-Key` por `(mesa, usuario)` en `localStorage` para reenvíos sin doble efecto, y hace visible la disputa por la última vacante (201 vs 409) en la UI.

## What Changes

- **`src/api/endpoints.js`**: `mesasApi.solicitarUnion(id, cuerpo, key)` contra `/api/v1/mesas/{id}/solicitudes` pasando `Idempotency-Key` explícita.
- **`src/composables/useSolicitud.js`** (nuevo): key persistida por `(mesa, usuario)` en `localStorage` (`tfinder-idem:solicitud:`) y estado `inactivo|enviando|solicitada|agotada|error` con mensaje.
- **`MesaDetailView.vue`**: botón con etiquetas por estado, `disabled`+`aria-busy` mientras envía, alerta de "última vacante en disputa" cuando `jugadores === plazas - 1`, aviso "Cupo agotado" visible con el mensaje del backend, y toast según resultado (201 → solicitada / 409 → sin vacantes).

## Capabilities

- **New Capabilities**: `unirse-carrera-idempotente` — solicitud real de la doble barrera con idempotencia visible del lado del cliente.

## Impact

- Requiere sesión (`Authorization`). Los `401/403/422` ya los maneja la capa HTTP de F01. La ocupación reflejada en la UI proviene del backend.