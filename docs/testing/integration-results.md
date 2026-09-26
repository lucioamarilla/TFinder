# Resultados de integración

**Commit de ejecución:** `b8a5301` + árbol de trabajo sin commitear
**Fecha:** 2026-09-26
**Comandos:** `pytest -m unit -q`, `pytest -m integration -q`, `ruff check .`
**Infraestructura:** PostgreSQL 16, Redis 7, RabbitMQ 3.13 y MailHog mediante Docker Compose.

## Resultado

```text
50 passed, 80 deselected   (pytest -m unit)
80 passed, 50 deselected   (pytest -m integration)
130 passed                  (suite completa)
ruff check .               All checks passed
```

## Frontend

```text
vitest tests/unit          15 passed (3 archivos)
vitest tests/integration    7 passed (2 archivos)
eslint src tests           0 errores
vue-tsc --noEmit           0 errores
vite build                 built in 1.77s
```

## Verificación E2E contra Docker

Se ejecutaron **99 casos** por HTTP contra los cuatro contenedores y se contrastaron con
el estado real de PostgreSQL y RabbitMQ. El detalle caso por caso, con el dato cargado y
el resultado, está en `tutorial-pruebas.md`.

| Área | Resultado |
|---|---|
| Salud de las 4 APIs (`/health`, `/live`, `/ready`) | 12/12 |
| Autenticación (registro, login, me, refresh, logout, admin-only) | 6/6 |
| Seguridad y autorización (401/403/404/405/400) | 31/31 |
| Mesas (CRUD, validaciones, miembros) | 13/13 |
| Solicitud de unión e idempotencia | 5/5 |
| Carrera por la última vacante | 1 `201` + 2 `409`, ocupación 1/1, 1 fila |
| Matchmaking (abrir, estado, errores) | 3/3 |
| QR single-use (6 variantes) | 6/6, una sola fila en `asistencias` |
| Builds y tags | 9/9 |
| Feed con filtros, orden y paginación | 13/13 |
| Wiki y diario | 4/4 |
| Notificaciones, SSE, email, event-log, DLQ | 18/18 |
| PDFs asíncronos (202 → listo → descarga) | 4/4, archivo `PDF 1.3, 1 page(s)` |

Trazabilidad de punta a ponta verificada: un `X-Correlation-Id` enviado a mesas-api aparece
en `notif_db.event_log` con el mismo valor y produce la notificación correspondiente.

## Defectos encontrados y corregidos

| ID | Severidad | Descripción | Corrección |
|---|---|---|---|
| D-01 | Alta | `POST /api/v1/matchmaking/{id}/abrir` con mesa inexistente devolvía `500` en vez de `404`: el `INSERT` en `matchmaking` disparaba un `ForeignKeyViolation` sin manejar. | `mesas_api/app/controllers/matchmaking_controller.py` valida la mesa y lanza `MesaNoExisteError`. Regresión en `tests/test_matchmaking_404.py`. |
| D-02 | Alta | El campo `enlace` de las notificaciones se emitía como mapa `{"/mesas/9": "ver mesa"}` (URL como clave) mientras `NotificacionesView.vue` consume `enlace.label` y `enlace.to`. El botón de enlace se renderizaba sin texto y `router.push(undefined)` no navegaba. | `notif_api/app/consumers/mesa.py`, `sesion.py` y `seed_demo.py` emiten `{"label", "to"}`. Regresión en `tests/test_contrato_enlace.py`. |
| D-03 | Alta | `tests/test_dlq.py` entraba en bucle infinito y la suite no terminaba. El helper requeueaba con `basic_nack(requeue=True)` los mensajes ajenos al `event_id`, y el `basic_get` siguiente devolvía el mismo mensaje. | El helper drena la cola con un techo de iteraciones; el test pide el fixture `dlq_general_vacia`. |
| D-04 | Alta | `builds-api`, `feed-api` y `notif-api` respondían los errores con `{"detail": "..."}` (default de FastAPI) mientras `mesas-api` usaba `{"error": {...}}`. Un cliente con una sola convención se rompía contra 3 de 4 servicios. | `app/infra/errors.py` centraliza el envelope y `registrar_manejadores()` lo aplica en los cuatro. `app/middleware/error_envelope.py` normaliza además los 404 y 405 que genera el router de Starlette antes de la capa de handlers. Regresión en `tests/test_envelope_error.py` (19 casos). |
| D-05 | Alta | `tfinder.dlx` estaba declarado y durable pero **sin un solo binding**. Las tres colas de consumo declaran `x-dead-letter-exchange`, así que cualquier `nack(requeue=False)` enruta el mensaje a un exchange sin destino y RabbitMQ lo descarta en silencio. | `notif_api/app/infra/amqp.py` vincula `dlq.general` al DLX con routing key `#`. Regresión en `tests/test_amqp_topologia.py` (5 casos). |
| D-06 | Media | La suite de integración publicaba en el broker de desarrollo. El `notif-api` de Docker consumía los mensajes de prueba y los rebotaba a `dlq.general` **después** del purgado de fin de sesión, dejando residuo que rompía la corrida siguiente. | `tests/conftest.py` apunta `RABBITMQ_URL` a un vhost propio (`tfinder_test`) y lo crea vía management API. Fixture autouse que impide que un test unitario escriba en el broker. Verificado: 3 corridas seguidas dejan el vhost de desarrollo en 0 mensajes. |
| D-07 | Media | `/api/v1/feed` no declaraba parámetros de consulta: los filtros se ignoraban en silencio y no había paginación. Hallazgo 14 de la auditoría. | `feed_api` acepta `tipo`, `autor_id`, `etiqueta`, `orden`, `limit` y `offset`, con validación de rangos. Cubierto en `tests/test_builds_feed_endpoints.py`. |
| D-08 | Baja | `conftest.py` no definía `BUILDS_DATABASE_URL` ni `FEED_DATABASE_URL`, así que esos dos servicios caían en sus bases de desarrollo (`builds_db`, `feed_db`) por default. | `conftest.py` fija las cuatro variables a las bases `*_db_test`. |
| D-09 | Baja | Un cuelgue de AMQP o de base de datos dejaba la suite colgada de forma indefinida sin diagnóstico. | `pytest-timeout` con `--timeout=120` en `pytest.ini`. |

## Brechas que siguen abiertas

1. **Sin E2E de navegador.** Solo hay vitest con jsdom. La auditoría (§4.2) pide 10
   recorridos: registro/login/logout, listado y detalle de mesas, unión con `201/409`,
   reintento con `Idempotency-Key`, matchmaking y expiración de TTL, QR válido/expirado/
   reutilizado, PDF `202`/listo/descarga, notificaciones con polling y badge, estados de
   error y protección de rutas. Requieren Playwright o Cypress. Los casos equivalentes
   están documentados en `tutorial-pruebas.md` §13 para verificar a mano.
2. **Sin tests de cierre ordenado de consumidores ni de reconexión de RabbitMQ.** Ambos
   requieren esperar un TTL o manipulate la conexión a nivel de socket.
3. **`llamado.py` sin test de expiración real del TTL en Redis.** El endpoint de estado lo
   reporta, pero no hay test que espere el vencimiento.
4. **`builds-api` no expone escritura.** Solo lectura y solicitud de PDF, así que no hay
   CRUD que probar; no es una brecha de cobertura sino de alcance.
5. **Los tests de integración dependen de la management API de RabbitMQ** para crear el
   vhost. Si no responde, la suite cae al vhost `/` con un `RuntimeWarning` y vuelve a
   perder el aislamiento.

## Nota

El tutorial `tutorial-pruebas.md` es la referencia operativa: cada caso indica URL, método,
campo, dato exacto y respuesta esperada, y fue validado caso por caso contra el ambiente.
`manual-tests.md` conserva la guía narrativa original.
