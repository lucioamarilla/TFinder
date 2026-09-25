## Context

El repo está en la rama `AE2-Backend` con un backend FastAPI modular en `app/{core,modules,shared}` que hoy persiste en SQLite (`app/core/db.py`) y un frontend Vue en `tfinder-vue/`. No existe OpenSpec previo (`openspec/specs/` vacío); B01 es la primera tarea de la Fase A de AE2. La entrada real de la app es `app.main:app` (el `main.py` de la raíz es residuo de AE1 e importa `app.controllers...`, que ya no existe). Docker/Compose están disponibles (Docker 29.4, Compose v5.1.3) y el Python local es 3.12. Ver `proposal.md - Why` para la motivación.

## Goals / Non-Goals

**Goals:**
- Defina un conjunto Compose donde postgres/redis/rabbitmq/mailhog se levanten con un comando y queden healthy.
- Configuración externa vía `.env` (`.env.example` sin secretos) y clientes compartidos en `app/infra/` para Redis y RabbitMQ.
- Imagen propia del API (`Dockerfile`) opcional pero verificable.
- Batería de verificación "done" que falle con salida != 0 si algo no responde.
- Ampliar `.gitignore` para todo artefacto nuevo que no deba versionarse.

**Non-Goals:**
- No migra el API de SQLite a PostgreSQL (eso es B02: pool `psycopg_pool` y `app/db.py` por servicio). Acá postgres levaño con sus 4 DBs.
- No implementa lógica de negocio ni defendiendo AJUSTE de esquemas.
- No implementa autenticación, caché, mensajería real ni tests completos de unidades (B03..B11).

## Decisions

1. **Un solo archivo `docker-compose.yml` en la raíz, con servicios `postgres`, `redis`, `rabbitmq`, `mailhog` y `api` (api opcional).**
   - Por qué: un único comando reproduce el entorno (criterio 10) y el resto de tareas solo agrega servicios.
   - Alternativa: multi-compose por carpeta por servicio (B02 separa servicios), pero B01 es esqueleto: mantener monolito Compose hasta que B02 defina carpetas.

2. **Puertos de host alternativos (redis `6390`, rabbitmq AMQP `5673` + UI `15673`).** Host namespaced para no chocar con daemons locales; los puertos internos estándar quedan dentro del contenedor. `postgres` y MailHog usan puertos estándar (5432, 1025/8025) documentados como requisito.

3. **Healthchecks por servicio.** `pg_isready -U tfinder -d mesas_db`, `redis-cli ping`, `rabbitmq-diagnostics ping`, con `interval/timeout/retries`. MailHog sin healthcheck (respuesta inmediata). El servicio `api` (si se activa) usa `depends_on` con `condition: service_healthy` para esperar al resto.

4. **Creación de las 4 DBs vía `docker-entrypoint-initdb.d`.**
   - `POSTGRES_DB: mesas_db` la crea la imagen; el script `infra/postgres-init/01-crear-dbs.sql` crea `builds_db`, `feed_db`, `notif_db`. El entrypoint corre cada sentencia con autocommit, por lo que `CREATE DATABASE` funciona.
   - Gotcha: solo corre la primera vez (volumen vacío). Para re-ejecutar: `docker compose down -v`.
   - Alternativa considerada: script idempotente con `WHERE NOT EXISTS ... \gexec` para tolerar resets del volumen sin `-v`; se adopta como mejora opcional del init si se quiere robustez extra.

5. **Dockerfile mínimo basado en `python:3.12-slim`** (misma versión que el host). Capas: copiar solo `requirements*.txt`, instalar, copiar el resto, `EXPOSE 8001`, `CMD uvicorn app.main:app --host 0.0.0.0 --port 8001`. `--host 0.0.0.0` es obligatorio dentro de un contenedor. El CMD apunta a `app.main:app`, no al `main.py` raíz (residuo de AE1).
   - Dockerfile en la raíz, `.dockerignore` excluyendo `venv/`,`.env`, `.git/`, `tfinder-vue/`, `tests/`, `__pycache__`, `*.db`, `.opencode/`, `openspec/`.

6. **`.env.example` orientado a host (localhost).** El API en desarrollo corre con venv y `--reload`, conectándose por los puertos publicados. Si se corre **dentro** del contenedor, las URLs cambian a los nombres de servicio (`postgres`, `redis`, `rabbitmq`) — se documenta en el README/comentario del compose. La decisión "host-first / container-ready" satisface el criterio 3 ("corre en contenedor o apunta a la red de compose").

7. **Clientes `app/infra/` como factories con lazy init.** `get_redis()` → `redis.from_url(REDIS_URL || default)`, `get_params()` → `pika.URLParameters(RABBITMQ_URL || default)`. Mismo patrón simple, defaults alineados con el compose. La conexión Postgres queda para B02 (pool en `app/db.py` de cada servicio).

8. **Verificación "done" como batería de comandos con `assert`.** Tres assets automáticos (`psycopg` select-1, `redis` ping, `docker compose ps`) + inspección manual de paneles (RabbitMQ `:15673`, MailHog `:8025`) y catálogo de DBs vía `docker exec`. Se deja explícito que el testing formal es B11; B01 aporta la base (pytest/httpx ya en `requirements-dev.txt`) sin duplicarlos.

9. **`.gitignore`**: `.env` ya está; se agregan entradas para lo nuevo que no debe versionarse (caches de pytest/ruff mypy, reportes de cobertura, `tfinder.db` ya cubierto por `*.db`, y cualquier dato local de infra si se usara bind-mount). Los archivos de config (compose, Dockerfile, `.env.example`, `infra/postgres-init/`) SÍ se versionan.

## Risks / Trade-offs

- [El init de DBs solo corre al primer arranque; reintentos posteriores no crean DBs] → documentar `docker compose down -v` para reset; opcionalmente init idempotente.
- [Solo para la API en contenedor: URLs con `localhost` rompen la conexión] → sobreescribir `DATABASE_URL/REDIS_URL/RABBITMQ_URL` con nombres de servicio; documentado en el compose/comentario del `.env`.
- [`main.py` de raíz está roto (imports AE1)] → el Dockerfile/CMD usa `app.main:app`; no tocar `app/core/db.py` en B01.
- [Conflictos de puerto si hay postgres/redis/rabbitmq locales] → puertos alternativos 6390/5673/15673 ya decididos; el resto es configurable por `.env`.
- [Agregar deps al `requirements.txt` duplica pytest/httpx ya presentes en `requirements-dev.txt`] → se mantiene `requirements-dev` como fuente única de testing y `requirements.txt` solo con deps de runtime (se documenta la convención; `requirements-dev.txt` ya hace `-r requirements.txt`).
- [Imagen del API con SQLite actual es efímera (DB dentro del contenedor)] → aceptado para B01; B02 migra a PostgreSQL con volumen.

## Migration Plan

- Despliegue: crear archivos nuevos, extender `requirements.txt`/`.env.example`/`.gitignore`, levantar infra, correr batería de verificación.
- Rollback: reversión git del commit de B01; los datos SQLite de AE1 no se tocan (se conserva `tfinder.db` hasta B02).
- No hay migración de datos: solo se agrega infraestructura en paralelo.

## Open Questions

- Ninguna que afecte specs/approach/tareas. La única decisión pendiente de preferencia (correr el API en host vs contenedor) no cambia el diseño: ambas rutas quedan soportadas y documentadas.