# Design — B02: Separación en cuatro servicios FastAPI

## Context

Ver `proposal.md — Why`. Partimos de B01 terminado (compose con Postgres con `mesas_db`, `builds_db`, `feed_db`, `notif_db`; Redis, RabbitMQ y MailHog; clientes compartidos en `app/infra`) y del monolito AE1 (`app/` FastAPI sobre `tfinder.db` SQLite). El frontend (`tfinder-vue`) es 100 % mock y define el contrato de nombres/errores que los servicios deben calcar (p. ej. `GET /api/v1/mesas`, shape de `build`/`notificacion` en `src/data/*.json`).

## Goals / Non-Goals

**Goals**
- Cuatro paquetes FastAPI importables por separado, cada uno con su propio pool `psycopg_pool` a su `*_db`.
- Capa base uniforme (main → routes → controllers → models/schemas) para que B03–B09 crezcan sin reestructurar.
- CRUD de mesas de AE1 migrado a `mesas_db` con el mismo contrato de API y errores.
- Endpoints de lectura básicos en builds/feed/notif con schemas calcados del mock.
- `docs/PROPIEDAD_DE_DATOS.md` + verificación `rg` de cero lecturas SQL cruzadas.
- Docker: `Dockerfile` con `ARG SERVICE` y compose con los 4 servicios.

**Non-Goals**
- No implementar los flujos completos de dominios (auth, solicitudes, matchmaking, sesiones, QR/PDF/email, eventos) — llegan en B03–B09.
- No migrar datos desde `tfinder.db` (datos de desarrollo descartables; se re-siembran si hace falta en B11).
- No escribir la batería pytest full (B11); en su lugar verificaciones de humo contra compose.

## Decisions

**D1 — Layout de cada servicio.** Cada servicio es un paquete con `main.py` en la raíz y subpaquete `app`:

```
mesas_api/
  main.py        # FastAPI app, lifespan (pool db), routers /health, /api/v1/*
  app/
    __init__.py
    config.py    # lee DATABASE_URL (default propio), APP_NAME, DEBUG
    db.py        # ConnectionPool de psycopg_pool: open()/close() + dependency get_connection()
    routes/
      v1/
        mesas.py # router CRUD
    controllers/
      mesas.py   # SQL + lógica de dominio
    models/
      mesa.py    # dataclass de dominio
    schemas.py   # pydantic request/response (calcados del mock)
scripts/         # utilidades de dev (seed tags, verificación)
```

*Alternativas descartadas*: un solo repo con prefijos `services/*` (sobre-desarrollo para el plazo); FastAPI app compartida montada por entornos (viola "independientes"). La estructura plana por dominio es la que seguirá B03 en adelante.

**D2 — Pool por servicio, life-cycle en lifespan.** Cada `app/db.py` define `get_pool()`/`get_connection()` leyendo `DATABASE_URL`; si no está definida, usa el default del servicio (`postgresql://tfinder:tfinder@localhost:5432/<su_db>`). El pool se abre con `open=False` en construcción y se `open()`a/`close()`a en el lifespan del `main.py`. *Alternativa descartada*: abrir pool en import (fragiliza tests y arranques parciales).

**D3 — Variable de base propia por servicio.** Cada `app/db.py` lee su variable (`MESAS_DATABASE_URL`, `BUILDS_DATABASE_URL`, `FEED_DATABASE_URL`, `NOTIF_DATABASE_URL`) y, si no está definida, usa su default local (`localhost:5432/<su_db>`). *Razón*: el `.env` raíz (AE1) define `DATABASE_URL=...mesas_db`; si los 4 servicios lo cargaran, todos conectarían a `mesas_db` (falla detectada y corregida en verificación). En compose cada servicio define su variable apuntando al host interno `postgres`; `DATABASE_URL` queda como var legacy para herramientas locales (psql). *Alternativa descartada*: un solo `DATABASE_URL` compartido — colisiona entre servicios locales.

**D4 — Schema DDL PostgreSQL por servicio** en `mesas_api/app/schema.sql` (y análogos), idempotente (`IF NOT EXISTS`). Columnas listas de mesas calcan el esquema SQLite de AE1 pero con tipos PG (`JSONB` para `lista_usuarios`, `TIMESTAMPTZ`). Tablas mínimas para los endpoints de lectura:

- `mesas_db.mesas`
- `builds_db`: `builds` (con `tags` JSONB) + catálogo `tags`
- `feed_db`: `publicaciones` (feed) + `wiki_paginas` (wiki)
- `notif_db`: `notificaciones` + `event_log`

**D5 — Schemas calcados del mock.** Los nombres de campos y códigos de error del frontend (`src/services/*.js` y `src/data/*.json`) son la especificación de contratos en B02; los pydantic schemas replican esos nombres y el controlador devuelve exactamente esas claves.

**D6 — Reuso de `app/infra`.** En B02 los servicios solo necesitan Postgres; `app/infra` (Redis/RabbitMQ, B01) se conserva como paquete compartido en `app/` y lo consumirá el servicio que lo use (B05/B06). Del monolito AE1 se eliminan `app/main.py`, `app/core/`, `app/modules/`, `app/shared/` y el `schema.sql` raíz (SQLite), integrándose lo útil en `mesas_api/`.

**D7 — Seed mínimo de catálogos.** El `tags` de builds se siembra con `scripts/seed_tags.py` si la tabla está vacía (constante local, sin dependencias del frontend), para que `GET /api/v1/tags` responda datos reales.

**D8 — Verificación de done.** Confirmar: `uvicorn mesas_api.main:app --port 8001` (builds/feed/notif análogos) responden; `rg "postgresql://.*(builds|feed|notif|mesas)_db" */app --glob '*.py'` devuelve solo el `db.py` del dueño; smoke test del CRUD de mesas real contra `mesas_db`; compose levanta los 4 y responden `/docs`.

## Risks / Trade-offs

- [Divergencia de schemas con el frontend] → Mitigación: D5, los schemas se derivan de `src/data/*.json`, no inventados.
- [Fuga de lecturas SQL cruzadas en fixes futuros] → Mitigación: `PROPIEDAD_DE_DATOS.md` explícito + `rg` en tareas B02 y como criterio de done.
- [Pérdida de la app AE1 en el corte] → Mitigación: los módulos vacíos de AE1 (`auth`, `solicitudes`, `shared`) no aportan comportamiento; su reemplazo por dominio ocurre en B03/B04.
- [Pool sin cerrar en dev] → Mitigación: D2 lifecycle en lifespan; default de dev cierra al apagar el proceso.
- [Conflicto de puerto con el servicio `api` de B01] → Mitigación: B02 reemplaza `api` por `mesas-api` en el mismo puerto 8001.

## Migration Plan

1. Crear los 4 paquetes con la capa base (config/db/main/health) en la rama de trabajo.
2. Migrar CRUD de mesas + DDL a `mesas_api/`; quitar el monolito `app/` residual y el `main.py` raíz.
3. Implementar endpoints de lectura de builds/feed/notif con sus DDL y schemas.
4. `docs/PROPIEDAD_DE_DATOS.md`, `.env.example` y `.dockerignore`; `Dockerfile` con `ARG SERVICE` y compose con 4 servicios.
5. Verificar live contra compose y ejecutar `rg` de no-cruzada.
6. Rollback: la rama es corta y el commit único por tarea; revertir el merge restaura `AE2-Backend` con B01 intacto.

## Open Questions

- Ninguna que cambie specs/approach/tasks. El seed de datos de demo (builds, feed, notif reales) queda para B11.