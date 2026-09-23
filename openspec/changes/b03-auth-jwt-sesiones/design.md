# Design: Autenticación JWT + roles con sesión en Redis

## Context

`mesas-api` (B02) ya tiene pool `psycopg_pool` a `mesas_db`, red de compose (B01) con Redis publicado en `6390` (interno `redis:6379`) y el cliente compartido `app/infra/redis.py`. El frontend simula el rol; hay que pasar a autenticación real con revocación inmediata.

## Decisions

**D1 — El dominio de auth vive en `mesas_api`.**
La tabla `usuarios`, el emisor de tokens, las sesiones y las rutas `/api/v1/auth/*` se implementan en el servicio de mesas (el único con capacidad de CRUD real de usuarios). Sin servicio propio de auth.

**D2 — Tokens JWT HS256 con `PyJWT` (ya en `requirements.txt`).**
`access` y `refresh` comparten algoritmo y secret (`JWT_SECRET`, default local `dev-secret`), con `jti` único por token. El `refresh` lleva `tipo: refresh` para distinguir uso. Expiración por `JWT_EXP_MIN` (default 1440 = 24 h).

**D3 — Sesión = par de `jti` en Redis con TTL.**
Cada token emitido registra su `jti` en `sesion:<jti>` → `usuario_id` con `SETEX` (24 h). `sesion_valida(jti)` → `EXISTS`. El logout borra el `jti` del access: al instante ese token deja de servir. Uso de `app/infra/redis.py` (`get_redis`, default `redis://localhost:6390/0`).

**D4 — Hash PBKDF2 con salt por usuario.**
`hash_password`: salt hex + iteraciones 120_000 SHA-256; formato `salt$digest`. Sin dependencias extra.

**D5 — Middleware como dependencies de FastAPI.**
`usuario_actual(creds=Depends(bearer))` valida: presencia (`401`), decodificación JWT (`401`), tipo ≠ refresh (`401`), sesión vigente (`401`). `requerir_roles(*roles)` evalúa `payload.rol` → `403`. Formato de error AE1 `{"error":{"codigo","mensaje"}}` vía handlers existentes.

**D6 — Protección mínima y no romper el frontend de exploración.**
Quedan protegidas solo las mutaciones de mesas (POST/PUT/DELETE) y las rutas de auth sensibles; los GET de lectura siguen abiertos para que F02/F03 no dependan de login para explorar.

**D7 — `refresh` renovando el access.**
`POST /api/v1/auth/refresh` acepta token `tipo: refresh` vigente → emite nuevo access (y registra su `jti`). Si el refresh fue revocado/borrado, `401`.

**D8 — Entorno de contenedor.**
`mesas-api` en compose recibe `REDIS_URL=redis://redis:6379/0`, `JWT_SECRET` y `JWT_EXP_MIN` (desde `.env.example`); el default `dev-secret`/1440 cubre el desarrollo local sin variables.

## Risks

- **Secreto JWT hardcodeado (default `dev-secret`)**: solo para desarrollo; producción provee `JWT_SECRET`. Sin secretos reales en `.env.example` (regla B01).
- **Redis caído** al validar sesión: `EXISTS` fallaría → el token se rechaza como `401`. Decisión de consistencia > disponibilidad para auth.
- **Compatibilidad frontend**: el schema de auth es nuevo; el frontend que consumía mesas con rol simulado no se rompe (solo las mutaciones de mesa piden token, y F02 lo cubre).

## Migration Plan

1. Agregar DDL de `usuarios` a `mesas_api/app/schema.sql` (idempotente).
2. Crear `models/auth_model.py` (hash, tokens, persistencia, sesiones), `controllers/auth_controller.py`, `middleware/auth.py`, `routes/auth_routes.py`.
3. Registrar el router en `mesas_api/main.py` y aplicar DDL en lifespan (ya lo hace `init_db`).
4. Proteger mutaciones de mesas en `routes/v1/mesas.py`.
5. `.env.example` documenta `JWT_SECRET`/`JWT_EXP_MIN` (ya estaban por B01) y `requirements.txt` suma `email-validator`.
6. Verificación: flujo register→login→me→logout→401; admin-only→403; /docs con tag auth; contenedor con `REDIS_URL` interno.

## Verification

- `venv/bin/python -c "import mesas_api..."` sin errores.
- Smoke: register(201, hash en PG) → login → `me` (200 rol) → logout → `me` con mismo token (401) → sin token (401) → `admin-only` con rol `usuario` (403) → `/refresh` renueva access (200) → repetir access→logout→401.
- `/docs` muestra tag `auth`.
- Contenedor: `curl http://localhost:8001/api/v1/auth/me` con token emitido en el contenedor → 200.
- `rg` de propiedad: `usuarios` solo en `mesas_api` y en `docs/PROPIEDAD_DE_DATOS.md` actualizado.