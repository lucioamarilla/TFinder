# auth-sesiones Specification

## Purpose

Define la autenticación real de TFinder AE2 en `mesas-api`: registro, login, refresh, logout y consulta de identidad con tokens JWT, sesiones centralizadas en Redis revocables al instante, roles `usuario`/`gm`/`admin`, y protección de rutas por autenticación y por rol, manteniendo el formato de error AE1.

## Requirements

### Requirement: Registro de usuarios con hash de contraseña
`mesas-api` DEBE exponer `POST /api/v1/auth/register` que cree un usuario (contraseña con hash PBKDF2, email único, rol por defecto `usuario`) y devuelva `access` + `refresh` con estado `201`, rechazando con `400` si el email ya existe.

#### Scenario: Alta exitosa de un usuario
- **WHEN** se envía `POST /api/v1/auth/register` con `email`, `password` (mínimo 8 caracteres), `nombre` y opcionalmente `rol`
- **THEN** el usuario queda persistido en `mesas_db.usuarios` con su `password_hash` y la respuesta es `201` con `access_token`, `refresh_token` y `rol`

#### Scenario: Email duplicado
- **WHEN** se registra un email ya existente
- **THEN** la API responde `400` con el formato de error AE1 y no crea otro usuario

### Requirement: Login y renovación con tokens JWT
`mesas-api` DEBE exponer `POST /api/v1/auth/login` que valida credenciales y emite `access` + `refresh`, y `POST /api/v1/auth/refresh` que renueva el `access` a partir de un `refresh` válido, rechazando con `401` credenciales inválidas o `refresh` revocado.

#### Scenario: Login exitoso
- **WHEN** se envía `POST /api/v1/auth/login` con credenciales válidas
- **THEN** la API responde `200` con `access_token`, `refresh_token` y `rol`, y ambas sesiones quedan registradas en Redis con TTL 24 h

#### Scenario: Credenciales incorrectas
- **WHEN** se envía `POST /api/v1/auth/login` con email o contraseña incorrectos
- **THEN** la API responde `401` con el formato de error AE1 y no emite tokens

#### Scenario: Renovación del access
- **WHEN** se envía `POST /api/v1/auth/refresh` con un token de tipo `refresh` vigente y no revocado
- **THEN** la API responde `200` con un nuevo `access_token` vigente para el mismo usuario

### Requirement: Logout con revocación inmediata de sesión
`mesas-api` DEBE exponer `POST /api/v1/auth/logout` (autenticado) que borre de Redis las sesiones asociadas al token, de modo que ese token deje de ser válido al instante.

#### Scenario: Cierre de sesión
- **WHEN** un usuario autenticado envía `POST /api/v1/auth/logout`
- **THEN** la API responde `200` y un uso posterior del mismo `access` en un endpoint protegido responde `401` por sesión revocada

### Requirement: Protección de rutas por token y por rol
`mesas-api` DEBE exponer una dependency `usuario_actual` que rechace con `401` peticiones sin token o con token expirado/revocado, y `requerir_roles(*roles)` que rechace con `403` si el rol del token no está permitido; las mutaciones de mesas (crear, actualizar, eliminar) DEBEN quedar protegidas.

#### Scenario: Petición sin token
- **WHEN** se accede a una ruta protegida sin `Authorization: Bearer`
- **THEN** la API responde `401` con el formato de error AE1

#### Scenario: Rol insuficiente
- **WHEN** un usuario con rol distinto al requerido accede a una ruta de rol
- **THEN** la API responde `403` con el formato de error AE1

#### Scenario: Mutaciones de mesas protegidas
- **WHEN** se crea, actualiza o elimina una mesa sin token válido
- **THEN** la API responde `401`; con token válido la operación procede con su código de éxito habitual

### Requirement: Documentación OpenAPI de los endpoints de auth
`mesas-api` DEBE exponer en `/docs` los endpoints de `auth` con schemas Pydantic visibles (body de registro/login y respuestas de tokens).

#### Scenario: Endpoints visibles en `/docs`
- **WHEN** se abre `/docs` de `mesas-api`
- **THEN** se listan `register`, `login`, `refresh`, `logout`, `me` y `admin-only` bajo el tag `auth`, con sus schemas de entrada/salida