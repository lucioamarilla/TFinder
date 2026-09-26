# Inventario de superficie de pruebas

Estado al 2026-09-26: **130 tests de backend** (50 `unit`, 80 `integration`) y **22 de
frontend** (15 `unit`, 7 `integration`).

Referencia operativa caso por caso: `tutorial-pruebas.md`.

## Backend

La suite unitaria debe cubrir los módulos públicos de:

- `app/infra`: logging, Redis, RabbitMQ, readiness y envelope de error.
- `mesas_api/app`: configuración, conexión, inicialización, errores, schemas, middleware, auth, mesas, solicitudes, sesiones, matchmaking, caché, idempotencia, vacantes, llamados, QR y eventos.
- `builds_api/app`: configuración, conexión, inicialización, errores, schemas, middleware, builds, tags y eventos PDF.
- `feed_api/app`: configuración, conexión, inicialización, errores, schemas, middleware, feed, wiki, diario y eventos PDF.
- `notif_api/app`: configuración, conexión, inicialización, errores, schemas, AMQP, notificaciones, event log, DLQ, consumidores, workers, modelos, streaming, email y PDF.

### Cobertura por archivo de test

| Archivo | Marker | Cubre |
|---|---|---|
| `test_public_surface.py` | unit | Importabilidad y funciones públicas de los 4 servicios (inventario automático) |
| `test_api_contracts.py` | unit | Conteo y validez de rutas en `/openapi.json` |
| `test_schema_contracts.py` | unit | Schemas Pydantic y su `json_schema` |
| `test_unit_shared.py` | unit | Logging, correlation id, hash de contraseñas, schemas de mesa, `/ready` |
| `test_envelope_error.py` | unit | Envelope canónico en los 4 servicios, incluidos 404 y 405 del router, y que el middleware no rompa el streaming |
| `test_contrato_enlace.py` | unit | Contrato `enlace: {label, to}` entre notif-api y el frontend, en fila guardada y en SSE |
| `test_notif_services.py` | unit | Email con éxito/fallo, generación de PDF |
| `test_auth_registro_rol.py` | integration | El registro público no escala privilegios |
| `test_cache.py` | integration | Redis: miss → hit → invalidación por write |
| `test_carrera.py` | integration | N concurrentes contra 1 vacante |
| `test_idempotencia.py` | integration | `Idempotency-Key` repetida no duplica |
| `test_qr.py` | integration | QR single-use |
| `test_dlq.py` | integration | Fallo repetido termina en `dlq.general` |
| `test_dlq_operativo.py` | integration | Reintentar, descartar, 404, 401, 403 |
| `test_event_log_correlation.py` | integration | Filtro por `correlation_id` y autorización |
| `test_notif_auth.py` | integration | Notificaciones, SSE, `dlq`, `event-log`, `emails`, `pdf` |
| `test_ready_degradado.py` | integration | `/ready` listo y degradado en los 4 servicios |
| `test_matchmaking_404.py` | integration | 404 ante mesa inexistente, sin filas huérfanas |
| `test_amqp_topologia.py` | integration | `dlq.general` vinculada al DLX, con prueba de ida y vuelta |
| `test_builds_feed_endpoints.py` | integration | Endpoints de builds y feed: filtros, orden, paginación, 400, 401, 404 |

### Módulos sin cobertura automatizada

Detectados por contraste entre `app/` y la suite. Cada uno necesita un test o una exclusión
documentada antes de cerrar el cambio:

- `notif_api/app/workers/pdf.py`: la rama de tipo inválido y la de `doc_id` ausente no tienen test.
- `mesas_api/app/services/llamado.py`: expiración real del TTL en Redis sin test (requiere
  esperar el TTL o manipular la clave).
- `notif_api/app/consumers/_base.py`: cierre ordenado del consumidor y reconexión tras caída
  del broker sin test.
- `feed_api` y `builds_api` quedaron cubiertos endpoint por endpoint en
  `test_builds_feed_endpoints.py`. `builds_api` no expone escritura, así que no hay CRUD
  que probar.

## Frontend

La suite frontend debe cubrir:

- Todos los `.vue` bajo `src/components`.
- Todos los `.vue` bajo `src/views`.
- `src/composables/*.js`.
- `src/services/*.js`.
- `src/api/http.js`, `src/api/endpoints.js`, `src/config/*.js` y guards del router.

Estado actual: `tests/unit/` cubre `components.spec.js`, `feature-gating.spec.js` e
`inventory.spec.js`; `tests/integration/` cubre `http.spec.js` y `services.spec.js`.

### Brecha principal

No hay E2E de navegador. La auditoría (§4.2) pide 10 recorridos. Requieren Playwright o
Cypress. Los 13 casos equivalentes para verificar a mano están en `tutorial-pruebas.md` §13.

## Criterio de sincronización

Si se agrega una función, componente, vista, composable, servicio o endpoint, debe agregarse un test o una exclusión documentada antes de cerrar el cambio.

## Ejecución

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt -r requirements-dev.txt

venv/bin/ruff check .
venv/bin/pytest -m unit -q
venv/bin/pytest -m integration -q

cd tfinder-vue
npm ci
npm run lint
npm run type-check
npm run test:unit -- --run
npm run test:integration -- --run
npm run build
```

`pytest.ini` define `--timeout=120`: un deadlock de AMQP o de base de datos corta la corrida
con un `FAIL` con traza en vez de dejar la suite colgada.

### Requisitos de los tests de integración

- PostgreSQL, Redis y RabbitMQ levantados.
- Las cuatro bases `*_db_test` existentes (las crea `infra/postgres-init/01-crear-dbs.sql`).
- La **management API** de RabbitMQ accesible, en `localhost:15673` o `localhost:15672`
  (puede sobreescribirse con `RABBITMQ_MGMT_URL`).

El vhost `RABBITMQ_VHOST_TEST` (por defecto `tfinder_test`) se crea solo al inicio de la
sesión y las colas se purgan al terminar. La suite **no toca** las colas del vhost `/`, que
son las del ambiente de desarrollo. Comprobación:

```bash
docker exec tfinder-rabbitmq rabbitmqctl list_queues -p / name messages
# dlq.general debe quedar en 0 después de correr la suite
```

Si la management API no responde, `conftest.py` emite un `RuntimeWarning` y cae al vhost
por defecto: la suite sigue ejecutándose pero pierde el aislamiento.


