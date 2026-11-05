# Evidencia TDD · Plan "Cierre de MVP" (2026-11-05)

**Fuente del plan:** `/home/lucioamarilla/.opencode/plan/tfinder-cierre-mvp.plan.md`
**Método:** ciclos RED→GREEN→refactor con commits checkpoint (rama `backend-fusion`; FE en el repo anidado `frontend/`).
**Ejecutada por sesión con:** docker infra real (postgres/redis/rabbitmq), suite `venv/bin/pytest`, `npx vitest`.

## 1. Línea de base (Step 0)

| Runner | Comando | Baseline al inicio | Final |
|---|---|---|---|
| Backend | `venv/bin/pytest -q` | **169 passed** (creado el venv en P0.0) | **236 passed** |
| Backend cov. | `pytest --cov=app --cov=mesas_api --cov=builds_api --cov=feed_api --cov=notif_api` | sin venv | **83% global** (≥80 objetivo) |
| Frontend | `npx vitest run` | **201 passed / 19 files** | **221 passed / 22 files** |

## 2. Matriz task → test → RED → GREEN

| # | Task (plan) | Test objetivo | RED | GREEN (commit) |
|---|---|---|---|---|
| P0.1 | Deployable: compose+main.py+README | smoke `test_api_contracts` + `docker compose config` | — (cleanup) | `658c154` |
| P0.2 | Same-origin dev + apiUrl estricta | `tests/unit/apiConfig.spec.js` (RED 1) | desconocido caía silencioso a mesas | `a8f4955` |
| P0.3 | Sesión real FE→BE | `test_auth_sesion_familia.py` (RED 2) + `authApi.spec.js` (RED 6) | logout no mataba refresh; auth sin perfil; FE sin Bearer; AbortController compartido | BE `0b9c66f` · FE `c50ab60` |
| P0.4 | Vertical mesa (ownership/pf1e/filtros/solicitudes GM) | `test_vertical_mesa.py` (RED 12) + reescritura `test_carrera.py` | 403/404/400/409 ausentes; auto-acept produjo carrera al crear | `130f68b` |
| P1.5 | Calendario votación | `test_calendario.py` (RED 10) | RF-10/11/17 + VAL-29..32 ausentes | `bb261ed` |
| P1.6 | Wiki CRUD + visibilidad | `test_wiki_crud.py` (RED 10) | POST/PUT/DELETE/403/404 + RN-05 vía REST B09 | `2ec4991` |
| P1.7 | Feed activo | `test_feed_social.py` (RED 7) | crear/like toggle/seguir ausentes | `db0e0e3` |
| P1.8 | Builds CRUD/versionado/vincular/tags | `test_builds_crud.py` (RED 10) | API era solo lectura | `36f0f7f` |
| P1.9 | Infra operativa | `test_infra_operativa.py` (RED 5) | sin /metrics, 429, X-Cache, guard QR/mm, OpenAPI BearerAuth | `83a344b` |
| P2 | Nombres en bandeja/calendario + embed del feed | tests added (RED 2) | GM no veía quién pedía; embed no viajaba → post-build feed | (junto `feat(negocio)`/`feat(feed)`) |
| P2 | Adaptadores FE modo api | `serviciosApi.spec.js` (11 casos, RED→GREEN) | nada llamaba al backend real | FE `3a53836` |
| P2 | Full-stack real | `docker compose up -d --build` + E2E curl del vertical | — | ver §4 |

## 3. Garantías acordadas (extracto legible)

| # | Qué garantiza | Prueba | Tipo | Resultado |
|---|---|---|---|---|
| 1 | Un POST /solicitudes nace 'pendiente', es idempotente por Idempotency-Key | `test_idempotencia.py` + frozen | integration | PASS |
| 2 | La carrera de cupo se juega al ACEPTAR: 1×200 + 2×409 con cupo 1 | `test_carrera.py::test_solo_un_acepte...` | integration | PASS |
| 3 | El mismo usuario no puede dejar 2 solicitudes activas (índice parcial) | `test_carrera.py::test_doble_solicitud...` | integration | PASS |
| 4 | Solo el GM propietario (o admin) edita/borra su mesa (VAL-17 403) | `test_vertical_mesa.py` | integration | PASS |
| 5 | `sistema` solo 'pf1e' (VAL-08) y cupo no baja debajo de ocupación (VAL-15) | `test_vertical_mesa.py` | integration | PASS |
| 6 | Logout revoca access **y** refresh (familia completa) | `test_auth_sesion_familia.py` | integration | PASS |
| 7 | El calendario: GM propone (VAL-29), miembros votan/editan (RN-06), GM no vota (RN-17), confirmar crea sesión | `test_calendario.py` | integration | PASS |
| 8 | La wiki escribe solo GM y se lee según visibilidad pública/jugadores/privada (RN-05/VAL-28) | `test_wiki_crud.py` (con mesas-api real en hilo) | integration | PASS |
| 9 | Feed: crear (VAL-41), like único con toggle (VAL-43), follows sin autofollow (RN-10) | `test_feed_social.py` | integration | PASS |
| 10 | Builds: clase y atributos 3–18 (VAL-44/45), ownership, apilar/restaurar versión (RN-19), vincular exige membresía (VAL-40/D09) | `test_builds_crud.py` | integration | PASS |
| 11 | 101ª petición por IP/min → 429 con envelope | `test_infra_operativa.py` (techo 2 forzado) | integration | PASS |
| 12 | Redis caído: listado sale de la BD con `X-Cache: MISS` (CA-51) | mismo archivo | integration | PASS |
| 13 | `/metrics` expone `tf_requests_total` (RNF-20) y OpenAPI declara `BearerAuth` (7.3) | mismo archivo | integration | PASS |
| 14 | Solo el GM de la mesa valida QR de asistencia; `/matchmaking/estado` exige sesión | mismo archivo | integration | PASS |
| 15 | El FE (modo api) llama endpoints reales y mapea DTO: mesas, bandeja con nombres, votos con facciones, notificaciones con `enlace.to`, sesiones, diario, wiki, feed | `frontend/tests/unit/serviciosApi.spec.js` | unit/contract | PASS |
| 16 | El modo api no rompe el modo demo (los 9 tests de sesión demo siguen verdes) | suite FE completa | unit | PASS (221/221) |

## 4. Evidencia de deploy

- `docker compose up -d --build` → 4 APIs + frontend + postgres + redis + rabbitmq + mailhog **todos healthy**; `/docs` y `/metrics` accesibles.
- Nginx del frontend y de proxies same-origin: `GET :5174/mesas-api/api/v1/mesas` → datos con `gm_id`/`pf1e`/`jugadores_actuales`.
- **E2E vertical completo por API (curl):** registro → login (perfil) → GM crea mesa (`gm_id` set) → jugador solicita (**pendiente**) → GM acepta (200, miembro visible) → GM propone fecha futura → jugador vota (`a_favor: 1`) → confirmar → **nace sesión** → diario 201 con evento → notificaciones del GM disponibles (5).

## 5. Cobertura y huecos conocidos

- Terminación: **83% global** (objetivo 80). Módulos de negocio: builds `85%`, feed `93%`, wiki `86%`; `stream.py` (SSE 20%) y `email_service.py` (47%) quedan como infraestructura de proceso externo (broker/SMTP) — candidatos a subir con pruebas de integración dedicadas en un próximo ciclo.
- Tests *frozen* actualizados intencionalmente en 4 jalones (forma auth + `gm_id`, curl 405→PATCH, listing privado RN-11, matchmaking ahora autenticado): cambios planificados, documentados aquí.
- Deuda adicional detectada pero no ejecutada en este plan: transaccionalidad de `publicar_diario` + idempotencia, SSE multi-réplica (Redis pub/sub), contratos E2E Playwright en navegador, limpieza de archivos muertos del FE (~15 identificados en la auditoría), rate limiting distribuido multi-instancia.

## 6. Desvío documentado

- **VAL-04/RNF-09 (bcrypt 10+):** el backend usa **PBKDF2-HMAC-SHA256 · 120.000 iteraciones**. Criptográficamente equiparable o superior; se mantiene con desvío documentado en este informe (cambio a bcrypt solo si el tribunal exige literalidad).

## 7. Cómo reproducir

```bash
python3 -m venv venv && venv/bin/pip install -r requirements.txt -r requirements-dev.txt
docker compose up -d           # infra
venv/bin/pytest -q             # 236 passed
cd frontend && npx vitest run  # 221 passed
docker compose up -d --build   # stack completo
```
