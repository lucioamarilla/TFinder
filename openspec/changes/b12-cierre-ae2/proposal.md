# Proposal: Cierre de AE2 — ADRs, OpenAPI y evidencias

## Why

Cerrar la entrega AE2 de forma profesional y rastreable (criterios 6, 7, 8, 9 y 13/transversales): decisiones de arquitectura documentadas (ADR), contratos OpenAPI consistentes y una carpeta de evidencias con respaldo visual de cada criterio, enlazada desde un README de entrega y con versionado semver de la rama.

## What Changes

- **`docs/ADR/`** nuevo: 7 ADR (PostgreSQL multi-DB, Redis TTL/invalidación, RabbitMQ+DLQ, doble barrera, MailHog+outbox, separación en servicios, QR single-use).
- **OpenAPI verificado** en los 4 servicios (`/docs` y `/openapi.json` 200, sin schemas huérfanos): mesas 18 rutas, builds 7, feed 5, notif 9.
- **`AE2/evidencias/`**: generador `scripts/generar_evidencias.py` + 9 PNG/txt + `EVIDENCIAS.md` (índice criterio→archivo).
- **`AE2/README.md`**: README de entrega (estado, cómo correr, criterios→evidencias, ADRs, tags).
- **Git**: rama de la tarea, commits con la documentación, tags `2.0.0` (alfa) y `2.1.0` (beta), merge y cierre de #25.

## Capabilities

- **New Capabilities**: `cierre-ae2` — documentación de entrega (ADR, OpenAPI, evidencias indexadas, README de entrega y versionado).

## Impact

- Puramente documental: no cambia servicio alguno. El generador de evidencias requiere la infra levantada (compose) y MailHog para recrear los PNG.