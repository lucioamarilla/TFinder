## 1. Dependencias y configuración de entorno

- [x] 1.1 Extender `requirements.txt` con las dependencias de runtime (`psycopg[binary]`, `psycopg_pool`, `redis`, `pika`, `PyJWT`, `qrcode`, `fpdf2`, `python-json-logger`) y verificar que `pip install -r requirements.txt` (dentro del venv) termina sin errores
- [x] 1.2 Reemplazar `.env.example` documentando `PORT`, `PGSQL_*`, `DATABASE_URL`, `REDIS_URL`, `RABBITMQ_URL`, `JWT_SECRET`, `JWT_EXP_MIN`, `SMTP_HOST`, `SMTP_PORT`, `MAIL_FROM`, `VITE_API_URL` sin valores sensibles y verificar que `cp .env.example .env` + `load_dotenv()` levanta la app en `uvicorn app.main:app`
- [x] 1.3 Ampliar `.gitignore` para los artefactos nuevos que no deben versionarse (caches pytest/ruff, reportes de cobertura, datos locales de bind-mount si se usan) y verificar con `git status` que `.env` y los artefactos ignorados no aparecen como untracked

## 2. Infraestructura con Docker Compose

- [x] 2.1 Crear `docker-compose.yml` con los servicios `postgres` (16-alpine), `redis` (7-alpine), `rabbitmq` (3-management-alpine) y `mailhog`, cada uno con `container_name`, healthcheck, y los puertos publicados del diseño (`5432`, `6390->6379`, `5673->5672` + `15673->15672`, `1025` + `8025`); verificar que `docker compose config` valida el archivo
- [x] 2.2 Crear `infra/postgres-init/01-crear-dbs.sql` que crea `builds_db`, `feed_db` y `notif_db` y verificar con `docker exec tfinder-postgres psql -U tfinder -d mesas_db -c '\l'` que las 4 bases (incl. `mesas_db`) están listadas al primer arranque
- [x] 2.3 Crear `Dockerfile` (base `python:3.12-slim`, `CMD uvicorn app.main:app --host 0.0.0.0 --port 8001`) y `.dockerignore` (excluye `venv/`, `.env`, `.git/`, `tfinder-vue/`, `openspec/`, `__pycache__`, `*.db`); verificar que `docker build -t tfinder-api .` compila sin errores y que la imagen no contiene `.env`
- [x] 2.4 Agregar el servicio opcional `api` al compose (build desde `.`, `env_file: .env`, port `8001:8001`, `depends_on` con `condition: service_healthy`) y verificar que `docker compose up -d api` responde en `http://localhost:8001/docs` (o documentar en README la vía host apuntando a la red de compose)

## 3. Clientes compartidos de infraestructura

- [x] 3.1 Crear `app/infra/__init__.py` y `app/infra/redis.py` con `get_redis()` que lee `REDIS_URL` (default `redis://localhost:6390/0`) y verificar con `python -c "from app.infra.redis import get_redis; assert get_redis().ping()"` que responde `True`
- [x] 3.2 Crear `app/infra/rabbitmq.py` con `get_params()` que lee `RABBITMQ_URL` (default `amqp://tfinder:tfinder@localhost:5673/`) retornando `pika.ConnectionParameters` y verificar que el objeto resultante expone `host` `localhost` y `port` `5673`

## 4. Verificación rigurosa (definición de done)

- [x] 4.1 Levantar los 4 servicios con `docker compose up -d postgres redis rabbitmq mailhog` y verificar que `docker compose ps` muestra los 4 en estado `running` y los 3 con healthcheck en `healthy` sin errores
- [x] 4.2 Ejecutar la batería de asserts de conectividad (`psycopg` contra `mesas_db` con `select 1` → `(1,)`, y `redis` `ping()` → `True`) y verificar que ambos comandos terminan con exit code `0`; repetirlos con servicios apagados para confirmar que fallan (exit != 0)
- [x] 4.3 Verificar el catálogo de DBs con `docker exec tfinder-postgres psql -U tfinder -d mesas_db -c '\l'` y confirmar que `mesas_db`, `builds_db`, `feed_db` y `notif_db` existen
- [x] 4.4 Verificar los paneles de soporte: RabbitMQ en `http://localhost:15673` (login `tfinder/tfinder`) y MailHog en `http://localhost:8025` cargan su interfaz

## 5. Documentación y cierre

- [x] 5.1 Agregar a `README.md` la sección de infraestructura (comando de levante, variables de entorno, tabla de servicios/puertos, diferencia `localhost` vs nombres de servicio dentro del contenedor, gotcha del init de DBs con `docker compose down -v`)
- [x] 5.2 Crear rama corta `f/B01_infra`, commite seguido de la convención AE2 referenciando el issue de B01 (ej. `feat(infra): docker compose con postgres/redis/rabbitmq/mailhog (#1)`) y verificar con `git status` que solo se versionan los archivos intencionales