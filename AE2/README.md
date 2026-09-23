# TFinder · Entrega AE2 (Paradigmas III)

Gestión de mesas de Pathfinder 1.ª edición como **sistema distribuido**: cuatro servicios FastAPI independientes que interoperan por contrato REST y eventos asíncronos, con autenticación, concurrencia con doble barrera, QR de asistencia single-use, PDF asíncrono, notificaciones por email en sandbox y observabilidad base.

**Integrantes:** Amarilla Lucio · Czajkowski Leonardo

## Estado

- Backend completo: B01–B11 cerrados, rama `AE2-Backend`, tags `2.0.0` (alfa) y `2.1.0` (beta).
- Suite pytest reproducible: `5 passed` (`tests/`).
- Evidencias del checklist del enunciado: [AE2/evidencias/EVIDENCIAS.md](evidencias/EVIDENCIAS.md).
- Decisiones de arquitectura: [docs/ADR](https://github.com/lucioamarilla/TFinder/tree/AE2-Backend/docs/ADR).
- Frontend (`tfinder-vue`): pautado F01–F09 (github issues #26–#34).

## Cómo correr todo desde cero

```bash
docker compose up -d --build mesas-api builds-api feed-api notif-api
```

- **PostgreSQL** (4 bases + 4 de test) en `postgres:16-alpine`; esquemas creados por cada servicio en su arranque.
- **Redis**, **RabbitMQ** e **infraestructura** listas vía compose; puerto AMQP externo `5673`, panel RabbitMQ `15673`.
- Host: mesas `8001`, builds `8002`, feed `8003`, notif `8004`, Redis `6390`, MailHog UI `8025`.
- `/docs` (OpenAPI/Swagger) en cada puerto; `/live` y `/ready` en los 4 servicios.

Suite de pruebas:

```bash
venv/bin/pip install -r requirements-dev.txt
venv/bin/pytest tests -v     # sobre bases *_test y Redis db 15
```

## Criterios AE2 → evidencias

Cada criterio del checklist tiene su respaldo en `AE2/evidencias/` (indexado en `EVIDENCIAS.md`): TTL de Redis, colas y DLQ de RabbitMQ, carrera por la última vacante (1×201 / 9×409), QR no reutilizable, email en MailHog, PDF asíncrono `202`→`200`, correlación `X-Correlation-Id`, `/ready` y la corrida `pytest -v`.

## ADR

| ADR | Decisión |
| --- | -------- |
| ADR-001 | PostgreSQL con una base por servicio |
| ADR-002 | Redis: TTL vs invalidación (sesiones, caché, reserva, QR) |
| ADR-003 | RabbitMQ topic + DLQ, ACK, reintentos backoff, idempotencia del consumidor |
| ADR-004 | Doble barrera de concurrencia (Redis NX + UPDATE condicional) |
| ADR-005 | MailHog sandbox con timeout y outbox |
| ADR-006 | Separación en servicios con cero SQL cruzada |
| ADR-007 | QR de asistencia single-use (GETDEL + HMAC) |

## Versionado

- Rama de entrega: `AE2-Backend` (merges incrementales de cada issue).
- `2.0.0` — alfa: infraestructura + servicios básicos + auth (B01–B03).
- `2.1.0` — beta: async/concurrencia (B05/B06), QR, PDF, email, observabilidad, testing y evidencias (B07–B12).