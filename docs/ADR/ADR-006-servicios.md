# ADR-006 · Separación en servicios con cero SQL cruzada

- Estado: **Aceptado**
- Fecha: 2026-09-23

## Contexto

AE1 era un monolito FastAPI con una sola entidad (`mesas`) en una DB SQLite y una única fuente de autenticación/errores. AE2 exige 4 dominios independientes (mesas, builds/PDF, feed, notificaciones), concurrencia y evidencia operacional. El criterio 13/RNF define que un servicio no debe leer las tablas de otro.

## Decisión

Dividir en **4 servicios FastAPI** (`mesas-api:8001`, `builds-api:8002`, `feed-api:8003`, `notif-api:8004`) con:

- **DB por servicio** dentro de un postgres compartido (ADR-001); cada pool apunta solo a su `*_db`.
- **Interoperación únicamente por contrato**:
  - **REST síncrono** (B09): notif-api → `GET /api/v1/mesas/{id}/miembros` en mesas-api (con auth de servicio).
  - **Eventos asíncronos** (B05/B06/B08): RabbitMQ topic `tfinder.events` (`mesa.solicitada`, `mesa.aceptada`, `sesion.confirmada`, `doc.pdf.build`, ...).
- **Librería compartida `app/`** (solo infra genérica: redis, rabbitmq, logs, ready, middleware de correlación) sin lógica de dominio; cada servicio importa su propio paquete (`mesas_api`, `builds_api`, `notif_api`, `feed_api`).
- Contratos versionados en `/api/v1/*` y documentados con OpenAPI en `/docs`.

## Consecuencias

- **Positivas**: aislamiento de fallos y de responsabilidades; deploy/escala independientes; cumplimiento de la regla de cero SQL cruzada; cada dominio evoluciona con su propia versión de spec OpenSpec.
- **Negativas**: 4 procesos + 4 bases que operar y monitorear; los consumidores y productores de eventos deben mantener contratos de mensaje compatibles; el monorepo requiere `pythonpath` correcto en los imports de tests; más superficie para la suite de integración.