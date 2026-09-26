# Design

## Context

El repositorio tiene pruebas pytest de integración para flujos de mesas, caché, concurrencia, idempotencia, QR y DLQ, pero no existe una suite unitaria amplia para backend ni una infraestructura Vitest en el frontend. Tampoco existe `.github/workflows/ci.yml`; las verificaciones dependen de ejecución manual y la infraestructura local.

El alcance “todas las funciones públicas” y “todos los componentes” se implementará mediante inventarios reproducibles: una prueba debe corresponder a una función/componente público identificado y los elementos excluidos deben quedar registrados con justificación.

## Goals / Non-Goals

**Goals:**

- Crear cobertura unitaria verificable para backend y frontend.
- Cubrir todos los endpoints y flujos críticos con integración.
- Mantener aislamiento de PostgreSQL, Redis y RabbitMQ.
- Ejecutar validaciones reproducibles en GitHub Actions.
- Documentar pruebas manuales de aceptación y diagnóstico.

**Non-Goals:**

- No cambiar contratos de API ni lógica de producción para hacer pasar tests.
- No medir 100% de líneas como equivalente a cobertura de comportamiento.
- No ejecutar pruebas de carga o E2E contra producción.
- No reemplazar la suite pytest existente; se complementa y se separa por markers cuando corresponda.

## Decisions

### D1 — Inventarios explícitos de unidades bajo prueba

Se generará un inventario de funciones públicas Python y componentes Vue. Cada elemento tendrá una prueba o una exclusión documentada. La cobertura de líneas se reportará como métrica secundaria, no como sustituto de escenarios.

### D2 — Pytest separado de integración

Se usarán markers `unit` e `integration`. Las pruebas unitarias aislarán Redis, RabbitMQ y PostgreSQL mediante fixtures/mocks; las de integración usarán servicios reales aislados, con cleanup entre tests.

### D3 — Vitest para frontend

Se configurará Vitest con Vue Test Utils y Testing Library, usando `jsdom`, mocks de API y rutas. Las pruebas de integración frontend usarán el router y servicios reales, pero API mockeada.

### D4 — CI con jobs independientes

El workflow tendrá jobs `backend-lint`, `backend-tests`, `frontend-lint-typecheck` y `frontend-tests`. El job final `ci` dependerá de todos y será el único control de merge.

### D5 — Integración con servicios de GitHub Actions

PostgreSQL, Redis y RabbitMQ se Initializes como servicios del job backend. Las variables de test usarán bases `*_test` y Redis DB aislada. MailHog se agregar solo si las pruebas lo requieren.

### D6 — Guía manual orientada a resultados

Cada escenario tendrá ID, prerrequisitos, pasos numerados, resultado esperado y criterio de bloqueo. Se separará un fallo de aplicación de un servicio caído o una configuración incorrecta.

## Risks / Trade-offs

- **La suite basada en servicios reales es más lenta** → usar jobs separados, paralelo donde sea seguro y cleanup fixture-scoped.
- **Acoplar tests a implementación puede fragile** → probar comportamiento público y usar mocks solamente en límites externos.
- **Frontend sin type-check estricto** → agregar `vue-tsc`/equivalente disponible y documentar errores preexistentes como bloqueantes solo si el comando está configurado.
- **RabbitMQ puede ser inestable en CI** → healthcheck, timeout y job explícito de diagnóstico.
- **“Todos” puede crecer continuamente** → inventarios versionados y un test que detecte unidades nuevas sin cobertura.

## Migration Plan

1. Inventariar módulos Python y componentes Vue.
2. Configurar pytest, Vitest, Vue Test Utils y scripts frontend.
3. Implementar pruebas unitarias backend y frontend.
4. Completar integración backend y frontend.
5. Agregar workflow GitHub Actions y variables de infraestructura.
6. Redactar guía manual.
7. Ejecutar suite local completa.
8. Corregir tests o código únicamente cuando el fallo sea legítimo y esté dentro del alcance.
9. Validar el workflow localmente mediante lint, type-check y comandos equivalentes.
10. Archivar el cambio solo cuando la evidencia de implementación esté completa.

## Open Questions

- La cantidad exacta de componentes Vue que se considerarán públicas debe mantenerse sincronizada con el inventario frontend.
- El comando de type-check frontend debe adaptarse a la configuración Vue/JavaScript existente si no existe TypeScript estricto.
