# Informe técnico de la Actividad de Evaluación 2 — TFinder

**Proyecto:** TFinder — plataforma de búsqueda y gestión de mesas de juego de rol (Pathfinder 1.ª edición)
**Asignatura:** Paradigmas y Lenguajes de Programación III
**Codificación de la asignatura:** ISI17PL324
**Codificación de la actividad:** ISI17PL324V26AE2V26
**Sede:** {a completar por la cátedra}
**Facultad:** FAITA
**Carrera:** Ingeniería en Sistemas de Información
**Modalidad:** Presencial
**Nombre y apellido del docente:** {a completar por la cátedra}
**Estudiantes:** Amarilla Lucio · Czajkowski Leonardo
**DNI de los estudiantes:** {a completar por la cátedra}
**Fecha y horario de entrega:** {a completar por la cátedra}
**Tipo de evaluación:** Actividad de Evaluación 2
**Modalidad de instancia evaluativa:** Individual · Asincrónica
**Versión base de AE1:** `1781e4efb516cb8ac7c3965d140ba476c932cad2` (2026-08-28)
**Versión entregada en AE2:** tags `2.0.0` (alfa) y `2.1.0` (beta)
**AÑO:** 2026

---

## 0. Cómo leer este documento

Este es el informe técnico del **sistema completo**. Está organizado siguiendo los doce criterios de la rúbrica analítica de AE2, de modo que cada sección responde a un criterio y todas las afirmaciones técnicas son verificables contra el código.

Los alcances individuales van en documentos separados, porque AE2 es una instancia **individual** sobre una base grupal:

| Documento | Alcance individual | Issues |
|---|---|---|
| Este documento | El sistema completo y las decisiones compartidas | — |
| [`INFORME-AE2-AMARILLA-LUCIO.md`](./INFORME-AE2-AMARILLA-LUCIO.md) | Backend: B01–B12 | #14–#25 |
| [`INFORME-AE2-CZAJKOWSKI-LEONARDO.md`](./INFORME-AE2-CZAJKOWSKI-LEONARDO.md) | Frontend: F01–F09 | #26–#34 |

Documentos de referencia que **no** se reproducen aquí sino que se citan:

- `docs/ADR/ADR-001` … `ADR-007` — decisiones de arquitectura con contexto, decisión y consecuencias
- [`PROPIEDAD_DE_DATOS.md`](./PROPIEDAD_DE_DATOS.md) — dueño de cada base y tabla
- [`AUDITORIA_CIERRE_AE2.md`](./AUDITORIA_CIERRE_AE2.md) — auditoría de cierre y hallazgos
- `docs/testing/` — inventario, tutorial de pruebas, resultados de integración
- `AE2/evidencias/EVIDENCIAS.md` — índice de capturas por criterio
- `openspec/specs/` — 25 especificaciones de capacidad en formato GIVEN/WHEN/THEN

**Convención de citas:** toda afirmación técnica lleva `archivo:línea`. Los comandos son copiables y están verificados contra el repositorio.

---

## 1. Introducción breve

**TFinder** es una plataforma distribuida que permite a jugadores de rol encontrar, unirse y administrar mesas de juego: consultar un catálogo público de mesas, solicitar una vacante, gestionar la campaña de una mesa (sesiones, asistencia por QR, diario), y recibir notificaciones y documentos generados de forma asíncrona.

AE1 (v1.0) fue una **aplicación monolítica**: una sola aplicación FastAPI que exponía un CRUD de mesas sobre SQLite, sin autenticación, sin mensajería y sin estado compartido. El objetivo de AE2 no fue reconstruir el sistema sino **evolucionarlo** hacia una arquitectura distribuida donde la concurrencia, la consistencia y el desacoplamiento dejaran de ser problemas pendientes.

El recorrido funcional que AE2 debía sostener es el siguiente, y es el que se usa como hilo conductor de todo el informe:

```text
 Jugador            Frontend (Vue 3)         Backend (mesas_api)      Infraestructura
    |                    |                        |                        |
    |-- listar --------->|-- GET /mesas -------->|-- cache-aside ------->| Redis
    |                    |<-- 200 + X-Cache-Tier-|   miss -> SELECT      | PostgreSQL
    |                    |                        |                        |
    |-- unirse --------->|-- POST solicitudes -->|-- B1: SET NX EX 60 --->| Redis
    |   (Idempotency-Key)|   + Idempotency-Key   |-- B2: UPDATE .. RETURNING
    |                    |                        |    -> 201 Created     | PostgreSQL
    |                    |                        |    -> 409 Conflict    |
    |                    |                        |-- publica ------------>| RabbitMQ
    |                    |                        |    mesa.aceptada       |
    |<-- polling 5s / SSE --------------------------|-- consumidor --------->| notif-api
    |<-- notif + email -----------------------------|   (idemp. por event_id)| MailHog
    |                    |                        |                        |
    |-- validar QR ----->|-- POST qr/validar ---->|-- GETDEL ------------->| Redis
```

---

## 2. Punto de partida y trazabilidad AE1 → AE2

*(criterios 1 y 2 de la rúbrica)*

### 2.1 La versión base

El punto de partida es el commit **`1781e4e`** — "Merge pull request #13 from lucioamarilla/AE1", del 2026-08-28. Sobre ese commit arrancan los 90 commits de AE2.

```bash
git log --oneline 1781e4e..HEAD | wc -l     # 90
git show --no-patch --format='%H %ci %s' 1781e4e
```

### 2.2 Qué existía y qué se conservó

La comparación entre AE1 y AE2 es el punto de partida del criterio 1, así que conviene que sea explícita.

| Dimensión | AE1 (base `1781e4e`) | AE2 (tags `2.0.0` / `2.1.0`) |
|---|---|---|
| Unidad de despliegue | 1 aplicación FastAPI | 4 servicios FastAPI (8001–8004) |
| Persistencia | SQLite, archivo local | PostgreSQL 16, una base por servicio |
| Autenticación | Ninguna | JWT con revocación en Redis, roles `jugador` / `gm` / `admin` |
| Concurrencia | Sin cubrir (SQLite serializa por diseño) | Doble barrera Redis + Postgres, `Idempotency-Key` |
| Mensajería | Inexistente | RabbitMQ, 3 colas de trabajo, 1 DLQ, reintentos con backoff |
| Estado efímero | Inexistente | Redis con 4 usos distintos y TTL documentados |
| Artefactos | Inexistente | QR single-use, PDF asíncrono, email con outbox |
| Observabilidad | Ninguna | Logs JSON con `correlation_id`, `/live`, `/ready` |
| Pruebas | Manuales | 130 backend + 22 frontend, CI bloqueante |
| Frontend | No existía en el repositorio | Vue 3, 46 rutas, 44 vistas |

**Lo que se conservó de AE1 sin cambios de contrato:** la entidad `Mesa` y su CRUD. Los cinco endpoints públicos (`GET/POST/PUT/DELETE /api/v1/mesas`, `GET /api/v1/mesas/{id}`) mantienen su semántica; lo que cambió fue el host (`8000` → `8001`), la persistencia y el prefijo de versión que ya estaba en la ruta. `tests/test_api_contracts.py` fija un piso contractual de rutas por servicio para que una regresión en la superficie pública sea detectable.

**Lo que se descartó de AE1:** el backend monolítico de `app/routes|controllers|models` con SQLite. No se conservó código; sí se conservó el modelo de dominio. La decisión está en [ADR-001](../docs/ADR/ADR-001-postgres.md) y su módulo espejo `app/infra/`, que es la única parte de `app/` que los cuatro servicios comparten.

### 2.3 Los 21 requerimientos funcionales de AE2

Cada RF tiene un commit, un issue y una especificación en OpenSpec. La trazabilidad completa está en las 25 capacidades de `openspec/specs/`.

| RF | Título | Issue | Commit | Capacidad OpenSpec | Autor individual |
|---|---|---|---|---|---|
| B01 | Infraestructura y contenedores | #14 | `f892f7d` | `infra-containers` | Lucio |
| B02 | Separación en 4 servicios + PostgreSQL | #15 | `8dae133` | `backend-servicios` | Lucio |
| B03 | Autenticación JWT y sesiones | #16 | `3dd0272` | `auth-sesiones` | Lucio |
| B04 | Redis: caché, TTL de llamado, reserva | #17 | `6395191` | `redis-cache-ttl` | Lucio |
| B05 | Eventos RabbitMQ, DLQ e idempotencia | #18 | `6a70869` | `eventos-rabbitmq` | Lucio |
| B06 | Concurrencia y última vacante | #19 | `6610e3d` | `concurrencia-vacantes` | Lucio |
| B07 | QR de asistencia single-use | #20 | `29058f6` | `qr-asistencia` | Lucio |
| B08 | PDF asíncrono | #21 | `20b6849` | `pdf-async` | Lucio |
| B09 | Proveedor de email (MailHog) | #22 | `756b3f9` | `proveedor-email` | Lucio |
| B10 | Observabilidad y correlación | #23 | `9f10f66` | `observabilidad` | Lucio |
| B11 | Testing automatizado | #24 | `47008b6` | `testing` | Lucio |
| B12 | Cierre documental, ADRs y evidencias | #25 | `834af06` | `cierre-ae2` | Lucio |
| F01 | Capa HTTP unificada | #26 | `bf3774c` | `capa-http` | Leo |
| F02 | Autenticación real | #27 | `ed696f2` | `autenticacion-real` | Leo |
| F03 | Explorar mesas reales | #28 | `229fee5` | `explorar-mesas-real` | Leo |
| F04 | Unirse con carrera e idempotencia | #29 | `a44264b` | `unirse-carrera-idempotente` | Leo |
| F05 | Matchmaking con TTL de Redis | #30 | `f76e883` | `matchmaking-llamado` | Leo |
| F06 | QR de asistencia en la UI | #31 | `31bd32f` | `qr-asistencia-single-use` | Leo |
| F07 | Exportar PDF async | #32 | `2c57f14` | `exportar-pdf-async` | Leo |
| F08 | Notificaciones en vivo | #33 | `1b13721` | `notificaciones-vivo` | Leo |
| F09 | Administración y observabilidad | #34 | `4dcba75` | `admin-observabilidad` | Leo |
| — | Feature gating + suite Vitest | — | `dd7674e` | `testing` | Leo |

### 2.4 Ramas

| Rama | Commits desde AE1 | Contenido |
|---|---|---|
| `AE2-Backend` | 79 | B01–B12 |
| `origin/A2-Frontend` | 9 | F01–F05 |
| `AE2-Testing` (actual) | 90 | Integración, F06–F09, auditoría, testing, CI |

> **Nota sobre la convención de ramas.** La consigna propone `ae2/<usuario-o-apellido>` "a modo de convención". Las ramas efectivamente usadas son `AE2-Backend`, `A2-Frontend` y `AE2-Testing`, que distinguen igualmente los alcances. Se deja constancia para que la trazabilidad sea fiel al repositorio real y no a una convención ideal.

---

## 3. Arquitectura alcanzada y límites de responsabilidad

*(criterio 3 de la rúbrica)*

### 3.1 Los cuatro servicios

La decisión está en [ADR-006](../docs/ADR/ADR-006-servicios.md). Cuatro servicios, no uno ni ocho: cuatro es el número en el que cada uno tiene una base propia y una responsabilidad que no se solapa con ninguna otra.

| Servicio | Puerto | Responsabilidad | Base de datos | Prefijo |
|---|---|---|---|---|
| `mesas_api` | 8001 | Mesas, usuarios, autenticación, solicitudes de unión, matchmaking, sesiones y QR | `mesas_db` | `/api/v1/mesas`, `/api/v1/auth`, `/api/v1/matchmaking`, `/api/v1/sesiones` |
| `builds_api` | 8002 | Builds de personaje y catálogo de tags | `builds_db` | `/api/v1/builds`, `/api/v1/tags` |
| `feed_api` | 8003 | Feed social y wiki de mesa | `feed_db` | `/api/v1/feed`, `/api/v1/wiki` |
| `notif_api` | 8004 | Notificaciones, event-log, DLQ, documentos PDF y email | `notif_db` | `/api/v1/notificaciones`, `/api/v1/event-log`, `/api/v1/dlq`, `/api/v1/pdf` |

Los límites siguen el **contexto acotado**: una mesa no sabe qué es una build, y una notificación no sabe por qué se originó. La excepción deliberada es que `notif_api` consulte los miembros de una mesa por REST para poder dirigir un email — que es exactamente el mecanismo que el diseño obliga a usar y no un atajo (ver §8.3).

### 3.2 El código compartido y su límite

```text
app/                       # biblioteca compartida, SIN lógica de dominio
├── infra/
│   ├── redis.py           # get_redis() — cliente único
│   ├── rabbitmq.py        # publicar() / get_params() — productor
│   ├── errors.py          # envelope de error canónico
│   ├── ready.py           # evaluar_ready() — salud con dependencias
│   ├── logge.py           # logs JSON + correlation_id_var
│   └── params.py          # get_params() — config por env
├── middleware/
│   ├── error_envelope.py  # normaliza errores emitidos por el router
│   └── log_context.py     # inyecta y propaga X-Correlation-Id
└── services/
    └── http.py            # cliente HTTP entre servicios
```

La regla que se sostuvo durante todo el desarrollo es: **`app/` contiene infraestructura genérica, nunca reglas de negocio.** `get_redis()` sabe cómo conectarse a Redis; no sabe qué es una vacante. La regla es verificable y su evidencia está en §8.2.

### 3.3 Evolución respecto de AE1

AE1 no tenía servicios: tenía carpetas. La evolución real no fue "dividir el monolito en cajas" sino **cambiar la unidad de despliegue** y con ella tres cosas que antes no existían:

1. **Un pool de conexiones por servicio.** Cada servicio abre su propio `ConnectionPool` contra su propia base en el `lifespan` de FastAPI. En AE1 había una conexión global; ahora hay cuatro, y cada código que habla con la base de datos importa *su* pool, lo que hace que un acceso indebido sea visible en el import.
2. **Un esquema de inicialización por servicio.** Cada servicio ejecuta su propio `schema.sql` idempotente al arrancar (`mesas_api/main.py:42`, `builds_api/main.py:26`, `feed_api/main.py:24`, `notif_api/main.py:31`).
3. **Un origen de configuración por servicio**, todo por variables de entorno, sin secretos en el repositorio.

---

## 4. Comunicación síncrona y contratos REST

*(criterio 4 de la rúbrica)*

### 4.1 Superficie pública

La superficie se mide desde el esquema OpenAPI de cada servicio, que es lo que el cliente real consume:

| Servicio | Rutas declaradas | Piso contractual |
|---|---|---|
| `mesas_api` | 18 | 18 |
| `builds_api` | 7 | 7 |
| `feed_api` | 6 | 5 |
| `notif_api` | 15 | 9 |
| **Total** | **46** | 39 |

```bash
source venv/bin/activate
python -c "
import importlib
for s in ['mesas_api','builds_api','feed_api','notif_api']:
    app = importlib.import_module(f'{s}.main').app
    print(s, len(app.openapi()['paths']))
"
```

El piso contractual vive en `tests/test_api_contracts.py:8-13`. La diferencia entre el conteo real y el piso (`feed_api` 6 vs 5, `notif_api` 15 vs 9) es deliberada: el piso es una guarda contra regresiones queBORRARON endpoints, no una lista cerrada. Documentar una API con un piso que coincida exactamente con el presente la vuelve inútil ante cualquier adición legítima.

Cada servicio expone su documentación interactiva en `/docs` y su esquema en `/openapi.json`. La verificación de que las cuatro están completas y sirven el schema está en `docs/testing/manual-tests.md` §15.

### 4.2 El envelope de error: un contrato, cuatro servicios

Este es el punto donde AE2 corrigió un defecto real de la arquitectura heredada. FastAPI serializa `HTTPException` como `{"detail": "..."}`, y las dependencias de autenticación añaden además `{"detail": "..."}` por su cuenta. El sistema tenía por lo menos **dos convenciones de error simultáneas**, y un cliente no podía distinguirlas sin conocer cada servicio.

La solución tiene dos capas, porque un solo manejador de excepciones no alcanza.

**Capa 1 — manejadores de excepciones** (`app/infra/errors.py:73-83`):

| Excepción | Código | Comportamiento |
|---|---|---|
| `HTTPException` | `exc.status_code` | Envuelve el `detail` en el envelope |
| `RequestValidationError` | **400** (no el 422 de FastAPI) | Aplana `loc` → `campo: mensaje`, unido por `; ` |
| `Exception` | 500 | Loguea con traceback; **no filtra internos** |
| Excepciones de dominio | 400 / 404 / 409 | Mapeo por servicio (`mesas_api/app/errors.py`) |

**Capa 2 — middleware ASGI** (`app/middleware/error_envelope.py`, 136 líneas). Existe porque hay errores que Starlette emite **antes** de la capa de manejadores: el 404 y el 405 del router. Sin el middleware, esos dos salían en el formato de Starlette. `canonicalizar()` (`error_envelope.py:59-75`) es idempotente: devuelve `None` si el cuerpo ya trae `"error"`, de modo que no hay doble envoltura.

Dos detalles de diseño que vale la pena subrayar:

- **La caché de buffering solo se activa con `status >= 400`, content-type JSON y sin el marcador `x-tfinder-envelope: 1`** (`error_envelope.py:106`). Esto garantiza que un `200` con `text/event-stream` o `application/pdf` pase intacto. Hay un test que lo verifica: `tests/test_envelope_error.py:102-129` comprueba que un stream SSE no se rompe. Un middleware de normalización que rompiera el streaming en vivo habría sido peor que la inconsistencia que corrige.
- **Se traduce el inglés al español** (`error_envelope.py:46-51`): `"Not Found"` → `"Recurso no encontrado"`, `"Method Not Allowed"` → `"Método no permitido para este endpoint"`.

El contrato resultante, en los cuatro servicios:

```json
{ "error": { "codigo": 409, "mensaje": "Cupo agotado: no quedan vacantes" } }
```

`tests/test_envelope_error.py` verifica 7 casos parametrizados sobre los cuatro servicios, incluido que los manejadores compartidos sean **el mismo objeto** (`:46-55`), lo que impide que un servicio se desvíe por accidente.

### 4.3 El cliente HTTP del frontend

Del lado del cliente hay un único punto de paso para toda la red: `src/api/http.js`. Su firma es:

```js
api(servicio, ruta, { metodo, cuerpo, idempotenciaKey, timeoutMs = 8000 })
```

Inyecta `Content-Type`, `X-Correlation-Id` (uno por request) y, si hay sesión, `Authorization`. Agrega `Idempotency-Key` **solo cuando hay body**, de modo que un `GET` nunca lleva una clave de idempotencia sin sentido. Ante un `401` limpia la sesión y redirige a `/login?redirect=…`. El detalle de por qué esto importa está en `INFORME-AE2-CZAJKOWSKI-LEONARDO.md` §4.

### 4.4 Propagación del identificador de correlación

`X-Correlation-Id` es lo que permite reconstruir un flujo que atraviesa tres procesos:

```text
HTTP  X-Correlation-Id: cid-ev-2026-09-26-7f3a
  -> app/middleware/log_context.py  (extrae o genera, lo pone en correlation_id_var)
  -> log JSON de mesas_api
  -> app/infra/rabbitmq.py:30      (viaja dentro del cuerpo del evento)
  -> notif_api/app/consumers/_base.py:100  (lo restaura en el contexto del consumidor)
  -> log JSON de notif_api
```

La evidencia de que el mismo identificador aparece en los logs de dos servicios distintos es `AE2/evidencias/logs_correlation_id.png`, y la de que además se puede consultar por filtro es `AE2/evidencias/event_log_correlation.png` con `GET /api/v1/event-log?correlation_id=…` (`tests/test_event_log_correlation.py`).

---

## 5. Comunicación asíncrona y mensajería

*(criterio 5 de la rúbrica)*

La decisión está en [ADR-003](../docs/ADR/ADR-003-rabbitmq.md).

### 5.1 Topología

```text
                        exchange "tfinder.events"  (topic, durable)
                          |            |              |
            mesa.*        |     sesion.*      doc.pdf.*
                          v            v              v
                   notif.mesa   notif.sesion      doc.pdf
                          |            |              |
                          |            |         notif_api/app/workers/pdf.py
                    notif_api    notif_api                  |
                    consumers    consumers                  |
                          |            |                     |
                          +-----+------++--------------------+
                                |
                    (nack/reject o agotamiento de reintentos)
                                v
                        exchange "tfinder.dlx"  (topic, durable)
                                |
                          routing_key "#"
                                v
                          dlq.general  ──> tabla mensaje_dlq (notif_db)
                                          ──> GET /api/v1/dlq (admin)
```

Declarado en `notif_api/app/infra/amqp.py`:

| Elemento | Nombre | Tipo | Atributos |
|---|---|---|---|
| Exchange principal | `tfinder.events` | topic | `durable=True` |
| Exchange de errores | `tfinder.dlx` | topic | `durable=True` |
| Cola de mesa | `notif.mesa` | — | `durable`, `x-dead-letter-exchange: tfinder.dlx`, bind `mesa.*` |
| Cola de sesión | `notif.sesion` | — | `durable`, `x-dead-letter-exchange`, bind `sesion.*` |
| Cola de PDF | `doc.pdf` | — | `durable`, `x-dead-letter-exchange`, bind `doc.pdf.*` |
| Cola de fallidos | `dlq.general` | — | `durable`, bind al DLX con `#` |

Los mensajes se publican con `delivery_mode=2` (`app/infra/rabbitmq.py:44`), o sea persistentes: el broker los escribe a disco antes de confirmar.

**Un detalle que costó encontrar.** El binding de `dlq.general` al DLX (`amqp.py:39-40`) no es decorativo. Las tres colas de trabajo declaran `x-dead-letter-exchange`, así que cuando un mensaje se rechaza sin requeue, RabbitMQ lo enruta al exchange de errores. Si ese exchange no tiene ninguna cola bound, **descarta el mensaje en silencio**. El comentario en `amqp.py:34-38` documenta exactamente esta trampa, y `tests/test_amqp_topologia.py` la verifica por la management API, que es la única forma de inspeccionar bindings (pika no los expone).

### 5.2 El catálogo de eventos

| Evento | Productor | Consumidores | Efecto |
|---|---|---|---|
| `mesa.solicitada` | `mesas_api/app/services/eventos.py:4` | `notif.mesa` | Notificación al usuario + SSE |
| `mesa.aceptada` | `mesas_api/app/services/eventos.py:12` | `notif.mesa` | Notificación + SSE + email de confirmación |
| `mesa.expulsada` | `mesas_api/app/services/eventos.py:20` | `notif.mesa` | Notificación + SSE |
| `doc.pdf.build` | `builds_api/app/services/eventos.py:22` | `doc.pdf` | Genera PDF del build con `fpdf2` |
| `doc.pdf.diario` | `feed_api/app/services/eventos.py:38` | `doc.pdf` | Genera PDF del diario de sesión |

Cada productor tiene una funciónwrapper con nombre en lugar de llamar a `publicar()` con un string suelto. Es una decisión chica que evita que un typo en el routing key pase inadvertido hasta que nadie recibe el evento.

### 5.3 Consumption, reintentos e idempotencia

El lazo de consumo es común a las tres colas: `notif_api/app/consumers/_base.py:52-79`.

```text
basic_qos(prefetch_count=1)        # un mensaje a la vez por consumidor
basic_consume(auto_ack=False)      # ACK explícito, nunca automático

_procesar(mensaje) devuelve True  -> basic_ack    y log "evento procesado"
_procesar(mensaje) lanza          -> catch:
    intentos = mensaje["_intentos"] + 1
    intentos >= 3  -> _dlq_final(): ack + a dlq.general + registro en mensaje_dlq
    intentos <  3  -> sleep(2 ** intentos)      # backoff 1s, 2s, 4s
                       republicar con _intentos incrementado
                       basic_ack del original
```

Tres decisiones de esta construcción merecen explicación:

**El contador de reintentos viaja en el cuerpo, no en los headers.** Es la razón por la que el mecanismo es *ACK + republicar* en lugar de `nack(requeue=True)`. Con `nack(requeue=True)`, pika reencola la copia original del mensaje: los headers que uno_modificara se pierden y el contador no avanza, con lo cual el mensaje se reencola para siempre. Publicar una copia nueva con `_intentos` incrementado en el body hace que el contador sobreviva al viaje, y por eso el DLQ tiene un destino alcanzable.

**`prefetch_count=1` garantiza que no haya dos mensajes en vuelo por consumidor.** Con un valor mayor, un consumidor podría tener en memoria un mensaje que ya canceló lógicamente, y si el proceso muriera antes del ACK, ese trabajo se perdería. Con 1, la cola de RabbitMQ actúa como la única fuente de verdad sobre qué se procesó.

**El consumidor es idempotente por `event_id`.** Cada mensaje lleva un `event_id` en el envelope, y el consumidor consulta `event_log` antes de aplicar el efecto. Como el mecanismo de reintento es *republicar el mismo mensaje*, el mismo `event_id` puede llegar más de una vez; sin esta guarda, un reintento generaría una notificación duplicada o un segundo PDF. La guarda convierte el reintento en una operación segura, que es lo que la consigna pide al exigir que los consumidores toleren reintentos sin duplicar efectos.

### 5.4 Por qué estos procesos son asíncronos y no síncronos

El criterio para elegir es si el usuario necesita el resultado **antes** de que surequest termine.

| Proceso | ¿Bloquea al usuario? | Decisión |
|---|---|---|
| Notificar que se unió a una mesa | No | Asíncrono. Publicar un evento y volver es más rápido y más resiliente que esperar a que el email salga. |
| Generar el PDF de una build | No | Asíncrono con `202 Accepted` + `documento_id`. El cliente consulta el estado. |
| Enviar el email de confirmación | No | Asíncrono. Además con outbox, así que un fallo de SMTP no rompe el flujo. |
| Unirse a una mesa | **Sí** | Síncrono. El usuario necesita saber si entró o si el cupo se agotó, y esa es exactamente la carrera que hay que resolver con bloqueos, no con una cola. |

La última fila es la que importa conceptualmente: **la asincronía no es una técnica de rendimiento, es una decisión de semántica.** Si el resultado determina la respuesta al usuario, tiene que ser síncrono y la concurrencia se resuelve con exclusion mutua. Si el resultado es un efecto posterior, la cola permite que el productor siga su camino y que el consumidor reintente sin arrastrar al primero.

---

## 6. Redis: caché, estado efímero y expiración

*(criterio 6 de la rúbrica)*

La decisión está en [ADR-002](../docs/ADR/ADR-002-redis.md). Redis tiene **cuatro usos distintos** en AE2, y cada uno usa un mecanismo de expiración diferente según lo que se esté protegiendo.

| Uso | Clave | Comando | TTL | Invalidación |
|---|---|---|---|---|
| Sesión de usuario | `sesion:{jti}` | `SETEX` | 86400 s (24 h) | `DEL` explícito en el logout |
| Caché del listado | `cache:mesas:list` | `SETEX` | 60 s | `DEL` explícito en cada escritura |
| Reserva de vacante | `reserva:vacante:{mesa_id}` | `SET NX EX` | 60 s | `DEL` en el `finally` |
| QR de asistencia | `qr:{sesion_id}:{usuario_id}` | `SETEX` | 600 s (10 min) | `GETDEL` — se consume al usarlo |
| Idempotencia | `idem:solicitud:{key}` | `SETEX` | 86400 s | Expira sola |

### 6.1 La distinción entre TTL e invalidación

`cache:mesas:list` usa las dos estrategias, y el motivo es que solas no alcanzan.

```text
cache-aside:  GET cache:mesas:list
              miss  -> leer PostgreSQL -> SETEX 60
              hit   -> devolver

invalidación: POST   /api/v1/mesas       -> DELETE cache:mesas:list
              PUT    /api/v1/mesas/{id}  -> DELETE cache:mesas:list
              DELETE /api/v1/mesas/{id}  -> DELETE cache:mesas:list
```

El TTL de 60 s es una **red de seguridad**: garantiza que si una invalidación se olvida, el datoeno se vuelve viejo de forma indefinida. La invalidación explícita es lo que da la corrección. Con TTL solo, un usuario que crea una mesa y recarga la lista ve la lista vieja durante hasta un minuto; con la invalidación, la ve al instante. La evidencia del ciclo miss → hit → invalidación está en `AE2/evidencias/redis_ttl.png` y el comportamiento se verifica con un spy sobre el número de consultas a la base en `tests/test_cache.py`.

El costo de esta estrategia está documentado como consecuencia negativa en ADR-002: **hay que recordar la invalidación en cada escritura.** Es un compromiso explícito, no un descuido.

### 6.2 El QR: expirar no es lo mismo que consumir

El QR de asistencia es el caso donde TTL e invalidación divergen por completo. Un QR con TTL de 10 minutos sigue siendo *válido* durante esos 10 minutos aunque ya se haya escaneado; y un QR puede escanearse dos veces. Por eso la validación usa `GETDEL`:

```text
generar:  SETEX qr:{sesion}:{usuario} 600  <payload firmado>
validar:  GETDEL qr:{sesion}:{usuario}  ->  nil  =>  409 "QR vencido o ya utilizado"
```

`GETDEL` es atómico: lee y borra en una sola operación, así que dos validaciones simultáneas del mismo QR no pueden pasar ambas. La evidencia es `AE2/evidencias/qr_single_use.png` (201 → 200 → 409) y `tests/test_qr.py`. La decisión, incluyendo por qué el payload no es un JWT, está en [ADR-007](../docs/ADR/ADR-007-qr-single-use.md).

### 6.3 La reserva de vacante

`SET reserva:vacante:{mesa_id} 1 NX EX 60` es el primero de los dos candados de §7. El `NX` es lo que lo convierte en un candado: si la clave existe, `SET NX` no hace nada y devuelve `nil`, que el código interpreta como "otra solicitud está en curso". El TTL de 60 s es la red de seguridad: si el proceso muere entre `reservar()` y `liberar()`, la clave se sola sola y la mesa no queda bloqueada para siempre.

---

## 7. Concurrencia, consistencia e idempotencia

*(criterio 7 de la rúbrica)*

La decisión está en [ADR-004](../docs/ADR/ADR-004-doble-barrera.md).

### 7.1 El problema

AE1 no tenía el problema porque no tenía el caso: SQLite serializa las escrituras por diseño, y no había acción de "unirse a una mesa". AE2 introduce una acción que compete por un recurso —**la última vacante**— y con ella un defecto real y demostrable.

`tests/repro_carrera.py` es la reproducción mínima, escrita **antes** de la corrección, y es la razón de que este apartado sea una respuesta y no una descripción:

```text
10 hilos concurrentes invocan "unirse" sobre una mesa con 1 sola vacante
   -> sin barreras: N filas creadas, N+1 jugadores en una mesa que admite 5
   -> con barreras:  1 × 201 Created, 9 × 409 Conflict
```

La causa no es la escritura duplicada sino la **lectura y la escritura separadas**:

```text
Thread A: SELECT jugadores_actuales -> ve 0          Thread B: SELECT jugadores_actuales -> ve 0
Thread A: UPDATE jugadores_actuales = 1              Thread B: UPDATE jugadores_actuales = 1
```

Ambas leen el mismo valor antes de que ninguna escriba. Sin una operación atómica que una la lectura con la escritura, cualquier cantidad de validación posterior no ayuda: el dato ya fue leído.

### 7.2 Las alternativas descartadas

**`SELECT ... FOR UPDATE`** — PostgreSQL bloquea la fila leída, de modo que B queda esperando hasta que A confirme. Funciona, pero con dos consecuencias: la segunda conexión ocupa un slot del pool bloqueada esperando, y el lock de fila se mantiene durante toda la transacción, lo que hace que el tiempo de lock sea la duración de la transacción en lugar de la duración de una operación.

**`LOCK TABLE`** — más fuerte todavía, y peor: serializa a **todas** las operaciones sobre esa mesa, no solo las que compiten por la vacante. Una lectura del detalle de la mesa quedaría detrás de una unión.

**Ambas se descartaron por la misma razón**: resuelven el problema en la base de datos, donde la contención es alta, cuando la contención real es por mesa y la mayoría de las mesas no tienen jamás dos solicitudes simultáneas.

### 7.3 La solución: doble barrera

La elección fue poner la exclusión mutua donde la competencia es real —por mesa, y solo mientras dura la sección crítica— y dejar la garantía definitiva en la base de datos.

```python
def solicitar_union(mesa_id, usuario_id, idem_key=None, correlation_id="-"):
    if idem_key:                                    # Capa 0 — idempotencia
        previo = obtener_resultado(idem_key)
        if previo is not None:
            return previo
        existente = obtener_solicitud_por_key(mesa_id, usuario_id, idem_key)
        if existente:
            guardar_resultado(idem_key, existente)
            return existente

    if obtener_mesa_por_id(mesa_id) is None:        # validación de entrada
        raise MesaNoExisteError(...)

    if not reservar(mesa_id):                       # Barrera 1 — Redis
        raise SolicitudEnProcesoError(...)          #   SET NX EX 60

    try:
        if not ocupar_vacante(mesa_id):             # Barrera 2 — PostgreSQL
            raise CupoAgotadoError(...)             #   UPDATE ... RETURNING
        solicitud = crear_solicitud(..., estado="aceptada", idem_key=idem_key)
        guardar_resultado(idem_key, solicitud)
        publicar_aceptacion(mesa_id, usuario_id, correlation_id=correlation_id)
        return solicitud
    finally:
        liberar(mesa_id)                            # siempre libera la barrera 1
```

`mesas_api/app/controllers/solicitudes_controller.py:23-56`

**Barrera 1 — `reserva:vacante:{mesa_id}`** (`mesas_api/app/services/vacante.py:8`). `SET NX` es atómico en Redis: el primero que llega gana la clave; los otros obtienen `nil` y reciben un `409` con un mensaje que dice qué hacer. El `finally` garantiza que la clave se libere incluso si la operación falla, y el TTL de 60 s cubre el caso en que el proceso muera antes de llegar al `finally`.

Esta barrera **no** decide quién se une. Reduce la competencia a un solo intento a la vez.

**Barrera 2 — `ocupar_vacante()`** (`mesas_api/app/models/mesa.py:70-79`):

```sql
UPDATE mesas SET jugadores_actuales = jugadores_actuales + 1
 WHERE id = %s AND jugadores_actuales < jugadores_max
RETURNING id
```

Esta es la garantía real. El `WHERE` y el `SET` están en **una sola sentencia**, así que PostgreSQL los evalúa con el lock de fila ya tomado: la condición `jugadores_actuales < jugadores_max` se evalúa contra el valor que la transacción concurrente ya había confirmado. Solo una de las dos devuelve fila; la otra recibe `None` y produce el `409 CupoAgotadoError`. No hay ventana entre el chequeo y la escritura porque no hay dos sentencias.

La división de responsabilidades es deliberada: **Redis aporta exclusion mutua barata; PostgreSQL aporta la verdad.** Si Redis se cayera, la barrera 2 sigue impidiendo la sobreventa, solo que más_utf8diferentes solicitudes llegarían a la base de datos. La consistencia no depende de Redis, que es lo que se busca en un sistema donde la caché es descartable.

### 7.4 Idempotencia: por encima de la concurrencia

Resolver la carrera de la última vacante no alcanza. Falta el caso de la **repetición**: el mismo usuario que reintenta, o una recarga de página, o un doble clic.

La respuesta es `Idempotency-Key`, en tres niveles (`solicitudes_controller.py:26-34`):

1. **Redis primero.** `idem:solicitud:{key}` con TTL 24 h. Si ya está, se devuelve el resultado guardado. Es el camino rápido y cubre el reintento inmediato.
2. **Base de datos después.** `obtener_solicitud_por_key(mesa_id, usuario_id, idem_key)` busca una fila previa con esa misma clave. Esto cubre el caso en que Redis se reinició y se perdió la clave, que es exactamente el escenario en que un caché no puede ser la única garantía.
3. **La respuesta se cachea al crearse** (`solicitudes_controller.py:51-52`), de modo que un reintento devuelve *el mismo objeto* que la primera vez, no uno equivalente reconstruido.

El cliente completa el circuito persistiendo la clave en `localStorage` por par (mesa, usuario), lo que hace que un doble clic o una recarga reutilicen la misma clave en lugar de generar una nueva. Está detallado en `INFORME-AE2-CZAJKOWSKI-LEONARDO.md` §5.

### 7.5 Evidencia

| Evidencia | Ubicación |
|---|---|
| Reproducción del bug previa a la corrección | `tests/repro_carrera.py` |
| 10 concurrentes → 1×201 / 9×409 | `tests/test_carrera.py`, `AE2/evidencias/carrera_antes_despues.png` |
| Misma `Idempotency-Key` dos veces → cuerpo idéntico, `jugadores_actuales == 1` | `tests/test_idempotencia.py` |
| QR usado dos veces → 200 y luego 409 | `tests/test_qr.py` |

---

## 8. Persistencia, propiedad de datos e interoperabilidad

*(criterio 8 de la rúbrica)*

La decisión está en [ADR-001](../docs/ADR/ADR-001-postgres.md) y el detalle operativo en [`PROPIEDAD_DE_DATOS.md`](./PROPIEDAD_DE_DATOS.md).

### 8.1 Una instancia, cuatro bases

Una sola instancia PostgreSQL 16 con cuatro bases, una por servicio. La separación es **lógica** en AE2, no física.

| Base | Tablas | Servicio dueño |
|---|---|---|
| `mesas_db` | `mesas`, `usuarios`, `matchmaking`, `solicitudes_uniones`, `sesiones`, `asistencias` | `mesas_api` |
| `builds_db` | `builds`, `tags` | `builds_api` |
| `feed_db` | `publicaciones`, `wiki_paginas` | `feed_api` |
| `notif_db` | `notificaciones`, `event_log`, `mensaje_dlq`, `documentos`, `emails` | `notif_api` |

Cada servicio crea además su base de test (`*_db_test`) para que la suite de integración no toque los datos de desarrollo.

### 8.2 La regla: cero SQL cruzada

Ningún servicio lee ni escribe tablas de otro. La regla tiene tres niveles de fuerza:

1. **Cada servicio tiene su propio pool** contra su propia base, y su modelo importa ese pool. No existe un `get_pool()` global que любой servicio pueda usar por error.
2. **Las referencias entre dominios son por identificador, sin clave foránea.** `builds.mesa_id` es un entero sin FK a `mesas_db.mesas`; `notificaciones.usuario_id` es un entero sin FK a `mesas_db.usuarios`. Un FK entre servicios de bases distintas es imposible en PostgreSQL, y omitirlo deliberadamente documenta que la integridad de esas referencias es responsabilidad de quien la escribe, no del motor.
3. **La regla es verificable con un comando.** `PROPIEDAD_DE_DATOS.md:35` da el `rg` exacto, y su resultado esperado es que liste únicamente el `db.py` del servicio dueño de cada base. Una documentación que afirma una regla pero no puede comprobarse es una declaración de intenciones.

Las únicas claves foráneas reales están **dentro** de `mesas_db` y sí tienen `ON DELETE CASCADE` (`matchmaking.mesa_id`, `solicitudes_uniones.mesa_id`, `sesiones.mesa_id`, `asistencias.sesion_id`), donde la integridad sí es responsabilidad de la base.

### 8.3 Interoperabilidad: cómo se cruzan los servicios

Cuando un servicio necesita información de otro, hay exactamente dos caminos permitidos.

| Situación | Mecanismo | Ejemplo |
|---|---|---|
| El llamador necesita el dato para responder | **REST síncrono** | `notif_api` pide los miembros de una mesa para dirigir un email: `GET /api/v1/mesas/{id}/miembros`, autenticado con la cuenta de servicio `email_svc@tfinder.dev` |
| El efecto es posterior y el llamador no lo necesita | **Evento asíncrono** | `mesas_api` publica `mesa.aceptada`; `notif_api` decide notificar y enviar email |

La distinción es la que determina el acoplamiento. Un evento es un **contrato de Notification**: el productor no sabe quién escucha ni qué hace, y puede haber tres consumidores futuros sin tocar al productor. Una llamada REST es un **contrato de consulta**: el consumidor depende de la forma de la respuesta y de su disponibilidad. Elegir REST donde alcanzaba un evento acopla al consumidor a la latencia y a la disponibilidad del productor; elegir un evento donde el llamador necesita el dato fuerza al usuario a esperar por un efecto que no le corresponde.

`notif_api` es el ejemplo de por qué esto importa: si el envío del email se hiciera por REST desde `mesas_api`, entonces un SMTP caído —o simplemente lento— haría fallar la unión de un jugador a una mesa. Al hacerlo por evento, el productor no sabe que hay un email en el mundo.

### 8.4 Por qué no database-per-service todavía

La separación física por servicio es la respuesta habitual, y es la correcta en un sistema de dozens de servicios. En AE2 no lo es por una razón concreta: los cuatro servicios se despliegan juntos, se versionan juntos y se prueban juntos. Cuatro instancias PostgreSQL en un entorno de demostración agregan cuatro fuentes de fallo sin agregar una capacidad que el sistema use, y la separación lógica ya garantiza lo que el diseño necesita —que nadie lea datos ajenos.

La separación física queda planteada para AE4, donde con dos o más réplicas y despliegue independiente el costo deja de estar justificado. La progresión está justificada, no sorteada: en AE2 se aprende a delimitar responsabilidades, y el salto a autonomía física tiene sentido cuando aparece la autonomía de despliegue que la motiva.

---

## 9. Integraciones y artefactos

*(criterio 9 de la rúbrica)*

### 9.1 QR de asistencia de un solo uso

`mesas_api/app/services/qr_asistencia.py` (66 líneas), con `qrcode==7.4.2` + Pillow.

| Aspecto | Implementación |
|---|---|
| Payload | `{sesion, u, exp}` en base64url — **sin datos personales**, ni email ni nombre |
| Firma | HMAC-SHA256 con `QR_SECRET`, truncado a 32 hex, sobre JSON canónico (`sort_keys=True`) |
| TTL | 600 s |
| Emisión | `SETEX qr:{sesion_id}:{usuario_id} 600` |
| Validación | `GETDEL` (atómico) + `hmac.compare_digest` + chequeo de `exp` |
| Respuestas | `200` válido · `409` vencido o ya usado · `400` firma inválida |

Dos decisiones que conviene explicitar. **El payload no es un JWT** aunque el sistema ya use JWT para las sesiones: la validación del QR no necesita un token autocontenido, porque la fuente de verdad es la clave en Redis y la operación que la consulta es un `GETDEL` que ya la consume. Un JWT habría que verificarlo y además verificar que exista la clave, o sea más trabajo para el mismo resultado. **La firma HMAC sirve para detectar manipulaciones**, no para autenticar: si el GM pierde la clave, la validación falla con `400` en vez de devolver un `false` engañoso. Las consecuencias negativas —incluida la rotación del secreto invalidando los QR pendientes— están en [ADR-007](../docs/ADR/ADR-007-qr-single-use.md).

### 9.2 PDF asíncrono

Dos/requestos, un worker, tres partes:

```text
1. POST /api/v1/builds/{id}/pdf                    -> 202 Accepted { documento_id }
   POST /api/v1/mesas/{mesa}/sesiones/{ses}/diario/pdf
   El emisor genera el uuid4().hex y lo devuelve

2. publica doc.pdf.build  |  doc.pdf.diario   -> cola doc.pdf

3. notif_api/app/workers/pdf.py  consume, renderiza con fpdf2==2.7.9
   -> actualiza documentos.estado = 'listo' (o 'error')

4. GET /api/v1/pdf/{documento_id}       -> application/pdf
   GET /api/v1/pdf/{documento_id}/estado -> en_proceso | listo | error
```

El `documento_id` lo genera **quien emite el evento**, no el consumidor. Es lo que permite responder `202` con un identificador útil de inmediato, en lugar de un "lo estamos procesando" sin referencia. Si lo generara el worker, el cliente no tendría nada que consultar hasta que el mensaje recorriera la cola.

El fallo en el render marca `estado = 'error'` y **relanza la excepción** (`workers/pdf.py:30-32`), que es lo que permite que el mecanismo de reintentos de §5.3 actúe y, si se agota, termine en la DLQ. Un fallo silencioso —capturar y registrar— habría dejado el documento en `en_proceso` para siempre, que es el peor de los tres estados posibles porque no dice ni que falló ni que va a pasar algo.

La máquina de estados `inactivo → enviando → en_cola → listo|error` es la que hace visible el contrato asíncrono en la interfaz, y está implementada en `F-07` (`exportar-pdf-async`).

### 9.3 Email con outbox

`notif_api/app/services/email_service.py` con `smtplib` de la biblioteca estándar, contra MailHog como sandbox.

```text
consumidor de mesa.aceptada
  -> recipients = GET /api/v1/mesas/{id}/miembros   (REST, cuenta de servicio)
  -> registrar fila en emails (outbox)   estado = 'pendiente'
  -> enviar por SMTP con SMTP_TIMEOUT = 3 s
  -> emails.estado = 'enviado' | 'fallido'   (nunca propaga excepción)
```

La decisión está en [ADR-005](../docs/ADR/ADR-005-mailhog-outbox.md) y su valor es que **`enviar_email` nunca lanza**. Si un envío falla, el evento ya fue procesado y no se reintenta infinitamente; el fallo queda registrado con su motivo y hay un endpoint de reintento manual (`POST /api/v1/emails/{id}/reintentar`, solo admin) y una vista de auditoría (`GET /api/v1/emails`).

El timeout de 3 s es lo que impide que un SMTP colgado bloquee el hilo del consumidor. Sin él, un sandbox detenido convertiría un email en un cuelgue silencioso.

La dependencia es explícita: los destinatarios se obtienen por REST, no leyendo `mesas_db.usuarios`. Es el caso que ilustra §8.3.

### 9.4 Recuperación de contraseña sin enumerar cuentas

`POST /api/v1/auth/recuperar` responde **siempre** `{"ok": true}`, exista o no la cuenta (`notif_api/app/routes/v1/auth.py:18`). Es una decisión de seguridad deliberada: si la respuesta distinguiera entre "email no registrado" y "email enviado", un atacante podría usarla para averiguar quién tiene cuenta en la plataforma. El costo es que el usuario legítimo no puede distinguir un typos de un email válido, lo que se resuelve en el mensaje que se le envía.

---

## 10. Seguridad y observabilidad

### 10.1 Autenticación y autorización

PBKDF2 para el hash de contraseñas, JWT para la sesión, y la revocación en Redis.

```text
login -> access_token (uso general) + refresh_token (uso restringido)
      -> SETEX sesion:{jti} 86400          el registro de sesión
      -> el middleware valida sesion_valida(jti) en CADA request autenticado
logout -> DEL sesion:{jti}  revocación inmediata
```

El registro en Redis es lo que hace que la revocación sea inmediata y real, y no un token que sigue siendo criptográficamente válido hasta que expira. `usuario_actual` (`app/middleware/auth.py`) devuelve `401` en cuatro casos distintos y distinguidos —sin header, token inválido, se usó un refresh como access, sesión revocada— y `requerir_roles` devuelve `403`.

| Superficie protegida | Rol | Ubicación |
|---|---|---|
| Abrir matchmaking | `gm` | `mesas_api/app/routes/v1/matchmaking.py:10` |
| Validar QR de asistencia | `gm` | `mesas_api/app/routes/v1/sesiones.py:19` |
| Event-log | `admin` | `notif_api/app/routes/v1/event_log.py:11` |
| Emails y reintento | `admin` | `notif_api/app/routes/v1/emails.py:12,15,20` |
| DLQ: ver, reintentar, descartar | `admin` | `notif_api/app/routes/v1/dlq.py:8,11,16,24` |

La defensa de no permitiendo escalamiento de privilegios en el registro público está en `tests/test_auth_registro_rol.py:29-54`, y el aislamiento de notificaciones por usuario en `tests/test_notif_auth.py:58-148`.

### 10.2 Observabilidad: correlación y salud

**Logs estructurados** (`app/infra/logge.py`) en JSON con `ts`, `nivel`, `servicio`, `mensaje` y `correlation_id`. Un `contextvar` (`correlation_id_var`) transporta el identificador por el contexto de la petición y por el hilo del consumidor, que es lo que permite que el log de un consumidor tenga el mismo `correlation_id` que el request que originó el evento.

**Salud** (`app/infra/ready.py`):

```text
GET /live   -> 200 siempre        (el proceso está vivo)
GET /ready  -> 200 {"estado": "listo",    "dependencias": {postgres, redis, rabbitmq: true}}
            -> 503 {"estado": "degradado", "dependencias": {..., "redis": false}}
```

`/live` y `/ready` están separados a propósito: un liveness probe que consulta la base de datos reinicia el proceso cuando la base cae, y en vez de esperar a que vuelva lo convierte en un ciclo de reinicios. La evidencia de ambos casos —los cuatro servicios en `listo`, y `notif-api` en `degradado` con `redis: false` tras pausar el contenedor de Redis— está en `AE2/evidencias/ready_live.png` y `AE2/evidencias/ready_degradado.png`, y se verifica en `tests/test_ready_degradado.py`.

**Event-log consultable.** `GET /api/v1/event-log?correlation_id=…` (`tests/test_event_log_correlation.py`) permite reconstruir un flujo a partir de un identificador, que es el complement natural de los logs: el log dice qué pasó en cada proceso, el event-log muestra el camino del evento entre ellos.

---

## 11. Testing y reproducibilidad

*(criterio 10 de la rúbrica)*

### 11.1 Volumen y reparto

| Suite | Unit | Integration | Total |
|---|---|---|---|
| Backend (`tests/`, pytest) | 50 | 80 | **130** |
| Frontend (`tfinder-vue/tests/`, Vitest) | 15 | 7 | **22** |
| **Total** | **65** | **87** | **152** |

```bash
source venv/bin/activate
pytest -m unit -q            # 50
pytest -m integration -q     # 80
```

El inventario completo, con qué cubre cada archivo, está en [`docs/testing/test-inventory.md`](./testing/test-inventory.md). La regla de sincronización que sostiene la cobertura es explícita: *"si se agrega una función, componente, vista, composable, servicio o endpoint, debe agregarse un test o una exclusión documentada antes de cerrar el cambio"*.

### 11.2 El aislamiento de las pruebas de integración

La parte difícil de probar un sistema con Redis y RabbitMQ no es ejecutar los tests, es evitar que **corriran contra el ambiente de desarrollo**. Tres aislamientos, cada uno atacando un riesgo distinto:

| Recurso | Aislamiento | Riesgo que previene |
|---|---|---|
| PostgreSQL | 4 bases `*_db_test` + `TRUNCATE … RESTART IDENTITY CASCADE` antes y después de cada test | Datos de test mezclados con datos de demo |
| Redis | Base 15 | `flushdb` sobre la base 0 borraría la caché del ambiente |
| **RabbitMQ** | **vhost `/tfinder_test`** | Los consumidores del contenedor `notif-api` en desarrollo robarían los eventos de test, los rebotarían y contaminarían la `dlq.general` |

El aislamiento del broker merece una línea propia porque no es evidente. `tests/conftest.py:25-35,124-151` reescribe `RABBITMQ_URL` para apuntar al vhost `/tfinder_test`, que se crea y se permisos con la management API. Se detectó en la práctica, no por diseño: el defecto `D-06` de `docs/testing/integration-results.md` registra que los tests contaminaban el ambiente de desarrollo. Además, un fixture `autouse` (`conftest.py:190-216`) hace que cualquier test **unitario** que intente publicar en el broker real levante un `AssertionError`, de modo que una fuga no puede pasar inadvertida.

El timeout global de `pytest.ini` (`--timeout=120`) es la defensa contra el defecto `D-09`: un test de AMQP puede colgarse esperando un broker que no responde, y sin timeout la suite completa se detiene.

### 11.3 Qué cubre cada comportamiento crítico

| Comportamiento | Test |
|---|---|
| Carrera de la última vacante (10 → 1×201 / 9×409) | `test_carrera.py` |
| Idempotencia (misma key → mismo cuerpo, 1 jugador) | `test_idempotencia.py` |
| QR de un solo uso (200 y luego 409) | `test_qr.py` |
| Caché: miss → hit → invalidación, con conteo de consultas a la base | `test_cache.py` |
| DLQ: mensaje envenenado llega a `dlq.general` | `test_dlq.py` |
| Topología AMQP: binding del DLX, round-trip de dead-letter | `test_amqp_topologia.py` |
| Envelope de error en los 4 servicios, incluido router 404/405 | `test_envelope_error.py` |
| SSE no se rompe con el middleware de errores | `test_envelope_error.py` |
| `/ready` en `listo` y en `degradado` | `test_ready_degradado.py` |
| Escalamiento de privilegios en el registro público | `test_auth_registro_rol.py` |
| Aislamiento de notificaciones por usuario | `test_notif_auth.py` |
| Correlation-id en el event-log | `test_event_log_correlation.py` |
| Sin escalamiento en el registro / forma del campo `enlace` | `test_auth_registro_rol.py`, `test_contrato_enlace.py` |

### 11.4 Los 9 defectos encontrados y corregidos

La verificación E2E contra Docker ejecutó 99 casos HTTP. De esa corrida surgieron 9 defectos, todos corregidos con su test de regresión. La tabla completa está en [`docs/testing/integration-results.md`](./testing/integration-results.md); los que tienen valor arquitectónico son:

- **D-04 — Divergencia del envelope de error entre servicios.** Dos servicios envolvían los errores de forma distinta. Corregido con la unificación en `app/infra/errors.py` y el middleware ASGI de §4.2. Es exactamente el tipo de defecto que solo aparece al integrar.
- **D-05 — `tfinder.dlx` sin binding.** El exchange de errores existía y las tres colas declaraban `x-dead-letter-exchange`, pero ninguna cola estaba bound al DLX: los mensajes rechazados se descartaban **en silencio**. Corregido con el binding `#` (`notif_api/app/infra/amqp.py:39-40`) y verificado por `test_amqp_topologia.py`.
- **D-02 — Forma del campo `enlace` distinta entre la fila de la base y el payload SSE.** El consumidor guardaba una estructura y emitía otra, así que el enlace del notification no navegaba. Regresión en `test_contrato_enlace.py`.

### 11.5 Dos defectos de la propia suite, corregidos

La verificación de reproducibilidad (§11.6) encontró dos problemas **en la suite misma**, que son distintos de los 9 del producto y conviene separar:

**1. La suite entera fallaba al collectionarse.** `tests/conftest.py:134` usaba `pytest.warn(...)`, que no existe en pytest — la API correcta es `warnings.warn(...)`. Como `vhost_de_pruebas` es un fixture `autouse` de scope de sesión, el `AttributeError` abortaba el setup de **los 130 tests**, no solo de los de integración. El bug estaba en la rama de degradación elegante (cuando la management API del broker no responde), lo que explica que pasara inadvertido: solo se manifiesta cuando el broker no está disponible, que es exactamente el caso en que uno espera que la suite degrade y funcione.

```python
# antes
pytest.warn("...", RuntimeWarning, stacklevel=1)
# despues
warnings.warn("...", RuntimeWarning, stacklevel=1)
```

**2. Un test unitario dependía de PostgreSQL.** `test_no_se_altera_una_respuesta_correcta` consultaba `/health`, que ejecuta `SELECT 1` (`mesas_api/main.py:80`). Al estar marcado `unit`, el job `backend-unit` de CI —que no levanta service containers, a diferencia de `backend-integration`— lo ejecutaría sin base de datos y fallaría. Se cambió a `/live`, que devuelve `200` sin tocar PostgreSQL, preservando exactamente la propiedad que el test verifica: que el middleware de errores no altera una respuesta correcta.

La diferencia entre ambos bugs es instructiva. El primero era un error de API en una línea que solo aparecía en un camino infrecuente. El segundo era un test marcado como unitario que verificaba algo correcto pero dependía de infraestructura. Los dosson el mismo tipo de problema: **el fixture de aislamiento protects contra la contaminación del ambiente, pero nadie lo ejecutó en el escenario en que falla** — sin Docker levantado.

### 11.6 Reproducibilidad

```bash
git clone <repo> && cd TFinder
cp .env.example .env
docker compose up -d --build          # 4 servicios + postgres + redis + rabbitmq + mailhog
docker compose ps                     # los que tienen healthcheck deben quedar "healthy"
```

Frontmatter en `http://localhost:5173`, `mesas-api` en `:8001/docs`, `builds-api` `:8002/docs`, `feed-api` `:8003/docs`, `notif-api` `:8004/docs`, panel de RabbitMQ en `:15673` (`tfinder`/`tfinder`), MailHog en `:8025`.

Para las pruebas de integración hacen falta las cuatro `*_db_test` y el vhost `/tfinder_test`; los prerrequisitos exactos están en [`docs/testing/test-inventory.md`](./testing/test-inventory.md) §"Requisitos de los tests de integración".

Las pruebas manuales tienen una referencia operativa con URL, método, campo, dato exacto y respuesta esperada para cada caso en [`docs/testing/tutorial-pruebas.md`](./testing/tutorial-pruebas.md), y los valores de prueba congelados en [`docs/testing/valores-prueba.md`](./testing/valores-prueba.md).

### 11.7 CI

`.github/workflows/ci.yml` — 6 jobs con un gate final (`if: always()`) que exige que todos pasen:

| Job | Qué corre |
|---|---|
| `backend-lint` | `ruff check .` |
| `backend-unit` | `pytest -m unit --cov=. --cov-report=term-missing` |
| `backend-integration` | `pytest -m integration` contra postgres/redis/rabbitmq como service containers reales, con las 4 `*_db_test` creadas por script |
| `frontend-lint-typecheck` | `npm run lint` + `npm run type-check` |
| `frontend-unit` | `npm run test:unit -- --run` |
| `frontend-integration` | `npm run test:integration -- --run` |

Se ejecuta con servicios reales, no con dobles: un mock de RabbitMQ no detectaría el defecto D-05, porque un binding faltante es una propiedad de la topología del broker.

---

## 12. Fundamentación: comparativa de alternativas

*(criterio 12 de la rúbrica)*

Las decisiones están registradas como ADR en `docs/ADR/`, cada uno con **Contexto**, **Decisión** y **Consecuencias** (positivas y negativas). El detalle está en esos archivos; lo que sigue es el índice y la comparación.

| # | Decisión | Alternativa descartada | Por qué |
|---|---|---|---|
| [ADR-001](../docs/ADR/ADR-001-postgres.md) | PostgreSQL 16, una base por servicio | SQLite (la de AE1) | SQLite serializa las escrituras: no hay forma de probar concurrencia real. Un sistema cuyo problema central es la carrera por la última vacante necesita una base donde esa carrera exista. |
| [ADR-002](../docs/ADR/ADR-002-redis.md) | Redis para sesión, caché, reserva y QR | Solo TTL para la caché | Con TTL solo, un usuario ve hasta 60 s de datos viejos. La invalidación explícita da corrección; el TTL queda como red de seguridad. |
| [ADR-003](../docs/ADR/ADR-003-rabbitmq.md) | Topic + ACK + reintentos en el body + DLQ | `nack(requeue=True)` | Reencolar la copia original pierde los headers modificados, el contador de reintentos no avanza y el mensaje vuelve para siempre. |
| [ADR-004](../docs/ADR/ADR-004-doble-barrera.md) | Doble barrera Redis + PostgreSQL | `SELECT FOR UPDATE`; `LOCK TABLE` | Lock de fila mantiene el lock durante toda la transacción y ocupa un slot del pool bloqueado; `LOCK TABLE` serializa además las lecturas. |
| [ADR-005](../docs/ADR/ADR-005-mailhog-outbox.md) | Outbox, `enviar_email` nunca lanza | Propagar la excepción | Un SMTP caído reintentaría en loop y, peor, si el error se propagara, la unión de un usuario fallaría por un email. |
| [ADR-006](../docs/ADR/ADR-006-servicios.md) | 4 servicios, interoperabilidad solo por REST o eventos | Base compartida con esquema común | Un esquema común hace que "no leer datos ajenos" dependa de la disciplina del desarrollador en lugar de la estructura. |
| [ADR-007](../docs/ADR/ADR-007-qr-single-use.md) | HMAC + payload mínimo + `GETDEL` | JWT para el QR | El QR se valida contra la clave en Redis con un `GETDEL` atómico. Un JWT exigiría verificar firma **y** existencia, sin ganar nada. |

### 12.1 El patrón que atraviesa a las siete decisiones

Leídas en conjunto, las siete decisiones comparten una misma forma de razonar, que es la que distingue una decisión fundamentada de una decisión por defecto:

**Cada mecanismo se eligió por lo que ocurre cuando falla, no solo por lo que hace cuando funciona.**

- El `finally` que libera la barrera existe para el caso en que la operación falla.
- El TTL de 60 s en `reserva:vacante` existe para el caso en que el proceso muere antes del `finally`.
- El DLQ existe para el caso en que un mensaje no se puede procesar nunca.
- El `finally` de la sesión y el outbox existen para el caso en que un componente externo no responde.
- La separación lógica de las bases existe para que la consistencia no dependa de que nadie cometa un error.

El criterio de diseño que se aplicó fue: *¿qué pasa si este componente no está disponible?* La respuesta fue que ninguna parte de la consistencia de datos depende de Redis ni de RabbitMQ, y de que ambos son recuperables por diseño.

---

## 13. Limitaciones conocidas y compromisos

Reconocer las limitaciones no es unaweakness del trabajo: es lo que permite que la evidencia sea creíble. Estas son las brechas identificadas durante el desarrollo, con su impacto y su tratamiento.

### 13.1 Brechas arquitectónicas

| # | Limitación | Impacto | Tratamiento |
|---|---|---|---|
| L1 | **Sin outbox transaccional.** `publicar()` se ejecuta fuera de la transacción de negocio (`solicitudes_controller.py:53`) | Si el broker está caído justo después del commit, el evento se pierde y la notificación no se emite | Se acepta en AE2. La solución es un outbox transaccional: escribir el evento en la misma transacción y un publicador que lo drene. Es la corrección natural para AE4 |
| L2 | **Hub SSE process-local** (`notif_api/app/services/stream.py:15`) | Con más de un worker o réplica, una notificación generada en la réplica A nunca llega a un cliente SSE en la B | Se acepta en AE2. La solución es Redis pub/sub como fan-out entre réplicas. El endpoint SSE ni el polling de 5 s del frontend no depende de esto |
| L3 | **Sin `UNIQUE` en `solicitudes_uniones.idem_key`** (`mesas_api/app/schema.sql:47`) | La idempotencia depende de la serialización de la barrera 1 y no de una restricción de base | Funcionalmente correcto con la barrera 1, pero la garantía es más débil de lo que sería con la restricción. Es la primera corrección de AE4 |
| L4 | **Barrera 1 sin fencing token** | Si el TTL de 60 s expira dentro de la sección crítica, un segundo llamador puede entrar | La barrera 2 sigue impidiendo la sobreventa, así que el defecto es de throughput y no de consistencia. Un fencing token o un TTL más holgado lo cierran |
| L5 | **PDFs sin volumen en Docker** | `PDF_DIR` (`pdf_service.py:6`) es `./storage/pdf` dentro del contenedor sin volumen montado, así que los PDF se pierden al recrear `notif-api` | Afecta a la persistencia del artefacto, no al flujo. Se resuelve montando un volumen en AE4 |
| L6 | **Reintento de DLQ no atómico** | `notif_api/app/controllers/dlq.py:11-28` borra la fila y después publica; si el publish falla, el mensaje se perdió | Afecta a la operación manual de admin, no al flujo normal. Se resuelve con un outbox también aquí |
| L7 | **El correlation-id no se propaga en la llamada notif → mesas** | `email_service.py:63-82` omite `X-Correlation-Id` en el `GET /miembros`, con lo que la traza se corta en ese tramo | La correlación funciona en el tramo principal request → evento → consumidor, que es el que se evidencia. Este tramo secundario se completa en AE4 |
| L8 | **`sesion.confirmada` y `sesion.diario_publicado` no tienen productor** | El consumidor `notif.sesion` y el fan-out de email de esa cola no son alcanzables desde ningún endpoint | La cola, el consumidor y la integración de email están implementados y probados; lo que falta es el endpoint de confirmación de sesión. Es una funcionalidad pendiente, no un defecto de diseño |

### 13.2 Deuda técnica del frontend

| # | Limitación | Impacto |
|---|---|---|
| L9 | **Sin refresh de token.** El `refresh_token` se persiste y no se usa; ante un `401` se limpia la sesión y hay una redirección dura | El usuario pierde el estado de la navegación en cada expiración. El endpoint de refresh existe en el backend (B03), de modo que la corrección es del lado cliente |
| L10 | **Dos implementaciones de "unirse" conviviendo.** `useSolicitud.unirse` (la viva) y `useMesas.unirse` (sin llamadores) | Código muerto con mensajes al usuario distintos. Se documenta en `INFORME-AE2-CZAJKOWSKI-LEONARDO.md` §7 |
| L11 | **Ramas con feature gate desactivado.** 14 de 20 pantallas, incluidas las 6 pestañas de `MesaGestionShell`, que llegan a renderizar cero | Es intencional —el gate es lo que permite presentar una pantalla sinMaartar los endpoints que la sostienen— pero deja vistas inaccesibles |
| L12 | **`X-Cache-Tier` se captura y no se renderiza.** El chip visible de "caché ~X ms" es una medición client-side con `performance.now()` | La medición mezcla red, backend y proxy, así que **no** es evidencia del tier de caché. El tier real sí se expone y se prueba en `tests/test_cache.py`, pero la UI no lo muestra |

### 13.3 Brechas de testing

Las cuatro están registradas en `docs/testing/test-inventory.md` §"Módulos sin cobertura automatizada":

- Sin pruebas E2E en navegador. La verificación E2E se hizo por HTTP (99 casos), lo que cubre los contratos pero no el DOM.
- Sin prueba del TTL real de `llamado` en Redis (requiere control del reloj).
- Sin prueba del apagado ordenado y la reconexión de los consumidores ante caída del broker.
- Dos ramas del worker de PDF (tipo inválido y `doc_id` ausente) sin cubrir.

### 13.4 Compromisos asumidos

Tres decisiones se tomaron sabiendo que dejaban trabajo pendiente, y se asumen explícitamente:

1. **La separación de bases es lógica, no física** (§8.4). Consistente con un despliegue conjunto; se revisa en AE4.
2. **MailHog es en memoria.** Los emails no sobreviven a un reinicio. El patrón de outbox es lo que se conserva al cambiar de transporte.
3. **El secret management es por variables de entorno**, suficiente para el ambiente de la actividad. Un secret manager es lo corresponde a un despliegue real, y `RABBITMQ_URL`, `JWT_SECRET` y las credenciales ya están todos externalizados, así que el cambio es de origen y no de código.

---

## 14. Anexo: índice de la documentación del proyecto

| Documento | Contenido |
|---|---|
| **Este documento** | Informe técnico conjunto de AE2 |
| [`INFORME-AE2-AMARILLA-LUCIO.md`](./INFORME-AE2-AMARILLA-LUCIO.md) | Alcance individual: backend B01–B12 |
| [`INFORME-AE2-CZAJKOWSKI-LEONARDO.md`](./INFORME-AE2-CZAJKOWSKI-LEONARDO.md) | Alcance individual: frontend F01–F09 |
| [`PROPIEDAD_DE_DATOS.md`](./PROPIEDAD_DE_DATOS.md) | Dueño de cada base y tabla; verificación con `rg` |
| [`AUDITORIA_CIERRE_AE2.md`](./AUDITORIA_CIERRE_AE2.md) | Auditoría de cierre, hallazgos priorizados y plan de ejecución |
| [`manual-usuario.md`](./manual-usuario.md) | Manual de usuario final del frontend |
| `docs/ADR/ADR-001` … `ADR-007` | Decisiones de arquitectura con contexto, decisión y consecuencias |
| [`testing/test-inventory.md`](./testing/test-inventory.md) | Superficie cubierta y brechas de cobertura |
| [`testing/tutorial-pruebas.md`](./testing/tutorial-pruebas.md) | Referencia operativa: caso por caso, con URL, método, campo, dato y respuesta esperada |
| [`testing/manual-tests.md`](./testing/manual-tests.md) | Guía narrativa de pruebas manuales, con separación entre seguras y destructivas |
| [`testing/integration-results.md`](./testing/integration-results.md) | Resultados de la corrida E2E y los 9 defectos corregidos |
| [`testing/valores-prueba.md`](./testing/valores-prueba.md) | Catálogo congelado de datos y valores de prueba |
| `AE2/README.md` | Readme de la entrega y mapeo criterio → evidencia |
| `AE2/evidencias/EVIDENCIAS.md` | 14 capturas indexadas por criterio |
| `openspec/specs/` | 25 especificaciones de capacidad en formato GIVEN/WHEN/THEN |
| `openspec/changes/` | 20 cambios activos y 7 archivados, con sus `tasks.md` |
| `README.md` (raíz) | Documento de AE1, conservado como registro histórico |

---

## 15. Cierre

TFinder pasó de un monolito CRUD sobre SQLite a un sistema de cuatro servicios con comunicación síncrona por REST y asíncrona por RabbitMQ, estado efímero y caché en Redis, y una base por servicio con propiedad de datos explícita.

Lo que sostiene el resultado no es la cantidad de tecnología incorporada sino tres decisiones que se sostienen entre sí: **la consistencia no depende de la caché** (la barrera definitiva está en el `UPDATE ... RETURNING` de PostgreSQL, no en el `SET NX` de Redis), **el productor no conoce a su consumidor** (los efectos posteriores van por eventos, no por llamadas), y **cada contrato tiene una forma única y verificada** (el envelope de error, el prefijo `/api/v1` y el piso de rutas se comprueban, no se надеquan).

Las 12 limitaciones de §13 están identificadas con su impacto y su tratamiento. Ninguna afecta la consistencia de los datos; las que afectan corrección —el outbox transaccional, la restricción `UNIQUE` sobre la clave de idempotencia— son la ruta natural de AE4.

La evidencia completa está en el repositorio: 90 commits, 21 requerimientos funcionales con su issue y su especificación, 7 ADR, 25 capacidades en OpenSpec, 152 pruebas automatizadas y 14 capturas indexadas por criterio de la rúbrica.
