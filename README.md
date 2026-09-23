# TFinder — Módulo de Gestión de Mesas (AE1)

**TFinder** es una API REST para gestionar la entidad **Mesa**, basada en el juego de rol **Pathfinder 1.ª edición**. El objetivo es realizar un **CRUD completo** (crear, listar, obtener, actualizar y eliminar) de mesas de juego, cumpliendo con las **consignas del AE1** de la materia Paradigmas III. La aplicación está construida con FastAPI, persiste en SQLite y maneja de forma centralizada los errores con un formato de respuesta uniforme.

## Integrantes
- Amarilla Lucio
- Czajkowski Leonardo

## Stack Tecnológico
- Lenguaje: Python 3.11+
- Framework: FastAPI
- Persistencia: SQLite
- Servidor ASGI: Uvicorn

## Requisitos previos
- Python 3.11 o superior instalado (`python --version`).
- `pip` disponible (incluido con Python).

## Estructura del proyecto
```bash
TFinder/
├── .env                        # (NO se sube, va en .gitignore)
├── .env.example                # sí se sube, con claves sin valores sensibles
├── .gitignore
├── requirements.txt
├── README.md
├── REPORTE_PRUEBAS.md          # reporte de pruebas funcionales de los endpoints
├── schema.sql                  # DDL de la tabla mesas
├── main.py                     # punto de entrada, instancia FastAPI, arranca Uvicorn
└── app/
    ├── __init__.py
    ├── db.py                   # conexión SQLite + init_db() + migraciones
    ├── routes/
    │   ├── __init__.py
    │   └── mesas_routes.py     # define los endpoints /api/v1/mesas
    ├── controllers/
    │   ├── __init__.py
    │   └── mesas_controller.py # lógica intermedia entre rutas y modelo
    ├── models/
    │   ├── __init__.py
    │   └── mesas_model.py      # esquemas Pydantic (MesaCreate, MesaUpdate, MesaOut) + acceso a datos
    └── middleware/
        ├── __init__.py
        └── error_handler.py    # manejador centralizado de excepciones (400/404/500)
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
docker compose up -d --build mesas-api builds-api feed-api notif-api
```

- Al arrancar, cada servicio abre su pool `psycopg_pool` contra su `*_db`, crea sus tablas (`schema.sql` idempotente) y aplica sus índices.
- Documentación interactiva de cada servicio en `http://localhost:<puerto>/docs`.

## Modelo de datos — entidad Mesa

| Campo | Tipo | Obligatorio | Validación |
|---|---|---|---|
| nombre | TEXT | Sí | mínimo 1 carácter |
| sistema | TEXT | Sí | mínimo 1 carácter |
| descripcion | TEXT | No | — |
| tono | TEXT | No | — |
| horario | TEXT | No | — |
| estado | TEXT | No | `abierta` o `cerrada` (default: `abierta`) |
| nivel_inicial | INTEGER | No | >= 0, tipo estricto |
| jugadores_max | INTEGER | No | > 0, tipo estricto |
| fecha_creacion | DATETIME | No | se asigna automáticamente |

> **Campos de tipo estricto**: `nivel_inicial` y `jugadores_max` deben enviarse como números JSON reales. Si se envían como string (ej. `"5"`), la API los rechaza con `400`.

## Endpoints

Todas las rutas tienen el prefijo `/api/v1`. Los errores siguen el formato unificado descrito en [Formato de errores](#formato-de-errores).

### GET /api/v1/mesas
Lista todas las mesas.
- Respuesta: `200 OK` + array JSON

```bash
curl http://localhost:8000/api/v1/mesas
```

**Respuesta — `200 OK`:**
```json
[
  {
    "id": 1,
    "nombre": "Mesa Alpha",
    "sistema": "Pathfinder",
    "descripcion": null,
    "tono": null,
    "horario": null,
    "estado": "abierta",
    "nivel_inicial": null,
    "jugadores_max": 5,
    "fecha_creacion": "2026-08-28 19:28:30"
  }
]
```

### GET /api/v1/mesas/{id}
Obtiene una mesa por ID.
- `200 OK` + objeto Mesa si existe
- `404 Not Found` + `{"error": {"codigo": 404, "mensaje": "..."}}` si no existe

```bash
curl http://localhost:8000/api/v1/mesas/1
```

**Respuesta — `200 OK`:**
```json
{
  "id": 1,
  "nombre": "Mesa Alpha",
  "sistema": "Pathfinder",
  "descripcion": null,
  "tono": null,
  "horario": null,
  "estado": "abierta",
  "nivel_inicial": null,
  "jugadores_max": 5,
  "fecha_creacion": "2026-08-28 19:28:30"
}
```

**Respuesta — `404 Not Found` (id inexistente):**
```json
{"error": {"codigo": 404, "mensaje": "Mesa 9999 no encontrada"}}
```

### POST /api/v1/mesas
Crea una mesa. Body: `{"nombre": "...", "sistema": "...", ...}`
- `201 Created` + objeto creado (campos obligatorios: `nombre`, `sistema`)
- `400 Bad Request` si faltan campos obligatorios o hay datos inválidos

```bash
curl -X POST http://localhost:8000/api/v1/mesas \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Mesa Alpha", "sistema": "Pathfinder", "jugadores_max": 5}'
```

**Respuesta — `201 Created`:**
```json
{
  "id": 1,
  "nombre": "Mesa Alpha",
  "sistema": "Pathfinder",
  "descripcion": null,
  "tono": null,
  "horario": null,
  "estado": "abierta",
  "nivel_inicial": null,
  "jugadores_max": 5,
  "fecha_creacion": "2026-08-28 19:28:30"
}
```

**Respuesta — `400 Bad Request` (faltan campos obligatorios):**
```json
{"error": {"codigo": 400, "mensaje": "body.nombre: Field required; body.sistema: Field required"}}
```

### PUT /api/v1/mesas/{id}
Actualiza una mesa existente (update parcial: solo cambia los campos enviados).
- `200 OK` + objeto actualizado
- `404 Not Found` si no existe
- `400 Bad Request` si hay datos inválidos

```bash
curl -X PUT http://localhost:8000/api/v1/mesas/1 \
  -H "Content-Type: application/json" \
  -d '{"estado": "cerrada", "jugadores_max": 4}'
```

**Respuesta — `200 OK`:**
```json
{
  "id": 1,
  "nombre": "Mesa Alpha",
  "sistema": "Pathfinder",
  "descripcion": null,
  "tono": null,
  "horario": null,
  "estado": "cerrada",
  "nivel_inicial": null,
  "jugadores_max": 4,
  "fecha_creacion": "2026-08-28 19:28:30"
}
```

**Respuesta — `404 Not Found` (id inexistente):**
```json
{"error": {"codigo": 404, "mensaje": "Mesa 9999 no encontrada"}}
```

### DELETE /api/v1/mesas/{id}
Elimina una mesa existente.
- `204 No Content` si se elimina (sin body)
- `404 Not Found` si no existe

```bash
curl -X DELETE http://localhost:8000/api/v1/mesas/1
```

**Respuesta — `204 No Content`** (sin cuerpo en la respuesta).

**Respuesta — `404 Not Found` (id inexistente):**
```json
{"error": {"codigo": 404, "mensaje": "Mesa 9999 no encontrada"}}
```

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
