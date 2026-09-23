# Proposal: Autenticación JWT + roles con sesión en Redis

## Why

El frontend simula el rol de usuario; la API no puede distinguir quién crea una mesa ni controlar permisos. B03 reemplaza esa simulación por autenticación real (registro, login, refresh, logout) con tokens JWT y sesiones revocables en Redis, manteniendo el formato de error AE1.

## What Changes

- **Nuevo dominio de auth en `mesas_api`** (B02): tabla `usuarios`, modelo/controlador/rutas de auth y middleware de protección.
- **Tokens JWT** con `PyJWT`: `access` + `refresh`; claims `sub`, `rol`, `email`, `jti`.
- **Sesiones en Redis** con TTL (24 h): `guardar_sesion`, `revocar_sesion`, `sesion_valida`. El logout revoca al instante (borra la sesión); un endpoint protegido rechaza tokens revocados con `401`.
- **Roles** `usuario` (default) / `gm` / `admin`: dependency `requerir_roles(*roles)` rechaza con `403`.
- **Rutas protegidas heredadas**: crear/actualizar/eliminar mesa exigen autenticación; el resto sigue público.
- **Endpoints** nuevos (`/api/v1/auth/*`): `register` (201), `login`, `logout`, `me`, `admin-only` (demo de rol).
- **`mesas_api/schema.sql`**: DDL idempotente de `usuarios` (email único, hash PBKDF2, rol con CHECK).
- **Requirements igual que AE1**: `email-validator` (para `EmailStr`) se agrega a `requirements.txt`.
- **Compose**: `mesas-api` recibe `REDIS_URL=redis://redis:6379/0` (interno) y `JWT_SECRET`/`JWT_EXP_MIN` documentados en `.env.example`.
- BREAKING: crear/actualizar/eliminar mesa pasan a requerir `Authorization: Bearer`. (El resto de la API queda igual.)

## Capabilities

- **New Capabilities**: `auth-sesiones` — autenticación JWT con sesiones revocables en Redis y roles.
- **Modified Capabilities**: ninguna (esta spec es agregada; `backend-servicios` no cambia comportamiento, solo se protegen rutas).

## Impact

- `mesas_api/schema.sql` → tabla `usuarios`.
- `mesas_api/app/models/auth_model.py`, `controllers/auth_controller.py`, `routes/auth_routes.py`, `middleware/auth.py`.
- `mesas_api/app/routes/v1/mesas.py` → depende de `usuario_actual` en mutaciones.
- `requirements.txt` (+`email-validator`), `docker-compose.yml` (env `REDIS_URL`/`JWT_*` en mesas-api), `.env.example`.
- Reusa `app/infra/redis.py` (cliente compartido B01) y el pool `mesas_api` (B02).
- Frontend lo consume en F02 (futuro issue).