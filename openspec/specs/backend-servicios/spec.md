# backend-servicios Specification

## Purpose

Define la arquitectura de servicios de TFinder AE2: cuatro aplicaciones FastAPI independientes (mesas, builds, feed, notif) con persistencia PostgreSQL propia por servicio, propiedad de datos documentada, cero lecturas SQL cruzadas y una API pública de lectura básica para que el frontend pueda conectarse.

## Requirements

### Requirement: Servicios independientes por dominio
El sistema SHALL descomponerse en cuatro servicios FastAPI ejecutables por separado — `mesas-api` (8001), `builds-api` (8002), `feed-api` (8003) y `notif-api` (8004) — de modo que cada uno arranca con `uvicorn` sobre el puerto de su servicio sin importar ni requerir el `app` de otro servicio.

#### Scenario: Arranque individual de cada servicio
- **WHEN** se ejecuta `uvicorn mesas_api.main:app --port 8001` (y análogos para los otros tres servicios)
- **THEN** cada proceso arranca y responde en su puerto sin errores de importación cruzada entre servicios

### Requirement: Persistencia PostgreSQL con pool por servicio
Cada servicio DEBE abrir su propio pool `psycopg_pool` sobre su base de datos designada — `mesas_api` sobre `mesas_db`, `builds_api` sobre `builds_db`, `feed_api` sobre `feed_db`, `notif_api` sobre `notif_db` — con un default de `DATABASE_URL` propio por servicio, y DEBE evitar conexiones a las bases de otros servicios.

#### Scenario: Pool propio y conectable
- **WHEN** se importa el `db.py` de un servicio en un entorno con su `*_db` disponible
- **THEN** el pool abre una conexión a esa base y responde `select 1` → `(1,)`, sin depender de las bases de los otros servicios

#### Scenario: Ausencia de lecturas SQL cruzadas
- **WHEN** se ejecuta la verificación `rg "postgresql://.*(builds|feed|notif|mesas)_db" */app --glob '*.py'`
- **THEN** la URL de cada `*_db` solo aparece dentro del `db.py` del servicio dueño de esa base

### Requirement: Propiedad de datos documentada
El sistema SHALL exponer en `docs/PROPIEDAD_DE_DATOS.md` el dueño de cada tabla de cada base, de modo que cada tabla pertenezca a un único servicio y el documento indique cómo un servicio obtiene datos de otro dominio (evento o contrato REST, nunca SQL directo).

#### Scenario: Catálogo de propiedad completo
- **WHEN** se revisa `docs/PROPIEDAD_DE_DATOS.md`
- **THEN** cada tabla de `mesas_db`, `builds_db`, `feed_db` y `notif_db` tiene un servicio dueño único y ninguna tabla figura con dos dueños

### Requirement: CRUD de mesas operativo sobre PostgreSQL
`mesas-api` DEBE conservar el CRUD de mesas de AE1 (crear, listar, obtener, actualizar, eliminar) funcionando contra `mesas_db` con la misma API y formato de errores.

#### Scenario: Ciclo completo de vida de una mesa
- **WHEN** se crea una mesa, se la lista, se la obtiene, se la actualiza y se la elimina vía `/api/v1/mesas`
- **THEN** cada operación responde con el código y el cuerpo esperados y los datos persisten en `mesas_db`.

### Requirement: API pública básica de lectura para integración
Los servicios `builds-api`, `feed-api` y `notif-api` DEBEN exponer endpoints de lectura básicos que permitan al frontend conectarse con datos reales: listado de builds (con filtro por mesa), tags, feed y wiki, notificaciones y event-log.

#### Scenario: Listado de builds filtrable por mesa
- **WHEN** se consulta `GET /api/v1/builds` (opcionalmente con `?mesa_id=`)
- **THEN** el servicio devuelve los builds del dominio, filtrados por mesa cuando se pasa el parámetro, con estado `200` y schemas consistentes

#### Scenario: Catálogo de tags
- **WHEN** se consulta `GET /api/v1/tags`
- **THEN** el servicio `builds-api` devuelve la lista de tags del dominio

#### Scenario: Feed y wiki
- **WHEN** se consultan `GET /api/v1/feed` y `GET /api/v1/wiki`
- **THEN** el servicio `feed-api` devuelve las publicaciones y páginas del dominio con estado `200`

#### Scenario: Notificaciones y event-log
- **WHEN** se consultan `GET /api/v1/notificaciones` (o `?solo_no_leidas=`) y `GET /api/v1/event-log`
- **THEN** el servicio `notif-api` devuelve las notificaciones y el historial de eventos con estado `200`

### Requirement: Servicios integrados al entorno de contenedores
El sistema SHALL exponer los cuatro servicios a la red de compose mediante imágenes propias (`ARG SERVICE` en el Dockerfile), de modo que `docker compose up -d mesas-api builds-api feed-api notif-api` los deje respondiendo en sus puertos publicados y `/docs` sin errores.

#### Scenario: Cuatro servicios en la red de compose
- **WHEN** se construyen y levantan `mesas-api`, `builds-api`, `feed-api` y `notif-api` con `docker compose`
- **THEN** cada contenedor responde en su puerto publicado (`8001`, `8002`, `8003`, `8004`) y expone `/docs` sin errores