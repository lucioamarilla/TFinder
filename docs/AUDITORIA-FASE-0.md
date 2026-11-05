# TFinder — FASE 0 · Auditoría integral y plan técnico definitivo

> Al 2026-11-05 · rama `backend-fusion` + frontend anidado `tfinder-vue@ef31c4c`.
> Estado comparable: backend 236 tests / 83% cobertura · frontend 221 tests · stack docker completo up.
> Este documento es el entregable de FASE 0: diagnosis + plan. No contiene implementación.

---

## 1. Estado actual (lo que existe y funciona)

### Backend (4 servicios FastAPI, verificado por suite real)

| Dominio | Estado | Evidencia |
|---|---|---|
| Auth: registro, login, refresh, **logout con revocación de toda la familia** (access+refresh) | ✅ sólido | `test_auth_sesion_familia.py` |
| Mesas CRUD + **gm_id + ownership** (403 no-propietario) + filtros/paginación + `sistema='pf1e'` | ✅ | `test_vertical_mesa.py` |
| Solicitudes de unión: **pendiente → GM acepta/rechaza** + expulsión (libera cupo), cupo atómico en el acepte, `UNIQUE parcial` anti-doble | ✅ | `test_carrera.py`, `test_idempotencia.py` |
| Sesiones: crear/confirmar/cerrar + **QR de asistencia single-use** (solo GM de la mesa) + diario ( асинхр en feed) | ✅ | `test_sesiones_flujo.py`, `test_qr.py` |
| **Calendario con votación**: propuesta del GM, voto editable de miembros, confirmar → nace sesión | ✅ | `test_calendario.py` |
| Builds: CRUD + **historial de versiones + restaurar**, publicar, vincular a mesa (verifica membresía via REST), tags filtrables, atributos 3–18 | ✅ | `test_builds_crud.py` |
| Wiki: CRUD del GM + **visibilidad privada/jugadores/publica** verificada por REST a mesas-api | ✅ | `test_wiki_crud.py` |
| Feed: crear post (con embed p/ build), like único con toggle, follows (sin autofollow) | ✅ | `test_feed_social.py` |
| Notificaciones async (RabbitMQ→SSE+email), event-log, DLQ con replay, /metrics, rate limit 429, envelope unificado | ✅ AE2 | `test_dlq*.py`, `test_infra_operativa.py` |

### Frontend (Vue 3, 221 tests)

| Dominio | Estado |
|---|---|
| Doble modo por ENV: `demo` (simulador local) vs `api` (backends reales) | ✅ infraestructura |
| Auth real: login/register/logout con Bearer, persistencia de tokens, guard guest/auth/admin | ✅ modo api |
| Mesas, bandeja GM de solicitudes, votaciones, sesiones, wiki, feed, notificaciones | ✅ capa de servicios modo api |
| **Builds: vistas 100% demo** (backend READY y testeado, capas no cableadas) | ⚠️ |
| Panel de administración: 10 vistas **100% simuladas** | ⚠️ fuera de alcance real |
| Playwright E2E: **inexistente** | ❌ |
| CSS: 3 sistemas conviviendo (arcade activa + `crono.css`/`harness.css` muertos pero con clases usadas) | ⚠️ deuda |
| Archivos muertos: ~15 identificados (MesaDetailView, LlamadoCard, placeholders, etc.) | ⚠️ |

---

## 2. Problemas identificados (con cita exacta)

### A. Contradicciones con los principios del pliego

| # | Principio violado | Dónde | Detalle |
|---|---|---|---|
| P-01 | **2.1 roles contextuales** | `mesas_api/app/schema.sql:21-22`, `usuarios.rol CHECK ('usuario','gm','admin')` | Hoy el "GM" es un **rol global de la cuenta**, no un dato de membresía. Un usuario no puede ser Master en una mesa y Jugador en otra. El pliego lo exige: un solo tipo de cuenta, roles por mesa. |
| P-02 | **2.1** | `requerir_roles("gm")` en `routes/v1/mesas.py` (crear/confirmar/cerrar sesión, QR validar), `matchmaking.py:abrir` | La autoridad de Master se evalúa por rol global, no por relación usuario↔mesa (`gm_id` de la mesa, usada solo en el CRUD). |
| P-03 | **2.2 membresía** | No existe tabla `miembros_mesa` | La membresía se infería de `solicitudes_uniones.estado='aceptada'` (diseño AE2). No soporta "privilegios correspondientes a integrantes" por mesa. |
| P-04 | **2.3 bitácora** | `views/ModoSesionGmView.vue` | Es un **simulador de combate**: iniciativa d20, PV contador, "Siguiente turno", botón `siguiente()` reordena. Contradice "no debe simular mecánicas". |
| P-05 | **2.3 bitácora** | No existe tabla ni endpoint de **anotaciones** | No hay registro cronológico por sesión con autor y fecha de cada participante. El "diario" es un solo post del GM en el feed. La vista demanda anotaciones (2.3). |
| P-06 | **2.5 no inventar** | `LandingView.vue:31-33` | Stats hardcodeadas "18 mesas / 340+ fichas / 12 comunidades" + `mesasMini` hardcodeado (`:187-191`) y menciones a Golarion. |
| P-07 | **2.5** | `FeedView.vue:15,25,92,99` | Sidebar demo: comunidades `r/…`, texto "TFinder v5, OGL 1.0a Paizo Inc.", "Próxima sesión" (sin datos reales), "Tendencias en Golarion" (sin función). |
| P-08 | **2.5** | `views/admin/*` (10 vistas) | Panel completo simulado con datos JSON falsos. |
| P-09 | **2.5** | `services/demo.js` (seed de dominio completo) | Es el "backend demo" legítimo para modo demo, pero en modo api quedan pantallas que siguen leyendo su store (builds, ficha, admin, perfil). |

### B. Filtraciones de permisos REALES en el backend (2.4) — detectadas y confirmadas

| # | Leak | Dónde | Impacto |
|---|---|---|---|
| L-01 | `GET /mesas/{id}/miembros` con solo `usuario_actual` | `routes/v1/mesas.py:31-32` | Cualquier usuario logueado lista miembros de CUALQUIER mesa (incluso ajenas). |
| L-02 | `GET /mesas/{id}/sesiones` con solo `usuario_actual` | `routes/v1/mesas.py:109-111` | Idem: sesiones ajenas visibles. |
| L-03 | `GET /api/v1/mesas/{id}/fechas` sin chequeo de membresía (`listar_controller` solo 404) | `controllers/fechas_controller.py` | Votaciones/tendencias de mesa ajena accesibles. |
| L-04 | `GET /api/v1/builds/{id}` **público sin auth ni chequeo de visibilidad** | `builds_api routes/v1/builds.py:46-47` | Un build `privado`/`borrador` es legible por ID (el LISTADO sí filtra, el DETALLE no). Viola RN-11/2.4. |
| L-05 | `GET /api/v1/wiki` (listado) devuelve TODAS las páginas, incluidas `privada` | `feed_api/controllers/wiki.py:26-31` | Filtra títulos/contenido privado — el detalle sí respeta visibilidad, el listado NO. |
| L-06 | Fechas/propostas `descartar_controller` exige GM ✓ pero el FE puede igualmente renderizar; listado votaciones filtrado en L-03. | — | modelo de control central ausente. |

### C. Gaps funcionales exigidos por el pliego y ausentes

| # | Requisito del pliego | Estado actual |
|---|---|---|
| G-01 | FASE 3: anotaciones de sesión por cada integrante (autor, fecha-hora, cronológico, historial persistido) | No existe (ni tabla ni endpoints ni UI). |
| G-02 | FASE 3: crear sesión desde el Master de ESA mesa (no rol global) | P-02 / P-03. |
| G-03 | FASE 4: contribuciones de jugadores a la wiki con **estados pendiente/aprobado/rechazado** | No existe; solo el GM escribe. La tabla `wiki_paginas` ya tiene visibilidad, no estados de contribución. |
| G-04 | FASE 5: foro con **adjuntos de imágenes** | **Cero soporte uploads en los 4 servicios** (grep multipart/FormData = 0). Faltan storage + endpoints + límites. |
| G-05 | FASE 5: foro con **builds públicas adjuntas; prohibir privadas — validado en backend** | El campo `embed` existe; NO valida visibilidad → hoy se puede adjuntar una build privada. |
| G-06 | FASE 5: múltiples builds/personajes por usuario | El modelo YA soporta N builds por `autor_id`; el FE (demo) muestra uno solo "mi personaje" — falta vista múltiple + desactivar ficha única. |
| G-07 | FASE 5: perfil con imagen, sin ficha | `FichaPersonajeView.vue` es una ficha global de perfil (pará contra 2.5 y pliego). Backend no tiene edición de perfil ni avatar. |
| G-08 | FASE 1: comunidades con filtrado REAL + prefijo `t/` | Backend filtra por `etiqueta` ✔; FE tiene tab "Comunidades" demo y prefijo `r/`. No hay vistas por comunidad reales. |
| G-09 | FASE 1: header único centralizado; auth pages sin header | `AppHeader` no se usa en Login (usa GuestLayout — que SÍ existe pero está desalineado o muerto según vista); la navegación del FEED duplica items; landing tiene su propio nave­. |
| G-10 | FASE 1: landing dado + scroll progresivo + sin cifras | Dado existe bajo `asciiD20` custom element pero arranca tras un hueco; stats falsas (P-06). |
| G-11 | FASE 2: "expiración de sesiones, cierre correcto, persistencia/renovación" | Refresh existe y logout mata la familia ✓; pero el FE **no renueva proactivamente** (sin auto-refresh en 401) y tokens viven en localStorage documentado diseño a discusión. |
| G-12 | FASE 2: rutas privadas protegidas real | Guard FE por `auth/admin` ✓ pero **no existe noción de membresía por mesa en el guard** — rutas de gestión de mesa se abren para cualquier autenticado (los datos al 403 fallarán, pero se renderiza Shell privados idéntico → UX rota). |
| G-13 | FASE 6: prueba funcional con 6 cuentas | No existe suite E2E (ni Playwright). La prueba funcional de 6 cuentas es nueva infraestructura. |

### D. Deuda saneable pero no bloqueante

- ~15 archivos muertos FE (`MesaDetailView.vue`, `LlamadoCard.vue`, `FeedNewView.vue`, `UsuarioDetailView.vue`, `ModalCambioPassword`, `public/assets/demo-store.js` v1 obsoleto, etc.).
- CSS triple (ver arriba). Botón `demo.reset()` accesible en build productivo.
- `main.py` root ya eliminado ✔. README ya refactorizado ✔.

---

## 3. Funcionalidades existentes (conservar) / modificarse / eliminarse / desarrollarse

| Acción | Ítems |
|---|---|
| **CONSERVAR (no reescribir)** | Auth familia completa; envelope + rate limit + metrics; mesas CRUD con ownership; solicitudes con cupo/carrera; calendario con votación y confirmación—sesión; wiki visibilidad; feed like/follow; notif SSE+DLQ+event-log; builds backend; QR single-use; seed demo (apagable); doble modo FE; suite de tests backend 236 + FE 221. |
| **MODIFICAR** | Modelo de roles → membresías por mesa (P-01..03); sesiones→bitácora con anotaciones (P-04/05, G-01/02); wiki + contribuciones (G-03); builds FE→modo api + visibilidad en detalle/listado (L-04); leaks de lectura (L-01..05); header/guard (G-09/12); comunidades `t/` (G-08); perfil nuevo (G-07); refresh automático FE (G-11); landing/feed limpieza (P-06/07). |
| **ELIMINAR** | Mecánicas de simulación del ModoSesion (iniciativa/PV/turno/d20); `FichaPersonajeView` (global ficha) + su estado demo; datos ficticios: stats landing, tendencias, comunidades seeded en pantallas reales, aparecencias de "OGL/v5" fuera de pie de página; tab "Próxima sesión" sin datos reales. |
| **DESARROLLAR** | Tabla + endpoints de anotaciones; tabla membresías (con migración); tabla contribuciones wiki con estados; sistema de uploads (btn: imágenes de perfil y del foro); vista comunidad real `/comunidad/:tag`; página de builds multi-personaje; guard por membresía/version contexto mesa en FE; suite Funcional 6-cuentas (API) + Playwright UI. |

---

## 4. Propuesta de solución (arquitectura objetivo, sin tocar código aún)

### 4.1 Modelo de datos (diff)

```sql
-- NUEVA: membresía por mesa (principio 2.1/2.2)
CREATE TABLE miembros_mesa (
  mesa_id     INTEGER NOT NULL REFERENCES mesas(id) ON DELETE CASCADE,
  usuario_id  BIGINT  NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  rol         TEXT    NOT NULL DEFAULT 'jugador' CHECK (rol IN ('master','jugador')),
  fecha       TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (mesa_id, usuario_id)
);
-- migración: backfill desde solicitudes.estado='aceptada' + mesas.gm_id → master.

-- NUEVA: anotaciones de bitácora (principio 2.3)
CREATE TABLE anotaciones_sesion (
  id        BIGSERIAL PRIMARY KEY,
  sesion_id INTEGER NOT NULL REFERENCES sesiones(id) ON DELETE CASCADE,
  mesa_id   INTEGER NOT NULL REFERENCES mesas(id)   ON DELETE CASCADE,
  autor_id  BIGINT  NOT NULL REFERENCES usuarios(id),
  texto     TEXT    NOT NULL CHECK (length(trim(texto)) > 0),
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_anotaciones_sesion ON anotaciones_sesion (sesion_id, creado_en);

-- NUEVA: contribuciones a la wiki con estados (FASE 4)
CREATE TABLE wiki_contribuciones (
  id        BIGSERIAL PRIMARY KEY,
  pagina_id INTEGER NOT NULL REFERENCES wiki_paginas(id) ON DELETE CASCADE,
  autor_id  TEXT    NOT NULL,           -- id de usuario (puente inter-DB como hoy)
  cuerpo    JSONB   NOT NULL,
  estado    TEXT    NOT NULL DEFAULT 'pendiente'
            CHECK (estado IN ('pendiente','aprobada','rechazada')),
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- NUEVA: uploads (FASE 5)
CREATE TABLE uploads (
  id         TEXT PRIMARY KEY,           -- uuid
  tipo       TEXT NOT NULL CHECK (tipo IN ('imagen')),
  contenido  TEXT NOT NULL,              -- mime
  tamano     INTEGER NOT NULL,
  owner_id   TEXT NOT NULL,
  ruta       TEXT NOT NULL,
  creado_en  TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS avatar_url TEXT;
```

### 4.2 Autorización objetiva (principio 2.4)

- Nuevo mód compartido `app.infra.permisos` (o por servicio): `rol_en_mesa(usuario, mesa_id) → master|jugador|N` resuelto en mesas-db, junto a dependencias FastAPI:
  - `requerir_miembro(mesa_id)` — lectura de contenido privado.
  - `requerir_master(mesa_id)` — administración de ESA mesa.
- Reemplazo commitments: `requerir_roles("gm")` (sesiones/QR/matchmaking) → `requerir_master` de la mesa implicada.
- Fechas: listado → `requerir_miembro`; `usuario.rol` queda solo para plataforma (`admin`) — nunca más como gate de juego.
- Lecturas que se cierran (L-01..L-05): miembros/sesiones→miembro; fechas→miembro; build detalle→payload de visibilidad o 404 si privado y no dueño/master de mesa vinculada; wiki listado→excluye `privada` salvo master.
- FE: guard de routes + vistas leen contexto "mi rol en esta mesa" vía `GET /mesas/{id}/mi rol` (nuevo endpoint liviano) y ocultan/deshabilitan; el backend SIEMPRE decide.

### 4.3 Bitácora (2.3) — reemplazo objetivo por la vista completa

- Borrar mecánicas del FE (iniciativa/PV/-turno/d20); crear
- Vista "Bitácora de la sesión": timeline orden cronológico, input de anotación para cada integrante y botón "registrar acontecimiento" (autor + fecha-hora automáticas del backend), filtrable por autor; historial persistido por sesión; creación/cierre de sesiones por el Master de la mesa.
- QR mantém como extra opcional del Master (D4).

### 4.4 Frontend — cambios estructurales F1

- Header único: AppHeader centraliza toda la nav autenticada (Mis mesas, Feed, Mesas, Perfil, saltear admin/mock); el FEED pierde su nav propia.
- GuestLayout real para /login /registro /recuperar (sin header autenticado).
- Feed: eliminar "Mis mesas activas", "Tendencias en Golarion", "Próxima sesión"→ estado vacío o datos reales; prefijo `t/`; página de comunidad única `/feed?comunidad=t/<tag>` con filtro backend real + estado vacío diseñado.
- Landing: dado visible desde el carga, scroll acompañado; eliminar cifras/mesasMini (o reemplazar por datos reales si deciden traerse del backend).
- Mesa activa: filters con `<select>` (estado/sistema/tono/orden); link de detalle ya con datos reales.

### 4.5 Pruebas (FASE 6) — el estándar "no es terminado si su interfaz funciona"

- Playwright (nueva devDep): suite 6 cuentas que recorre el checklist de 19 ítems del pliego.
- Suite funcional por API (pytest, determinística) cubriendo los mismos 19 ítems — corre en CI sin navegador.
- Cobertura objetivo ≥80% backend (hoy 83%) y tests de contrato FE↔BE ampliados.

---

## 5. Dependencias entre fases

```
F1 navegación/UX ──┐
                   ├──► F2 usuarios/permisos/membresías ──► F3 mesas+bitácora ──► F4 wiki colaborativa ──► F5 foro/builds/perfil ──► F6 pruebas integrales
(uploads/base) ────┴─────────────────────────────────────► (F5 usa uploads; F4 usa membresías; F6 usa todo)
```

- F2 desbloquea F3/F4/F5 (los permisos real).
- uploads (nuevo) necesario para F4/F5 ―lo introducimos dentro de F5 (foro/perfil) para no adelantar infra sin usos.
- F6 cierra y no puede empezar antes de F5.

---

## 6. Plan técnico de implementación (por fase, incremental)

| Fase | Tareas técnicas (archivos/endpoints) | Criterio de cierre |
|---|---|---|
| **F1** (nav/UX) | header único, GuestLayout en auth, landing (dado+scroll, sin cifras), feed limpieza (sidebar real, `t/`), filtros `<select>` en mesas, estado vacíos diseñados; **sin cambiar backend** (excepto `/metrics` en FE real counts si decidido) | Playwright manual/visual sin links rotos; vitest suite extendida; 0 strings ficticias |
| **F2** (membresías/permisos) | DDL `miembros_mesa` + migración + seed; `rol_en_mesa` + dependencias; reemplazo de gates; cierre de L-01..L-05; endpoint `GET /mesas/{id}/mi-rol`; FE: contexto de rol por mesa + guard bytes + refreshing tokens on 401 | tests: leaks cerrados (403/404), M asters reales, auto-rol al crear mesa; suite contratual ampliada |
| **F3** (mesas/sesión-bitácora) | DDL anotaciones; endpoints `POST/GET /sesiones/{id}/anotaciones` (miembro; autor del token; ts server); quitar mecánicas del ModoSesion y nueva vista Bitácora; crear sesión por master; historial paginado | test: cronológico correcto, autor id/persistencia, permisos; UI bitácora con anotaciones de 2 autores |
| **F4** (wiki colaborativa) | DDL contribuciones + estados; endpoints jugador envía (miembro), master acepta/rechaza; UI estados visibles; backend valida en cada transición | tests: ciclo pendiente→aprobada/rechazada + permisos |
| **F5** (uploads/foro/builds/perfil) | uploads (mime/size whitelist, disco+tabla, borrado lógico), adjuntos en publicaciones (multi-imagen + build ref validated pública); vistas builds modo api multi-personaje; perfil real (avatar+descripción...) | tests: límite mime/size, private-build ref rechazada 400/403 |
| **F6** (integración) | Suite 6 cuentas (API pytest 19 checks) + Playwright UI recorridos críticos | checklist 19/19 verdes |

---

## 7. Decisiones que necesito confirmar antes de cambios irreversibles

| # | Decisión | Recomendación | ¿Por qué importa? |
|---|---|---|---|
| **D1** | ✅ **CONFIRMADA** — Migrar autoridad de "Master" de `usuarios.rol` global → `miembros_mesa.rol` por mesa (removiendo los gates globales) | **Sí** | Confirmada por el usuario el 2026-11-05 |
| **D2** | ✅ **CONFIRMADA** — Rol `master` en BD y UI | sí | Confirmada |
| **D3** | ✅ **CONFIRMADA** — Solo master/jugador (co-GM y observador dejarán un campo extensible) | sí | Confirmada |
| **D4** | ✅ **CONFIRMADA** — QR conservado como panel opcional del Master | sí | Confirmada |
| **D5** | ✅ **CONFIRMADA** — Infra de uploads (tabla + disco, servida por feed-api, avatares en `usuarios.avatar_url`) | sí | Confirmada |
| **D6** | ✅ **CONFIRMADA** — Contribuciones en tabla nueva con estados | sí | Confirmada |
| **D7** | ✅ **CONFIRMADA** — Eliminación definitiva (no ocultar) de ficha global y mecánicas de simulación | sí | Confirmada |
| **D8** | ✅ **CONFIRMADA** — Tokens en localStorage + auto-refresh (sin BFF/cookies) | sí | Confirmada |
| **D9** | ✅ **CONFIRMADA** — Playwright como devDep para F6 | sí | Confirmada |
| **D10** | ✅ **CONFIRMADA** — Panel admin simulado: ocultar en modo api | sí | Confirmada |

---

## 8. Registro de skills ECC (§8 del pliego)

| Skill | Uso previsto | Fase |
|---|---|---|
| `tdd-workflow` | ya aplicada en TODO el MVP previo y continuará: RED→GREEN por cambio con commits checkpoint | todas |
| `click-path-audit` | metodología de rastreo de clicks→estado aplicada en esta auditoría (P-07: "Próxima sesión" → modo sesión, CTA `/builds/nuevo` réparable) | F1, re-run por fase |
| `e2e-testing` | setup Playwright + Page Object Model para la suite de 6 cuentas | F6 |
| `archify` / `architecture-decision-records` | diagramas y ADR-007 (membresías), ADR-008 (uploads), ADR-009 (contribuciones) | F2/F5/F4 |
| `error-handling` | tipos de error y mensajes de permisos centralizados FE/BE | F2 |
| `verification-loop` | gate de verificación (build/typecheck/coverage/diff) al cierre de cada fase | todas |
| `agent-self-evaluation` | evaluación 5 ejes al cierre de cada fase | todas |
| `hallmark` / `browser-qa` (si se usan pantallas nuevas) | diseño de estado vacíos, accesibilidad y QA visual | F1 |

Notas de calidad: ninguna skill garantiza el resultado por sí sola — cada fase cierra con la suite de pruebas corriendo (236→N) y la verificación de cobertura.

---

## 9. Documento de seguimiento (torre de control)

`docs/SEGUIMIENTO-REFACTOR.md` (a crear fuera de modo plan) — fases, tareas completadas/pendientes, archivos modificados, decisiones, problemas, pruebas ejecutadas, resultados; se actualiza al cerrar cada fase y registra las skills usadas.
