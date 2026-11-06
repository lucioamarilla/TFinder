# Informe de evidencia TDD · Corrección del rediseño de frontend (AE4)

- **Rama:** `entrega/proyecto-final`
- **Fecha:** 2026-11-06
- **Plan fuente:** conversación (informe de revisión AE4 + decisiones del usuario)
- **Workflow:** TDD (RED → GREEN → checkpoint por ciclo)

## 1. Decisiones acordadas con el usuario

| Decisión | Elección |
|---|---|
| Alcance | P0 + P1 + P2 completo (ciclos 0.1 → 15) |
| D-07 estilos | Mantener el diseño visual actual: compilar lo escrito (Tailwind + pergamino), sin re-estilizar vistas |
| D-06 ambientación | Mapear a `tono` (solo frontend) |
| Backend | Cambios mínimos permitidos (D-17 `gm_nombre`, D-14 `mi_voto`), con pytest de cada uno |
| F09 admin | Re-implementar consola sobre los endpoints reales de notif-api; módulos sin backend quedan fuera |

## 2. Jornadas de usuario que guiaron los tests

1. Como **invitado**, quiero ver la ficha pública de una mesa aunque la pestaña de personal no cargue.
2. Como **GM**, quiero gestionar mi mesa aunque falle una llamada secundaria.
3. Como **GM**, quiero ver sesiones reales (fecha + estado) y llegar a diario/QR sin 404.
4. Como **GM**, quiero proponer día y hora reales y ver mi voto propio.
5. Como **usuario**, quiero crear una mesa con ambientación escrita en libertad.
6. Como **usuario autenticado**, quiero reconocer mi sesión en todas las pantallas y cerrar sesión.
7. Como **admin**, quiero el event log, la DLQ y los emails en la consola.

## 3. Mapa plan → test → RED → GREEN

| # Ciclo | Qué garantiza | Test (comando `npm test`) | Resultado RED | Resultado GREEN |
|---|---|---|---|---|
| 0.1 | package.json sin scripts rotos (`test:integration` fuera, `test:coverage` disponible) | `npm run test:integration` | "No test files found" | 91/91 suite baseline |
| 1 | La mesa no se anula por `getMiembros`/`getSolicitudes` fallando (401/403) — D-01/D-21 | `tests/unit/detalleMesa.spec.js` (5) | 3 specs: "Mesa no encontrada" con mesa existente | 5/5 · suite 96 |
| 2 | MesaGestionShell carga parcial + fallback ocupación + esGM reconoce `master` — D-02 | `tests/unit/gestionShell.spec.js` (4) | 4 specs | 4/4 · suite 100 |
| 3 | SesionesView sobre `SesionOut` real; enlaces `/gestion/sesiones/:sid/…` — D-04 | `tests/unit/sesionesGestion.spec.js` (5) | TypeError `s.numero` craseando montaje | 5/5 · suite 105 |
| 4 | ISO `YYYY-MM-DDTHH:mm:00` aceptado; `miVoto` (backend `mi_voto` + inferencia por nombre); capacidad desde plazas; marcas por fecha — D-05/D-14 | `tests/unit/calendarioGestion.spec.js` (8) | 7 specs | 8/8 · suite 113 |
| 5 | Ambientación libre → `tono`; frecuencia→horario en crear y actualizar; sin "A coordinar" contaminante — D-06/D-08 | `tests/unit/mesasFormulario.spec.js` (5) | 5 specs | 5/5 · suite 118 |
| 6 | Landing con sesión (perfil + cerrar sesión), sin bestiario/compendio; trigger real del menú móvil — D-03 | `tests/unit/navegacionSesion.spec.js` (7) | 6 specs | 7/7 · suite 125 |
| 7 | Tailwind compilado + crono/harness importados + fuentes mason/tarzana/minion + `.sim-panel` — D-07 | `npm run build` + grep del CSS dist | 0 apariciones de `font-mason`/`btn-gold` en la imagen previa | build OK: `font-mason` ×1, `btn-gold` ×6, `sim-panel` ×13 |
| 8 | Estado canónico abierta|cerrada; cupo/plazas unificados (sin undefined/NaN) — D-09/D-10 | `tests/unit/estadoCupo.spec.js` (4→6) | 4 specs ('Completa' en vez de 'Cerrada'; NaN) | 6/6 · suite +2 |
| 9 | getMiembros con rol real (Master) y capacidad de la mesa — D-11 | `tests/unit/jugadoresMiembros.spec.js` (1) | 'Jugador' para el GM | 1/1 · suite 130 |
| 10 | GestionView con estados/fecha/GM reales (sin "Aldren Valeros") — D-12 | `tests/unit/gestionResumen.spec.js` (1) | 'Aldren Valeros' presente | 1/1 · suite 131 |
| 11 | META-TEST permanente nav↔rutas; limpieza /matchmaking /busqueda /indice — D-13/D-19 | `tests/unit/navConsistencia.spec.js` (4) | 4 specs (incl. `NAV[guest]: Matchmaking -> not-found`) | 4/4 · suite 135 |
| 12 | BE: crear mesa devuelve `gm_nombre` (D-17); FE: `uploadsApi.subir` retirado (D-16) | `tests/test_crear_mesa_gm_nombre.py` | gm_nombre vacío | 18/18 vertical |
| 13 | BE: GET fechas incluye `mi_voto` del votante (D-14) | `tests/test_fechas_mi_voto.py` | KeyError 'mi_voto' | 27/27 (cong. + vertical) |
| 14 | Consola admin real: event-log + DLQ (reintentar/descartar) + emails; guard por rol — F09/D-15 | `tests/unit/adminConsola.spec.js` (5) | vista inexistente + guard | 5/5 · suite 140 |
| 15 | Deuda P2: eslint limpio; `validarMesa` con literal del contrato en GM (guardaba bloqueado) | `tests/unit/estadoCupo.spec.js` (acciones PUT) | PUT no disparado ('Abierta' Rechazada por regla) | 142/142 vgm |

## 4. Cobertura

- Comando: `npm test -- --coverage --coverage.include="…"` sobre el código tocado.
- **Referencias medias del código modificado:** `mesas.js` 93.75% · `MesaGestionShell` 95.81% · gestión `CalendarioView` 90.52% · `MesaDetailJugador` 89.62% · `MesaCalendario` 87.58% · `GestionLayout` 88% · `MesaDetailGm` 79.25% (acciones cubiertas; pendientes de manejo visual).
- **Cobertura global del repo: 38.56%** — deuda pre-existente (vistas legacy sin tests, p. ej. `DiarioEditorView`, `JugadoresView`, `PaginaWikiView`, `WikiEditorView` con 0%). No era el alcance de esta sprint (corrección del rediseño).
- Backend: suite completa `pytest tests/` → **303 passed, 1 skipped** (skips existente de infra del repo).

## 5. Verificación de cierre (Fase 3)

| Puerta | Comando | Resultado |
|---|---|---|
| Suite FE | `npm test` | 24 archivos · **142/142** |
| Lint FE | `npm run lint` | **0 errores, 0 warnings** |
| Build FE | `npm run build` | OK (1.6s) |
| Suite BE | `python -m pytest tests/ -q` | **303 passed, 1 skipped** |
| E2E | `npx playwright test` | **3/3** (login real, feed, mesas) sobre la app servida en `:5173` |
| Entorno | `docker compose up -d` (7 servicios) | todos up, frontend healthy en :5173 |

## 6. Notas, riesgos y hallazgos durante la ejecución

1. **Árbol pre-modificado sin commitear:** el working tree tenía ~40 archivos ya modificados (migración demo→API real) no visibles en el primer `git status` recortado. Un `git checkout` accidental regresó `frontend/src/services/mesas.js` a la versión de HEAD; se recompuso a mano y quedó commiteado en el checkpoint del ciclo 2 (contenido garantizado contra la suite 91/91).
2. **Runner de vitest:** el primer `import()` dinámico evaluado solo desde un hook asíncrono (sin gráfico previo) no resuelve en el runner de tests; los specs "calientan" los módulos de servicios antes de montar (documentado en los helpers del spec).
3. **Contenedor con código viejo:** las imágenes Docker de los servicios y el frontend estaban construidas con código anterior (hash PBKDF2). `docker compose build` + `up` las actualizó; el login e2e volvió a 200.
4. **Cuentas de e2e:** el seed demo fue eliminado por política del repo; la cuenta `gm@tfinder.dev` existía con otra contraseña. Se alineó su hash con la contraseña que el spec e2e usa (DemoTFinder123!) vía el hasher oficial del modelo.
5. **D-20/D-21 documentados:** en modo demo `perfilDe` sigue dejando `id: null` (no afecta modo `api`, usado en producción); el 401 de invitados ya no rompe el detalle de mesa (ciclo 1).
6. **Checkpoint commits:** uno RED y uno GREEN por ciclo (`test(ciclo-N)` / `fix(ciclo-N)`). Ninguno se aplastó; todos en la rama activa.
7. **Fuera de alcance (deuda abierta):** portar F07/F08/F09 desde `tfinder-vue` no es posible (la rama de referencia no existe en este repo); la consola admin se re-implementó sobre lo que notif-api ya expone. Moderación de contenidos, gestión de usuarios y resiliencia configurable siguen sin backend (quedan fuera de `/admin`).

## 7. Auditoría de navegación (post-entrega) y fixes backend

### 7.1 Síntoma reportado por el usuario
"Muchísimos errores al navegar; no entiendo nada": mesas que "desaparecen", listas vacías, notificaciones que llevan a pantallas en blanco.

### 7.2 Causa raíz identificada (reproducida con 4 usuarios reales)
1. **Rate limit compartido por IP del proxy.** `app/middleware/rate_limit.py` usaba `request.client.host` (siempre la IP del contenedor nginx en el despliegue). Todos los usuarios del mismo entorno compartían un único cubo de 100/min → navegando 2-3 pantallas en secuencia (cada una con 8-10 llamadas + 3 del header en `router.afterEach`) saltaba 429. El frontend convertía el 429 en "No encontramos la mesa"/"Silencio: nada sin leer", así que el usuario percibía que su mesa desaparecía.
2. **Enlaces muertos generados por el backend** en notificaciones: `/mesas/demo` (seed viejo) y `/mesas/{id}/gestion/solicitudes` (ruta inexistente; la bandeja vive en `/gestion/jugadores`).
3. **`/builds/nuevo` colisionaba** con `/builds/:id` (frontend, ruta muerta).
4. **Dashboard "Jugador (undefined)"** por usar `m.personaje` inexistente en el normalizador (frontend).
5. **Sesión expirada silenciosa** (frontend redirigía sin banner).

### 7.3 Fixes aplicados (solo backend/datos, sin tocar el frontend)
- `app/middleware/rate_limit.py`: `_cliente_real()` respeta `X-Forwarded-For` (nginx ya lo firma) con fallback a `client.host`; cada cliente real tiene su propio cupo (RNF-22 intacto). La 429 firma `Retry-After`.
- `notif_api/app/consumers/mesa.py`: enlace de la notificación `mesa.solicitada` → `/mesas/{id}/gestion/jugadores` (ruta real).
- `scripts/limpiar_enlaces_notificaciones.py`: sanea enlaces legacy (`/mesas/demo` → `/mesas`; `/gestion/solicitudes` → `/gestion/jugadores`). Ejecutado en dev: 2 remapeos + 1 corrección.
- Tests nuevos: `tests/test_rate_limit_xff.py` (3 specs) + ampliación de `tests/test_contrato_enlace.py` (1 spec). Suite backend completa: **307 passed, 1 skipped**.

### 7.4 Verificación live (post-fix)
- `docker compose build` + `up -d` (apis + frontend) → 9 contenedores healthy.
- Live: 429 aparece recién en la llamada 101 con XFF propio; un cliente B inmediatamente después recibe 200 (cupos separados).
- Playwright E2E: **3/3** (login real, feed, mesas).
- Auditoría de navegación con 4 usuarios (invitado, jugador nuevo, GM, admin): rutas resuelven, sin NotFound/undefined/NaN; la notificación de solicitud ahora lleva a `/mesas/4/gestion/jugadores` (verificado con click real).

### 7.5 Deuda abierta (no tocada por la regla "no cambiar el frontend")
- `/builds/nuevo` → redirigir a `/builds/asistente` (1 línea de FE).
- `http.js` → manejar 429 con mensaje honesto + dedupe de llamadas.
- `LoginView` → banner "Tu sesión venció" cuando viene `?sesion=expirada`.
- `DashboardView` → `m.personaje` undefined + actividad vacía (stubs).
- `MisMesasJugadorView` excluye mesas donde el usuario es master (filtro por rol; UX confuso).
- `BuildsListView` default tab "Públicos" (confunde post-creación).
- `admin@tfinder.dev` no existe por defecto (bootstrap CLI manual).

Estas quedan documentadas para una iteración posterior; el producto funciona de punta a punta con el flujo core (mesas + gestión + calendario + sesiones + wiki + jugadores + builds + notificaciones).
