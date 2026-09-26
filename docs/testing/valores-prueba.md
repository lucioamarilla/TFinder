# Valores de prueba cargados

Estos son los datos que quedaron cargados en el ambiente Docker verificado. Son datos de demostración; no usar credenciales ni datos reales en producción.

## 1. Infraestructura

| Servicio | Dirección | Credenciales o detalle |
|---|---|---|
| Frontend | `http://localhost:5173` | — |
| Mesas API | `http://localhost:8001` | Docs: `/docs` |
| Builds API | `http://localhost:8002` | Docs: `/docs` |
| Feed API | `http://localhost:8003` | Docs: `/docs` |
| Notificaciones API | `http://localhost:8004` | Docs: `/docs` |
| PostgreSQL | `localhost:5432` | `tfinder` / `tfinder` |
| Redis | `localhost:6390` | — |
| RabbitMQ AMQP | `localhost:5673` | `tfinder` / `tfinder` |
| RabbitMQ Management | `http://localhost:15673` | `tfinder` / `tfinder` |
| MailHog | `http://localhost:8025` | SMTP `localhost:1025` |

## 2. Usuarios

Todos usan la contraseña:

```text
DemoTFinder123!
```

| ID | Email | Nombre | Rol |
|---:|---|---|---|
| 1 | `admin@tfinder.dev` | Admin Demo | `admin` |
| 2 | `gm@tfinder.dev` | GM Demo | `gm` |
| 3 | `jugador1@tfinder.dev` | Jugador Uno | `usuario` |
| 4 | `jugador2@tfinder.dev` | Jugador Dos | `usuario` |
| 5 | `jugador3@tfinder.dev` | Jugador Tres | `usuario` |
| 6 | `email_svc@tfinder.dev` | Servicio Email | `usuario` |

Para obtener tokens actuales:

```bash
curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"jugador1@tfinder.dev","password":"DemoTFinder123!"}'
```

Los JWT no se incluyen aquí porque cambian con el tiempo, el `jti` y la configuración del servidor.

## 3. Mesas

| ID | Nombre | Sistema | Estado | Ocupación | Nivel inicial | Horario |
|---:|---|---|---|---|---:|---|
| 1 | Mesa Demo Abierta | PF1e | `abierta` | 2/4 | 1 | Viernes 20:00 |
| 2 | Mesa Demo Casi Llena | PF1e | `abierta` | 3/4 | 3 | Sábado 18:00 |
| 3 | Mesa Demo Cerrada | D&D 5e | `cerrada` | 0/6 | 5 | Sin reuniones |

### Solicitudes de unión cargadas

| ID | Mesa | Usuario | Estado | Clave de idempotencia |
|---:|---|---|---|---|
| 1 | 1 | Jugador Uno | `aceptada` | `demo-open-1` |
| 2 | 1 | Jugador Dos | `aceptada` | `demo-open-2` |
| 3 | 2 | Jugador Uno | `aceptada` | `demo-full-1` |
| 4 | 2 | Jugador Dos | `aceptada` | `demo-full-2` |
| 5 | 2 | Jugador Tres | `aceptada` | `demo-full-3` |
| 6 | 3 | Jugador Tres | `pendiente` | `demo-closed-pending` |

### Sesiones y asistencias

| Sesión ID | Mesa ID | Estado |
|---:|---:|---|
| 1 | 1 | `abierta` |
| 2 | 3 | `cerrada` |

| Asistencia ID | Sesión ID | Usuario ID |
|---:|---:|---:|
| 1 | 1 | 3 |
| 2 | 1 | 4 |

## 4. Builds y tags

| ID | Nombre | Persona | Clase | Raza | Nivel | Rol | Privacidad |
|---:|---|---|---|---|---:|---|---|
| 1 | Mago del Alba | PF Demo | Mago | Humano | 3 | Soporte | `publico` |
| 2 | Guardiana de Ustalav | Guerrera Demo | Guerrero | Humana | 4 | Defensa | `privado` |

Tags cargados:

```text
PF1e, Mago, Guerrero, Exploración, Táctica, Narrativa, Novato,
Veterano, Hechicero, Combate, Social, Campaña, Personaje
```

## 5. Feed y wiki

### Publicaciones

| ID | Tipo | Autor | Título | Etiqueta |
|---:|---|---|---|---|
| 1 | `post` | Admin Demo | ¡TFinder Demo disponible! | `seed-demo-post` |
| 2 | `build` | Jugador Uno | Build de mago listo | `seed-demo-build` |
| 3 | `wiki` | GM Demo | Guía de la campaña | `seed-demo-wiki` |

### Wiki

| ID | Mesa externa | Carpeta | Título | Tipo |
|---:|---|---|---|---|
| 1 | `demo-mesa` | `notas` | Bienvenida a la campaña | Nota |
| 2 | `demo-mesa` | `reglas` | Reglas de mesa | Regla |

## 6. Notificaciones y eventos

### Notificaciones

| ID | Grupo | Mensaje | Entidad |
|---:|---|---|---|
| 1 | mesas | Tu solicitud fue aceptada | Mesa Demo Abierta |
| 2 | sesiones | La campaña comienza el viernes | Mesa Demo Casi Llena |
| 3 | social | Nueva publicación de la comunidad | TFinder Demo |

### Event log

| Event ID | Tipo | Entidad | Acción | Correlation ID |
|---|---|---|---|---|
| `seed-demo-mesa` | `mesa` | `demo` | `seed` | `seed-demo-correlation` |
| `seed-demo-sesion` | `sesion` | `demo` | `seed` | `seed-demo-correlation` |

## 7. Valores para pruebas manuales

### Correlation IDs

Usar valores distintos para cada ejecución:

```text
manual-check-001
manual-join-001
manual-pdf-001
manual-email-001
```

### Claves de idempotencia

No reutilizar estas claves en operaciones nuevas salvo que se quiera probar la repetición de la misma solicitud:

```text
manual-join-mesa-1-001
manual-join-mesa-2-001
```

### Caso válido para login

```json
{
  "email": "jugador1@tfinder.dev",
  "password": "DemoTFinder123!"
}
```

### Caso válido para crear mesa

Enviar con un access token válido:

```json
{
  "nombre": "Mesa Manual de Pruebas",
  "sistema": "PF1e",
  "descripcion": "Mesa creada para pruebas manuales",
  "tono": "Exploración",
  "horario": "Viernes 20:00",
  "estado": "abierta",
  "nivel_inicial": 1,
  "jugadores_max": 4
}
```

### Caso de recuperación de email

```json
{
  "email": "jugador1@tfinder.dev"
}
```

### Caso de evento de notificación

```json
{
  "event_id": "manual-event-001",
  "tipo": "mesa.aceptada",
  "mesa_id": 1,
  "usuario_id": 3,
  "correlation_id": "manual-check-001"
}
```

## 8. Verificación de que los datos siguen cargados

```bash
docker exec tfinder-postgres psql -U tfinder -d mesas_db -c "SELECT count(*) AS usuarios FROM usuarios; SELECT count(*) AS mesas FROM mesas;"
docker exec tfinder-postgres psql -U tfinder -d builds_db -c "SELECT count(*) AS builds FROM builds; SELECT count(*) AS tags FROM tags;"
docker exec tfinder-postgres psql -U tfinder -d feed_db -c "SELECT count(*) AS publicaciones FROM publicaciones; SELECT count(*) AS wiki FROM wiki_paginas;"
docker exec tfinder-postgres psql -U tfinder -d notif_db -c "SELECT count(*) AS notificaciones FROM notificaciones; SELECT count(*) AS eventos FROM event_log;"
```

En una base limpia se esperan respectivamente `6/3`, `2/13`, `3/2` y `3/2`. Si una base ya tenía datos, los IDs pueden ser distintos; en ese caso usar los nombres y emails como identificadores de referencia.

## 9. Evidencia de la corrida E2E del 2026-09-26

Valores reales obtenidos contra el ambiente Docker, sin reinicios ni `docker compose down -v`.
Los casos marcados `PASS` fueron verificados con `curl` o por SQL directo.

### Salud de los servicios

| Puerto | `/health` | `/live` | `/ready` | Rutas en `/openapi.json` |
|---:|---|---|---|---:|
| 8001 | `{"status":"ok","servicio":"mesas-api"}` | `{"estado":"vivo"}` | `listo` | 18 |
| 8002 | `{"status":"ok","servicio":"builds-api"}` | `{"estado":"vivo"}` | `listo` | 7 |
| 8003 | `{"status":"ok","servicio":"feed-api"}` | `{"estado":"vivo"}` | `listo` | 6 |
| 8004 | `{"status":"ok","servicio":"notif-api"}` | `{"estado":"vivo"}` | `listo` | 15 |

Proxy del frontend (`http://localhost:5173`): las cuatro rutas responden y alcanzan las APIs reales.

```text
mesas-api  /api/v1/mesas            200  (lista de 3 mesas)
builds-api /api/v1/builds           200  (lista de 2 builds)
feed-api   /api/v1/feed             200  (lista de 3 publicaciones)
notif-api  /api/v1/notificaciones   401  (correcto: exige sesión)
```

### Autenticación (§8) — 14 casos, todos PASS

| ID | Resultado | Evidencia |
|---|---|---|
| A-01 | PASS | `200`, access y refresh token |
| A-02 | PASS | `401` `{"error":{"codigo":401,"mensaje":"Credenciales inválidas"}}` |
| A-03 | PASS | `401` con mensaje **idéntico** a A-02: no enumera usuarios |
| A-04 | PASS | `200` con `sub`, `rol`, `email`, `tipo`, `jti` |
| A-05 | PASS | `401` `Autenticación requerida` |
| A-06 | PASS | `401` `Token inválido o expirado` |
| A-07 | PASS | `200` con nuevo access token |
| A-08 | PASS | `401` `Use el refresh_token` |
| A-09 | PASS | `401` `Use the access_token` |
| A-10 | PASS | `200 {"ok":true}`; el access usado después responde `401 Sesión revocada` |
| A-11 | PASS | `200 {"ok":true}` con rol `admin` |
| A-12 | PASS | `403 Rol insuficiente` con `usuario` y también con `gm` |
| A-13 | PASS | `201`; la cuenta nace con `rol: "usuario"` pese a enviar `rol: "admin"` |
| A-14 | PASS | `403` en `/auth/admin-only` con la cuenta escalada |

### Mesas (§9) — 12 casos, todos PASS

`ME-01` 3 mesas · `ME-02` 200 · `ME-03` 404 · `ME-04` 201 (id=4) · `ME-05` 401 · `ME-06` 400
`body.nombre: Field required` · `ME-07` 400 `body.estado: Input should be 'abierta' or 'cerrada'` ·
`ME-08` 200 con `PUT` (no `PATCH`) · `ME-09` 404 · `ME-10` 204 y luego 404 · `ME-11` 2 miembros ·
`ME-12` 401.

> La guía no especifica el método HTTP de actualización. El endpoint
> `PUT /api/v1/mesas/{mesa_id}` acepta `get`, `put` y `delete`; `PATCH` devuelve `405`.

### Solicitud de unión (§10) — PASS

| Caso | Resultado |
|---|---|
| Primera unión | `201`, `id=7` |
| Misma `Idempotency-Key` repetida | `201` con el **mismo** `id=7`, sin fila duplicada |
| Ocupación tras la repetición | `1/1` (no se consumió una segunda vacante) |
| Mesa inexistente | `404` |
| Sin token | `401` |
| Legacy `POST /mesas/{id}/solicitar` | `202 {"estado":"pendiente"}` |
| Mesa llena | `409 Cupo agotado: no quedan vacantes` |

**Concurrencia** sobre mesa con 1 sola vacante y 3 usuarios simultáneos:

```text
201   (1 ganador)
409   (2 perdedores)
ocupación final: 1/1
filas en solicitudes_uniones: 1
```

### Matchmaking y QR (§11) — PASS salvo D-01

| ID | Resultado | Evidencia |
|---|---|---|
| MM-01 | PASS | `200 {"id":2,"estado":"abierto",...}` |
| MM-02 | PASS | `200 {"estado":"abierto","ttl_restante":120}` |
| MM-03 | PASS | `403 Rol insuficiente` para usuario normal |
| MM-04 | PASS | `401` sin token |
| MM-05 | **FAIL → corregido** | devolvía `500`; ahora `404` (defecto D-01) |

QR single-use: primera validación `200 {"asistencia":"registrada"}`; segunda `409`; QR alterado
`409`; sesión inexistente `404`; sin token `401`. Se generó **una sola** fila en `asistencias`.

### Builds, feed y PDFs (§12, §13) — PASS

`2` builds, `13` tags. Filtro por mesa inexistente devuelve `[]` sin error. `builds/99999` → `404`.
PDF de build y de diario: `202` con `documento_id`, estado `listo` al primer sondeo, descarga
`200` con `content-type: application/pdf` y archivo `PDF document, version 1.3, 1 page(s)`.
Sin token `401`; documento inexistente `404`.

Contenido real extraído del PDF de build:

```text
Ficha de personaje ID build: 1 Personaje: PF Demo Clase: Mago - Nivel: 3
Sistema: Pathfinder 1e - Fecha: 2026-09-26 - Ficha generada por TFinder AE2
```

`/api/v1/wiki?mesa_id=99999` devuelve `{"carpetas":[],"paginas":[],"total":0}`.
`/api/v1/feed` no declara parámetros de consulta: los filtros se ignoran en silencio.

### Notificaciones, SSE y email (§14) — 12 casos, todos PASS

`401` sin token en `notificaciones`, `PATCH leida` y `stream`. `403` con rol no admin en `dlq`,
`event-log` y `emails`; `200` con `admin`. `PATCH` sobre aviso ajeno → `404` y el aviso sigue
sin leerse. SSE verificado en vivo: la solicitud disparó la entrega de
`data: {"id":35, "titulo":"Solicitud aceptada", ...}`.

Recuperación de contraseña: `202 {"ok":true}` tanto para un email existente como para uno
inexistente, con **respuesta idéntica** (no hay enumeración de cuentas). Ambos correos llegaron
a MailHog (`http://localhost:8025`, total 2).

> Observación: el servicio envía el correo de recuperación también a direcciones que no existen
> en la base. No es una fuga por respuesta, pero en producción sería tráfico de correo saliente
> innecesario.

### Trazabilidad de punta a punta

Un `correlation_id` seguido desde mesas-api hasta notif-api a través de RabbitMQ:

```text
X-Correlation-Id: e2e-trace-1790455007
  -> POST /api/v1/mesas/8/solicitudes        (mesas-api)
  -> exchange tfinder.events, routing mesa.*  (RabbitMQ)
  -> cola notif.mesa, consumer notif-api
  -> event_log: entidad_tipo=mesa.aceptada, metadata={"mesa_id": 8},
     correlation_id=e2e-trace-1790455007
  -> GET /api/v1/event-log?correlation_id=e2e-trace-1790455007  (200, solo admin)
  -> notificaciones creadas para los usuarios 3 y 5
```

### RabbitMQ y DLQ (§15) — PASS

```text
exchanges: tfinder.events (topic, durable), tfinder.dlx (topic, durable)
colas:     notif.mesa, notif.sesion, doc.pdf, dlq.general
bindings:  mesa.* -> notif.mesa, sesion.* -> notif.sesion, doc.pdf.* -> doc.pdf
```

Ciclo operativo de DLQ: listar `200` (13 entradas) → reintentar `200` → descartar `200` →
descarte repetido `404 Mensaje no encontrado en DLQ`.

> `tfinder.dlx` no tiene ningún binding: la DLQ funciona por publicación directa desde
> `_base._dlq_final`, no por dead-letter de TTL.

### Casos no ejecutados

La §16 de la guía (reinicio limpio, pausa de Redis/RabbitMQ/Postgres, corte de SMTP, expiración
de TTL) queda `N/A` por decisión de alcance: no se autorizaron reinicios de contenedores ni
pausas de dependencias en esta corrida. El `/ready` degradado está cubierto de todos modos por
`tests/test_ready_degradado.py`, que simula la caída con mocks.

La §6 (M-01 a M-06) requiere navegador y quedó `N/A` en esta corrida: se verificó por HTTP que
todas las rutas de la SPA devuelven `200` y que el proxy alcanza las 4 APIs, pero no se validó
el renderizado ni la interacción.

## 10. Regenerar datos desde cero


Este comando borra los volúmenes Docker y todos los datos locales:

```bash
docker compose down -v
docker compose up -d --build
```

Después esperar el arranque de los servicios y repetir las consultas de la sección 8.
