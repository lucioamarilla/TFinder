# Spec Delta

## Purpose

Define una estrategia reproducible de pruebas unitarias, integración, validación manual y CI/CD para backend FastAPI y frontend Vue, con cobertura de flujos críticos y bloqueo automático de regresiones.

## ADDED Requirements

### Requirement: Cobertura de pruebas unitarias backend
El proyecto SHALL ejecutar pruebas unitarias pytest para las funciones públicas de todos los módulos Python de aplicación, incluyendo servicios, controladores, modelos, middleware, utilidades, consumidores, workers y configuración observable.

#### Scenario: Ejecutar suite unitaria backend
- **WHEN** se ejecuta el comando de pruebas unitarias backend con sus dependencias instaladas
- **THEN** todas las funciones públicas incluidas en el inventario de módulos se ejercitan y la suite termina sin tests fallidos

### Requirement: Cobertura de pruebas unitarias frontend
El frontend SHALL tener pruebas Vitest con `@testing-library/vue` para todos los componentes, composables, servicios y utilidades Vue que formen parte del producto, incluyendo estados de carga, error, vacío y éxito.

#### Scenario: Ejecutar suite unitaria frontend
- **WHEN** se ejecuta Vitest sobre el frontend
- **THEN** cada componente y unidad incluida en el inventario frontend tiene al menos una prueba de comportamiento o una justificación explícita de exclusión

### Requirement: Cobertura de integración backend
El proyecto SHALL ejecutar pruebas pytest con TestClient contra los cuatro servicios, PostgreSQL, Redis y RabbitMQ aislados, cubriendo todos los endpoints públicos y los flujos de autenticación, persistencia, caché, eventos, reintentos y DLQ.

#### Scenario: Ejecutar integración backend
- **WHEN** se ejecuta la suite de integración con sus servicios disponibles
- **THEN** cada endpoint expuesto tiene una prueba de éxito y, cuando sea aplicable, de validación, autorización, conflicto y recurso inexistente

### Requirement: Cobertura de integración frontend
El frontend SHALL tener pruebas de integración para los flujos críticos de registro, login, exploración de mesas, solicitud de unión, matchmaking, QR, PDF, notificaciones y administración.

#### Scenario: Ejecutar flujo crítico frontend
- **WHEN** se ejecuta la suite de integración frontend
- **THEN** los flujos críticos muestran estados observables, manejan respuestas exitosas y de error, y no dependen de una API real durante la prueba

### Requirement: Pipeline CI/CD bloqueante
El repositorio SHALL ejecutar en GitHub Actions jobs separados para backend y frontend, incluyendo lint, type-check, unit tests e integration tests, y SHALL impedir el merge cuando cualquier job obligatorio falle.

#### Scenario: Pull request con regresión
- **WHEN** un pull request contiene un test, lint o type-check fallido
- **THEN** el workflow termina con estado fallido y el job bloqueante reporta el error

#### Scenario: Pull request válido
- **WHEN** todos los jobs obligatorios terminan correctamente
- **THEN** el workflow queda en verde y publica un resumen de resultados

### Requirement: Guía de pruebas manuales
La documentación SHALL incluir escenarios manuales numerados con prerrequisitos, pasos, datos de entrada y resultados esperados para flujos normales, casos borde y errores.

#### Scenario: Ejecutar guía manual
- **WHEN** una persona sigue un escenario de la guía manual
- **THEN** puede reproducir el resultado esperado y distinguir claramente una falla de producto de una falla de infraestructura
