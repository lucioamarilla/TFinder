# Guía de demostración — Qué hay que mostrar y en qué orden

> **Objetivo de este documento:** ser la única fuente que necesitas para levantar TFinder, desbloquear **todas** sus pantallas y recorrer **todas** sus funcionalidades dejando evidencia verificable de cada una.
>
> **Audiencia:** docente, jurado o cualquier persona que quiera ver el sistema funcionando sin leer código.
>
> **Versión documentada:** AE2 · `mesas-api` v0.5.0 · `builds-api` v0.4.0 · `feed-api` v0.3.0 · `notif-api` v0.6.0

---

## Índice

| # | Sección | Qué resuelve |
|---|---|---|
| 1 | [Resumen del alcance](#1-resumen-del-alcance) | Cuántas pantallas y endpoints existen |
| 2 | [Mapa de funcionalidades](#2-mapa-de-funcionalidades) | Qué está activo y qué está bloqueado |
| 3 | [Prerrequisitos](#3-prerrequisitos) | Qué necesitas instalado |
| 4 | [Fase 0 — Levantar el stack](#4-fase-0--levantar-el-stack) | Poner todo en pie |
| 5 | [Fase 1 — Habilitar las 13 flags bloqueadas](#5-fase-1--habilitar-las-13-flags-bloqueadas) | Ver el 100% de las pantallas |
| 6 | [Fase 2 — Datos y credenciales](#6-fase-2--datos-y-credenciales) | Con qué cuentas entrar |
| 7 | [Fase 3 — Recorrido por rol](#7-fase-3--recorrido-por-rol) | El guion de la demo, paso a paso |
| 8 | [Fase 4 — Evidencia de backend e infraestructura](#8-fase-4--evidencia-de-backend-e-infraestructura) | Cómo probar lo que no se ve en pantalla |
| 9 | [Límites de la demostración](#9-límites-de-la-demostración) | Qué **no** se puede probar (léelo antes de presentar) |
| 10 | [Checklist de verificación](#10-checklist-de-verificación) | Criterio de aceptación |

---

## 1. Resumen del alcance

TFinder es un sistema distribuido para gestionar campañas de rol. Se compone de:

| Capa | Cantidad | Detalle |
|---|---|---|
| APIs | 4 servicios FastAPI | `mesas-api` (8001), `builds-api` (8002), `feed-api` (8003), `notif-api` (8004) |
| Endpoints REST | 46 rutas | 18 + 7 + 6 + 15 respectivamente |
| Infraestructura | 4 servicios | PostgreSQL 16, Redis 7, RabbitMQ 3.13, MailHog |
| Pantallas Vue | 51 vistas | 4 bases de datos, una por servicio (ADR-006) |
| Rutas de navegación | 44 | En `tfinder-vue/src/router/index.js` |
| Flags de funcionalidad | 20 | En `tfinder-vue/src/config/features.js` |
| Pruebas automatizadas | 88 backend + 3 suites frontend | `pytest` + `vitest` |

**El dato central de esta guía:** de las 51 pantallas compiladas, **solo 7 funcionalidades están habilitadas por defecto**. Las otras 13 flags están en `available: false`, y el guard de rutas redirige a `/proximamente/:feature` incluso si se escribe la URL a mano. Ver [sección 2](#2-mapa-de-funcionalidades).

---

## 2. Mapa de funcionalidades

### 2.1 Las 20 feature flags

Archivo: `tfinder-vue/src/config/features.js`

| Flag | Etiqueta visible | Estado | Rutas que desbloquea |
|---|---|:---:|---|
| `crearMesa` | Crear mesa | ✅ activo | `/mesas/nueva` |
| `editarMesa` | Editar mesa | ✅ activo | `/mesas/:id/editar` |
| `qr` | Asistencia por QR | ✅ activo | `/mesas/:id/sesiones/:sesionId/qr` |
| `notificaciones` | Notificaciones | ✅ activo | `/notificaciones` |
| `matchmaking` | Matchmaking | ✅ activo | `/matchmaking` |
| `encuentros` | Encuentros | ✅ activo | `/encuentros` |
| `recuperacion` | Recuperación de contraseña | ✅ activo | `/recuperar` |
| `dashboard` | Dashboard | ❌ bloqueado | `/dashboard` |
| `perfil` | Perfil extendido | ❌ bloqueado | `/perfil` |
| `misMesas` | Mis campañas | ❌ bloqueado | `/mis-mesas` |
| `gestionMesa` | Gestión de campaña | ❌ bloqueado | `/mesas/:id/gestion` |
| `wiki` | Wiki de campaña | ❌ bloqueado | `/mesas/:id/wiki`, `/wiki/nueva`, `/wiki/:paginaId`, `/wiki/:paginaId/editar` |
| `calendario` | Calendario y votación | ❌ bloqueado | `/mesas/:id/calendario` |
| `sesiones` | Sesiones y diario | ❌ bloqueado | `/mesas/:id/sesiones`, `/mesiones/:sesionId/diario` |
| `jugadores` | Gestión de jugadores | ❌ bloqueado | `/mesas/:id/jugadores` |
| `builds` | Builds | ❌ bloqueado | `/builds`, `/builds/nuevo`, `/builds/:id`, `/builds/:id/editar`, `/builds/:id/historial`, `/mesas/:id/builds` |
| `feed` | Feed Social | ❌ bloqueado | `/feed`, `/feed/nuevo` |
| `directorio` | Directorio de aventureros | ❌ bloqueado | `/usuarios/:id` |
| `tags` | Tags | ❌ bloqueado | `/tags` |
| `admin` | Administración | ❌ bloqueado | Las 10 rutas `/admin/*` |

**Resumen: 7 activas, 13 bloqueadas.**

### 2.2 Cómo funciona el bloqueo

`tfinder-vue/src/router/guard.js:3` decide en cada navegación:

```js
export function resolveGuard(to, role) {
  const feature = to.meta.feature
  if (feature && !isFeatureEnabled(feature)) {
    return { name: 'proximamente', params: { feature } }   // ← bloqueo
  }
  const need = to.meta.roles
  ...
}
```

Son **dos capas de bloqueo independientes**:

1. **La flag** (`meta.feature`) → redirige a la pantalla "Próximamente".
2. **El rol** (`meta.roles`) → redirige a `/login` o a `/mesas`.

Consecuencia práctica: **escribir la URL a mano no esquiva el bloqueo.** Hay dos excepciones que conviene conocer antes de la demo:

- **`qr` está activo pero es inalcanzable por navegación.** Su ruta es `/mesas/:id/sesiones/:sesionId/qr`, y la pantalla `/mesas/:id/sesiones` está apagada porque depende de `sesiones`. Hay que entrar por URL directa con un `sesionId` real. Ver [Fase 3.3](#73-flujo-qr--asistencia).
- **`/proximamente/:feature` nunca está bloqueada** (no lleva `meta.feature`). Cualquier URL de feature apagada termina ahí, y esa pantalla sí muestra el nombre de la funcionalidad.

### 2.3 Menú de navegación

`tfinder-vue/src/config/nav.js` oculta los ítems del menú que apuntan a flags apagadas. Por eso, **con las flags como vienen, el menú autenticado solo muestra "Explorar" y "Encuentros"** de 6 entradas. Al habilitar las flags de la [Fase 1](#5-fase-1--habilitar-las-13-flags-bloqueadas), los 6 ítems aparecen automáticamente. No hay que tocar `nav.js`.

---

## 3. Prerrequisitos

| Requisito | Versión | Para qué |
|---|---|---|
| Docker Engine + Compose v2 | reciente | Forma recomendada de correr todo |
| Node.js + npm | 20+ | Solo si el frontend corre fuera de Docker |
| Puertos libres | ver tabla | Sin conflictos |

### Puertos que se ocupan

| Puerto | Servicio | Nota |
|---:|---|---|
| 5173 | Frontend (Nginx) | |
| 8001 / 8002 / 8003 / 8004 | Las 4 APIs | Internamente todas corren en 8001; Docker publica cada una en su puerto |
| 5432 | PostgreSQL | |
| 6390 | Redis | **6390, no 6379** — evita chocar con un Redis local |
| 5673 | RabbitMQ (AMQP) | **5673, no 5672** |
| 15673 | RabbitMQ (panel web) | usuario `tfinder` / `tfinder` |
| 1025 | SMTP (MailHog) | |
| 8025 | MailHog (bandeja web) | |

---

## 4. Fase 0 — Levantar el stack

### Paso 0.1 — Configurar el entorno

```bash
cd TFinder
cp .env.example .env
```

Verificá que en `.env` estén estas dos líneas (son las que habilitan los datos de demostración):

```bash
DEMO_SEED_ENABLED=true
DEMO_SEED_PASSWORD=DemoTFinder123!
```

### Paso 0.2 — Levantar

```bash
docker compose up -d --build
```

La primera vez tarda varios minutos (instala dependencias Python y construye el frontend).

### Paso 0.3 — Confirmar que todo está sano

```bash
docker compose ps
```

**Criterio:** los 8 servicios (4 infra + 4 APIs + frontend) deben figurar como `healthy` o `running`. Si algún servicio de infraestructura está `unhealthy`, esperá y volvé a consultar; las APIs arrancan después que Postgres, Redis y RabbitMQ.

```bash
docker compose logs -f mesas-api    # para ver el arranque si algo falla
```

### Paso 0.4 — Verificar las 4 APIs

```bash
for p in 8001 8002 8003 8004; do
  echo "--- $p ---"
  curl -s http://localhost:$p/ready
  echo
done
```

Cada una debe devolver `200` con `"estado":"listo"`. Si devuelve `503`, el cuerpo explica qué dependencia falta (`degradado`).

### Paso 0.5 — Abrir las 4 documentaciones interactivas

| Servicio | URL |
|---|---|
| mesas-api | http://localhost:8001/docs |
| builds-api | http://localhost:8002/docs |
| feed-api | http://localhost:8003/docs |
| notif-api | http://localhost:8004/docs |

Dejá las cuatro pestañas abiertas: son la evidencia de los 46 endpoints y permiten ejecutar los `curl` de la [Fase 4](#8-fase-4--evidencia-de-backend-e-infraestructura) desde la propia interfaz.

### Paso 0.6 — Abrir la aplicación

http://localhost:5173

Deberías ver la landing pública. Todavía no inicies sesión: primero hay que habilitar las flags.

---

## 5. Fase 1 — Habilitar las 13 flags bloqueadas

Las pantallas existen, están compiladas y son navegables. Lo único que falta es el interruptor.

### Paso 1.1 — Editar el archivo

Abrí `tfinder-vue/src/config/features.js` y cambiá `available: false` → `available: true` en estas **13 líneas**:

| Línea | Flag | Valor actual | Valor nuevo |
|---:|---|---|---|
| 2 | `dashboard` | `false` | `true` |
| 3 | `perfil` | `false` | `true` |
| 6 | `misMesas` | `false` | `true` |
| 7 | `gestionMesa` | `false` | `true` |
| 8 | `wiki` | `false` | `true` |
| 9 | `calendario` | `false` | `true` |
| 10 | `sesiones` | `false` | `true` |
| 12 | `jugadores` | `false` | `true` |
| 13 | `builds` | `false` | `true` |
| 14 | `feed` | `false` | `true` |
| 15 | `directorio` | `false` | `true` |
| 19 | `tags` | `false` | `true` |
| 21 | `admin` | `false` | `true` |

### Paso 1.2 — Verificación rápida

Con Docker, el frontend se reconstruye:

```bash
docker compose up -d --build frontend
```

Sin Docker, en modo desarrollo:

```bash
cd tfinder-vue
npm ci
npm run dev
```

### Paso 1.3 — Comprobación automática

```bash
cd tfinder-vue
npm run test:unit
```

> ⚠️ **Advertencia importante:** el test `tests/unit/feature-gating.spec.js` **falla de forma esperada** después de este cambio. Su primer caso afirma que `builds` debe estar deshabilitada:
>
> ```js
> expect(resolveGuard({ meta: { roles: ['auth'], feature: 'builds' } }, 'auth'))
>   .toEqual({ name: 'proximamente', params: { feature: 'builds' } })
> ```
>
> Ese test valida el gating **con la configuración de entrega**, no con la de demo. Tenés dos opciones:
>
> - **Opción A (recomendada para presentar):** corré solo los specs que no dependen del gating — `npm run test:unit -- --exclude '**/feature-gating.spec.js'`.
> - **Opción B:** comentá ese caso durante la demo y volvé a restaurarlo después.
>
> `tests/unit/inventory.spec.js` **no** se ve afectado: solo comprueba que los módulos sean importables, no cuántas flags hay.

### Paso 1.4 — Cómo revertir

Volver los 13 valores a `false`. Es el estado en que el sistema debe entregarse.

---

## 6. Fase 2 — Datos y credenciales

Con `DEMO_SEED_ENABLED=true`, cada servicio siembra datos **idempotentes** al arrancar (si ya existen, no los duplica).

### 6.1 Cuentas

Contraseña para **todas**: `DemoTFinder123!`

| Email | Rol | Uso en la demo |
|---|---|---|
| `admin@tfinder.dev` | `admin` | Abre las 10 pantallas de administración |
| `gm@tfinder.dev` | `gm` | Mesa master:QR de asistencia, matchmaking |
| `jugador1@tfinder.dev` | `usuario` | Vista de jugador: notificaciones, validar QR |
| `jugador2@tfinder.dev` | `usuario` | Segundo jugador |
| `jugador3@tfinder.dev` | `usuario` | Tercero — completa la mesa "Casi Llena" |
| `email_svc@tfinder.dev` | `usuario` | Cuenta de servicio, no usar en la demo |

> **Cómo se traduce el rol en el router:** `useAuth.js` mapea `admin` → `'admin'` y cualquier otro rol logueado → `'auth'`. Un usuario `gm` **no** es admin: no puede ver `/admin/*`.

### 6.2 Mesas sembradas

| Mesa | Sistema | Estado | Ocupación | Para qué sirve |
|---|---|---|:---:|---|
| Mesa Demo Abierta | PF1e | abierta | 2 / 4 | El flujo normal: explorarla, unirse, ver vacantes |
| Mesa Demo Casi Llena | PF1e | abierta | 3 / 4 | **Una sola vacante** — la prueba de concurrencia |
| Mesa Demo Cerrada | D&D 5e | cerrada | 0 / 6 | Ver que el sistema rechaza unirse |

Además: 2 sesiones (una en *Abierta*, una en *Cerrada*), 5 membresías aceptadas, 1 solicitud pendiente y 1 matchmaking abierto.

### 6.3 Datos que son solo de demostración visual

Estos datasets viven en `tfinder-vue/src/data/` y alimentan las pantallas con latencia simulada de 280–400 ms. **No provienen del backend** (ver [sección 9](#9-límites-de-la-demostración)): actividad, admin (10 archivos), builds, eventos, feed, jugadores, matchmaking, membresias, notificaciones, sesiones, usuarios, votaciones, wiki.

---

## 7. Fase 3 — Recorrido por rol

> **Sugerencia de dinámica:** el recorrido completo se puede hacer con una sola pestaña, pero el flujo de notificaciones rinde mucho mejor con **dos perfiles de navegador separados** (uno que actúa y otro que observa la notificación llegar en vivo). El flujo de QR, en cambio, lo hace íntegramente una sola cuenta `gm@`.

Abrí DevTools → pestaña **Network** en el navegador. Cada fila de la tabla indica la URL a abrir y la llamada de red que debe aparecer.

### 7.1 Bloque A — Visitante (sin sesión)

Sesioná que **no** haya iniciado sesión en el navegador.

| # | URL | Qué se ve | Llamada de red esperada |
|---|---|---|---|
| 1 | `/` | Landing pública | — |
| 2 | `/mesas` | Listado de las 3 mesas demo, con plazas y estado | `GET /mesas-api/api/v1/mesas` |
| 3 | `/mesas/1` | Detalle de *Mesa Demo Abierta* | `GET /mesas-api/api/v1/mesas/1` |
| 4 | `/mesas/2` | Detalle de *Mesa Demo Casi Llena* — nótese "1 vacante" | `GET /mesas-api/api/v1/mesas/2` |
| 5 | `/registro` | Formulario de registro | — |
| 6 | `/recuperar` | Recuperación de contraseña (flag `recuperacion`, activa) | `POST /notif-api/api/v1/auth/recuperar` |

**Punto de demo:** en `/mesas`, la primera carga pega a Redis (TTL 60 s). Recargá dentro de los 60 s y observá que responde más rápido — es la caché de `cache:mesas:list`. Se renueva con cada escritura de mesa.

### 7.2 Bloque B — Aventurero (cuenta `gm@`)

Iniciá sesión con `gm@tfinder.dev` / `DemoTFinder123!`.

#### 7.2.1 Crear y editar una mesa

| # | URL | Qué se ve | Llamada de red |
|---|---|---|---|
| 7 | `/mesas/nueva` | Formulario de creación | — |
| 8 | *(enviar el formulario)* | La mesa aparece en el listado | `POST /mesas-api/api/v1/mesas` → `201` |
| 9 | `/mesas/{id}/editar` | Formulario precargado (flag `editarMesa`) | `GET /mesas-api/api/v1/mesas/{id}` |
| 10 | *(guardar cambios)* | Actualización parcial | `PUT /mesas-api/api/v1/mesas/{id}` → `200` |
| 11 | *(eliminar)* | Confirmación | `DELETE /mesas-api/api/v1/mesas/{id}` → `204` |

Al crear o borrar una mesa, la caché de Redis se invalida automáticamente. Eso es lo que hace que el paso 3 de la demo nunca muestre datos viejos.

#### 7.2.2 Unirse a una mesa

La ruta real es `POST /api/v1/mesas/{id}/solicitudes` (**plural**, con header `Idempotency-Key`). La singular `/solicitar` es legacy y no reserva cupo — ver la [sección 9.2](#92-coupling-del-qr-el-emisor-y-el-asistente-deben-ser-el-mismo).

| # | URL | Qué se ve | Llamada de red |
|---|---|---|---|
| 12 | `/mesas/2` | *Casi Llena* muestra la última vacante | `GET /mesas-api/api/v1/mesas/2` |
| 13 | *(botón de unirse)* | Se incorpora a la mesa | `POST /mesas-api/api/v1/mesas/2/solicitudes` → `201` |
| 14 | *(repetir el paso 13 con la misma mesa)* | "Cupo agotado: no quedan vacantes" | `POST .../solicitudes` → `409` |
| 15 | `/mesas/3` | Mesa cerrada: el botón está bloqueado | — |

**Punto de demo — doble barrera (ADR-004).** Unirse no es un simple `UPDATE`. Son dos barreras, y **cada una produce un `409` distinto** — eso es lo que hace la doble barrera:

1. **Barrera 1 — Redis:** `SET reserva:vacante:{mesa_id} NX EX 60`. Si otra petición tiene la reserva tomada, se corta acá con:
   `409` → *"Otra solicitud se está procesando para esta mesa, reintentá"* (`SolicitudEnProcesoError`)
2. **Barrera 2 — Postgres:** `UPDATE mesas SET jugadores_actuales = jugadores_actuales + 1 WHERE id = %s AND jugadores_actuales < jugadores_max RETURNING id`. La condición va **dentro del `WHERE`**, así que es atómica a nivel de fila. Si no hay fila devuelta:
   `409` → *"Cupo agotado: no quedan vacantes"* (`CupoAgotadoError`)

Las dos excepciones se registran con el mismo manejador (`manejar_conflicto`) en `mesas_api/main.py:56-57`, por eso ambas dan `409` pero con mensajes que te dicen **en qué barrera cortó**.

La reserva de Redis se libera en un `finally` (`vacante.py:13`), así que una petición que muera a mitad de camino no deja la mesa bloqueada: la clave expira sola a los 60 s.

Para ver la concurrencia de verdad se necesitarían 10 solicitudes simultáneas (resultado: 1×`201` + 9×`409`). Está documentado en `AE2/evidencias/` y en `docs/testing/tutorial-pruebas.md`.

**Punto de demo — idempotencia.** El header `Idempotency-Key` se guarda en `idem:solicitud:{key}` con TTL 86400 s. Repetir la misma solicitud con la misma clave devuelve la misma respuesta sin crear un segundo vínculo.

#### 7.2.3 Matchmaking

| # | URL | Qué se ve | Llamada de red |
|---|---|---|---|
| 16 | `/matchmaking` | Pantalla de busca (flag `matchmaking`, activa) | — |
| 17 | *(abrir la mesa 2 como `gm`)* | Se crea/reabre el matchmaking | `POST /matchmaking/2/abrir` → `200` |
| 18 | *(consultar estado desde otra pestaña)* | `abierto` + `ttl_restante` | `GET /matchmaking/{mm_id}/estado` |

El TTL de la llamada es de **120 s** en `llamado:{matchmaking_id}`. Pasados los 120 s, el estado vuelve a `cerrado` solo. Vale la pena mostrarlo: es una decisión de diseño (ADR-002) para no dejar la ventana de búsqueda abierta para siempre.

### 7.3 Flujo QR — Asistencia

Es el flujo más completo para mostrar y **lo hace una sola cuenta**: `gm@`. La emisión no exige rol GM, pero la **validación sí** (`requerir_roles("gm")`), así que hace falta una sesión `gm@` para las dos operaciones.

> ⚠️ **Detalle de diseño que conviene explicar:** el QR que se emite está atado a quien lo emite (`usuario["sub"]` del token), y la validación marca la asistencia del `usuario_id` que se mande en el body. O sea: el GM genera su propio sello y lo usa para registrar la asistencia de un jugador. La clave de Redis incluye a ambos: `qr:sesion:{sesion_id}:{usuario_emisor}`.

#### Paso 7.3.1 — Conseguir el `sesionId`

Las sesiones solo existen en el seed (no hay endpoint de alta de sesiones). Buscá el ID en la base:

```bash
docker compose exec postgres psql -U tfinder -d mesas_db \
  -c "SELECT s.id, m.nombre, s.estado FROM sesiones s JOIN mesas m ON m.id = s.mesa_id;"
```

Anotá el `id` de la sesión de *Mesa Demo Abierta*. En un seed limpio es `1`.

Para el paso de validación también necesitás el **id del jugador** que va a quedar con asistencia registrada:

```bash
docker compose exec postgres psql -U tfinder -d mesas_db \
  -c "SELECT id, email, rol FROM usuarios ORDER BY id;"
```

#### Paso 7.3.2 — Generar el QR (como `gm@`)

Entrá directo por URL — **no hay enlace de navegación** porque la pantalla padre `/mesas/:id/sesiones` depende de la flag `sesiones`:

```
http://localhost:5173/mesas/1/sesiones/1/qr
```

| Qué se ve | Qué pasa por detrás |
|---|---|
| Panel con el sello del gremio (PNG) | `POST /mesas-api/api/v1/sesiones/1/qr` → `201` |
| Contador de expiración | TTL de **600 s** en `qr:sesion:1:{id_del_gm}` |

La respuesta trae `qr_data` (payload en base64url con firma HMAC-SHA256 truncada a 32 hex), `png_base64` y `expira_en_seg`. La firma usa `QR_SECRET`.

#### Paso 7.3.3 — Validar la asistencia (también como `gm@`)

En la misma pantalla aparece el panel de validación (visible solo si sos GM).

> ⚠️ **Detalle que hay que respetar para que el flujo funcione:** el `usuario_id` que mandás en el body **tiene que ser el mismo que generó el QR** (o sea, el del GM). No es un detalle menor — la clave de Redis se guarda con el emisor y se busca con ese id. Mandar el id de un jugador devuelve `409`, no `200`. Está explicado en la [sección 9.2](#92-coupling-del-qr-el-emisor-y-el-asistente-deben-ser-el-mismo).

| # | Acción | Respuesta | Significado |
|---|---|---|---|
| 1 | Validar el QR por primera vez | `200` — "asistencia: registrada" | Se inserta en la tabla `asistencias` |
| 2 | Validar el **mismo** QR otra vez | `409` — "QR vencido o ya utilizado" | Uso único garantizado por `GETDEL` (ADR-007) |
| 3 | Validar un QR con firma alterada | `400` — "QR inválido: firma incorrecta" | El HMAC no cierra |
| 4 | Esperar 600 s y validar | `409` — "QR vencido" | La clave expiró en Redis |
| 5 | Mandar un `usuario_id` distinto al del emisor | `409` | La clave de Redis no existe para ese id |

Podés verificar la inscripción desde la base:

```bash
docker compose exec postgres psql -U tfinder -d mesas_db \
  -c "SELECT * FROM asistencias WHERE sesion_id = 1;"
```

**Punto de demo — por qué `GETDEL`.** El uso único no depende de "consultar y después borrar" (que dejaría una ventana de carrera). `GETDEL` lee y borra **en una sola operación atómica**. Aunque 5 personas validen el mismo QR a la vez, solo una obtiene `200`; las otras 4 reciben `409`.

**Punto de demo — la firma se verifica *después* del borrado.** Mirá el orden en `qr_asistencia.py:46-58`: primero `GETDEL`, después el `compare_digest` de la firma y el chequeo de `exp`. Es una decisión deliberada — el borrado es la garantía de uso único y la verificación es la de integridad — pero conviene conocerla si alguien pregunta por el orden.

### 7.4 Bloque C — Notificaciones

Sesioná como `jugador1@`.

| # | URL | Qué se ve | Llamada de red |
|---|---|---|---|
| 24 | `/notificaciones` | Bandeja con las notificaciones del usuario | `GET /notif-api/api/v1/notificaciones` |
| 25 | *(marcar una como leída)* | El punto azul desaparece | `PATCH /notif-api/api/v1/notificaciones/{id}/leida` |
| 26 | *(dejar abierta la pantalla)* | Llega una notificación **sin recargar** | `GET /notif-api/api/v1/notificaciones/stream` (SSE) |

**Punto de demo — la cadena asíncrona completa.** Para ver llegar algo en vivo, con `gm@` solicitá entrar a una mesa en otra pestaña. La cadena es:

```
POST /mesas/{id}/solicitudes          (mesas-api)
  └─> publica evento  mesa.solicitada  (RabbitMQ, exchange tfinder.events)
        └─> cola notif.mesa  ──> consumer ──> notif-api
              ├─> INSERT en notificaciones     ──> SSE  ──> aparece en pantalla
              └─> INSERT en bandeja de email   ──> SMTP  ──> MailHog
```

El `stream` es un Server-Sent Events con **heartbeat cada 15 s** y cola de 200 ítems. Para verlo en Network, filtrá por **Fetch/XHR** y abrí la petición `/stream`: queda abierta en `pending`.

### 7.5 Bloque D — Pantallas de gestión de campaña

Con `gm@` (o cualquier usuario autenticado) y las flags de la Fase 1 habilitadas, entrá a `/mesas/1/gestion`. Es un shell con 6 pestañas:

| Pestaña | URL directa | Qué se ve |
|---|---|---|
| Wiki | `/mesas/1/wiki` | Índice de páginas de campaña |
| — | `/mesas/1/wiki/nueva` | Editor de página nueva |
| — | `/mesas/1/wiki/{paginaId}` | Lectura de una página |
| — | `/mesas/1/wiki/{paginaId}/editar` | Edición |
| Calendario | `/mesas/1/calendario` | Calendario y votación de fechas |
| Sesiones | `/mesas/1/sesiones` | Listado de sesiones |
| — | `/mesas/1/sesiones/1/diario` | Editor del diario de sesión |
| Jugadores | `/mesas/1/jugadores` | Miembros, solicitudes pendientes, expulsiones |
| Builds | `/mesas/1/builds` | Builds asociados a la mesa |
| Diario | (incluido en la pestaña Sesiones) | — |

> **Importante:** `/mesas/1/gestion` es la forma más cómoda de recorrer todo. Sin la flag `gestionMesa`, cada pestaña sigue siendo accesible por URL propia, pero no hay índice visual.

### 7.6 Bloque E — Builds, feed y directorio

| # | URL | Qué se ve | Origen de los datos |
|---|---|---|---|
| 27 | `/builds` | Listado de builds | ⚙️ mock `src/data/builds.json` |
| 28 | `/builds/nuevo` | Asistente de creación (wizard) | ⚙️ mock |
| 29 | `/builds/1` | Detalle de un build | ⚙️ mock |
| 30 | `/builds/1/historial` | Historial de cambios | ⚙️ mock |
| 31 | `/feed` | Feed social | ⚙️ mock `src/data/feed.json` |
| 32 | `/feed/nuevo` | Crear publicación | ⚙️ mock |
| 33 | `/tags` | Catálogo de etiquetas | ⚙️ mock |
| 34 | `/usuarios/1` | Perfil de un usuario | ⚙️ mock `src/data/usuarios.json` |
| 35 | `/perfil` | Perfil propio extendido | ⚙️ mock |
| 36 | `/dashboard` | Panel de inicio | ⚙️ mock |
| 37 | `/mis-mesas` | Campañas del usuario | ⚙️ mixto |
| 38 | `/encuentros` | Encuentros del jugador | ⚙️ mock |

**Estos endpoints sí existen en el backend y se pueden mostrar aparte** (ver Fase 4):

```bash
curl -s "http://localhost:8002/api/v1/builds" | head
curl -s "http://localhost:8002/api/v1/tags" | head
curl -s "http://localhost:8003/api/v1/feed?tipo=post&limit=5" | head
curl -s "http://localhost:8003/api/v1/wiki?mesa_id=1" | head
```

### 7.7 Bloque F — Administración

Cerrá sesión. Entrá con `admin@tfinder.dev` / `DemoTFinder123!`.

Las 10 pantallas quedan accesibles desde `/admin/plataforma` y la navegación lateral:

| # | URL | Qué muestra |
|---|---|---|
| 39 | `/admin/moderacion` | Cola de moderación con casos pendientes |
| 40 | `/admin/usuarios` | Gestión de cuentas |
| 41 | `/admin/estadisticas` | Estadísticas y logs |
| 42 | `/admin/plataforma` | Vista general de los 4 servicios |
| 43 | `/admin/trazabilidad` | Traza por `correlation-id` |
| 44 | `/admin/observabilidad` | Métricas de operación |
| 45 | `/admin/dlq` | **Cola de mensajes fallidos** — la más interesante |
| 46 | `/admin/resiliencia` | Circuit breaker y reintentos |
| 47 | `/admin/comparador` | Comparativa entre servicios |
| 48 | `/admin/prometheus` | Métricas estilo Prometheus |

> ⚠️ **Las 10 pantallas de admin leen datos mock** de `src/data/admin/*.json` con 350 ms de latencia simulada. Se ven perfecto, pero **no reflejan el estado real** de RabbitMQ, la DLQ ni las métricas. Para la evidencia real, usá la [Fase 4](#8-fase-4--evidencia-de-backend-e-infraestructura): la API de notif expone `GET /api/v1/dlq` y `GET /api/v1/event-log` con datos de verdad.

**Comprobación de que el bloqueo por rol funciona:** con `gm@` todavía logueado, entrá directo a `/admin/usuarios` → el guard te devuelve a `/mesas` (`guard.js:19`).

### 7.8 Recorrido completo de una sentada

Si solo tenés 10 minutos, este es el orden mínimo:

1. `/` → landing (10 s)
2. `/mesas` → listado + filtro por estado (30 s)
3. `/mesas/2` → detalle con la última vacante (20 s)
4. Loguear como `gm@` (20 s)
5. `/mesas/nueva` → crear mesa → aparece en el listado (60 s)
6. Unirse a la *Casi Llena* → `201` → repetir → `409` (60 s)
7. `/mesas/1/sesiones/1/qr` → generar QR (40 s)
8. Con el mismo `gm@`: validar el QR → `200` → revalidar → `409` (60 s)
9. `/notificaciones` → marcar leída → dejar el SSE abierto (40 s)
10. MailHog en http://localhost:8025 → mostrar el correo recibido (20 s)
11. RabbitMQ en http://localhost:15673 → mostrar `dlq.general` (30 s)
12. `/ready` en las 4 APIs (20 s)

---

## 8. Fase 4 — Evidencia de backend e infraestructura

Lo que no se ve en la pantalla, se demuestra por API o por panel.

### 8.1 Los 46 endpoints

| Servicio | Puerto | Endpoints |
|---|---:|---|
| **mesas-api** | 8001 | `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `GET /auth/me`, `GET /auth/admin-only`, `GET /mesas`, `GET /mesas/{id}`, `GET /mesas/{id}/miembros`, `POST /mesas`, `PUT /mesas/{id}`, `DELETE /mesas/{id}`, `POST /mesas/{id}/solicitar`, `POST /mesas/{id}/solicitudes`, `POST /matchmaking/{id}/abrir`, `GET /matchmaking/{id}/estado`, `POST /sesiones/{id}/qr`, `POST /sesiones/{id}/qr/validar` |
| **builds-api** | 8002 | `GET /builds`, `GET /builds/{id}`, `GET /tags`, `POST /builds/{id}/pdf` |
| **feed-api** | 8003 | `GET /feed`, `GET /wiki`, `POST /mesas/{id}/sesiones/{id}/diario/pdf` |
| **notif-api** | 8004 | `GET /notificaciones`, `GET /notificaciones/stream`, `PATCH /notificaciones/{id}/leida`, `POST /auth/recuperar`, `GET /event-log`, `GET /emails`, `POST /emails/{id}/reintentar`, `GET /pdf/{doc_id}`, `GET /pdf/{doc_id}/estado`, `GET /dlq`, `POST /dlq/{id}/reintentar`, `DELETE /dlq/{id}` |
| **Todos** | | `GET /health`, `GET /live`, `GET /ready` en cada uno |

Prefijo común: `/api/v1`.

### 8.2 Autenticación por terminal

```bash
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"gm@tfinder.dev","password":"DemoTFinder123!"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

echo $TOKEN
```

### 8.3 Crear una mesa por API

```bash
curl -s -X POST http://localhost:8001/api/v1/mesas \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
        "nombre": "Mesa de prueba en vivo",
        "sistema": "PF1e",
        "descripcion": "Creada durante la demostración",
        "tono": "Táctica",
        "horario": "Domingo 21:00",
        "estado": "abierta",
        "nivel_inicial": 3,
        "jugadores_max": 6
      }'
```

Los campos `nombre` y `sistema` son obligatorios; `descripcion`, `tono`, `horario`, `nivel_inicial` y `jugadores_max` son opcionales. El esquema usa `extra="forbid"`: un campo desconocido devuelve `400`, no `422`.

### 8.4 QR por API

`$TOKEN` debe ser el de una cuenta **`gm@`** (ver 8.2), porque la validación exige rol `gm`.

```bash
# Emitir — cualquier usuario autenticado; el QR queda atado a SU propio id
QR_DATA=$(curl -s -X POST http://localhost:8001/api/v1/sesiones/1/qr \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["qr_data"])')

echo "$QR_DATA"

# Validar — rol gm obligatorio.
# usuario_id DEBE ser el del emisor (2 = gm en un seed limpio).
# Cualquier otro id devuelve 409. Ver la sección 9.2.
curl -s -X POST http://localhost:8001/api/v1/sesiones/1/qr/validar \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{\"usuario_id\": 2, \"qr_data\": \"$QR_DATA\"}"
# → {"asistencia":"registrada"}

# Repetir la misma llamada → 409 "QR vencido o ya utilizado"
```

### 8.5 PDF asíncrono (el flujo más elegante de mostrar)

El request devuelve `202 Accepted` **de inmediato** y el documento se arma en background. Un worker thread de `notif-api` escucha el evento `doc.pdf.build` en la cola `doc.pdf`, genera el PDF con `fpdf2` y lo guarda en `PDF_DIR`.

```bash
# 1. Disparar (builds-api) → 202 + documento_id
DOC=$(curl -s -X POST http://localhost:8002/api/v1/builds/1/pdf \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["documento_id"])')

# 2. Consultar estado → en_proceso, luego listo
curl -s http://localhost:8004/api/v1/pdf/$DOC/estado \
  -H "Authorization: Bearer $TOKEN"

# 3. Descargar el PDF → 200 + application/pdf
curl -s http://localhost:8004/api/v1/pdf/$DOC \
  -H "Authorization: Bearer $TOKEN" -o build.pdf
```

**Punto de demo:** el `sleep 1` entre el paso 2 y el 3 da tiempo a que el worker termine. Si se consulta demasiado pronto, el estado es `en_proceso` — y eso es exactamente lo que hay que mostrar: **el cliente no espera al servidor**.

El mismo flujo existe para el diario de sesión:

```bash
curl -s -X POST http://localhost:8003/api/v1/mesas/1/sesiones/1/diario/pdf \
  -H "Authorization: Bearer $TOKEN"
```

### 8.6 Redis — clave por clave

```bash
# Listado de mesas cacheado (TTL 60 s)
docker compose exec redis redis-cli TTL cache:mesas:list

# Reserva de vacante durante un unirse (TTL 60 s, se borra en el finally)
docker compose exec redis redis-cli KEYS 'reserva:*'

# QR de asistencia (TTL 600 s) — la clave incluye sesion, emisor y usuario
docker compose exec redis redis-cli KEYS 'qr:sesion:*'

# Idempotencia (TTL 86400 s)
docker compose exec redis redis-cli KEYS 'idem:*'

# Ventana de llamada de matchmaking (TTL 120 s)
docker compose exec redis redis-cli KEYS 'llamado:*'

# Sesión revocada tras logout (TTL 86400 s)
docker compose exec redis redis-cli KEYS 'sesion:*'
```

El `TTL` devuelve `-2` si la clave no existe. Eso sirve para mostrar que la reserva de vacante **se libera sola** aunque la petición muera a mitad de camino.

### 8.7 RabbitMQ — topología

Panel: http://localhost:15673 (`tfinder` / `tfinder`)

```
Exchange  tfinder.events  (topic, durable)
Exchange  tfinder.dlx     (topic, durable)

  mesa.*    ──> notif.mesa     (durable, x-dead-letter-exchange = tfinder.dlx)
  sesion.*  ──> notif.sesion   (durable, x-dead-letter-exchange = tfinder.dlx)
  doc.pdf.* ──> doc.pdf        (durable, x-dead-letter-exchange = tfinder.dlx)
                          ──> dlq.general  (bound a DLX con routing_key "#")
```

**Punto de demo — reintentos con backoff.** El consumer corre con `prefetch_count=1` y `auto_ack=False`. El contador de reintentos `_intentos` viaja **dentro del cuerpo del mensaje** (no en el header, porque AMQP no lo conserva al redeliver). El backoff es `2^n` y `MAX_REINTENTOS=3`. Al cuarto fallo, el mensaje se confirma y se manda a `dlq.general` + a la tabla `mensaje_dlq`.

Para verlo funcionar: generá un evento que rompa, por ejemplo un PDF contra un build inexistente, y observá el contador de *ready* subiendo en `notif.mesa` antes de caer en `dlq.general`.

La API expone la DLQ con datos reales (a diferencia de la pantalla admin):

```bash
ADMIN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@tfinder.dev","password":"DemoTFinder123!"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

curl -s "http://localhost:8004/api/v1/dlq?limite=10" -H "Authorization: Bearer $ADMIN"
```

### 8.8 MailHog — correo como outbox

Panel: http://localhost:8025

El servicio de email usa `smtplib` contra MailHog y **además** persiste cada envío en una tabla outbox (ADR-005). El panel no es la fuente de verdad: para consultar lo que el sistema *cree* que envió:

```bash
curl -s "http://localhost:8004/api/v1/emails?limite=10" -H "Authorization: Bearer $ADMIN"
curl -s -X POST "http://localhost:8004/api/v1/emails/{id}/reintentar" -H "Authorization: Bearer $ADMIN"
```

### 8.9 Trazabilidad por `correlation-id`

Cada request entra con un `X-Correlation-Id` (o se genera uno) y ese valor viaja por los logs JSON de **los 4 servicios** y por los mensajes de RabbitMQ.

```bash
CID="demo-$(date +%s)"
curl -s http://localhost:8001/api/v1/mesas -H "X-Correlation-Id: $CID"

docker compose logs | grep "$CID"
```

La API también:

```bash
curl -s "http://localhost:8004/api/v1/event-log?correlation_id=$CID" -H "Authorization: Bearer $ADMIN"
```

### 8.10 Modo degradado de `/ready`

`/ready` es distinto de `/health`: verifica **las tres** dependencias.

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8001/ready   # 200
curl -s http://localhost:8001/live                                        # siempre 200
```

Para verlo en 503, detené una dependencia:

```bash
docker compose stop rabbitmq
curl -s http://localhost:8001/ready     # 503, estado "degradado", dice qué falta
docker compose start rabbitmq
```

`/live` sigue respondiendo `200` — es la diferencia entre "el proceso está vivo" y "el servicio puede atender tráfico".

### 8.11 Pruebas automatizadas

```bash
# Backend
pytest -m unit -q
pytest -m integration -q
pytest -m unit --cov=. --cov-report=term-missing
ruff check .

# Frontend
cd tfinder-vue
npm run test:unit
npm run test:integration
```

Las de integración necesitan PostgreSQL, Redis y RabbitMQ levantados, y las cuatro bases `*_db_test`.

---

## 9. Límites de la demostración

> **Leé esta sección antes de presentar.** Evita sobredeclarar capacidades.

### 9.1 Qué pantallas leen datos reales

Solo **2 de los 14 servicios** frontend llaman a la API:

| Servicio | Estado |
|---|---|
| `services/mesas.js` | ✅ real |
| `services/notificaciones.js` | ✅ real |
| `services/{actividad,admin,builds,eventos,feed,jugadores,matchmaking,membresias,sesiones,usuarios,votaciones,wiki}.js` | ⚙️ mock |

Y 4 composables reales: `useAuth`, `useMesas`, `useSolicitud`, `useLlamado`.

**Traducción:** listar, crear, editar y borrar mesas, unirse, autenticación, matchmaking, QR y notificaciones **sí** van al backend. Wiki, builds, feed, calendario, jugadores y **las 10 pantallas de admin** muestran datos coherentes pero ficticios, con una latencia simulada de 280–400 ms. Si en la demo preguntan por qué una pantalla tarda 350 ms en "cargar", esa es la respuesta.

### 9.2 Otras salvedades

| # | Salvedad |
|---|---|
| 1 | El chip "caché ~X ms" es una medición del cliente con `performance.now()`, **no** evidencia del tier de caché. El header `X-Cache-Tier` que el frontend espera nunca lo emite ningún backend. Para probar la caché de verdad, hay que usar `redis-cli TTL cache:mesas:list` ([8.6](#86-redis--clave-por-clave)). |
| 2 | No hay productores para los eventos `sesion.confirmada` ni `sesion.diario_publicado`. La cola `notif.sesion` existe y el consumer también, pero nunca recibe nada: ese camino **no se puede demostrar en vivo**. |
| 3 | `builds-api` es **solo lectura**. No hay alta, edición ni borrado de builds en el backend; los que se ven en pantalla son mock. |
| 4 | `POST /mesas/{id}/solicitar` (nota: singular) es la ruta **legacy**. Publica `mesa.solicitada` pero **no reserva cupo**. La ruta real, segura contra carreras, es `POST /mesas/{id}/solicitudes` (plural) con header `Idempotency-Key`. En la demo usá la plural. |
| 5 | `useMesas.unirse` es código muerto. El camino vivo es `useSolicitud.unirse`. |
| 6 | No hay endpoint de alta de sesiones. Solo las 2 del seed. Para crear una sesión hay que insertarla por SQL. |
| 7 | `DEMO_SEED_ENABLED` en `.env.example` viene en `true` (para la demo), pero el default en el código de cada servicio es `false` (para producción). |
| 8 | La variable `DEBUG` se lee en los cuatro `config.py` pero **ningún entrypoint la usa**. No activarla esperando efectos. |
| 9 | El `main.py` de la raíz es código muerto de AE1 con imports rotos. **No lo ejecutes.** Arrancá con `uvicorn mesas_api.main:app`. |
| 10 | El `README.md` de la raíz describe AE1 y SQLite. La documentación vigente es `AE2/README.md` y `docs/INFORME-AE2.md`. |

### 9.2 Coupling del QR: el emisor y el asistente deben ser el mismo

Este es el único punto donde la implementación impose una restricción que no es obvia, y conviene tenerlo presente **antes** de la demo para no mostrar un `409` inesperado.

**Cómo funciona:** la clave de Redis se escribe con el id del **emisor** y se lee con el `usuario_id` del **body de validación**.

```python
# generar (sesiones.py:11) — usuario["sub"] del token
get_redis().setex(f"qr:sesion:{sesion_id}:{usuario_id}", TTL_QR, data)   # id del GM

# validar (qr_asistencia.py:48) — usuario_id del body
ok = r.getdel(f"qr:sesion:{sesion_id}:{usuario_id}")                      # id del body
```

Como `usuario["sub"]` (el GM) y `body.usuario_id` son valores independientes, **si no coinciden el `GETDEL` devuelve `None` y la respuesta es `409`**. En la práctica, el único camino que devuelve `200` es: el GM emite su propio QR y lo valida pasando su propio id — lo que registra la asistencia del propio GM, no la de un jugador.

**Cómo tratarlo en la demo:** mostrar el flujo tal cual (emite → valida → revalida → `409`) y explicar el acoplamiento como una limitación conocida de la implementación, no como un comportamiento diseñado. Si te preguntan si un jugador puede registrar su asistencia escaneando el QR, la respuesta honesta es que **hoy no**.

### 9.3 Documentos que complementan esta guía

| Documento | Qué aporta |
|---|---|
| `docs/INFORME-AE2.md` | Informe técnico completo: arquitectura, contratos, concurrencia, 12 limitaciones |
| `docs/ADR/ADR-001..007` | Las 7 decisiones de arquitectura y sus alternativas descartadas |
| `docs/testing/tutorial-pruebas.md` | 1013 líneas: cada caso con URL, campos, valores y respuesta esperada |
| `docs/testing/manual-tests.md` | Qué pruebas son seguras y cuáles destructivas |
| `docs/testing/valores-prueba.md` | Fixtures congelados para reproducir |
| `docs/manual-usuario.md` | Manual de usuario final (18 secciones) |
| `tfinder-vue/docs/GUIA_USO.md` | Recorrido por rol del frontend |
| `AE2/evidencias/EVIDENCIAS.md` | 14 evidencias ya capturadas con su índice |
| `docs/AUDITORIA_CIERRE_AE2.md` | Auditoría con hallazgos priorizados |

---

## 10. Checklist de verificación

Usá esto como criterio de aceptación antes de dar por buena la demo.

### 10.1 Infraestructura

- [ ] `docker compose ps` muestra los 8 servicios en `healthy` / `running`
- [ ] `GET /ready` devuelve `200` en los 4 servicios
- [ ] `GET /live` devuelve `200` en los 4 servicios
- [ ] `GET /ready` devuelve `503` al detener `rabbitmq`
- [ ] Los 4 `/docs` cargan y listan sus endpoints
- [ ] Redis: `TTL cache:mesas:list` > 0
- [ ] Redis: existen `qr:sesion:*`, `idem:*`, `llamado:*` según la fase
- [ ] RabbitMQ: existen `notif.mesa`, `notif.sesion`, `doc.pdf`, `dlq.general`
- [ ] MailHog muestra al menos un correo recibido
- [ ] Un `correlation-id` aparece en los logs de más de un servicio

### 10.2 Feature flags

- [ ] `features.js` tiene las 20 flags presentes
- [ ] Las 7 originally activas siguen en `true`
- [ ] Las 13 bloqueadas están en `true` (Fase 1)
- [ ] `/proximamente/:feature` ya no aparece al navegar
- [ ] El menú autenticado muestra los 6 ítems
- [ ] `npm run test:unit` → solo falla `feature-gating.spec.js`, por la razón documentada

### 10.3 Recorrido de pantallas

- [ ] Invitado: `/`, `/mesas`, `/mesas/1`, `/mesas/2`, `/registro`, `/recuperar` (6)
- [ ] Aventurero: crear mesa, editar mesa, unirse, QR, matchmaking, notificaciones, encuentros (7)
- [ ] Gestión: wiki ×4, calendario, sesiones ×2, jugadores, builds de mesa (9)
- [ ] Descubrimiento: builds ×5, feed ×2, tags, usuario, perfil, dashboard, mis-mesas (11)
- [ ] Admin: las 10 pantallas `/admin/*` (10)

### 10.4 Casos de negocio con respuesta observable

- [ ] Crear mesa → `201`, aparece en el listado, caché invalidada
- [ ] Unirse con vacante → `201`
- [ ] Unirse sin vacante → `409` con `"Cupo agotado: no quedan vacantes"`
- [ ] Repetir la misma `Idempotency-Key` → misma respuesta, sin duplicar
- [ ] QR emitir → `201` + PNG, TTL 600
- [ ] QR validar 1ª vez → `200`
- [ ] QR validar 2ª vez → `409` (uso único por `GETDEL`)
- [ ] QR con firma alterada → `400`
- [ ] PDF asíncrono → `202` → `en_proceso` → `listo` → descarga `200`
- [ ] Notificación llega por SSE **sin recargar** la página
- [ ] Evento fallido aparece en `dlq.general` y en `GET /api/v1/dlq`
- [ ] `/admin/usuarios` con `gm@` redirige a `/mesas`
- [ ] Contrato de error uniforme en los 4 servicios: `{"error":{"codigo":…,"mensaje":…}}`

---

## Anexo A — Referencia rápida de comandos

```bash
# ── Levantar / detener ──────────────────────────────────
cp .env.example .env
docker compose up -d --build
docker compose ps
docker compose logs -f mesas-api
docker compose down              # detiene, conserva datos
docker compose down -v           # RESETEA TODO (recrea las 4 bases)

# ── Verificar ──────────────────────────────────────────
for p in 8001 8002 8003 8004; do curl -s http://localhost:$p/ready; echo; done

# ── Solo infraestructura ───────────────────────────────
docker compose up -d postgres redis rabbitmq mailhog

# ── Redis ──────────────────────────────────────────────
docker compose exec redis redis-cli KEYS '*'
docker compose exec redis redis-cli TTL cache:mesas:list

# ── RabbitMQ ───────────────────────────────────────────
docker compose exec rabbitmq rabbitmqctl list_queues name messages_ready messages_unacknowledged

# ── SQL directo ─────────────────────────────────────────
docker compose exec postgres psql -U tfinder -d mesas_db -c "\dt"
docker compose exec postgres psql -U tfinder -d notif_db  -c "SELECT * FROM mensaje_dlq;"

# ── Frontend ───────────────────────────────────────────
cd tfinder-vue
npm ci && npm run dev
npm run lint && npm run type-check
npm run test:unit

# ── Backend ────────────────────────────────────────────
pytest -m unit -q
pytest -m integration -q
ruff check .
```

## Anexo B — Mapa flag → archivo → vista

| Flag | Archivo de la vista | Notas |
|---|---|---|
| `dashboard` | `views/DashboardView.vue` | Datos mock |
| `perfil` | `views/PerfilView.vue` | Datos mock |
| `crearMesa` | `views/MesaFormularioView.vue` | ✅ Backend real |
| `editarMesa` | `views/MesaFormularioView.vue` | ✅ Backend real |
| `misMesas` | `views/MisMesasView.vue` | Mixto |
| `gestionMesa` | `views/gestion/GestionView.vue` | Shell con 6 pestañas |
| `wiki` | `views/gestion/{WikiView,PaginaWikiView,WikiEditorView}.vue` | Datos mock |
| `calendario` | `views/gestion/CalendarioView.vue` | Datos mock |
| `sesiones` | `views/gestion/{SesionesView,DiarioEditorView}.vue` | Datos mock |
| `qr` | `views/gestion/SesionQrView.vue` | ✅ Backend real |
| `jugadores` | `views/gestion/JugadoresView.vue` | Datos mock |
| `builds` | `views/{BuildsListView,BuildDetailView,BuildEditorView,BuildWizardView,BuildHistorialView}.vue` + `views/gestion/BuildsView.vue` | Datos mock |
| `feed` | `views/{FeedView,FeedNewView}.vue` | Datos mock |
| `directorio` | `views/UsuarioDetailView.vue` | Datos mock |
| `notificaciones` | `views/NotificacionesView.vue` | ✅ Backend real |
| `matchmaking` | `views/MatchmakingView.vue` | ✅ Backend real |
| `encuentros` | `views/EncuentrosView.vue` | Sin backend |
| `tags` | `views/TagsView.vue` | Datos mock |
| `recuperacion` | `views/RecuperarView.vue` | ✅ Backend real |
| `admin` | `views/admin/Admin*.vue` (10 archivos) | Datos mock |

---

*Documento redactado sobre el estado del repositorio en la rama `AE2-Testing`. Si los flags o las rutas cambian, actualizá la [sección 2](#2-mapa-de-funcionalidades) y la [sección 7](#7-fase-3--recorrido-por-rol).*
