# Auditoría y plan de cierre de AE2

**Proyecto:** TFinder
**Rama auditada:** `AE2-Backend`
**Commit auditado:** `b8a5301`
**Fecha de auditoría:** 2026-09-25
**Alcance:** B01–B12, F01–F09, arquitectura, seguridad, testing, Docker, documentación, OpenSpec y cierre de entrega.

## 1. Resumen ejecutivo

La funcionalidad principal de AE2 está implementada y existen merges de Git para B01–B12 y F01–F09. El problema principal no es la ausencia de funcionalidades, sino la falta de trazabilidad entre el código, los checklists de OpenSpec, las issues de GitHub, las evidencias y el estado real de cierre.

La conclusión actual es:

- **Funcionalidad B01–B12:** implementada en el historial del repositorio.
- **Funcionalidad F01–F09:** implementada en el historial del repositorio.
- **Cierre administrativo:** incompleto en OpenSpec, issues, tags, Kanban y PR final.
- **Calidad de entrega:** requiere resolver o aceptar explícitamente los bloqueos de seguridad y operación.
- **Testing:** existe una suite de integración útil, pero no cubre todos los servicios ni el frontend E2E.
- **CI/CD:** no está implementado.

No se debe declarar AE2 como definitivamente cerrado hasta verificar los hallazgos críticos y completar el proceso administrativo documentado en este archivo.

## 2. Estado de las tareas

### 2.1 Backend

| Tarea | Funcionalidad | Evidencia principal | Estado formal |
|---|---|---|---|
| B01 | Infraestructura y contenedores | `f892f7d`; `docker-compose.yml` | Implementada; archivada en OpenSpec |
| B02 | Separación de servicios | `8534b80`; cuatro paquetes API | Implementada; archivada en OpenSpec |
| B03 | Autenticación JWT y sesiones | `993e6a1`; Redis/JWT | Implementada; archivada en OpenSpec |
| B04 | Redis, caché y TTL | `6395191` | Implementada; archivada en OpenSpec |
| B05 | Eventos RabbitMQ, ACK, reintentos y DLQ | `6a70869`; `b05-rabbitmq-eventos` 16/16 | Implementada |
| B06 | Concurrencia y última vacante | `6610e3d`; `b06-concurrencia-vacantes` 14/14 | Implementada |
| B07 | QR de asistencia single-use | `29058f6` | Implementada; falta cierre de issue #20 |
| B08 | PDF asíncrono | `20b6849` | Implementada; falta cierre de issue #21 |
| B09 | Email mediante MailHog | `756b3f9` | Implementada; falta cierre de issue #22 |
| B10 | Observabilidad y correlación | `9f10f66` | Implementada; falta cierre de issue #23 |
| B11 | Testing automatizado | `47008b6`; `tests/` | Suite implementada; falta cierre de issue #24 |
| B12 | Cierre documental de AE2 | `834af06`; `AE2/README.md` y evidencias | Documentación implementada; falta cierre de issue #25, tags y archivo final |

### 2.2 Frontend

| Tarea | Funcionalidad | Evidencia principal | Estado formal |
|---|---|---|---|
| F01 | Capa HTTP unificada | `bf3774c` | Implementada; falta cierre de issue #26 |
| F02 | Autenticación real | `ed696f2` | Implementada; falta cierre de issue #27 |
| F03 | Explorar mesas reales | `229fee5` | Implementada; falta cierre de issue #28 |
| F04 | Unirse a mesa con carrera e idempotencia | `a44264b` | Implementada; falta cierre de issue #29 |
| F05 | Matchmaking y llamado con TTL | `f76e883` | Implementada; falta cierre de issue #30 |
| F06 | QR de asistencia | `31bd32f` | Implementada; falta cierre de issue #31 |
| F07 | PDF asíncrono | `2c57f14` | Implementada; falta cierre de issue #32 |
| F08 | Notificaciones en vivo | `1b13721` | Implementada; falta cierre de issue #33 |
| F09 | Administración y observabilidad | `4dcba75` | Implementada; falta cierre de issue #34 |

**Nota:** B01–B12 y F01–F09 suman 21 tareas funcionales. La guía que habla de 22 archivos debe aclararse: el archivo restante, si existe, es documentación auxiliar y no una tarea adicional.

## 3. Hallazgos que deben cambiarse o agregarse

### 3.1 Bloqueadores de cierre

#### B-01 — Aplicación raíz rota

- **Archivos:** `main.py:9-16`
- **Problema:** se importan módulos que no existen en el árbol actual, como `app.controllers.mesas_controller`, `app.routes.mesas_routes` y `app.middleware.error_handler`.
- **Impacto:** el comando raíz puede fallar con `ModuleNotFoundError`.
- **Cambio requerido:** eliminar el entrypoint legado o restaurarlo completamente y documentar cuál es el entrypoint oficial.
- **Verificación:** importar el módulo y ejecutar el healthcheck del servicio oficial.

#### B-02 — Endpoints administrativos de DLQ sin autenticación

- **Archivo:** `notif_api/app/routes/v1/dlq.py`
- **Problema:** las operaciones para listar, reintentar y descartar mensajes no tienen dependencia de autenticación/autorización.
- **Impacto:** una persona con acceso al servicio puede manipular mensajes fallidos.
- **Cambio requerido:** proteger las tres operaciones con autenticación y autorización administrativa; validar acceso antes de leer o modificar la DLQ.
- **Verificación:** requests anónimos reciben `401/403`; un administrador autorizado puede operar; un usuario común no puede operar.

#### B-03 — Recuperación de contraseña y enumeración de cuentas

- **Archivo:** `notif_api/app/routes/v1/auth.py`
- **Problema:** el flujo de recuperación puede revelar si una dirección de correo está registrada mediante una respuesta o flujo diferente.
- **Impacto:** permite descubrir cuentas válidas.
- **Cambio requerido:** respuesta, tiempo y mensaje uniformes exista o no la cuenta; registrar internamente el resultado sin exponerlo.
- **Verificación:** comparar respuestas HTTP y cuerpo para correo existente e inexistente.

#### B-04 — Secretos y credenciales por defecto

- **Archivos:** `app/infra/rabbitmq.py`, `mesas_api/app/db.py`, `mesas_api/app/models/auth_model.py`, `mesas_api/app/services/qr_asistencia.py`, `notif_api/app/services/email_service.py`
- **Problema:** existen valores sensibles o credenciales de desarrollo como fallback.
- **Impacto:** una configuración incompleta puede iniciar el sistema con credenciales conocidas.
- **Cambio requerido:** separar configuración de desarrollo de producción; en producción, fallar al iniciar si falta una variable sensible; conservar ejemplos únicamente en `.env.example`.
- **Verificación:** iniciar con configuración incompleta en modo producción y comprobar fallo explícito; revisar que no haya secretos reales en Git.

#### B-05 — SQL con columnas construidas dinámicamente

- **Archivo:** `mesas_api/app/models/mesa.py:25-29`
- **Problema:** los nombres de columnas se generan a partir de datos que provienen del modelo de entrada.
- **Impacto:** aunque los valores de Pydantic y psycopg estén validados, la construcción dinámica amplía la superficie de riesgo y dificulta demostrar una allowlist segura.
- **Cambio requerido:** definir una lista explícita de columnas permitidas y usarla para construir el `INSERT`; rechazar cualquier campo desconocido.
- **Verificación:** prueba con campos válidos, campos extra y valores maliciosos; confirmar que nunca se agregan columnas no autorizadas.

### 3.2 Prioridad alta

#### A-01 — RabbitMQ abre conexiones por publicación

- **Archivo:** `app/infra/rabbitmq.py`
- **Problema:** cada publicación puede crear una conexión nueva.
- **Cambio requerido:** definir un ciclo de vida seguro para conexión/canal, con reconexión y cierre controlado.
- **Verificación:** prueba de varias publicaciones, observando conexiones abiertas y comportamiento ante caída del broker.

#### A-02 — Consumidores sin cierre coordinado

- **Archivo:** `notif_api/main.py` y consumidores relacionados
- **Problema:** los hilos se inician como daemon y no tienen una barrera de apagado coordinada.
- **Cambio requerido:** agregar evento de parada, señal de cancelación, cierre de canales y espera ordenada de finalización.
- **Verificación:** apagar el proceso durante una prueba y comprobar que no se pierden ni duplican mensajes no confirmados.

#### A-03 — Manejo de errores inconsistente

- **Archivos:** `mesas_api/main.py`, `builds_api/main.py`, `feed_api/main.py`, `notif_api/main.py`
- **Problema:** no todos los servicios aplican el mismo formato para errores HTTP y excepciones.
- **Cambio requerido:** unificar errores `400`, `401`, `403`, `404`, `409` y `500` sin filtrar datos internos.
- **Verificación:** comparar respuestas de error entre servicios para el mismo tipo de fallo.

#### A-04 — No existe rate limiting

- **Problema:** no hay límite de peticiones para registro, login, recuperación, PDF, DLQ ni operaciones costosas.
- **Cambio requerido:** agregar rate limiting distribuido usando Redis, con límites separados para autenticación y operaciones administrativas.
- **Verificación:** superar el límite y comprobar `429`, headers de retry y ausencia de impacto en otros servicios.

### 3.3 Prioridad media

- **M-01:** cambiar el valor por defecto de `DEBUG` de `true` a `false` en `mesas_api/app/config.py`.
- **M-02:** definir CORS con una allowlist de orígenes, nunca `*` en producción.
- **M-03:** centralizar TTL de Redis en configuración.
- **M-04:** agregar paginación a listados de mesas, builds, feed y notificaciones.
- **M-05:** usar transacciones explícitas para las operaciones que actualizan cupo y solicitudes.
- **M-06:** agregar timeout explícito a llamadas HTTP externas de `notif_api`.
- **M-07:** mejorar el Dockerfile multi-stage y definir healthchecks internos para los cuatro servicios.
- **M-08:** activar o reemplazar los access logs deshabilitados en `Dockerfile`.

### 3.4 Prioridad baja

- **L-01:** no mutar el scope ASGI para transportar correlation ID; conservar el valor en context vars.
- **L-02:** evitar la configuración global de logger que sobrescribe handlers durante pruebas.
- **L-03:** verificar índices con consultas `EXPLAIN ANALYZE`.
- **L-04:** definir una política común de `response_model` para evitar respuestas sin contrato.
- **L-05:** agregar tipado y validación de parámetros de path, incluyendo IDs positivos.

## 4. Cambios de testing que deben agregarse

### 4.1 Backend

Agregar pruebas para:

1. Registro, login, logout, recuperación y revocación.
2. Validaciones `400` de todos los schemas.
3. `404` para recursos inexistentes.
4. Autorización `401/403` de DLQ, administración y endpoints sensibles.
5. Recuperación de contraseña con correo existente e inexistente.
6. CRUD y errores de `builds_api`.
7. Feed, wiki y diario de `feed_api`.
8. Notificaciones, email outbox, PDF y `/ready` de `notif_api`.
9. Cierre ordenado de consumidores.
10. Reintento y descarte de DLQ con autorización.
11. Consultas SQL con campos permitidos y campos rechazados.
12. Reinicio y recuperación de la conexión RabbitMQ.
13. Configuración incompleta de secretos en producción.
14. Paginación y filtros.

### 4.2 Frontend

Agregar pruebas E2E para:

1. Registro, login, persistencia de sesión y logout.
2. Listado y detalle de mesas.
3. Solicitud de unión con respuestas `201/409`.
4. Reintento con `Idempotency-Key`.
5. Matchmaking y expiración de TTL.
6. QR: validación correcta, expirado y reutilizado.
7. PDF: estado `202`, listo y descarga.
8. Notificaciones: polling, badge y marcar como leída.
9. Pantallas de error, carga, vacío y no autorizado.
10. Protection de rutas privadas y administrativas.

## 5. CI/CD que debe agregarse

Crear un pipeline que ejecute, en cada push y pull request:

```text
1. Instalar Python 3.12 y dependencias de desarrollo.
2. Ejecutar ruff check.
3. Ejecutar pytest con PostgreSQL, Redis y RabbitMQ aislados.
4. Levantar los servicios necesarios con Docker Compose.
5. Ejecutar validaciones OpenSpec.
6. Verificar /openapi.json y /docs de los cuatro servicios.
7. Construir las imágenes Docker.
8. Construir el frontend Vue.
9. Publicar artefactos y evidencia de la corrida.
10. Bloquear el merge si falla lint, tests, contratos o construcción.
```

### Recomendación mínima

- GitHub Actions si el repositorio se mantiene en GitHub.
- Secretos almacenados en GitHub Actions Secrets, no en archivos.
- Servicios de PostgreSQL, Redis y RabbitMQ como `service containers` de la CI.
- Cache de dependencias Python y Node.
- Job separado para backend y frontend.
- Publicación de imágenes solamente desde la rama de entrega.

## 6. Archivos que deben cambiarse o agregarse

### Agregar

- `docs/AUDITORIA_CIERRE_AE2.md` — este documento.
- `.github/workflows/ci.yml` — lint, tests, OpenSpec, Docker y frontend.
- `docs/SEGURIDAD.md` — política de secretos, DLQ y recuperación de contraseña.
- `docs/TESTING.md` — matriz de pruebas, prerrequisitos y cobertura.
- Tests unitarios, de integración y E2E nuevos.
- Issues de remediación para los hallazgos críticos y altos.

### Modificar

- `main.py` — corregir o retirar el entrypoint legado.
- `notif_api/app/routes/v1/dlq.py` — agregar autenticación y autorización.
- `notif_api/app/routes/v1/auth.py` — unificar respuestas de recuperación.
- Archivos de configuración de secretos — eliminar fallbacks inseguros en producción.
- `mesas_api/app/models/mesa.py` — usar allowlist de columnas.
- `mesas_api/app/config.py` — corregir `DEBUG`.
- `app/infra/rabbitmq.py` — corregir ciclo de vida de conexiones.
- `notif_api/main.py` — implementar cierre de consumidores.
- `Dockerfile` — healthchecks, build y logging.
- `AE2/README.md` — enlazar este informe y separar funcionalidad de cierre.
- `openspec/changes/*/tasks.md` — marcar tareas realmente completadas y dejar pendientes las técnicas.
- `requirements-dev.txt` y `pyproject.toml`, si corresponde — herramientas de lint, coverage y E2E.

## 7. Plan de ejecución ordenado

### Fase 1 — Congelar la evidencia

- [ ] Registrar el commit auditado y no mezclarlo con correcciones posteriores sin actualizar la matriz.
- [ ] Ejecutar la suite actual y guardar el resultado.
- [ ] Ejecutar validaciones OpenSpec, OpenAPI, Docker y lint.
- [ ] Guardar cada resultado como evidencia reproducible.

### Fase 2 — Corregir bloqueadores

- [ ] Resolver o retirar `main.py`.
- [ ] Proteger DLQ.
- [ ] Corregir enumeración de correos.
- [ ] Eliminar secretos por defecto en producción.
- [ ] Endurecer SQL dinámico.
- [ ] Agregar rate limiting.
- [ ] Coordinar cierre de consumidores.

### Fase 3 — Completar testing

- [ ] Agregar pruebas de seguridad.
- [ ] Agregar pruebas de los cuatro servicios.
- [ ] Agregar E2E frontend.
- [ ] Agregar coverage y umbral mínimo.
- [ ] Ejecutar la suite completa después de cada corrección.

### Fase 4 — Agregar CI/CD

- [ ] Crear workflow de CI.
- [ ] Ejecutar lint, pytest, OpenSpec, OpenAPI y builds.
- [ ] Verificar que la CI falla ante errores reales.
- [ ] Documentar cómo reproducir los resultados localmente.

### Fase 5 — Cerrar OpenSpec y GitHub

- [ ] Actualizar B01–B12 y F01–F09.
- [ ] Archivar únicamente cambios realmente completos.
- [ ] Crear o actualizar issues #20–#34.
- [ ] Asociar issue, commit, evidencia y cambio OpenSpec.
- [ ] Cargar issues en Kanban.
- [ ] Crear/verificar tags `2.0.0` y `2.1.0`.
- [ ] Preparar PR final contra la rama acordada.
- [ ] Revisar que la matriz, Kanban, OpenSpec, issues y PR digan lo mismo.

## 8. Criterios para declarar AE2 cerrado

AE2 solo debe marcarse como cerrado cuando:

- [ ] B01–B12 y F01–F09 tienen implementación verificada.
- [ ] No quedan hallazgos críticos abiertos sin aceptación explícita.
- [ ] `pytest tests -v` termina correctamente.
- [ ] Las validaciones OpenSpec terminan correctamente.
- [ ] Los cuatro servicios exponen `/docs`, `/openapi.json`, `/live` y `/ready`.
- [ ] Los cuatro servicios tienen healthcheck y logs útiles.
- [ ] Existen tests de seguridad para endpoints administrativos.
- [ ] Existe workflow de CI ejecutándose correctamente.
- [ ] No hay secretos reales ni credenciales en el repositorio.
- [ ] Todas las evidences están indexadas.
- [ ] Las tareas OpenSpec están actualizadas.
- [ ] Las issues están actualizadas y asociadas a commits.
- [ ] Kanban, tags y PR final están sincronizados.

## 9. Orden recomendado de implementation

```text
Evidencia y auditoría
        |
        v
Bloqueadores críticos
        |
        v
Tests backend y seguridad
        |
        v
Tests E2E frontend
        |
        v
CI/CD
        |
        v
OpenSpec e issues
        |
        v
Tags, Kanban y PR final
```

La prioridad no es crear más issues sin evidencia. Primero hay que ejecutar verificaciones, corregir los bloqueadores reales y recién después cerrar administrativamente las tareas que tengan implementación comprobada.

## 10. Resultado de verificaciones del 2026-09-25

| Verificación | Resultado | Motivo |
|---|---|---|
| `openspec validate cierre-ae2-auditoria-documentacion` | PASS | Cambio válido |
| `docker compose config --quiet` | PASS | Configuración Compose válida |
| `pytest tests -v` | NO EJECUTADA | `pytest` no está instalado o no está disponible en el entorno |
| `ruff check .` | NO EJECUTADA | `ruff` no está instalado o no está disponible en el entorno |
| `/openapi.json` en puertos 8001–8004 | NO VERIFICABLE | Los cuatro servicios no están levantados |
| `gh auth status` | NO EJECUTADA | `gh` no está instalado o no está disponible en el entorno |

### Prerrequisitos pendientes

Para completar la verificación se necesita:

```text
Python 3.11+ con requirements-dev.txt instalado
PostgreSQL con bases normales y *_test
Redis
RabbitMQ
MailHog
Los cuatro servicios API levantados
GitHub CLI autenticado para issues, Kanban, tags y PR
```

No se debe marcar como verde ninguna verificación que figure como `NO EJECUTADA` o `NO VERIFICABLE` en esta tabla.

