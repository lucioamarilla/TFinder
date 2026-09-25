# Purpose

Conectar la autenticación del frontend Vue con los servicios reales: registro/login/logout contra `/api/v1/auth/*` de mesas-api, email transaccional de recuperación contra notif-api, y perfil real del usuario en el shell (AppHeader) en lugar de perfiles hardcodeados.

## ADDED Requirements

### Requirement: Sesión basada en tokens
`useAuth` DEBE emitir y guardar `access_token`/`refresh_token` al loguearse contra `authApi.login`, cargar el perfil con `authApi.me`, persistir la sesión (`tfinder-sesion`) y exponer `currentAccessToken()`, `clearSession()` y `currentRole()` compatibles con la capa HTTP y el guard del router.

#### Scenario: Login real
- **WHEN** un usuario envía credenciales válidas a `/api/v1/auth/login`
- **THEN** se guardan `access`/`refresh`, el perfil se obtiene de `/auth/me` y `useAuth.user` deja de usar `PROFILES` hardcodeado
#### Scenario: Logout revoca
- **WHEN** el usuario hace logout
- **THEN** se llama a `/api/v1/auth/logout` (revoca la sesión en Redis) y se limpia el estado local; reutilizar el token revocado produce `401`

### Requirement: Registro real
`RegistroView` DEBE enviar `POST /api/v1/auth/register` con `{email, password, nombre}`, continuar logueado tras el alta y mostrar el error de email duplicado (400) sin romper el formulario.

#### Scenario: Email duplicado
- **WHEN** el backend responde 400 en el registro
- **THEN** se muestra "Ese correo ya está registrado" y el form permanece utilizable

### Requirement: Recuperar contraseña vía notif-api
`RecuperarView` DEBE enviar `POST /api/v1/auth/recuperar` al servicio `notif`, mostrar el aviso de revisar la casilla al recibir 202 y un mensaje de servicio no disponible si la request falla o expira el timeout de 8 s.

#### Scenario: Email transaccional
- **WHEN** se solicita recuperar con un correo existente
- **THEN** notif-api responde 202 genérico y el email "Recuperar contraseña" aparece en MailHog

### Requirement: Perfil real en AppHeader
`AppHeader`/shell DEBEN mostrar el nombre y rol derivados del `auth/me` real (no "Aldren Valeros"), con badge de admin cuando el rol del token es `admin`.

#### Scenario: Usuario logueado
- **WHEN** hay sesión activa
- **THEN** el header muestra iniciales, nombre y título perfilados del email real y el botón de logout revoca la sesión