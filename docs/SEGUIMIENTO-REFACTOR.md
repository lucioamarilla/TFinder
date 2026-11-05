# SEGUIMIENTO DE REFACTOR — TFinder (torre de control)

> Pliego: `2189665929853-tfinder-frontend-standardization` → "Plan de refactorización y evolución funcional".
> Auditoría completa: `docs/AUDITORIA-FASE-0.md`. Decisiones D1–D10 CONFIRMADAS (ver auditoría §7).

## Estado general

| Fase | Estado | Fecha |
|---|---|---|
| F0 Auditoría | ✅ completa | 2026-11-05 |
| F1 Navegación/UX | ✅ completa | 2026-11-05 |
| F2 Membresías/permisos | ✅ completa | 2026-11-05 |
| F3 Bitácora de sesión | ⏳ próxima | — |
| F4 Wiki colaborativa | ⏳ | — |
| F5 Foro/Builds/Perfil + uploads | ⏳ | — |
| F6 Pruebas 6 cuentas | ⏳ | — |

## FASE 1 — tareas

| # | Tarea | Estado |
|---|---|---|
| 1.1 | Header único (Mis mesas + toda la nav autenticada; no duplicar) | ✅ `34dc872` |
| 1.2 | Auth sin header (GuestLayout real en /login /registro /recuperar) | ✅ `34dc872` |
| 1.3 | Landing: dado visible desde el primer frame + hero sin vacíos + sin cifras ficticias + datos reales con estados vacíos | ✅ `4eb7624` |
| 1.4 | Feed dual-mode: comunidades `t/` con filtro real, sin sidebar fake ni tendencias ni "Próxima sesión" | ✅ `dc87790` |
| 1.5 | Mesas activas: detalle accesible (link real) + filtros `<select>` + sin redirección prohibida al modo sesión | ✅ `34dc872`/`e401867` |
| 1.6 | Endpoint BE `GET /api/v1/feed/comunidades` + campo `comunidad` + `GET /mesas/mias` + `gm_nombre` | ✅ `20a76c1` |
| 1.7 | D10: consola admin simulada oculta en modo api | ✅ `15d4697` |

## Registro de skills (por pliego §8)

| Fase | Skill | Motivo | Resultado |
|---|---|---|---|
| F0 | tdd-workflow | marco de suite existente (236 BE / 221 FE) | base de confianza |
| F0 | click-path-audit (metodología) | rastreo de CTAs muertos ("Próxima sesión"→modo sesión, /builds/nuevo) | hallazgos P-07/G-listados |
| F1 | tdd-workflow | RED→GREEN por tarea con commits checkpoint | en curso |
| F1 | verification-loop | gate post-cambios de nav (vitest + ruff + pytest) | pendiente |

## Pruebas ejecutadas (cierre F1)

- Backend: `venv/bin/pytest -q` → **241 passed** (+5 de F1: comunidades/mias) · `ruff` clean.
- Frontend: `npx vitest run` → **221 passed** (feed dual-mode, landing real, header unificado) · `eslint` clean.
- Deploy: `docker compose up -d --build frontend` → healthy; **0 errores de consola** verificado con navegador (landing con hero desde el primer frame, mesas reales del backend, post más votado, comunidades real=0 → estado vacío diseñado).

## Archivos modificados en F1

- FE: `App.vue`, `router/index.js` (meta layout guest), `layouts/GuestLayout.vue` (reescrito), `components/AppHeader.vue` (nav única + servicios), `views/FeedView.vue` (reescrito dual-mode), `views/LandingView.vue` (reescrita real), `views/MesasListView.vue` (selects + dual), `views/MesaDetailJugadorView.vue` (dual + sin modal redundante), `services/{mesas,feed}.js`, `api/endpoints.js`, `utils/asciiD20.js` (reveal fijo).
- BE: `feed_api` (coluna comunidad + endpoints), `mesas_api` (`/mesas/mias`, `gm_nombre`), tests nuevos.
- Docs: `docs/AUDITORIA-FASE-0.md`, `docs/SEGUIMIENTO-REFACTOR.md` (este archivo).

## Decisiones arquitectónicas registradas

- Ver `docs/AUDITORIA-FASE-0.md` §7 (D1–D10 confirmadas por el usuario).

## Problemas encontrados durante F1

- (se registra a medida que aparecen)
