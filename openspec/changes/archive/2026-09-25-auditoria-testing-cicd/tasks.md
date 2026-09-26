# Tasks

## 1. Configuración e inventario

- [x] 1.1 Inventariar funciones públicas de todos los módulos Python y componentes/composables/servicios Vue; verificar que el inventario esté versionado y actualizado.
- [x] 1.2 Configurar pytest con markers `unit` e `integration`, fixtures aisladas y una forma de ejecutar cada grupo por separado.
- [x] 1.3 Configurar Vitest, Vue Test Utils, Testing Library, jsdom y scripts de test frontend en `tfinder-vue`.
- [x] 1.4 Verificar que las dependencias de desarrollo de backend y frontend se instalan desde archivos reproducibles.

## 2. Tests unitarios backend

- [x] 2.1 Cubrir con pytest las funciones públicas de configuración, infraestructura, logging, Redis, readiness y middleware; ejecutar `pytest -m unit`.
- [x] 2.2 Cubrir con pytest las funciones públicas de schemas, modelos, controladores y servicios de `mesas_api`; verificar ramas válidas, errores y límites.
- [x] 2.3 Cubrir con pytest las funciones públicas de modelos, controladores y servicios de `builds_api`; verificar CRUD, validación y errores.
- [x] 2.4 Cubrir con pytest las funciones públicas de modelos, controladores y servicios de `feed_api`; verificar feed, wiki, diario y errores.
- [x] 2.5 Cubrir con pytest las funciones públicas de email, eventos, consumidores, workers, autenticación, PDFs, readiness y DLQ de `notif_api`.
- [x] 2.6 Ejecutar `pytest -m unit` y corregir los tests fallidos sin ocultar errores de producción mediante mocks excesivos.

## 3. Tests unitarios frontend

- [x] 3.1 Crear pruebas de composables, servicios HTTP, configuración de API, autenticación, notificaciones y estado global.
- [x] 3.2 Crear pruebas de todos los componentes de layout, navegación, formularios, tablas, cards, badges, modales y estados vacíos.
- [x] 3.3 Crear pruebas de componentes de mesas, solicitudes, builds, feed, wiki, PDF, QR, administración y observabilidad.
- [x] 3.4 Ejecutar `npm run test:unit -- --run` y corregir los tests fallidos sin depender de una API real.

## 4. Tests de integración backend

- [x] 4.1 Completar fixtures de PostgreSQL, Redis y RabbitMQ aislados, healthchecks, limpieza y autenticación para todos los servicios.
- [x] 4.2 Cubrir con TestClient todos los endpoints de `mesas_api`, incluyendo auth, mesas, solicitudes, sesiones, matchmaking y errores.
- [x] 4.3 Cubrir con TestClient todos los endpoints de `builds_api`, `feed_api` y `notif_api`, incluyendo permisos y recursos inexistentes.
- [x] 4.4 Cubrir caché, invalidación, TTL, idempotencia, QR, PDF, email/outbox, retry, DLQ, correlación y `/ready` con servicios reales aislados.
- [x] 4.5 Ejecutar `pytest -m integration` y registrar la matriz de endpoints, resultados y requisitos de infraestructura.

## 5. Tests de integración frontend

- [x] 5.1 Probar flujo de registro/login/logout y navegación protegida con API mockeada.
- [x] 5.2 Probar exploración, solicitud de unión, carrera de vacante, idempotencia y estados de error.
- [x] 5.3 Probar matchmaking, QR, PDF, notificaciones y administración con respuestas exitosas, conflictivas y fallidas.
- [x] 5.4 Ejecutar la suite frontend de integración y verificar que los flujos críticos no dependan de red real.

## 6. CI/CD y guía manual

- [x] 6.1 Crear `.github/workflows/ci.yml` con jobs separados backend/frontend, lint, type-check, unit tests e integration tests.
- [x] 6.2 Configurar servicios PostgreSQL, Redis y RabbitMQ en CI con healthchecks y variables de test aisladas.
- [x] 6.3 Configurar el job bloqueante para fallar ante cualquier lint, type-check, unit test o integration test fallido.
- [x] 6.4 Crear `docs/testing/manual-tests.md` con escenarios numerados, pasos, datos, resultados esperados, casos borde y errores.
- [x] 6.5 Documentar ejecución local equivalente a CI y el diagnóstico de fallos de infraestructura.
- [x] 6.6 Ejecutar localmente lint, type-check, unit tests e integration tests; corregir los fallos dentro del alcance.
- [x] 6.7 Validar el workflow YAML, ejecutar `openspec validate` y actualizar el checklist con evidencia final.
