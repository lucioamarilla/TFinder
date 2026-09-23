## 1. Estructura base de los cuatro servicios

- [ ] 1.1 Crear los paquetes `mesas_api/`, `builds_api/`, `feed_api/` y `notif_api/`, cada uno con `main.py`, `app/__init__.py`, `app/config.py` y `app/db.py`, y verificar que `find mesas_api builds_api feed_api notif_api -type f` lista los archivos esperados
- [ ] 1.2 En cada `app/config.py` definir `DATABASE_URL` con default propio por servicio (`mesas_db`, `builds_db`, `feed_db`, `notif_db`) y `APP_NAME`, y verificar con un `print` de import que cada config lee su default
- [ ] 1.3 En cada `app/db.py` implementar `get_pool()`/`get_connection()` con `psycopg_pool.ConnectionPool` (lifecycle en lifespan) y verificar que importar el pool de `mesas_api` no importa nada de `builds_api`/`feed_api`/`notif_api`
- [ ] 1.4 En cada `main.py` crear la app FastAPI con lifespan que abre/cierra el pool, exponer `/health` y montar routers v1, y verificar `uvicorn mesas_api.main:app --port 8001` (y análogos en 8002/8003/8004) responde `/health` con `200`

## 2. Persistencia PostgreSQL y CRUD de mesas

- [ ] 2.1 Escribir `mesas_api/app/schema.sql` con DDL idempotente (`CREATE TABLE IF NOT EXISTS`) de `mesas` en PostgreSQL (tipos PG, `JSONB` para lista de usuarios, `TIMESTAMPTZ`) calando el esquema de AE1, y verificar que se aplica sobre `mesas_db` sin errores
- [ ] 2.2 Implementar en `mesas_api/app/` el modelo `mesa.py`, `schemas.py` (pydantic calcos del mock) y el CRUD en `controllers/mesas.py` + `routes/v1/mesas.py` con el mismo contrato (crear/listar/obtener/actualizar/eliminar) y formato de errores que AE1, y verificar el smoke test real contra `mesas_db`: crear→listar→obtener→actualizar→eliminar responde los códigos esperados
- [ ] 2.3 Escribir DDL idempotente de `builds_db.builds` y `tags`, `feed_db.publicaciones` + `feed_db.wiki_paginas`, y `notif_db.notificaciones` + `notif_db.event_log` en los `schema.sql` de cada servicio, y verificar que cada uno se aplica a su base sin errores
- [ ] 2.4 Implementar `scripts/seed_tags.py` que siembra `tags` si está vacío (constante local) y verificar que `GET /api/v1/tags` devuelve la lista sembrada

## 3. Endpoints de lectura básicos (builds/feed/notif)

- [ ] 3.1 En `builds_api/` implementar `GET /api/v1/builds` (con filtro `?mesa_id=`) y `GET /api/v1/builds/{id}` devolviendo `200` con datos reales de `builds_db`, y verificar el listado con y sin filtro contra la base
- [ ] 3.2 En `feed_api/` implementar `GET /api/v1/feed` y `GET /api/v1/wiki` y verificar `200` con datos de `feed_db`
- [ ] 3.3 En `notif_api/` implementar `GET /api/v1/notificaciones` y `GET /api/v1/event-log` y verificar `200` con datos de `notif_db`

## 4. Propiedad de datos y verificación de no-cruzada

- [ ] 4.1 Escribir `docs/PROPIEDAD_DE_DATOS.md` que liste cada tabla de las cuatro bases con un dueño único, y verificar que solo incluye tablas definidas en los `schema.sql`
- [ ] 4.2 Actualizar `.env.example` y `.dockerignore` para los cuatro servicios y verificar que `.env.example` documenta `DATABASE_URL` con su default por servicio (proxy a `localhost:5432/<db>`)
- [ ] 4.3 Ejecutar `rg "postgresql://.*(builds|feed|notif|mesas)_db" */app --glob '*.py'` y verificar que cada URL solo aparece en el `app/db.py` del servicio dueño (cero lecturas SQL cruzadas)

## 5. Docker: Dockerfile parametrizado y compose

- [ ] 5.1 Parametrizar `Dockerfile` con `ARG SERVICE` (CMD `uvicorn <SERVICE>.main:app --port 8001`) y verificar `docker compose build mesas-api builds-api feed-api notif-api` construye sin errores
- [ ] 5.2 Actualizar `docker-compose.yml`: renombrar el servicio `api` a `mesas-api` (puerto 8001) y agregar `builds-api` (8002), `feed-api` (8003) y `notif-api` (8004), cada uno con `DATABASE_URL` apuntando al host interno `postgres`, y verificar `docker compose config --quiet` no reporta errores
- [ ] 5.3 Levantar con `docker compose up -d mesas-api builds-api feed-api notif-api` y verificar que los cuatro responden `/docs` y `/health` en sus puertos publicados sin errores

## 6. Cierre de la tarea

- [ ] 6.1 Ejecutar `openspec validate` y verificar que el change `b02-servicios` es válido
- [ ] 6.2 Crear la rama `f/B02_servicios` desde `AE2-Backend`, commitear el change y la implementación con mensaje AE2 `refactor(backend): separacion en 4 servicios (#15)`, mergear a `AE2-Backend` y archivar el change con `openspec archive`
- [ ] 6.3 Cerrar el issue GitHub #15