# Proposal: Capa HTTP del frontend — cliente unificado y contrato real

## Why

El frontend Vue consume hoy `services/*.js` mockeados. F01 habilita el criterio AE2·2 (integración real): una capa `fetch` que inyecta `Authorization`, `Idempotency-Key` y `X-Correlation-Id`, trata `401 → login`, normaliza `{error:{codigo,mensaje}}` a `ApiError` y agrupa los endpoints reales por servicio (catálogo B02: 8001–8004). No migra vistas todavía (F03+).

## What Changes

- **`src/config/api.js`**: orígenes por servicio (`VITE_*_API` con default 8001–8004) y `apiUrl()`.
- **`src/api/http.js`**: `api(servicio, ruta, opts)` con timeout 8 s (AbortController), headers `Content-Type`/`X-Correlation-Id` (nuevo por request), `Authorization` si hay token, `Idempotency-Key` si hay cuerpo, `401 → clearSession + /login?redirect`, y conversión de errores a `ApiError{codigo,mensaje,detalles}`; retorna `{status,datos,idempotenciaKey}`.
- **`src/api/endpoints.js`**: `authApi` (register/login/logout/me), `mesasApi` (listar/detalle/crear/solicitarUnion), `notifApi` (notificaciones/leida/eventLog/pdf) como base para F03–F09.
- **`src/composables/useAuth.js`**: exports aditivos `currentAccessToken()` y `clearSession()` (no rompe las vistas actuales; F02 migra la auth completa).

## Capabilities

- **New Capabilities**: `capa-http` — cliente unificado hacia el backend real (auth, headers de trazabilidad, manejo de errores, catálogo de endpoints).

## Impact

- No cambia vistas: `services/*.js` mockeados siguen usados hasta F03. `dist/` del build no se versiona (gitignore existente).