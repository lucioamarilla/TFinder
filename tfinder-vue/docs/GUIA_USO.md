# Guía de uso · TFinder Frontend (Vue 3)

**Proyecto:** TFinder · **Stack:** Vue 3 + Vite + Tailwind + Vue Router
**Carpeta:** `tfinder-vue/` · **Datos:** mock en `src/data/*.json` consumidos por `src/services/*.js` con latencia simulada (~300–400 ms).

Esta guía recorre todas las pantallas con los **datos reales que ya existen en el repo**, indicando qué hacer y qué resultado esperar. Sirve como prueba manual de humo de punta a punta.

---

## 1. Puesta en marcha

```bash
cd tfinder-vue
npm install          # solo la primera vez
npm run dev          # app disponible en http://localhost:5173
```

Para ver la build de producción:

```bash
npm run build && npm run preview   # http://localhost:4173
```

Para empezar siempre desde cero (limpiar la sesión guardada):

```js
// Consola del navegador
localStorage.clear();
location.reload();
```

---

## 2. Roles de acceso

| Rol | Qué puede ver | Cómo entrar |
| --- | --- | --- |
| `guest` (invitado) | Landing, mesas, login, registro, recuperar | sesión limpia por defecto |
| `auth` (usuario) | Toda la app social + gestión de mesas y builds | iniciar sesión o registrarse |
| `admin` (consola) | Todo lo anterior + `/admin/*` | **solo** forzado por consola (no hay UI) |

El login simulado **siempre** autentica como `auth`:

```js
// /login → usuario semilla
//   Nombre: Aldren Valeros · Iniciales: AV · Título: Aventurero & Cronista
localStorage.setItem('tfinder-rol', 'auth');
location.href = '/dashboard';

// /admin/* → usuario semilla
//   Nombre: Alguacil del Cónclave · Iniciales: AC
localStorage.setItem('tfinder-rol', 'admin');
location.href = '/admin/moderacion';
```

El guard de rutas redirige: invitado a `/login?redirect=...`, usuario común a `/dashboard` si intenta entrar a `/admin/*`.

---

## 3. Recorrido invitado (`guest`)

### 3.1 Landing (`/`)
- CTA "Explorar", "Registrarse" y "Iniciar sesión" en el header y en el hero.

### 3.2 Explorar Mesas (`/mesas`)
Lista **6 mesas** reales:

| id | Mesa | GM | Modalidad |
| --- | --- | --- | --- |
| `la-corona-de-carrona` | La Corona de Carroña | Aldren van Richten | Online |
| `auge-senores-runas` | El Auge de los Señores de las Runas | Kaelen Valeros | Mixta |
| `la-ira-de-los-justos` | La Ira de los Justos | Seelah la Radiante | Online |
| `calaveras-y-grilletes` | Calaveras y Grilletes | Capitán Barnabas | Online |
| `mundo-de-hierro` | Mundo de Hierro (Homebrew) | Grimm Forjarrunas | Presencial |
| `maldicion-trono-carmesi` | Maldición del Trono Carmesí | Lady Cressida | Online |

Qué probar:
- **Búsqueda**: escribí "corona" → queda solo la tarjeta correspondiente.
- **Filtros**: cambiá Sistema / Modalidad / Disponibilidad y pulsá **Aplicar** → el listado filtra. **Limpiar** restaura todo.
- **Ordenar**: select "publicación / plazas / inicio / épico" reordena la grilla.
- **Vacío**: combiná filtros incompatibles (ej. Presencial + documentos) → estado vacío con "Limpiar filtros".

### 3.3 Detalle de mesa (`/mesas/la-corona-de-carrona`)
- Cargá y verifiqué la crónica (lore, GM, sistema, modalidad, frecuencia, cupos).
- **Estados no nominales:** `/mesas/mesa-inexistente` → pantalla *not-found* con enlace de vuelta.

### 3.4 Registro (`/registro`)
- **Validaciones:** email inválido, contraseña corta y contraseñas distintas muestran alertas.
- Enviá un form válido → toast de bienvenida y navega a `/dashboard` como `auth`.

### 3.5 Login (`/login`)
- Email inválido → error. Con cualquier email + contraseña → sesión `auth` y redirección a `/dashboard` (o al `redirect` original).
- **Recuperar contraseña** (`/recuperar`): enviá y verificá el aviso.

### 3.6 Guard de rutas
- Con sesión limpia entrá a `/dashboard` o `/admin/moderacion` → te redirige a `/login?redirect=...`.
- Con sesión `auth`, entrá a `/admin/moderacion` → te redirige a `/dashboard`.

---

## 4. Recorrido usuario (`auth`)

### 4.1 Dashboard (`/dashboard`)
- Widgets: stats cards, actividad reciente, próximos eventos, badge.
- **Mis Mesas** (tarjetas): para mesas GM el enlace va directo a `/mesas/{id}/gestion`.

### 4.2 Mis Mesas (`/mis-mesas`)
**5 membresías** reales:

| Mesa | Rol | Estado | Botón |
| --- | --- | --- | --- |
| La Corona de Carroña | GM | Abierta | **Administrar** → `/gestion` |
| Maldición del Trono Carmesí | GM | En Pausa | **Administrar** → `/gestion` |
| El Auge de los Señores de las Runas | Jugador | Abierta | **Entrar** |
| La Ira de los Justos | Jugador | Abierta | **Entrar** |
| Calaveras y Grilletes | Jugador | Abierta | **Entrar** |

- Probá buscador + filtro de estado (Abierta/En Pausa/Cerrada).
- Crear mesa: `/mesas/nueva` (formulario con validación, latencia y toast; persiste y navega).
- Editar mesa: `/mesas/la-corona-de-carrona/editar`.

### 4.3 Gestión de campaña (pantallas 9x)

Entrá a `/mesas/la-corona-de-carrona/gestion`. El shell (`MesaGestionShell`) muestra 6 tabs que son **sub-rutas** deep-linkables.

| Tab | Ruta | Qué probar |
| --- | --- | --- |
| Resumen | `/gestion` | métricas, acciones de GM, **Disolver mesa** (modal de confirmación) |
| Wiki | `/wiki` | árbol + listado de **14 páginas** en 4 carpetas |
| Calendario & Votación | `/calendario` | votar/desvotar, proponer fecha, confirmar |
| Sesiones | `/sesiones` | listado y acceso al diario por sesión |
| Jugadores | `/jugadores` | miembros + modal **Expulsar** |
| Builds | `/builds` | builds de la mesa + modal **Asociar build** |

**4.3.1 Wiki (9a/9b/9c)** — páginas reales de *La Corona de Carroña*:

| id | Página | Carpeta |
| --- | --- | --- |
| `kendra-lorrimor` | Kendra Lorrimor (Heredera del Códice) | Personajes & NPCs |
| `petros-lorrimor` | Petros Lorrimor (El Profesor Difunto) | Personajes & NPCs |
| `la-via-susurrante` | Culto de la Vía Susurrante | Personajes & NPCs |
| `ravengro` | Ravengro (Aldea de Canterwall) | Lugares & Escenarios |
| `prision-piedra-hendida` | Prisión de Piedra Hendida (Harrowstone) | Lugares & Escenarios |
| `el-juicio-de-la-bestia` | El Juicio de la Bestia (nota de GM) | Notas de Trama & Secretos |

- **Lectura:** `/mesas/la-corona-de-carrona/wiki/kendra-lorrimor` renderiza párrafos, listas y citas.
- **Editor:** `/mesas/la-corona-de-carrona/wiki/kendra-lorrimor/editar` → **Guardar** → toast + navega a la lectura.
- **Nueva página:** `/mesas/la-corona-de-carrona/wiki/nueva` → alta con toast.
- **Eliminar página:** botón en el editor abre `ConfirmModal`.

**4.3.2 Calendario y votación (9d)** — votaciones reales:

| id | Título | Favor / Contra | `miVoto` |
| --- | --- | --- | --- |
| `vot-s30` | Venganza en el Pantano Diabólico | 3 / 0 | favor |
| `vot-s30-alt` | Adelanto de Sesión #30 al viernes | 1 / 0 | — |
| `vot-s31` | El Santuario de la Vía Susurrante | 3 / 0 | contra |

- Pulsá **Votar a favor/contra** → se marca como tu voto y cambia el conteo. Volvé a pulsar para **desvotar**.
- **Proponer fecha** abre el modal date-picker (P24) → la selección se propaga al ancla.
- **Confirmar fecha** aplica el quórum.

**4.3.3 Sesiones y diarios (9e/9f)** — sesiones reales:

| id | Título | Estado |
| --- | --- | --- |
| `corona-s31` | El Santuario de la Vía Susurrante | tentativa |
| `corona-s30` | Venganza en el Pantano Diabólico | borrador |
| `corona-s29` | El Tribunal de la Justicia Ciega | confirmada |
| `corona-s28` | Los Cimientos de Harrowstone | ejecutada |

- **Diario:** `/mesas/la-corona-de-carrona/sesiones/corona-s31/diario` → escribí y **Guardar** → toast "Diario guardado".

**4.3.4 Jugadores y solicitudes (9g)**
- Listado de miembros + contador de ocupación en el tab.
- **Expulsar** abre `ModalExpulsar` (P23) → confirmar → la lista se actualiza y el modal cierra.

**4.3.5 Builds asociados (9h)**
- Builds asociados a la mesa (los de categoría `mio` con `mesaId`).
- **Asociar build** abre `ModalAsociarBuild` (P25) → al aceptar, la asociación se refleja sin recargar.

### 4.4 Builds (Fase 3)

Listado en `/builds` — **8 builds** reales:

| id | Personaje | Clase | Mesa |
| --- | --- | --- | --- |
| `bld-kaelen-valeros` | Valeros | Guerrero | La Corona de Carroña |
| `bld-seelah-radiante` | Seelah | Paladín | La Corona de Carroña |
| `bld-ezren-fox` | Ezren | Mago | La Corona de Carroña |
| `bld-harsk-buscapistas` | Harsk | Explorador | — |
| `bld-merisiel-sombra` | Merisiel | Pícaro | — |
| `bld-kyra-sol` | Kyra | Clérigo | — |
| `bld-damiel-alquimista` | Damiel | Alquimista (comunidad) | — |
| `bld-aldren-augedelrunas` | Kaelen Valeros | Guerrero | El Auge de los Señores de las Runas |

- **Ficha:** `/builds/bld-kaelen-valeros` → navegación bidireccional build ↔ mesa (modal asociar).
- **Asistente:** `/builds/nuevo` (P29) → completá los 6 pasos → "¡Build generada!" → deriva al editor.
- **Editar:** `/builds/bld-kaelen-valeros/editar` → guardar → toast.
- **Historial:** `/builds/bld-kaelen-valeros/historial` (P34) → seleccioná dos versiones y compará en el panel diff; **Restaurar versión** → toast; **Exportar** (.PDF, simulado).

### 4.5 Feed Social (`/feed`)

**9 posts** reales (`post-01`…`post-09`), entre ellos:

| id | Autor | Título |
| --- | --- | --- |
| `post-01` | Valeros_ElTemerario | ¿Es viable un Guerrero con Combate con Dos Armas en la campaña? |
| `post-03` | Cronista_Ravengro | Compendio histórico: Los Cinco Prisioneros Notorios de la Prisión |
| `post-04` | Seelah_Hermana | Diario de Campaña: El asalto a la Prisión de Harrowstone |

- **Ordenar:** Hot / Nuevo / Top.
- **Votar:** flechas up/down cambian el score y marcan tu voto.
- **Guardar:** toggle que marca el post como guardado.
- **Comentar:** desplegá el hilo (comentarios anidados hasta 3 niveles).
- **Copiar enlace:** toast de confirmación.
- **Crear post:** `/feed/nuevo` → **Publicar** → el post aparece en el feed.

### 4.6 Notificaciones (`/notificaciones`)

**8 avisos** reales, **4 sin leer** → el badge de la campana muestra `4`:

| id | Grupo | Sin leer | Enlace |
| --- | --- | --- | --- |
| `n01` | mesas | sí | `/mis-mesas` |
| `n02` | social | sí | `/feed` |
| `n03` | sesiones | sí | `/mis-mesas` |
| `n08` | mesas | sí | `/matchmaking` |
| `n04`–`n07` | variados | no | `/builds`, `/mis-mesas` |

- **Marcar leída** decrementa el badge; **Marcar todas** lo deja en 0; paginación y archivo.

### 4.7 Perfil (`/perfil`, P16 + P26)
- Editar campos y **Guardar** (toast "Formulario de perfil (simulado)").
- **Cambiar contraseña** abre `ModalCambioPassword`; confirmar → toast.

### 4.8 Matchmaking (`/matchmaking`, P27)

**3 candidatos** reales:

| id | Nombre | Rol | Modalidad | Disponibilidad |
| --- | --- | --- | --- | --- |
| `mm-seelah` | Seelah Corazón de Oro | Jugador | Presencial | Fines de semana |
| `mm-ezren` | Ezren de Absalom | Director de Juego | En línea (VTT) | Flexible |
| `mm-harsk` | Harsk el Explorador | Jugador | En línea (VTT) | Entre semana |

- **Aplicar filtros** con los defaults (Jugador + Presencial + Fines de semana) → queda **1 candidato** (Seelah).
- **Llamado abierto** → toast; **Enviar solicitud** → toast por candidato.

### 4.9 Tags y Encuentros
- **Tags** (`/tags`, P36, dados en memoria): creá un tag nuevo → toast ok; tag repetido → toast info; aplicá/quitalo sobre un build → toasts.
- **Encuentros** (`/encuentros`, P35): **Lanzar encuentro** → genera `d20 + CR sugerido + grupo` de monstruos; **Añadir a la próxima sesión** → toast.

### 4.10 Perfil ajeno (`/usuarios/seelah`)
- Render de perfil público de otro usuario desde el servicio (`/usuarios/:id`). Id reales: `seelah`, `ezren`.

---

## 5. Recorrido administrador (`admin`)

Configurá el rol admin (sección 2) para acceder a la consola.

### 5.1 Moderación (`/admin/moderacion`, P19 + P22)
**4 casos** reales:

| id | Autor | Estado |
| --- | --- | --- |
| `caso-412` | Kragor_ElGris | pendiente |
| `caso-411` | MagoOscuro_99 | pendiente |
| `caso-410` | DadosGolarionShop | oculto |
| `caso-409` | CheaterLord_PF | pendiente |

Tabs Pendiente/Oculto/Todos. Probá **Ocultar**, **Eliminar** (modal destructivo de confirmación) y **Restaurar**; paginación.

### 5.2 Usuarios (`/admin/usuarios`, P20)
**6 cuentas** reales:

| id | Nombre | Estado |
| --- | --- | --- |
| `u-seelah` | Seelah Corazón de Oro · Paladín Nvl 6 | activo |
| `u-kragor` | Kragor El Gris · Reincidencia difamación | suspendido |
| `u-kyra` | Kyra Sarenrae · Clériga Nvl 5 | activo |
| `u-dados` | DadosGolarionShop · Cuenta de spam | suspendido |
| `u-ezren` | Ezren el Sabio · Mago Nvl 7 | activo |
| `u-mago` | MagoOscuro_99 · Conjurador Nvl 3 | activo |

Buscador por nombre/handle/email/rol + filtro por estado; **Suspender/Activar** actualiza el estado con toast.

### 5.3 Estadísticas (`/admin/estadisticas`, P21)
- Resumen real: **Total Logs Hoy 4,892 · Nuevas Mesas (7D) 68 · Alertas de IP 0**.
- Dos gráficos de barras (usuarios por semana · mesas por día) + tabla de logs.
- Filtro por rango → **Filtrar logs** y **Exportar CSV** (toast).

### 5.4 Plataforma (`/admin/plataforma`, P28)
- 3 KPIs + 6 **accesos directos de gobierno**:

| Acceso | Ruta |
| --- | --- |
| Trazabilidad de solicitudes | `/admin/trazabilidad` |
| Observabilidad | `/admin/observabilidad` |
| Gestor de DLQ | `/admin/dlq` |
| Resiliencia | `/admin/resiliencia` |
| Comparador as-is / to-be | `/admin/comparador` |
| Prometheus & Grafana | `/admin/prometheus` |

### 5.5 Trazabilidad (`/admin/trazabilidad`, P30)
**2 cadenas completas** Problema → Necesidad → Requisito → HU → CU:

| Cadena | Problema | Necesidad | Requisitos | HUs | CUs |
| --- | --- | --- | --- | --- | --- |
| `TRAZ-001` | `PB-01` Organización dispersa | `NC-01` Centralizar mesas | `RF-01` `RF-02` `RNF-01` | `HU-01` `HU-02` | `CU-01` `CU-02` |
| `TRAZ-002` | `PB-02` Builds sin control de versión | `NC-02` Versionar fichas OGL | `RF-03` `RF-04` `RNF-02` | `HU-03` | `CU-03` |

- Matriz de cobertura Requisito↔HU↔CU + **Registro de trazas** con payload y **Reintentar (DLQ)**.

### 5.6 Observabilidad (`/admin/observabilidad`, P31)
- **3 servicios:** `mesas-api`, `builds-api`, `feed-api` con barra de salud, latencia y uptime.
- **2 últimas alertas** + **6 logs** con correlation ID, entre ellos:

| Servicio | Nivel | Correlation ID |
| --- | --- | --- |
| `builds-api` | WARN/ERROR | `cid-7b1e09aa` |
| `mesas-api` | INFO | `cid-9f2a41c7` |
| `feed-api` | INFO | `cid-3c88d410` |

- **Activar seguimiento** (auto-refresco) y **Abrir dashboards** → navega a `/admin/prometheus`.

### 5.7 DLQ (`/admin/dlq`, P32)
**3 mensajes** reales:

| id | Cola |
| --- | --- |
| `dlq-1` | builds-notif |
| `dlq-2` | mesas-sync |
| `dlq-3` | notif-outbox |

- **Reintentar** elimina el mensaje de la cola (toast ok), **Descartar** lo quita, **Inspeccionar** expande el payload, **Drenar cola** vacía la tabla.

### 5.8 Resiliencia (`/admin/resiliencia`, P33)
Valores por defecto y rangos:

| id | Concepto | Default |
| --- | --- | --- |
| `cb-umbral` | Umbral de fallos del breaker | 5 |
| `retries-max` | Reintentos máximos | 3 |
| `timeout-cola` | Timeout de cola (seg) | 5 |
| `ventana-observacion` | Ventana de observación (min) | 60 |

- Editá un valor **fuera de rango** → error de validación; dentro → **Guardar** (toast ok).
- **Simular caída** → el breaker pasa de `CERRADO` a `ABIERTO`; **Restaurar valores** vuelve al estado guardado.

### 5.9 Comparador (`/admin/comparador`, P37)
- Tabla **4 capacidades** lado a lado (estado actual · monolito vs. destino · microservicios) + orden de migración recomendada (empezando por `notif-api`).
- **Ver plan de migración** → navega a `/admin/prometheus`; **Exportar informe** → toast.

### 5.10 Prometheus & Grafana (`/admin/prometheus`, P38)
- Consulta por defecto real: `rate(mesas_requests_total[5m])`.
- **3 paneles:** CPU · builds-api, Memoria · mesas-api, Latencia · notif-api.
- Escribí otra consulta → **Consultar** (vacía → error); **Agregar al dashboard** y **Silenciar alerta** (toasts).

---

## 6. Estados no nominales (resumen)

| Estado | Cómo generarlo | Qué esperar |
| --- | --- | --- |
| Carga | recargar cualquier lista (F5) | skeleton/spinner con `role="status"` |
| Vacío | filtros sin coincidencia · DLQ drenada · cola de notificaciones sin avisos | `EmptyState` o fila vacía |
| Error | DevTools → Network → Offline y pulsar **Reintentar** | `ErrorState` con botón Reintentar |
| No encontrado | `/mesas/mesa-inexistente`, `/builds/bld-x`, `/usuarios/x` | vista not-found con volver |
| Guard de roles | invitado a `/dashboard` · `auth` a `/admin/*` | redirección a `/login` o `/dashboard` |

---

## 7. Mapa completo de rutas → vistas

Fuente: `tfinder-vue/src/router/index.js` (44 rutas declaradas + `not-found`).

### Públicas (invitado)

| Ruta | Nombre | Vista |
| --- | --- | --- |
| `/` | landing | `LandingView` |
| `/mesas` | mesas | `MesasListView` |
| `/mesas/:id` | mesa-detalle | `MesaDetailView` |
| `/registro` | registro | `RegistroView` |
| `/login` | login | `LoginView` |
| `/recuperar` | recuperar | `RecuperarView` |

### Usuario autenticado

| Ruta | Nombre | Vista |
| --- | --- | --- |
| `/dashboard` | dashboard | `DashboardView` |
| `/mis-mesas` | mis-mesas | `MisMesasView` |
| `/mesas/nueva` | mesa-nueva | `MesaFormularioView` |
| `/mesas/:id/editar` | mesa-editar | `MesaFormularioView` |
| `/mesas/:id/gestion` | mesa-gestion | `GestionView` |
| `/mesas/:id/wiki` | mesa-wiki | `WikiView` |
| `/mesas/:id/wiki/nueva` | mesa-wiki-nueva | `WikiEditorView` |
| `/mesas/:id/wiki/:paginaId` | mesa-wiki-pagina | `PaginaWikiView` |
| `/mesas/:id/wiki/:paginaId/editar` | mesa-wiki-editar | `WikiEditorView` |
| `/mesas/:id/calendario` | mesa-calendario | `CalendarioView` |
| `/mesas/:id/sesiones` | mesa-sesiones | `SesionesView` |
| `/mesas/:id/sesiones/:sesionId/diario` | mesa-diario-editar | `DiarioEditorView` |
| `/mesas/:id/jugadores` | mesa-jugadores | `JugadoresView` |
| `/mesas/:id/builds` | mesa-builds | `BuildsView` |
| `/builds` | builds | `BuildsListView` |
| `/builds/nuevo` | build-nuevo | `BuildWizardView` |
| `/builds/:id` | build-detalle | `BuildDetailView` |
| `/builds/:id/editar` | build-editar | `BuildEditorView` |
| `/builds/:id/historial` | build-historial | `BuildHistorialView` |
| `/feed` | feed | `FeedView` |
| `/feed/nuevo` | feed-nuevo | `FeedNewView` |
| `/perfil` | perfil | `PerfilView` |
| `/usuarios/:id` | usuario-detalle | `UsuarioDetailView` |
| `/notificaciones` | notificaciones | `NotificacionesView` |
| `/matchmaking` | matchmaking | `MatchmakingView` |
| `/encuentros` | encuentros | `EncuentrosView` |
| `/tags` | tags | `TagsView` |

### Consola de administración (solo admin)

| Ruta | Nombre | Vista |
| --- | --- | --- |
| `/admin/moderacion` | admin-moderacion | `AdminModeracionView` |
| `/admin/usuarios` | admin-usuarios | `AdminUsuariosView` |
| `/admin/estadisticas` | admin-estadisticas | `AdminEstadisticasView` |
| `/admin/plataforma` | admin-plataforma | `AdminPlataformaView` |
| `/admin/trazabilidad` | admin-trazabilidad | `AdminTrazabilidadView` |
| `/admin/observabilidad` | admin-observabilidad | `AdminObservabilidadView` |
| `/admin/dlq` | admin-dlq | `AdminDlqView` |
| `/admin/resiliencia` | admin-resiliencia | `AdminResilienciaView` |
| `/admin/comparador` | admin-comparador | `AdminComparadorView` |
| `/admin/prometheus` | admin-prometheus | `AdminPrometheusView` |

### Catch-all

| Ruta | Nombre | Vista |
| --- | --- | --- |
| `/:pathMatch(.*)*` | not-found | `NotFoundView` |

---

## 8. Correspondencia con el prototipo

| Prototipo (`tfinder-prototipo-nuevo/`) | Vista Vue |
| --- | --- |
| `pantalla_2_listado_de_mesas_explorar` | `MesasListView` |
| `pantalla_9_detalle_de_mesa_gesti_n_gm` · `9a`/`9b`/`9c` (wiki) | `GestionView` · `WikiView`/`PaginaWikiView`/`WikiEditorView` |
| `9d` calendario y votación · `9e`/`9f` sesiones y diarios | `CalendarioView` · `SesionesView`/`DiarioEditorView` |
| `9g` jugadores y solicitudes · `9h` builds asociados | `JugadoresView` · `BuildsView` |
| `pantalla_11_alta_y_gestion_de_builds`…`13` | `BuildsListView`/`BuildDetailView`/`BuildEditorView` |
| `pantalla_14` (feed) · `15` (nuevo post) | `FeedView` · `FeedNewView` |
| `pantalla_16` perfil · `17` perfil público · `18` notificaciones | `PerfilView` · `UsuarioDetailView` · `NotificacionesView` |
| `pantalla_19`…`21` (admin: moderación/usuarios/estadísticas) | `Admin*View` |
| `pantalla_22` (confirmación) · `23` (expulsar) · `24` (date-picker) · `25` (asociar) · `26` (password) | `ConfirmModal` · `ModalExpulsar` · `ModalDatePicker` · `ModalAsociarBuild` · `ModalCambioPassword` |
| `pantalla_27` matchmaking | `MatchmakingView` |
| `pantalla_28` plataforma · `30` trazabilidad · `31` observabilidad | `AdminPlataformaView` · `AdminTrazabilidadView` · `AdminObservabilidadView` |
| `pantalla_32` DLQ · `33` resiliencia · `37` comparador · `38` prometheus | `AdminDlqView` · `AdminResilienciaView` · `AdminComparadorView` · `AdminPrometheusView` |
| `pantalla_34` historial · `35` encuentros · `36` tags | `BuildHistorialView` · `EncuentrosView` · `TagsView` |