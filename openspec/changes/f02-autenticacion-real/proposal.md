# Proposal: Autenticación real — login, registro, recuperar y perfil en AppHeader

## Why

El login social simulado (`useAuth.js` con roles en `localStorage`) impide cumplir AE2·2 (integración real). F02 conecta el frontend a `/api/v1/auth/*` de mesas-api y a `notif-api` para el email transaccional de recuperación.

## What Changes

- **`src/composables/useAuth.js`**: reemplazado por sesión con tokens (`access`/`refresh` + `user` persistidos en `tfinder-sesion`), `login()` contra `authApi.login` + `authApi.me`, `logout()` que revoca la sesión en Redis, `clearSession()`/`currentAccessToken()`/`currentRole()` compatibles con F01 y guard. Roles backend (`usuario`/`gm`/`admin`) se mapean a las claves de navegación (`auth`/`admin`/`guest`).
- **`LoginView.vue`**: login real con `ApiError` (`e.mensaje`), redirección a `route.query.redirect`, rol `admin` → `/admin/moderacion`; se quitó el selector falso "Recuérdame".
- **`RegistroView.vue`**: `authApi.register` → `login` automático → dashboard; 400 de duplicado se muestra como "ese correo ya está registrado".
- **`RecuperarView.vue`**: `POST /api/v1/auth/recuperar` en notif; éxito → "revisá tu casilla"; timeout 8 s → mensaje de servicio caído.
- **`notif-api` (backend)**: nuevo router `POST /api/v1/auth/recuperar` (202, respuesta genérica anti-enumeración) que envía el email de recuperación por SMTP→MailHog usando el path transaccional existente.

## Capabilities

- **New Capabilities**: `autenticacion-real` — sesión con tokens contra el backend (register/login/logout/me), recuperación vía notif y perfil en AppHeader.

## Impact

- `AppHeader`, `MobileMenuPanel`, `AppFooter`, guard y vistas usan `useAuth()`/`currentRole()` que mantienen su misma API (aditivo). Los `services/*.js` mockeados siguen intactos para otras vistas (F03+). Se rebuildó la imagen `notif-api`.