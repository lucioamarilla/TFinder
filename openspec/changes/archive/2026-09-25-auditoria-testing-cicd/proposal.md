# Proposal

## Why

TFinder tiene pruebas de integración para algunos flujos críticos, pero no existe una estrategia completa de pruebas unitarias de backend/frontend, cobertura de todos los endpoints ni un pipeline CI/CD que ejecute y bloquee cambios de forma reproducible. Esta falta de cobertura permite regresiones y dificulta validar el cierre de AE2.

## What Changes

- Incorporar pruebas unitarias backend con pytest para las funciones públicas de los módulos Python.
- Incorporar pruebas unitarias frontend con Vitest y Testing Library para componentes, composables y servicios Vue.
- Ampliar las pruebas de integración backend con TestClient, PostgreSQL, Redis y RabbitMQ aislados.
- Incorporar pruebas de integración frontend para flujos críticos de usuario.
- Crear un workflow de GitHub Actions con jobs separados de backend y frontend, lint, type-check, unit tests, integration tests y bloqueo del merge ante fallos.
- Crear una guía manual con escenarios reproducibles, casos borde y errores esperados.
- Documentar cómo ejecutar localmente la misma validación que ejecuta CI.

## Capabilities

### New Capabilities

- `auditoria-testing-cicd`: Estrategia completa de pruebas unitarias, integración, validación frontend/backend y pipeline CI/CD reproducible.

### Modified Capabilities

- Ninguna. La nueva capability organiza la ampliación de testing y CI/CD sin cambiar los requisitos funcionales existentes.

## Impact

- Backend Python: nuevas pruebas y configuración de pytest.
- Frontend Vue: nuevas pruebas, configuración Vitest/Vue Test Utils y dependencias de desarrollo.
- GitHub Actions: workflow `.github/workflows/ci.yml`.
- Infraestructura: servicios aislados para integración y pruebas de concurrencia/DLQ.
- Documentación: `docs/testing/manual-tests.md` y guía de ejecución local.
- No se modifican contratos de API ni funcionalidades de producción como parte de la planificación.
