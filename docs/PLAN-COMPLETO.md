# PLAN — TFinder: Cierre completo + hardening + UX (TDD)

> Base: rama `backend-fusion` + frontend anidado `frontend/`.
> Runners: backend `venv/bin/pytest -q`; frontend `npx vitest run`; E2E `npx playwright test`.
> Convención: RED (`test: add reproducer for X`) → GREEN (`fix: X`) → REFACTOR (`refactor: clean up after X`), commits solo en rama activa.
> Plan como dato: validar contra el repo antes de ejecutar.

---

## 0. Alcance y reglas

- **No tocar** código de producción hasta tener RED verificado (compilado + ejecutado) para la tarea en curso.
- **Una tarea a la vez**: no mezclar hardening de un módulo con features de otro en el mismo commit.
- **Seguridad en cada módulo**: cada tarea incluye una sub-tarea "Hardening" con controles concretos.
- **Verificación manual** al final de cada etapa: pasos reproducibles en el frontend (modo api).

---

## Etapa A — Hardening transversal (seguridad base) · P0

### A1. Secrets fail-fast
- **Archivos**: `app/infra/token.py`, `mesas_api/main.py`, `notif_api/main.py`, `.env.example`.
- **Cambio**: si `JWT_SECRET` es default y `DEMO_SEED_ENABLED != false`, abortar arranque con error claro; documentar en README.
- **Hardening**: no imprimir el secret; usar `secrets.compare_digest` donde aplique; rotar familia en logout (ya existe, verificar).
- **Tests**: `tests/test_secrets_failfast.py` (RED: arranque con default → RuntimeError; GREEN: con secret válido → ok).
- **Manual FE**: levantar stack con `.env` sin JWT_SECRET → debe fallar con mensaje; con secret → login normal.

### A2. Rate limiting distribuido (Redis)
- **Archivos**: `app/infra/ratelimit.py` (nuevo o existente), `mesas_api/main.py`, etc.
- **Cambio**: migrar contador de memoria a Redis (sliding window por IP) con fallback degradado (CA-51) si Redis cae.
- **Hardening**: clave por IP+ruta; límite 100/min; 429 con envelope; no filtrar internals.
- **Tests**: `tests/test_ratelimit_distribuido.py` (RED: 101 req → 429; GREEN: con Redis caído → sigue sirviendo con X-Cache MISS).
- **Manual FE**: spam de requests en `/mesas` → ver 429 en consola; Redis down → app sigue con warning.

### A3. Política CORS (decisión)
- **Decisión**: mantener proxy same-origin (sin CORS) y documentar; si se abre CORS, whitelist explícita (no `*`).
- **Hardening**: si se implementa, `allow_origins` desde env, `allow_credentials=True` solo con origins explícitos.
- **Tests**: `tests/test_cors.py` (opcional, solo si se abre).
- **Manual FE**: verificar que el frontend sigue funcionando vía proxy.

### A4. Auth: bcrypt + rotación + reuso
- **Decisión**: migrar hash de PBKDF2 a bcrypt (10+ rondas) con migración perezosa de usuarios existentes; además invalidar sesiones al cambiar password; detectar reuso de refresh → revocar familia.
- **Archivos**: `mesas_api/app/models/auth_model.py`, `notif_api` (si valida).
- **Hardening**: no loguear hashes; invalidar sesiones al cambiar password; refresh rotation (ya existe); detectar reuso de refresh → revocar familia.
- **Tests**: `tests/test_auth_bcrypt.py` + `tests/test_refresh_reuse.py`.
- **Manual FE**: registrar usuario nuevo → login ok; usuario demo legacy → login ok; cambiar password → sesiones anteriores mueren.

### A5. Input validation centralizada (ampliado)
- **Archivos**: schemas Pydantic en cada servicio; `app/infra/validacion.py` (nuevo); frontend `src/rules/*`.
- **Cambio**: límites de tamaño en texto (título, cuerpo, anotaciones, bio), sanitización de HTML en wiki/feed (escape), validación de mime/size en uploads (ya parcial), validación frontend (v-model + mensajes).
- **Hardening**: rechazar payloads > N KB (413/400); escapar HTML; validar extensiones; no confiar en frontend.
- **Tests**: `tests/test_validacion_inputs.py` + `frontend/tests/unit/validacionCampos.spec.js`.
- **Manual FE**: intentar post con cuerpo gigante → error claro; wiki con `<script>` → texto plano; upload .exe → 400.

### A6. SSE token por query (en curso)
- **Archivos**: `notif_api/app/middleware/auth.py`, `notif_api/app/routes/v1/notificaciones.py`.
- **Cambio**: completar el diff actual (token por query) y agregar expiración corta / revocación.
- **Hardening**: no loguear token; validar `sesion_valida`; rate limit por conexión.
- **Tests**: `tests/test_sse_auth.py`.
- **Manual FE**: abrir notificaciones → stream conecta; logout → stream se corta.

### A7. Expiración de sesión por inactividad + sliding
- **Archivos**: `app/infra/token.py`, `mesas_api/app/models/auth_model.py`, `frontend/src/composables/useAuth.js`.
- **Cambio**: agregar `last_activity` en Redis por jti; si inactividad > N min, revocar; sliding refresh del access en cada request autenticado (opcional).
- **Hardening**: no extender sesión con tokens robados; revocar familia si se detecta reuso.
- **Tests**: `tests/test_session_expiry.py` (RED: token inactivo 31 min → 401; GREEN: actividad renueva).
- **Manual FE**: dejar pestaña inactiva 31 min → próxima acción pide login.

---

## Etapa B — Cobertura async y transaccionalidad · P1

### B1. Cobertura `stream.py`
- **Archivo**: `notif_api/app/services/stream.py`.
- **Cambio**: tests de connect/disconnect/broadcast/reconnect.
- **Hardening**: no exponer otros usuarios; validar payload.
- **Tests**: `tests/test_stream.py` (target ≥70%).
- **Manual FE**: dos pestañas con usuarios distintos → notif de uno no aparece al otro.

### B2. Cobertura `pdf worker`
- **Archivo**: `notif_api/app/workers/pdf.py`.
- **Cambio**: tests de generación/estado/descarga + DLQ.
- **Hardening**: validar doc_id; no path traversal.
- **Tests**: `tests/test_pdf_worker.py` (target ≥70%).
- **Manual FE**: publicar diario → estado "listo" → descarga PDF.

### B3. Cobertura `email_service`
- **Archivo**: `notif_api/app/services/email_service.py`.
- **Cambio**: tests con MailHog (mock SMTP) + templates.
- **Hardening**: no loguear contenido sensible; timeout.
- **Tests**: `tests/test_email_service.py` (target ≥70%).
- **Manual FE**: MailHog UI muestra email de notificación con template.

### B4. Transaccionalizar `publicar_diario`
- **Archivos**: `feed_api/app/controllers/diario.py`, `feed_api/app/services/eventos.py`.
- **Cambio**: insert + publish en transacción (outbox pattern) o documentar best-effort con retry.
- **Hardening**: idempotency key por (mesa, sesión); no duplicar notificaciones.
- **Tests**: `tests/test_diario_transaccional.py`.
- **Manual FE**: publicar diario dos veces → una sola notificación.

### B5. SSE multi-réplica (opcional)
- **Cambio**: Redis pub/sub para broadcast entre réplicas.
- **Tests**: `tests/test_sse_multireplica.py`.
- **Manual FE**: dos instancias → notif llega a ambas.

### B6. Limpieza cross-DB al borrar mesa
- **Cambio**: evento `mesa.eliminada` consumido por builds/feed/notif.
- **Hardening**: solo el master/admin dispara; idempotente.
- **Tests**: `tests/test_mesa_eliminada.py`.
- **Manual FE**: borrar mesa → builds/feed ya no la referencian.

### B7. Email en producción (SMTP real + templates)
- **Archivos**: `notif_api/app/services/email_service.py`, `.env.example`, `docker-compose.yml`.
- **Cambio**: soportar SMTP real (STARTTLS, auth) vía env; templates HTML/texto para notificaciones; retry con backoff y DLQ si falla.
- **Hardening**: no loguear credenciales; timeout; no exponer internals en 500.
- **Tests**: `tests/test_email_prod.py` (con mock SMTP).
- **Manual FE**: configurar SMTP real → recibir email real; MailHog sigue para dev.

---

## Etapa C — E2E + contract tests · P2

### C1. Playwright: flujos críticos
- **Archivo**: `frontend/e2e/*.spec.js`.
- **Flujos**: registro→login→crear mesa→solicitar→GM acepta→votar fecha→anotación→publicar diario→PDF→perfil.
- **Hardening**: no exponer tokens en screenshots; usar usuarios demo.
- **Tests**: `frontend/e2e/flujo-completo.spec.js`.
- **Manual FE**: ejecutar `npx playwright test` → verde.

### C2. Contract tests FE↔BE
- **Cambio**: validar responses contra OpenAPI exportado.
- **Tests**: `frontend/tests/unit/contract.spec.js`.
- **Manual FE**: cambiar un campo en BE → test falla.

### C3. Coverage gate
- **Cambio**: threshold 80% en módulos de negocio (notif async incluido).
- **Manual FE**: `pytest --cov` + `vitest --coverage` → ≥80%.

---

## Etapa D — Decisiones y documentación · P3

### D1. ADRs (007 membresías, 008 uploads, 009 contribuciones)
- **Archivos**: `docs/adr/ADR-007.md`, etc.
- **Manual FE**: revisar docs.

### D2. Diagramas (archify)
- **Archivos**: `docs/diagramas/*.html`.
- **Manual FE**: abrir en navegador.

### D3. Decisiones del owner (bcrypt, cupo, /solicitar, CORS, QR)
- **Cambio**: documentar en SEGUIMIENTO y README.
- **Manual FE**: n/a.

---

## Etapa E — Plan visual revert · P4

### E1. Ejecutar `tfinder-visual-revert.plan.md`
- **Cambio**: textura de pergamino, Landing/Feed/Mesas visual, filtros pills.
- **Hardening**: no reintroducir cifras fake; CSP limpia.
- **Tests**: visuales (Playwright screenshots) + 0 errores de consola.
- **Manual FE**: comparar con capturas originales.

---

## Etapa F — Funcionalidades de visión (opcional) · P5

### F1. Comentarios en feed
- **Backend**: endpoints `POST/PUT/DELETE /feed/{id}/comentarios`.
- **Hardening**: ownership, rate limit, sanitización.
- **Tests**: `tests/test_comentarios.py`.
- **Manual FE**: comentar post → editar → eliminar.

### F2. Moderación + admin real
- **Backend**: endpoints admin (listar reportados, ocultar/restaurar).
- **Hardening**: rol admin verificado server-side; audit log.
- **Tests**: `tests/test_moderacion.py`.
- **Manual FE**: admin oculta post → no visible.

### F3. Wiki jerárquica + markdown + imágenes
- **Backend**: parent_id, markdown, upload en wiki.
- **Hardening**: validación de tamaño/mime; permisos por visibilidad.
- **Tests**: `tests/test_wiki_jerarquica.py`.
- **Manual FE**: crear página hija, insertar imagen.

### F4. Publicar wiki al feed
- **Backend**: endpoint `POST /mesas/{id}/wiki/{pagina_id}/publicar-feed`.
- **Tests**: `tests/test_wiki_feed.py`.
- **Manual FE**: publicar página → aparece en feed.

### F5. Co-GM / observador
- **Backend**: extender `miembros_mesa.rol` CHECK.
- **Hardening**: permisos por rol; no escalar privilegios.
- **Tests**: `tests/test_roles_extra.py`.
- **Manual FE**: asignar co-GM → ve panel.

---

## Etapa G — UX del header y builds · P6

### G1. Avatar: que la inicial no se desborde
- **Archivos**: `frontend/src/styles/app.css`, `frontend/public/assets/app.css`.
- **Cambio**: `.nav-avatar` → agregar `line-height: 1; font-size: var(--text-sm);` y asegurar `place-items: center`.
- **Hardening**: n/a (solo CSS).
- **Tests**: `frontend/tests/unit/AppHeader.spec.js` (verificar avatar visible con inicial).
- **Manual FE**: login con nombre "Lucio" → avatar muestra "L" centrada dentro del cuadrado.

### G2. Link "Builds" en el header
- **Archivos**: `frontend/src/components/AppHeader.vue`.
- **Cambio**: agregar `<RouterLink to="/builds">Builds</RouterLink>` en el nav (solo autenticados) y en el menú móvil.
- **Hardening**: n/a.
- **Tests**: `frontend/tests/unit/AppHeader.spec.js`.
- **Manual FE**: logueado → header muestra "Builds" → click → `/builds`.

### G3. Acciones de build: wiki + bitácora + foro
- **Archivos**: `frontend/src/views/BuildDetailView.vue`, `frontend/src/views/BuildEditorView.vue`.
- **Cambio**: botones:
  - "Agregar a wiki de la campaña" → `wikiApi.crear` con embed `{ build_id }`.
  - "Poner en mi bitácora" → POST anotación con referencia al build.
  - "Publicar en el foro" (solo si `privacidad === 'publico'`) → `feedApi.crear` con `embed.build_id`.
- **Hardening**: validar permisos (solo dueño o master de mesa vinculada); no exponer builds privados.
- **Tests**: `frontend/tests/unit/buildAcciones.spec.js` + `tests/test_build_feed_endpoints.py` (ya cubre embed privado → 409).
- **Manual FE**: build público → los 3 botones; build privado → solo "Agregar a wiki/bitácora"; publicar en foro → aparece en feed.

### G4. Sacar botón "Compendio" de Bestiario
- **Archivos**: `frontend/src/views/BestiarioView.vue`.
- **Cambio**: eliminar `<RouterLink class="btn btn--secondary" to="/compendio">Compendio</RouterLink>` (ya está en el header).
- **Hardening**: n/a.
- **Tests**: `frontend/tests/unit/BestiarioView.spec.js` (verificar que no hay link a compendio).
- **Manual FE**: `/bestiario` → no hay botón "Compendio"; header sigue teniendo link.

### G5. Publicar en el foro: guía de auth + composer condicional
- **Archivos**: `frontend/src/views/FeedView.vue`, `frontend/src/services/feed.js`.
- **Cambio**: si `!isAuthenticated`, ocultar/deshabilitar el composer y mostrar "Iniciá sesión para publicar"; mostrar error claro si 401.
- **Hardening**: no enviar token en modo demo; validar campos antes de enviar.
- **Tests**: `frontend/tests/unit/FeedView.spec.js`.
- **Manual FE**: sin login → composer oculto + mensaje; con login → publica ok; campos vacíos → error.

---

## Orden de ejecución recomendado (de más fácil a más difícil)

G1 → G4 → G2 → G5 → E1 → D1 → D2 → A3 → A6 → B3 → C2 → A1 → A2 → A4 → A5 → A7 → B1 → B2 → B4 → B6 → B7 → C1 → C3 → (F* opcional) → G3.

Cada tarea cierra con: RED verificado + GREEN verificado + refactor + commit checkpoint + actualización de `docs/SEGUIMIENTO-REFACTOR.md`.
