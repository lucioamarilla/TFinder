## Why

La base AE1 corre un monolito FastAPI sobre una única SQLite sin contenedores, mientras que el objetivo AE2 requiere un entorno reproducible (criterio 10) compuesto por API + PostgreSQL + Redis + RabbitMQ + MailHog, configurado por variables de entorno y sin secretos en el código (RNF-11). Sin esta infraestructura no se puede avanzar con B02 (separación de servicios) ni con ningún criterio que dependa de Redis, RabbitMQ o el email sandbox.

## What Changes

- `docker-compose.yml` nuevo: servicios `postgres`, `redis`, `rabbitmq`, `mailhog` (+ servicio `api` opcional con `Dockerfile`) con nombres de contenedor fijos y healthchecks.
- `infra/postgres-init/01-crear-dbs.sql` nuevo: crea `builds_db`, `feed_db` y `notif_db` al primer arranque (`mesas_db` ya la crea `POSTGRES_DB`).
- `.env.example` reemplazado: documenta `PORT`, `DATABASE_URL`, `REDIS_URL`, `RABBITMQ_URL`, `SMTP_HOST`, `SMTP_PORT`, `MAIL_FROM`, `JWT_SECRET`, `JWT_EXP_MIN`, `VITE_API_URL` con valores de ejemplo no sensibles.
- `Dockerfile` y `.dockerignore` nuevos: imagen del API existente (entrada real `app.main:app`).
- `app/infra/` nuevo: clientes centralizados `redis.py` (`get_redis()`) y `rabbitmq.py` (`get_params()`).
- `requirements.txt` extendido: `psycopg[binary]`, `psycopg_pool`, `redis`, `pika`, `PyJWT`, `qrcode`, `fpdf2`, `python-json-logger`, `httpx`, `pytest` (estos dos últimos ya viven en `requirements-dev.txt`, se documenta el criterio).
- `.gitignore` ampliado: entradas para artefactos nuevos que no deben versionarse (caches de test/lint, reportes de cobertura, `.env` ya cubierto queda consistente).
- **Verificación rigurosa**: comandos de smoke test (`psycopg`/`psql`, `redis-cli`/`redis-py`, paneles RabbitMQ y MailHog) más pruebas puntuales de infra tan automatizadas como sea posible.

## Capabilities

### New Capabilities
- `infra-containers`: entorno de desarrollo reproducible vía Docker Compose — servicios de infraestructura (PostgreSQL, Redis, RabbitMQ, MailHog) levantados con un comando, configuración 100 % por variables de entorno, secretos fuera del código y clientes compartidos (`app/infra/`) para Redis y RabbitMQ.

### Modified Capabilities
- Ninguna (no existen specs previas; `openspec/specs/` está vacío).

## Impact

- **Código**: `app/infra/{__init__,redis,rabbitmq}.py` nuevos; no se toca lógica de negocio.
- **Configuración**: `.env.example` y `.gitignore` actualizados; `docker-compose.yml`, `Dockerfile`, `.dockerignore`, `infra/postgres-init/01-crear-dbs.sql` nuevos.
- **Dependencias**: `requirements.txt` (además de `requirements-dev.txt` existente para test/httpx/ruff).
- **Datos**: se conserva `tfinder.db` (SQLite) para no romper AE1 hasta B02; el API sigue funcionando en el host con venv o dentro del contenedor `api`.
- **Externos**: puertos publicados 5432 (postgres), 6390 y 6379-interno (redis), 5673/15673 (RabbitMQ AMQP + UI), 1025/8025 (MailHog SMTP + UI). Puerto alternativo 6390/5673 para no chocar con servicios locales.