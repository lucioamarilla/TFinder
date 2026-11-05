# SEGUIMIENTO DE REFACTOR — TFinder (torre de control)

> Pliego: `2189665929853-tfinder-frontend-standardization` → "Plan de refactorización y evolución funcional".
> Auditoría completa: `docs/AUDITORIA-FASE-0.md`. Decisiones D1–D10 CONFIRMADAS (ver auditoría §7).

## Estado general

| Fase | Estado | Fecha |
|---|---|---|
| F0 Auditoría | ✅ completa | 2026-11-05 |
| F1 Navegación/UX | 🚧 en curso | 2026-11-05 |
| F2 Membresías/permisos | ⏳ | — |
| F3 Bitácora de sesión | ⏳ | — |
| F4 Wiki colaborativa | ⏳ | — |
| F5 Foro/Builds/Perfil + uploads | ⏳ | — |
| F6 Pruebas 6 cuentas | ⏳ | — |

## FASE 1 — tareas

| # | Tarea | Estado |
|---|---|---|
| 1.1 | Header único (Mis mesas + toda la nav autenticada; no duplicar) | ⏳ |
| 1.2 | Auth sin header (GuestLayout real en /login /registro /recuperar) | ⏳ |
| 1.3 | Landing: dado visible desde el inicio + scroll progresivo + sin cifras ficticias | ⏳ |
| 1.4 | Feed: sin "Mis mesas activas", sin texto v5/OGL, sin tendencias; comunidades reales `t/` con filtro backend | ⏳ |
| 1.5 | Mesas activas: detalle accesible + filtros con selectores predefinidos | ⏳ |
| 1.6 | Endpoint BE `GET /api/v1/feed/comunidades` (fuente real de comunidades) | ⏳ |

## Registro de skills (por pliego §8)

| Fase | Skill | Motivo | Resultado |
|---|---|---|---|
| F0 | tdd-workflow | marco de suite existente (236 BE / 221 FE) | base de confianza |
| F0 | click-path-audit (metodología) | rastreo de CTAs muertos ("Próxima sesión"→modo sesión, /builds/nuevo) | hallazgos P-07/G-listados |
| F1 | tdd-workflow | RED→GREEN por tarea con commits checkpoint | en curso |
| F1 | verification-loop | gate post-cambios de nav (vitest + ruff + pytest) | pendiente |

## Pruebas ejecutadas (línea de base al iniciar F1)

- Backend: `venv/bin/pytest -q` → **236 passed** · cov 83% · `ruff` clean.
- Frontend: `npx vitest run` → **221 passed**.
- Stack: docker full up + login real por UI verificado.

## Decisiones arquitectónicas registradas

- Ver `docs/AUDITORIA-FASE-0.md` §7 (D1–D10 confirmadas por el usuario).

## Problemas encontrados durante F1

- (se registra a medida que aparecen)
