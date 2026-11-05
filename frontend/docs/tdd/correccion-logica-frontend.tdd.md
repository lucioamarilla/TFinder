# Reporte de evidencia TDD · Corrección de lógica del frontend v5

**Fecha:** 2026-11-05 · **Repo:** `stitch_rediseno_v5/tfinder-vue` (git inicializado en el proyecto)
**Comandos válidos:** `npm test` (Vitest), `npm run lint`, `npm run build`.

> **Fase 11 (2026-11-05):** pantallas estructurales del mapa de navegación original construidas con estética v5 — campana con badge (CA-48), selector de campañas, buscador global + `/busqueda` (alcance), `/mesas/:id/calendario` arcade canónica con `rules/fechas.js` (RN-06/17, VAL-29..32), `/mesas/:id/sesion/jugador` (panel del jugador) + material «en uso» fijado por el GM, tabs Tablero/Personajes en el detalle de mesa, y perfil con preferencias + cambio de contraseña (VAL-03). Dominio y pantallas: RED→GREEN con `fase11Dominio.spec.js` (18) y `fase11Pantallas.spec.js` (17).
>
> **Fase 9 (2026-11-05):** cierre de integraciones — Calculadora APL con validaciones de reglas (sin valores silenciosos), ruta `/mesas/:id/editar` revivida vía `MesaFormularioView` (con mapeo plazas→cupo/estado normalizado y VAL-15 activo), y los servicios de gestión `votaciones.js` + `jugadores.js` ahora SON adaptadores del store demo unificado (votos por sesión con nombres de membresías, VAL-30..32/RN-17; aceptar/rechazar/expulsar delegan en `responderSolicitud`/`salirMesa`, RN-08/VAL-17). Humos de montaje para Builds/Tags/Encuentros y las 10 vistas admin. `fase9.spec.js` (12 tests). Total suite: **201/201**.


## 1. Plan y origen

Plan acordado en sesión con el usuario (modo Plan):
- Sesión demo sin backend (elección explícita), reglas RN/VAL del doc maestro `Documentacion_TFinder-1.md`.
- No borrar nada; revivir todo lo muerto (router/guard/api-header/etc).
- Suite: Vitest unit + componentes (`@vue/test-utils`). Cobertura ≥80% en lo tocado.
- `src/api/*` queda intacto (modo demo no lo usa): bugs de su reintento (`http.js` AbortController compartido) quedan documentados, fuera de alcance.

## 2. User journeys (del plan)

1. Como jugador, quiero que al iniciar sesión el header muestre mi perfil, para abandonar el estado fantasma de invitado (bug reportado).
2. Como jugador, quiero postularme a una mesa y que el asiento solo se libere cuando el GM acepte (RN-07/08/09).
3. Como GM, quiero una bandeja de solicitudes por mesa con aceptar/rechazar y un 409 visible si la mesa está llena (RNAVAL-17..24).
4. Como lector, quiero una wiki con visibilidad privada/jugadores/pública según mi sesión (RN-05) y 404 reales.
5. Como director de juego, quiero cerrar/abrir/reconfigurar el cupo de mi mesa con validación VAL-15.
6. Como jugador, quiero un feed con votos únicos y actualizables por sesión y posts de mesa solo para miembros (RN-18, VAL-41/43).
7. Como GM, quiero guardar el diario de sesión con resumen obligatorio (VAL-33) y seguir la iniciativa sin errores.
8. Como nuevo usuario, quiero registrarme con validaciones VAL-01/03/05 y quedar con sesión activa (CA-01).
9. Como admin, quiero consola `/admin` solo para mi rol (guard).

## 3. Task mapping (plan → RED → GREEN)

| # | Plan | Test (RED → GREEN) | Evidencia |
|---|------|--------------------|-----------|
| F0 | Baseline suites | `npm run build` + `vitest` verde (2 smoke) | baseline `chore:` |
| F1 | Sesión demo, guard, header | Commit `test:` (10 fallos) → `feat:` (30/30) | `-b main` |
| F2a | Reglas mesas/solicitudes + store | `test:` 16 fallos → `feat:` 70/70 | |
| F2b | Vistas de mesas (unión, bandeja GM, cupo VAL-15, 404) | `test:` 18 fallos → `feat:` 88/88 (+ lint) | |
| F3 | Wiki RN-05/VAL-25/26 + sesión VAL-33 | `test:` 12 fallos → `feat:` 118/118 | |
| F4 | Feed VAL-41/43 y notificaciones por sesión | Verde directo tras darker RED interno → 128/128 | |
| F5 | Revividos: router completo, gestión tabs, admin, builds VAL-44/45, matchmaking | `revividos.spec` 6 fallos → 149/149 + `npm run build` ok | |
| F6 | Perfil/VAL-05, bestiario, landing CTAs | 154/154 | |
| F7 | Cobertura + evidencia | Este archivo | ver §4 |

## 4. Cobertura (núcleo del cambio; `npx vitest run --coverage`)

| Zona | % Stmts | % Branch | Estado |
|---|---|---|---|
| `src/rules/*` (auth, mesas, solicitudes, wiki, sesiones, feed, builds) | **95.6** | 92.4 | ✅ ≥80 |
| `src/services/demo.js` (store de dominio) | **93.8** | 77.9 | ✅ |
| `src/composables/useAuth.js` | **87.5** | 75.7 | ✅ |
| `src/services/mesas.js` (rewired a demo) | 100 | 62 | ✅ |
| `src/services/notificaciones.js` (rewired) | 100 | 66 | ✅ |
| `src/config/*` | 87 | 75 | ✅ |
| Vistas v5 activas | 84–100 por archivo | | ✅ media |
| Servicios self-contained revividos (votaciones, wiki.js, sesiones.js, jugadores.js, builds.js, usuarios, actividad, eventos, admin) | 0–46 | | ⚠ gap conocido |
| Vistas de consola `admin/*` y tabs `gestion/*` | humo de montaje en `adminGestionHumo.spec.js` | | ⚠ gap aceptado |

El total del proyecto baja por archivos legacy revividos con datos demo estáticos (consola admin / tabs de gestión / utilities). Los límites del negocio (validadores y store) están por encima del objetivo del 80%.

## 5. Reglas implementadas (referencia doc maestro)

- RN-02/04/07/08/09/11/12/15/16/18/19 parcialmente en flujos demo (mesas, solicitudes, cupo, cascada al eliminar, wiki visibilidad, folio de versiones de builds).
- VAL-01/03/05 (auth), VAL-06/07/08/09/13/14/15/17 (mesas), VAL-18..24 (solicitudes), VAL-25/26/28 (wiki), VAL-29..33 (sesión/diario), VAL-37..40,44/45 (builds), VAL-41/43 (feed), RN-20/VAL-46 (idempotencia vía UUID local).
- Mensajes 400/403/409 de backend replicados (`errorNegocio`), mostrados inline o toast.

## 6. Cambios técnicos adicionales

- `router.beforeEach` instalado con `resolveGuard` (reutilizable en tests vía `instalarGuard`).
- Ruta `proximamente/:feature` (ComingSoonView) — guard ya no 404ea.
- Navegación `config/nav.js` sin rutas fantasmas (test lo fija).
- Header de sesión: invitado vs avatar+menú (bug del reporte usuario); admin link a consola.
- Store demo v2 (`tf-demo-v2`) con `membresias`/`solicitudes` derivadas; ocupación siempre derivada.
- Servicios `services/mesas.js` + `services/notificaciones.js` adaptables a la demo mantención misma firma; `src/api/*` intacto.
- Toasts: unificación ligera vía demo.toast (DOM) ya existente; ToastHost (Vue) en uso por vistas revividas.
- A11y de lógica: `role="alert"` y `role="status"` en errores y estados no nominales.

## 7. Gaps conocidos (intencionales)

- `src/api/http.js` reintento AbortController compartido (código no usado en modo demo). Al activar backend: reponer cuerpo por suscripción de `useAuth` backend + fix del AbortController.
- Tabs de gestión revividos con datos demo JSON; sus validaciones de alta de página usan la misma `validarPaginaWiki`. La votación de fechas (volteos RN-06) usa semilla demo AUSTRALIANA; integrar con calendario del v5 si se desea.
- Sin E2E Playwright (elección de suite del usuario). Sugerencia de smoke manual en `docs/GUIA_USO.md` §1.

## 8. How-to

```bash
cd tfinder-vue
npm test            # 154 tests
npm run lint        # ESLint clean
npm run build       # build de producción ok
npx vitest run --coverage
```
