## 1. Persistencia y modelo

- [x] 1.1 Agregar DDL idempotente de `usuarios` a `mesas_api/app/schema.sql` (id, email UNIQUE, password_hash, rol CHECK usuario/gm/admin, nombre, fecha_creacion) y verificar que `init_db` lo aplica sobre `mesas_db`
- [x] 1.2 Crear `mesas_api/app/models/auth_model.py` con `hash_password`/`verificar_password` (PBKDF2), `crear_token`/`decodificar_token` (PyJWT HS256, `JWT_SECRET`/`JWT_EXP_MIN`), persistencia de usuarios (psycopg `dict_row`, `RETURNING`) y sesiones Redis (`guardar_sesion`/`revocar_sesion`/`sesion_valida` con `get_redis`)
- [x] 1.3 Agregar `email-validator` a `requirements.txt` e instalarlo en el venv

## 2. Controlador, middleware y rutas

- [x] 2.1 Crear `mesas_api/app/controllers/auth_controller.py` con `registrar` (400 si email existe), `iniciar_sesion` (401 si credenciales inválidas), `_emitir_tokens` (access+refresh+guardar sesiones) y `cerrar_sesion`
- [x] 2.2 Crear `mesas_api/app/middleware/auth.py` con `usuario_actual` (401 sin token, token inválido, refresh, sesión revocada) y `requerir_roles(*roles)` (403)
- [x] 2.3 Crear `mesas_api/app/routes/auth_routes.py` con `/api/v1/auth/register|login|refresh|logout|me|admin-only` (schemas Pydantic) y registrarlo en `mesas_api/main.py`
- [x] 2.4 Proteger mutaciones de mesas (POST/PUT/DELETE) con `Depends(usuario_actual)` en `mesas_api/app/routes/v1/mesas.py`

## 3. Entorno y composición

- [x] 3.1 Agregar a `docker-compose.yml` en `mesas-api` `REDIS_URL=redis://redis:6379/0`, `JWT_SECRET` y `JWT_EXP_MIN`; verificar `docker compose config --quiet`
- [x] 3.2 Actualizar `docs/PROPIEDAD_DE_DATOS.md` con la tabla `usuarios` (dueño `mesas-api`)

## 4. Verificación (done)

- [x] 4.1 Smoke local: register(201) → login(200) → missing/correcto `me` (200 rol) → logout(200) → `me` mismo token (401) → sin token (401) → `admin-only` con `usuario` (403) → `/refresh` renueva access (200)
- [x] 4.2 Verificar que `/docs` lista el tag `auth` con schemas
- [x] 4.3 Verificar en contenedor: `mesas-api` con `REDIS_URL` interno responde `me`/auth correctamente

## 5. Cierre de la tarea

- [x] 5.1 Ejecutar `openspec validate` y verificar que el change `b03-auth-jwt-sesiones` es válido
- [x] 5.2 Crear rama `f/B03_auth_jwt`, commitear con `feat(mesas-api): autenticacion JWT con sesiones en Redis (#16)`, mergear a `AE2-Backend` y archivar el change
- [x] 5.3 Cerrar el issue GitHub #16