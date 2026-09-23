# Propiedad de Datos — TFinder AE2 (B02–B03)

Cada base de datos pertenece a **un único servicio** (su dueño). Ningún servicio
lee ni escribe SQL sobre las bases de los demás dominios (RNF-04: cero lecturas
SQL cruzadas). Cuando un servicio necesita datos de otro dominio, los obtiene por
contrato REST (API del servicio dueño) o por evento (cola RabbitMQ, B06) — nunca
por consulta SQL directa.

## Dueños por base y tabla

| Base        | Tabla            | Servicio dueño | Endpoints que la exponen                |
| ----------- | ---------------- | -------------- | --------------------------------------- |
| `mesas_db`  | `mesas`          | `mesas-api`    | `GET/POST /api/v1/mesas`, `GET/PUT/DELETE /api/v1/mesas/{id}` |
| `mesas_db`  | `usuarios`       | `mesas-api`    | `POST /api/v1/auth/register`, `POST /api/v1/auth/login` (B03) |
| `builds_db` | `builds`         | `builds-api`   | `GET /api/v1/builds`, `GET /api/v1/builds/{id}` |
| `builds_db` | `tags`           | `builds-api`   | `GET /api/v1/tags`                      |
| `feed_db`   | `publicaciones`  | `feed-api`     | `GET /api/v1/feed`                      |
| `feed_db`   | `wiki_paginas`   | `feed-api`     | `GET /api/v1/wiki`                      |
| `notif_db`  | `notificaciones` | `notif-api`    | `GET /api/v1/notificaciones`            |
| `notif_db`  | `event_log`      | `notif-api`    | `GET /api/v1/event-log`                 |

## Reglas

- Un servicio abre pool con `psycopg_pool` únicamente contra su propia `*_db`
  (ver `app/db.py` de cada servicio — ahí vive el default de `DATABASE_URL`).
- Cualquier tabla o columna nueva se agrega al `schema.sql` del servicio dueño.
- `mesas_db` guarda el catálogo de mesas y los usuarios del dominio de autenticación (B03); los flujos de sesiones (B07) y matchmaking (B10) agregan tablas al servicio dueño correspondiente o consumen eventos, sin tocar tablas ajenas.

## Verificación automatizable

Ninguna URL de base debe aparecer fuera del `db.py` del servicio dueño:

```bash
rg "postgresql://.*(builds|feed|notif|mesas)_db" */app --glob '*.py'
```

El resultado debe listar únicamente el `db.py` del servicio que es dueño de esa base.