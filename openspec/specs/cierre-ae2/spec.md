# Purpose

Definir el cierre documental de AE2: decisiones de arquitectura (ADR), contratos OpenAPI completos, evidencias indexadas por criterio del enunciado, README de entrega y versionado semver de la rama.

## Requirements

### Requirement: ADRs de decisiones clave
El repo DEBE contener al menos 5 ADR en `docs/ADR/ADR-*.md`, cada uno con las secciones Contexto, Decisión y Consecuencias, cubriendo: PostgreSQL multi-DB, Redis con TTL/invalidación, RabbitMQ con DLQ, la doble barrera de concurrencia, la integración externa (MailHog/outbox) y la separación en servicios.

#### Scenario: Documentación revisable
- **WHEN** se enumera `docs/ADR/`
- **THEN** existen los ADR 001–007 con las secciones pedidas y texto que refleja las decisiones reales del backend

### Requirement: OpenAPI completo y consistente
Cada uno de los 4 servicios DEBE servir `GET /docs` y `GET /openapi.json` sin errores, y ninguna respuesta de sus rutas DEBE referenciar un schema inexistente.

#### Scenario: Verificación de contrato
- **WHEN** se consulta `/openapi.json` en los puertos 8001–8004
- **THEN** los 4 responden 200, con rutas definidas y sin `$ref` huérfanos hacia `components.schemas`

### Requirement: Evidencias indexadas por criterio
`AE2/evidencias/` DEBE tener al menos 6 capturas PNG que respalden los criterios del enunciado (TTL Redis, colas/DLQ, carrera, QR, email, PDF, correlación, /ready, pytest), con un índice `EVIDENCIAS.md` que mapee cada criterio a su archivo.

#### Scenario: Inventario de evidencias
- **WHEN** se listan los PNG de `AE2/evidencias/` y se abre `EVIDENCIAS.md`
- **THEN** hay ≥6 PNG y cada fila del índice referencia un archivo que sí existe

### Requirement: README de entrega y versionado
`AE2/README.md` DEBE describir el estado de la entrega, cómo correr todo, y enlazar a evidencias y ADRs; la entrega DEBE quedar con tags semver `2.0.0` (alfa) y `2.1.0` (beta) en la rama AE2.

#### Scenario: Entrega rastreable
- **WHEN** se abre `AE2/README.md` y se ejecuta `git tag -l` y `git log --oneline`
- **THEN** el README enlaza evidencias/ADRs y los tags `2.0.0`/`2.1.0` existen sobre el historial de `AE2-Backend`