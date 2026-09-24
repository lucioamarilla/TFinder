# Proposal: Matchmaking con "llamado abierto" y cuenta regresiva TTL (Redis)

## Why

`MatchmakingView` dejó de ser un catálogo local estático: el GM abre un llamado real contra `POST /api/v1/matchmaking/{mesa}/abrir` (Redis TTL 120 s) y el frontend muestra el `ttl_restante` real de Redis vía polling de `/matchmaking/{mm_id}/estado`. Los jugadores se anotan a la carrera usando la solicitud idempotente de B06/F04 (`POST /mesas/{id}/solicitudes`), que trae la validación real de la vacante (201/409). La expiración del llamado nunca depende del timer del navegador: Redis es la autoridad.

## What Changed

- **`src/api/endpoints.js`**: nuevo `matchmakingApi` con `abrir(mmId)` (POST) y `estado(mmId)` (GET sobre `mesas-api`).
- **`src/composables/useLlamado.js`** (nuevo): gestiona `abrir`, captura el `matchmaking_id` devuelto por el backend y hace polling periódico (2 s) de `estado`, exponiendo `estado`/`ttl` en vivo; al expirar Redis, `estado=cerrado` y ttl=0 sin intervención cliente.
- **`src/components/LlamadoCard.vue`** (nuevo): tarjeta por mesa que muestra el chip `estado: abierto · N s`, el botón GM "Abrir llamado" (solo rol `gm`) y el botón jugador "Anotarse al llamado" que usa `useSolicitud` de F04 y traduce 201→"¡Vacante reservada!" / 409→"Cupo agotado".
- **`src/views/MatchmakingView.vue`**: usa el catálogo real de mesas de F03 (`getMesas()`), filtra por `vacante`, muestra el chip de caché y renderiza las `LlamadoCard`.

## Impact

- Requiere sesión: "Abrir llamado" solo para rol `gm` (403 en el backend si no), "Anotarse" para cualquier usuario autenticado.
- Depende de la doble barrera B06 ya implementada (solicitud idempotente con `Idempotency-Key`).
- Sin cambios de backend (endpoints y TTL ya existentes en `mesas-api`).