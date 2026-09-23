## Why

El monolito de AE1 (una app FastAPI + una SQLite `tfinder.db`, carpeta `app/`) no puede sostener el catálogo de servicios de AE2 (`mesas-api`, `builds-api`, `feed-api`, `notif-api`) ni la propiedad de datos con **cero lecturas SQL cruzadas** (RNF-04). Sin esta separación en servicios con DB PostgreSQL propias (ya provistas por B01) no se puede avanzar con B03–B11, que construyen sobre servicios/módulos específicos.

## What Changes

- **BREAKING**: Reestructura el repo en cuatro servicios FastAPI independientes:
  - `mesas_api/` (puerto 8001, `mesas_db`) — CRUD de mesas AE1 migrado + próximos flujos (auth, matchmaking, sesiones).
  - `builds_api/` (puerto 8002, `builds_db`) — builds/tags/encuentros.
  - `feed_api/` (puerto 8003, `feed_db`) — feed/wiki/diarios.
  - `notif_api/` (puerto 8004, `notif_db`) — notificaciones/emails/event_log/documentos.
- **Migración SQLite → PostgreSQL**: cada `app/db.py` abre un pool `psycopg_pool` a **su** `*_db`; el `schema.sql` de mesas pasa a DDL PostgreSQL por servicio; `tfinder.db` deja de usarse.
- **Endpoints básicos de lectura en builds/feed/notif** (`GET /api/v1/builds`, `GET /api/v1/tags`, `GET /api/v1/feed`, `GET /api/v1/wiki`, `GET /api/v1/notificaciones`, `GET /api/v1/event-log`) para que el mock del frontend pueda conectarse. Los flujos completos (solicitudes, matchmaking, sesiones, QR, PDF, email) llegan en B03–B09.
- `docs/PROPIEDAD_DE_DATOS.md` documenta quién es dueño de cada tabla; verificación automática (`rg`) de que ningún servicio consulta la `*_db` de otro.
- Docker: `Dockerfile` parametrizado con `ARG SERVICE`; `docker-compose.yml` pasa el servicio `api` a `mesas-api` y agrega `builds-api`, `feed-api`, `notif-api` (opcionales); `.dockerignore` y `.env.example` actualizados.

## Capabilities

### New Capabilities
- `backend-servicios`: arquitectura de cuatro servicios FastAPI independientes, persistencia PostgreSQL por servicio con pool propio y sin lecturas SQL cruzadas, propiedad de datos documentada, y API pública básica de lectura en los servicios builds/feed/notif para integrarse con el frontend. El servicio `mesas-api` conserva el CRUD de mesas operativo.

### Modified Capabilities
- Ninguna: `infra-containers` (B01) sigue describiendo el entorno de infraestructura; la exposición de los cuatro servicios a la red de compose se incorpora como parte de `backend-servicios` (escenario del servicio `api` de B01 sigue cubierto por `mesas-api`).

## Impact

- **Código**: se reemplaza `app/` (monolito) por `mesas_api/`, `builds_api/`, `feed_api/`, `notif_api/`; `app/infra/` (redis/rabbitmq) se replica como base común reutilizada por los servicios. Se elimina el `main.py` raíz residual de AE1.
- **Configuración**: `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `.env.example` actualizados.
- **Datos**: tablas de mesas creadas en `mesas_db` (DDL PostgreSQL); sin migración de datos desde `tfinder.db` (datos de desarrollo descartables).
- **Dependencias**: `psycopg[binary]` y `psycopg_pool` ya están en `requirements.txt` (B01); se quita la dependencia de SQLite del runtime.
- **Pruebas**: el smoke test de AE1 se adapta a `mesas_api` contra `mesas_db`; la batería pytest full queda para B11.