# TFinder — Plataforma de Rol de Mesa (MVP · Fase 1)

**TFinder** centraliza las herramientas de una mesa de rol —gestión de mesas/campañas, matchmaking, sesiones con asistencia y calendario, builds de personajes (Pathfinder 1e), wiki de campaña, feed social y notificaciones— en una plataforma multi-servicio. Fase 1: **FastAPI + PostgreSQL** con Redis, RabbitMQ y MailHog; el frontend es una app **Vue 3** consumiendo los cuatro servicios por proxy same-origin.

## Integrantes
- Amarilla Lucio
- Czajkowski Leonardo

## Stack Tecnológico
- Framework: FastAPI (4 microservicios, Dockerfile multi-use con `ARG SERVICE`)
- Persistencia: PostgreSQL (una base por servicio: `mesas_db`, `builds_db`, `feed_db`, `notif_db`)
- Infraestructura: Redis (caché + sesiones JWT), RabbitMQ (eventos asíncronos + DLQ), MailHog (sandbox SMTP)
- Frontend: Vue 3 + Vite + Tailwind (`frontend/`), servido por Nginx con proxies same-origin
- Errores: envelope unificado `{"error": {"codigo": <int>, "mensaje": <str>}}` en todos los servicios

## Arquitectura

| Servicio | Carpeta | Puerto (host) | Dominio |
|---|---|---|---|
| mesas-api | `mesas_api/` | 8001 | mesas CRUD, auth JWT, solicitudes de unión, sesiones+QR de asistencia, matchmaking |
| builds-api | `builds_api/` | 8002 | builds y tags (lectura), generación de PDF de build |
| feed-api | `feed_api/` | 8003 | feed público, wiki de campaña, diario de sesión |
| notif-api | `notif_api/` | 8004 | notificaciones (REST + SSE), emails, event-log, DLQ, descarga de PDFs |

Comunicación entre servicios: eventos asíncronos vía exchange topic **`tfinder.events`** (reintentos con backoff y routing a DLQ `dlq.general` tras agotar) y REST `notif→mesas` para obtener miembros. Idempotencia de POSTs críticos por header `Idempotency-Key` (Redis, TTL 24 h). `/docs` de cada puerto es la referencia OpenAPI autoritativa.

## Requisitos previos
- Python 3.11+ (`python3 --version`) y Docker Compose para la infraestructura.

## Estructura del proyecto
```bash
App_Final/
├── app/            # paquete compartido: infra (pg, redis, rabbitmq, token, ready, logs)
├── mesas_api/      # 8001 · mesas, auth, solicitudes, sesiones/QR, matchmaking
├── builds_api/     # 8002 · builds/tags + PDF de build
├── feed_api/       # 8003 · feed, wiki, diario de sesión
├── notif_api/      # 8004 · notificaciones (REST+SSE), emails, event-log, DLQ, PDF
├── frontend/       # app Vue 3 (repo anidado tfinder-vue) + nginx same-origin
├── infra/          # init de PostgreSQL (crea las 4 bases + bases *_test)
├── tests/          # suite pytest con infraestructura real (docker) — 169+ casos
├── scripts/        # seed/demo y generadores de evidencias
├── docker-compose.yml
├── Dockerfile      # uno para los 4 servicios (ARG SERVICE)
└── requirements.txt · requirements-dev.txt
```

## Instalación

```bash
git clone https://github.com/lucioamarilla/TFinder
cd TFinder
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> **Nota**: el comando usa `python3`. En sistemas Ubuntu/Debian recientes `python` no existe por defecto; será `python3`. En otras distribuciones o si tenés un alias `python` (que apunte a Python 3), también podés usar `python -m venv venv`.

## Configuración

Copiar `.env.example` a `.env` y completar los valores:

```bash
cp .env.example .env
```

Variables:

| Variable | Descripción | Ejemplo |
|---|---|---|
| PORT | Puerto del servidor | 8000 |
| DATABASE_URL | Ruta al archivo SQLite | ./tfinder.db |

> **Nota**: si las variables se dejan vacías, el servidor usa sus valores por defecto (`PORT=8000` y `SQLite` en `./tfinder.db`).

## Infraestructura con Docker Compose (AE2 / B01)

Entorno de desarrollo reproducible: PostgreSQL, Redis, RabbitMQ y MailHog se levantan con un solo comando. La configuración es 100 % por variables de entorno (`.env`, ver `.env.example`) y no hay secretos en el código.

### Levantar la infraestructura

```bash
cp .env.example .env          # unica vez; ajustar si hace falta
docker compose up -d postgres redis rabbitmq mailhog
docker compose ps            # los 3 con healthcheck deben quedar "healthy"
```

Para detener todo, sin borrar datos: `docker compose down`. Para resetear **todo** (incluidas las bases extra del init): `docker compose down -v`.

### Servicios y puertos

| Servicio | Imagen | Container | Puertos publicados | Healthcheck |
|---|---|---|---|---|
| postgres | `postgres:16-alpine` | `tfinder-postgres` | `5432` | `pg_isready` |
| redis | `redis:7-alpine` | `tfinder-redis` | `6390 → 6379` | `redis-cli ping` |
| rabbitmq | `rabbitmq:3.13-management-alpine` | `tfinder-rabbitmq` | `5673 → 5672` (AMQP), `15673 → 15672` (UI) | `rabbitmq-diagnostics ping` |
| mailhog | `mailhog/mailhog:v1.0.1` | `tfinder-mailhog` | `1025` (SMTP), `8025` (UI) | — |
| api (opcional) | build local | `tfinder-api` | `8001` | — |

- PostgreSQL crea 4 bases al primer arranque: `mesas_db` (via `POSTGRES_DB`) y `builds_db`, `feed_db`, `notif_db` (via `infra/postgres-init/01-crear-dbs.sql`).
- Paneles: RabbitMQ `http://localhost:15673` (login `tfinder/tfinder`) y MailHog `http://localhost:8025`.
- API en contenedor: `docker compose up -d --build api` → `http://localhost:8001/docs`.

### Variables de entorno

Documentadas en `.env.example` (todas con valores de ejemplo no sensibles):

| Variable | Descripción | Ejemplo (host) |
|---|---|---|
| PORT | Puerto del API | 8001 |
| PGSQL_HOST / PGSQL_PORT / PGSQL_USER / PGSQL_PASSWORD | Conexión Postgres (host) | localhost / 5432 / tfinder / tfinder |
| DATABASE_URL | URL completa de la DB principal | postgresql://tfinder:tfinder@localhost:5432/mesas_db |
| REDIS_URL | Cliente Redis compartido (`app/infra/redis.py`) | redis://localhost:6390/0 |
| RABBITMQ_URL | Broker RabbitMQ (`app/infra/rabbitmq.py`) | amqp://tfinder:tfinder@localhost:5673/ |
| JWT_SECRET / JWT_EXP_MIN | Firma y expiración de JWT | change-me-en-produccion / 1440 |
| SMTP_HOST / SMTP_PORT / MAIL_FROM | Email sandbox (MailHog) | localhost / 1025 / noreply@tfinder.local |
| VITE_API_URL | URL del API para el frontend | http://localhost:8001 |

### `localhost` vs nombres de servicio (dentro del contenedor)

Los valores de `.env` apuntan a **`localhost`** porque el desarrollo principal corre el API con venv en el host, usando los puertos publicados. Cuando el API corre **dentro** de un contenedor (servicio `api`), está en la misma red de compose y debe usar los **nombres de servicio** en lugar de `localhost`:

| Servicio | Host | Dentro del contenedor |
|---|---|---|
| postgres | `localhost:5432` | `postgres:5432` |
| redis | `localhost:6390` | `redis:6379` |
| rabbitmq | `localhost:5673` | `rabbitmq:5672` |
| mailhog | `localhost:1025` | `mailhog:1025` |

### Gotcha: init de bases de datos

Los scripts de `docker-entrypoint-initdb.d` (que crean `builds_db`, `feed_db` y `notif_db`) **solo corren la primera vez**, cuando el volumen de postgres está vacío. Si borraste un servicio o reseteaste con `docker compose up` sin volumen, para recrear las bases extra: `docker compose down -v && docker compose up -d postgres`. (El script es idempotente, así que un segundo arranque no falla.)

## Ejecución

Desde el host (requiere la infraestructura de compose levantada):

```bash
uvicorn mesas_api.main:app --port 8001    # CRUD de mesas (http://localhost:8001/docs)
uvicorn builds_api.main:app --port 8002   # builds/tags
uvicorn feed_api.main:app --port 8003     # feed/wiki
uvicorn notif_api.main:app --port 8004    # notificaciones/event-log
```

O dentro de contenedores:

```bash
docker compose up -d --build
```

- Frontend Vue servido por Nginx en `http://localhost:5173`.
- El frontend usa proxies same-origin hacia las cuatro APIs.
- Al arrancar, cada servicio abre su pool `psycopg_pool` contra su `*_db`, crea sus tablas (`schema.sql` idempotente) y aplica sus índices.
- Documentación interactiva de cada servicio en `http://localhost:<puerto>/docs`.

### Datos demo

Al levantar Compose se inicializan datos de demostración idempotentes en las cuatro bases. Para regenerarlos desde cero:

```bash
docker compose down -v
docker compose up -d --build
```

Usuarios disponibles con contraseña `DemoTFinder123!`:

- `admin@tfinder.dev`
- `gm@tfinder.dev`
- `jugador1@tfinder.dev`
- `jugador2@tfinder.dev`
- `jugador3@tfinder.dev`

Para desactivarlos: `DEMO_SEED_ENABLED=false`.

## Modelo de datos — entidad Mesa

| Campo | Tipo | Obligatorio | Validación |
|---|---|---|---|
| nombre | TEXT | Sí | mínimo 1 carácter |
| sistema | TEXT | Sí | **Literal `pf1e` (VAL-08)** |
| descripcion | TEXT | No | — |
| tono | TEXT | No | — |
| horario | TEXT | No | — |
| estado | TEXT | No | `abierta` o `cerrada` (default: `abierta`) |
| nivel_inicial | INTEGER | No | >= 0, tipo estricto |
| jugadores_max | INTEGER | No | > 0, tipo estricto; no puede bajar debajo de `jugadores_actuales` (VAL-15 → 409) |
| **gm_id** | BIGINT FK usuarios | Sí (peticiones nuevas) | propietario: solo el GM (o admin) edita/elimina (RN-02/VAL-17 → 403) |
| jugadores_actuales | INT | cachea | contador atómico de cupo (409 cuando se agota) |
| fecha_creacion | DATETIME | No | se asigna automáticamente |

> **Campos de tipo estricto**: `nivel_inicial` y `jugadores_max` deben enviarse como números JSON reales. Si se envían como string (ej. `"5"`), la API los rechaza con `400`.

## Endpoints

Todas las rutas tienen el prefijo `/api/v1` y los errores usan el envelope unificado
`{"error":{"codigo","mensaje"}}`. La referencia OpenAPI de cada puerto (`/docs`)
incluye `securitySchemes: BearerAuth`. Resumen por servicio (puerto host):

**mesas-api 8001** — `mesas`, `auth` (register/login/refresh/logout/me + acceso
admin), `matchmaking/{mesa_id}/abrir` + `estado` (con sesión), `sesiones`
(crear/confirmar/cerrar + QR `emitir/validar` — valida asistencia solo el GM de
la mesa), **`fechas`** (propuestas del GM + voto editable de miembros +
`confirmar` → crea la sesión, RF-10/11).

**builds-api 8002** — `builds` (listado con filtros `mesa_id/autor_id/tag`,
oculta `privado/borrador` ajenos), **`POST/PUT/DELETE /builds`** con
atributos 3–18 (VAL-44/45), historial de versiones apilable y
`POST /builds/{id}/restaurar/{idx}` (RN-19), `publicar`, `vincular/{mesa_id}`
(exige membresía vía REST a mesas-api, VAL-40), `tags` (GET/POST).

**feed-api 8003** — `feed` (GET con filtros + **POST publicar** con
`embed`/`autorNombre`), `POST /feed/{id}/like` (toggle, VAL-43),
`POST /usuarios/{id}/seguir` + `GET seguidores` (RN-10),
**`wiki`** (listado público + CRUD del GM bajo `mesas/{id}/wiki` con
visibilidad `privada|jugadores|publica`, RN-05), `diario` (POST + PDF).

**notif-api 8004** — `notificaciones` (listado/leída/leer-todas + SSE
`/stream` con token), `auth/recuperar`, `event-log`, `emails`, `pdf`
(estado/descarga), `dlq` (listar/reintentar/descartar).

## Formato de errores

Todos los errores de la API (400, 404, 500) devuelven una respuesta con la misma estructura:

```json
{"error": {"codigo": 404, "mensaje": "Mesa no encontrada"}}
```

| Código | Significado |
|---|---|
| 400 | Datos de entrada inválidos (validación) |
| 404 | Recurso no encontrado |
| 500 | Error interno del servidor |
