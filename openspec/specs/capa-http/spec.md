# Purpose

Definir la capa HTTP del frontend que conecta el cliente Vue con los 4 servicios reales del backend (4001–4004 si se re-mapan; aquí 8001–8004): un cliente `fetch` con timeout, headers de trazabilidad y sesión, normalización de errores a `ApiError` y un catálogo de endpoints por servicio. No migra vistas (F03+ lo hará).

## Requirements

### Requirement: Cliente HTTP unificado
`api(servicio, ruta, opts)` DEBE resolver requests a cualquier servicio configurable en `src/config/api.js`, respetar un timeout de 8 s, inyectar `X-Correlation-Id` (nuevo por request), `Authorization: Bearer` cuando existe sesión e `Idempotency-Key` cuando el request tiene cuerpo; y DEBE retornar `{status, datos, idempotenciaKey}`.

#### Scenario: Request sin sesión
- **WHEN** se llama `api('mesas', '/api/v1/mesas')` sin token guardado
- **THEN** la request no lleva `Authorization` y responde con `{status, datos}`
#### Scenario: Request con cuerpo auto-Idempotency-Key
- **WHEN** se envía un POST con `cuerpo`
- **THEN** la request lleva un `Idempotency-Key` generado (o el provisto)

### Requirement: Manejo de 401 y de errores del backend
Ante un `401`, el cliente DEBE limpiar la sesión y redirigir a `/login?redirect=...`; ante un error con formato `{error:{codigo,mensaje}}`, DEBE propagarse como `ApiError` con `.codigo` y `.mensaje`.

#### Scenario: 401 expulsa
- **WHEN** el backend responde 401
- **THEN** la sesión se limpia, se navega a `/login?redirect=<ruta actual>` y se lanza `ApiError(401, 'Sesión expirada')`
#### Scenario: Error normalizado
- **WHEN** el backend responde un error JSON `{error: {codigo, mensaje}}` no 2xx
- **THEN** se lanza `ApiError` con esos `codigo`/`mensaje` (fallback `HTTP <status>`)

### Requirement: Catálogo de endpoints reales por servicio
`src/api/endpoints.js` DEBE agrupar endpoints reales del backend por servicio (auth, mesas, notif) usando el cliente `api`.

#### Scenario: Base lista para F03–F09
- **WHEN** se inspecciona `src/api/endpoints.js`
- **THEN** existen `authApi`, `mesasApi` y `notifApi` con rutas del catálogo real (`/api/v1/*` sobre 8001–8004)