# Informe técnico individual de AE2 — Czajkowski Leonardo · Frontend F01–F09

**Proyecto:** TFinder — plataforma de búsqueda y gestión de mesas de juego de rol
**Asignatura:** Paradigmas y Lenguajes de Programación III — `ISI17PL324`
**Actividad:** `ISI17PL324V26AE2V26` — Actividad de Evaluación 2
**Estudiante:** Czajkowski Leonardo
**Alcance individual:** frontend F01–F09 + feature gating y suite Vitest (issues #26 a #34)
**Rama:** `origin/A2-Frontend`
**Versión base de AE1:** `1781e4efb516cb8ac7c3965d140ba476c932cad2` (2026-08-28)
**Tags de entrega:** `2.0.0` (alfa) y `2.1.0` (beta)
**AÑO:** 2026

> El informe del sistema completo está en [`INFORME-AE2.md`](./INFORME-AE2.md). El del backend, en [`INFORME-AE2-AMARILLA-LUCIO.md`](./INFORME-AE2-AMARILLA-LUCIO.md). Este documento se limita a mi alcance individual —el frontend— y explica cómo la interfaz consume los contratos que el backend expone, porque esa es la parte del trabajo donde se cruzan las dos capas.

---

## 1. Alcance comprometido

### 1.1 El punto de partida

AE1 no tenía frontend en el repositorio. El punto de partida de mi trabajo fue el **port a Vue 3 de un prototipo HTML estático** que se había recuperado de un respaldo (`b5b3c1e`), más una capa de datos de prueba en JSON.

Ese punto de partida tenía un problema que condicionó todo lo demás: **el listado de mesas estaba escrito con datos incrustados en el template**. Seis tarjetas repetidas a mano, con el mismo marcado y distintos valores. La consigna de la actividad pedía explícitamente lo contrario: template declarativo, sin datos embebidos, alimentado por estado reactivo y alimentado con datos desde un servicio. El razonamiento de ese traspaso está documentado en `tfinder-vue/docs/ENTREGA.md` y es el antecedente directo de mi alcance.

### 1.2 Los nueve bloques que me comprometí

| RF | Título | Issue | Commit | Entregado |
|---|---|---|---|---|
| F01 | Capa HTTP unificada con auth, idempotencia y `correlation_id` | #26 | `bf3774c` | Sí |
| F02 | Autenticación real: tokens, registro, recuperación, perfil | #27 | `ed696f2` | Sí |
| F03 | Explorar mesas reales: listado con filtros, detalle, evidencia de caché | #28 | `229fee5` | Sí |
| F04 | Unirse a una mesa con carrera de vacantes e `Idempotency-Key` | #29 | `a44264b` | Sí |
| F05 | Matchmaking real con TTL de Redis en vivo | #30 | `f76e883` | Sí |
| F06 | Sesión con QR de asistencia single-use y validación del GM | #31 | `31bd32f` | Sí |
| F07 | Exportar PDF asíncrono (`202` → en cola → listo) | #32 | `2c57f14` | Sí |
| F08 | Notificaciones en vivo con polling y modo degradado | #33 | `1b13721` | Sí |
| F09 | Administración y observabilidad: `/live`, `/ready`, DLQ, broker | #34 | `4dcba75` | Sí |
| — | Feature gating con `ComingSoon` + suite Vitest | — | `dd7674e` | Sí |

```bash
# Verificación de la trazabilidad
git log --oneline origin/A2-Frontend        # F01..F05
git log --format='%h %s' --all | grep -E '#(2[6-9]|3[0-4])'   # F01..F09
cd tfinder-vue && npm run test:unit -- --run    # 15
cd tfinder-vue && npm run test:integration -- --run   # 7
```

### 1.3 Qué queda fuera de alcance

| Fuera de alcance | Motivo |
|---|---|
| Conectar `builds` y `feed` a la API | Sus endpoints existen y el proxy de nginx está preparado, pero no hay functions en el catálogo para ellos. Es un alcance no comprometido en AE2 |
| E2E en navegador (Playwright/Cypress) | La verificación E2E del proyecto se hizo por HTTP (99 casos), no sobre el DOM. Declarado como brecha del proyecto |
| Sistema de estado global (Pinia) | El alcance no lo requería y una librería de estado para siete composables habría sido infraestructura especulativa. La decisión está en §2.2 |
| Internacionalización | Fuera del escenario |
| Migrar los servicios mock restantes a API | 12 servicios siguen sobre JSON. Es alcance de AE4 |

---

## 2. Arquitectura del frontend

### 2.1 La forma general

```text
tfinder-vue/src/
├── api/              http.js          punto único de salida a la red
│                     endpoints.js     catálogo de endpoints por servicio
├── config/
│   ├── api.js        resolución de base URL por servicio
│   ├── features.js   mapa de feature flags
│   └── nav.js        navegación por rol
├── router/
│   ├── index.js      46 registros de ruta, todos lazy
│   └── guard.js      resolveGuard() — función pura
├── composables/      7 composables, estado a nivel de módulo
├── services/         14 servicios: 2 reales + 12 sobre JSON
├── layouts/          AppShell + 3 wrappers por rol
├── components/       shell, estados, modales, tarjetas
├── views/            44 vistas (raíz + gestion/ + admin/)
└── styles/           tokens, harness y clases compartidas
```

**Stack:** Vue 3.5 con `<script setup>` en todos los SFC, Vite 6, `vue-router` 4, JavaScript (sin TypeScript en el código de aplicación), Tailwind 3 más un sistema de diseño propio en CSS, y Vitest 3 con jsdom.

**46 rutas, todas lazy.** Cada vista es un `() => import(...)`, lo que produce un chunk por vista y hace que la carga inicial no arrastre 44 pantallas.

### 2.2 Por qué no hay Pinia

No hay librería de estado. El estado compartido vive en **singletons a nivel de módulo**: `useAuth.js` expone un `reactive({access, refresh, user})` de scope de módulo, y cualquier importador del módulo obtiene la misma instancia.

La decisión tiene tres partes:

1. **Siete composables no justifican una librería.** Pinia resuelve el problema del estado global grande con devtools, time-travel y convenciones. Con siete piezas de estado, la librería es más ceremonia que ayuda.
2. **El patrón de módulo es el equivalente conceptual de un store de un solo módulo.** El singleton cumple la misma función sin la dependencia.
3. **Cambiar de opinión es barato.** Si el estado crece, migrar siete singletons a stores de Pinia es un cambio mecánico y local.

Donde el estado es local a una vista, es simplemente un `ref` dentro del composable. La regla que seguí: **un `ref` local hasta que dos componentes necesiten el mismo dato; recién ahí, un singleton de módulo.**

Hay un matiz en `MesaGestionShell`, que usa `provide`/`inject` en lugar de un singleton: el estado de gestión de una mesa se pasa por contexto porque es **jerárquico** —un shell y sus nueve sub-vistas—, y `provide` expresses esa relación mejor que un store global al que todas las vistas podrían reachar.

### 2.3 El enrutado y la Guardia

`router/index.js` declara 46 registros; `router/guard.js` contiene la decisión de acceso en **una función pura**:

```js
export function resolveGuard(to, role) {
  const feature = to.meta.feature
  if (feature && !isFeatureEnabled(feature)) {
    return { name: 'proximamente', params: { feature } }    // 1. feature gate
  }
  const need = to.meta.roles
  if (!need) return true
  if (need.includes(role)) return true
  if (need.includes('guest')) return '/mesas'               // 2. usuario en ruta de invitado
  if (role === 'guest') {
    return { path: '/login', query: { redirect: to.fullPath } }  // 3. redirigir al login
  }
  if (need.includes('admin')) return '/mesas'                // 4. admin: fuera de alcance
  return true
}
```

`src/router/guard.js`

Extraer la lógica a una función pura en vez de dejarla en el `beforeEach` es una decisión de testabilidad, y tiene un efecto secundario valioso: `tests/unit/feature-gating.spec.js` puede verificar la matriz completa de seis casos **sin montar un router ni un componente**. Una guarda probada así es una guarda que se puede refactorizar sin miedo.

**El orden de las reglas importa, y no es arbitrario:** el feature gate se evalúa **antes** que la autenticación. Un usuario anónimo que navega a `/builds` (funcionalidad desactivada) aterriza en `ComingSoon`, no en el login. La razón es que pedirle a alguien que se autentique para comprobar que la funcionalidad que quiere no existe es una fricción sin propósito.

### 2.4 El feature gating: tres piezas coordinadas

`src/config/features.js` declara 21 features, 7 activas y 14 desactivadas. El gating se apoya en tres piezas que deben coincidir:

```text
1. Banderas     FEATURES = { clave: { label, available } }
2. Rutas        meta.feature en el registro + comprobación en resolveGuard()
3. Navegación   navTarget(item) en AppHeader, AppFooter y MobileMenuPanel
                -> item.feature && !isFeatureEnabled(item.feature)
                   ? comingSoonPath(item.feature)
                   : item.to
                + sub-etiqueta "Próximamente"
```

`ComingSoonView` es el destino de la redirección y muestra el `label` de la función.

**Por qué existe este mecanismo.** El prototipo tenía 44 pantallas, muchas de ellas apoyadas en endpoints que el backend todavía no expone. Sin el gate, presentar la aplicación significaba presentar pantallas que fallan al usarse. Con el gate, la navegación es coherente —no hay enlaces rotos ni errores en pantalla— y la demarcación entre lo implementado y lo pendiente es explícita y centralizada: cambiar `available` a `true` en un solo lugar activa la función en rutas, navegación y vistas.

**Consecuencia asumida:** como las 6 pestañas de `MesaGestionShell` están todas bajo features desactivadas, el shell llega a renderizar cero pestañas. Es un efecto secundario del mecanismo, no un error, y está declarado en §7.

---

## 3. La capa HTTP: un solo punto de paso

*(criterio 4 de la rúbrica)*

### 3.1 La decisión y su firma

`src/api/http.js` es el **único** lugar del frontend que toca la red. Toda la aplicación pasa por `api()`.

```js
export async function api(
  servicio,
  ruta,
  { metodo = 'GET', cuerpo = null, idempotenciaKey = null, timeoutMs = 8000 } = {}
)
```

Que exista un solo punto de paso no es una cuestión de estilo. Es lo que hace posible:

- **Agregar un header a toda la aplicación** (el `X-Correlation-Id`) cambiando un archivo.
- **Centralizar el manejo de `401`** en lugar de repetir la redirección al login en quince componentes.
- **Poder testear la capa de red** con un `fetch` simulado, en lugar de probar cada componente por separado.

Con quince componentes haciendo `fetch` por su cuenta, cada uno tendría su propio manejo de error, su propio timeout —o su ausencia— y su propia interpretación del envelope del backend. Los tres son errores esperando a ocurrir.

### 3.2 Lo que `api()` hace y por qué

| Comportamiento | Implementación | Razón |
|---|---|---|
| **Timeout de 8 s** | `AbortController` + `setTimeout`, limpiado en ambos caminos | Un request colgado deja la interfaz en carga infinita. El timeout convierte un bloqueo silencioso en un error que la UI sabe mostrar |
| **`X-Correlation-Id` por request** | `idAleatorio()` en cada llamada | Es lo que permite reconstruir el recorrido de una acción del usuario en los logs del backend (§6) |
| **`Idempotency-Key` solo con body** | `if (cuerpo != null)` | Un `GET` no puede tener efectos, así que una clave de idempotencia en un `GET` es ruido que confunde el registro del servidor |
| **`Authorization` condicional** | Solo si hay token | Evita mandar `Bearer null` en las rutas públicas, que es un patrón fácil de dejar y difícil de detectar |
| **`ApiError` con `codigo`** | `class ApiError extends Error { codigo, mensaje, detalles }` | Mapea directamente el envelope `{"error":{"codigo","mensaje"}}` del backend, de modo que la UI puede preguntar `e.codigo === 409` sin parsear el mensaje |
| **Normalización de headers** | Copia en minúsculas, maneja `Headers.forEach` y objeto plano | Un `Response` real y un mock de test exponen los headers de formas distintas; normalizar hace que el test pueda usar un objeto simple |
| **`204` y cuerpos vacíos** | `respuesta.json()` dentro de `try` | Un `204 No Content` no tiene JSON, y no es un error |
| **Error de red distinguiendo timeout** | `ApiError('timeout', '… no respondió en 8000 ms')` | El usuario necesita saber si el servicio no responde o si no está levantado. Son mensajes distintos, con la acción distinta que corresponde |

### 3.3 El manejo del `401` y su costo

```text
401 -> clearSession()
    -> window.location.assign('/login?redirect=' + encodeURIComponent(path + search))
    -> throw ApiError('unauthorized', 'Sesión expirada o inválida.')
```

La redirección es **dura** —recarga la página—, y es la decisión de la que más me convenzo después de escribirla, porque tiene un costo real que dejé declarado: el usuario **pierde el estado de la navegación** en cada expiración, incluido el scroll y cualquier formulario a medio completar.

La alternativa descartada era un interceptor que intentara un refresh y reintentara. No la implementé por dos razones: el refresh ya no es parte del flujo actual (§7), y un reintento automático sobre un endpoint no idempotente puede duplicar operaciones. Preferí un comportamiento simple y honesto —"tu sesión terminó, volvé a entrar y seguí desde donde estabas" con el `redirect` preservando el destino— antes que una recuperación transparente con casos límite que no puedo probar.

El detalle completo del refresh está en §7.

### 3.4 El catálogo de endpoints

`src/api/endpoints.js` declara 4 grupos, 20 funciones:

```text
authApi         register · login · logout · me · recuperar
mesasApi        listar · detalle · crear · actualizar · eliminar · solicitarUnion
sesionesApi     qr · validarQr
matchmakingApi  abrir · estado · anotarse
notifApi        notificaciones · marcarLeida · eventLog · pdf
```

El servicio se elige como primer argumento de `api()`, de modo que agregar una función es agregar una entrada a un objeto — no crear un módulo nuevo ni decidir de nuevo a qué backend pertenece. `mesas` y `notif` tienen funciones; `builds` y `feed` todavía no, aunque sus proxies de nginx y sus variables `VITE_*` ya están preparados.

`solicitarUnion(mesaId, cuerpo, key)` es la única función que recibe una clave de idempotencia **del llamador**, y esa excepción es deliberada: es la que necesita que la clave persista entre intentos (§5).

### 3.5 Resolución de la base URL

`src/config/api.js` resuelve por servicio contra `import.meta.env`:

```js
export const BASE = {
  mesas:  import.meta.env.VITE_MESAS_API  ?? 'http://localhost:8001',
  builds: import.meta.env.VITE_BUILDS_API ?? 'http://localhost:8002',
  feed:   import.meta.env.VITE_FEED_API   ?? 'http://localhost:8003',
  notif:  import.meta.env.VITE_NOTIF_API  ?? 'http://localhost:8004'
}
```

Dos propiedades que quiero dejar explícitas porque tienen consecuencias:

**En desarrollo no hay proxy.** `vite.config.js` no define `server.proxy`; el frontend llama directo a `localhost:8001..8004`, que son los puertos publicados por Compose. La alternativa —un proxy de Vite— daría same-origin en desarrollo, lo que es más limpio, pero agregaría una capa que solo existe en dev y cuya diferencia con producción es justamente lo que hay que probar. Ir directo hace que el desarrollo ejercite el mismo camino de red que producción.

**En producción la URL es de build, no de runtime.** `VITE_*` se inyectan como `ARG`/`ENV` en el `Dockerfile`, y valen `/mesas-api`, `/builds-api`, etc. — rutas relativas que nginx resuelve con `proxy_pass`. La consecuencia es que **cambiar la URL de la API exige reconstruir la imagen**, no alcanza con reiniciar el contenedor. Es la contrapartida de `import.meta.env`, que no existe en runtime. Para un despliegue con URL fija como este es aceptable; en un entorno con URLs por ambiente habría que pasar a runtime config, y lo dejo anotado como deuda.

`nginx.conf` declara los cuatro `location` con sus reescrituras de barra final y los headers `X-Real-IP`, `X-Forwarded-For` y `X-Forwarded-Proto`, más un `/health` propio que usa el healthcheck de Compose.

---

## 4. Autenticación real

*(criterio 4 de la rúbrica, y el frontend de la separación de responsabilidades)*

### 4.1 De la sesión simulada a la sesión real

Antes de F02, la "sesión" era un rol escrito en `localStorage` —`tfinder-rol`— que el guard leía para decidir el acceso. Eso es una demostración de guard, no autenticación: cualquiera podía escribir `admin` en el `localStorage` y obtener permisos.

F02 lo reemplazó por un modelo de sesión real:

```text
localStorage['tfinder-sesion'] = { access, refresh, user }

login -> POST /api/v1/auth/login
      -> guarda access_token y refresh_token
      -> GET /api/v1/auth/me
      -> perfilDe(email, rol) deriva nombre + iniciales
      -> persiste
```

`src/composables/useAuth.js`

`currentRole()` mapea `'admin'` a `admin` y cualquier otro rol verdadero a `auth`, y `null` a `guest`. El guard no sabe qué roles existen en el backend: solo compara contra lo que declara `meta.roles`. Esa separación es la que permite que el guard siga siendo una función pura y testeable sin conocer la API.

`leerGuardada()` valida los tipos del objeto guardado defensivamente y cae a una sesión vacía ante cualquier error de parseo, en lugar de propagar una excepción al montar la aplicación.

### 4.2 La frontera que respeta la separación de responsabilidades

El frontend **no decide permisos**. `meta.roles` decide a qué pantalla puede llegar un usuario según su rol, y nada más. Cada endpoint protegido vuelve a verificar el rol en el backend —abrir matchmaking y validar QR exigen `gm`; event-log, emails y DLQ exigen `admin`—.

Es la separación correcta: la verificación en el frontend es una **experiencia de usuario** —no mostrar una pantalla que va a fallar— y la del backend es la **seguridad**. Que las dos existan no es duplicación, es defensa en profundidad. Un `manual-usuario.md` §17 lo dice con la frase exacta que usaría: *"las restricciones visuales del frontend no sustituyen los permisos del backend"*.

### 4.3 Recuperación de contraseña sin enumerar cuentas

`RecuperarView` muestra siempre el mismo mensaje tras el POST, y esa es la consecuencia de una decisión de backend: `POST /api/v1/auth/recuperar` responde `{"ok": true}` exista o no la cuenta.

Desde el frontend, esto se traduce en no diferenciar la respuesta. Si la UI mostrara "no encontramos ese email" cuando el backend devuelve 200 con un cuerpo distinto, **la propia interfaz se convertiría en el oráculo de enumeración** aunque el backend fuera correcto. Es un ejemplo de por qué un contrato de seguridad se respeta en las dos capas: proteger el endpoint no alcanza si el cliente lo contradice.

---

## 5. Unirse a una mesa: hacer visible la concurrencia

*(criterio 7 de la rúbrica, del lado del cliente)*

### 5.1 La clave que persiste

La acción de unirse es la que corre contra la carrera por la última vacante. La idempotencia no la resuelve solo el backend: el cliente tiene que **reutilizar la misma clave** entre reintentos, o cada intento es una operación nueva.

```js
function keyDe(mesaId, usuarioSub) {
  const almacen = `${PREFIJO}${mesaId}:${usuarioSub}`      // 'tfinder-idem:solicitud:'
  const previa = localStorage.getItem(almacen)
  if (previa) return previa                                   // reintento: misma clave
  const nueva = `${usuarioSub}-${mesaId}-${Date.now().toString(36)}`
  localStorage.setItem(almacen, nueva)
  return nueva
}
```

`src/composables/useSolicitud.js`

La clave se indexa por el par **(mesa, usuario)**, no por acción. Esa elección resuelve los dos casos que importan:

- **Doble clic** → las dos llamadas leen la misma clave y envían la misma.
- **Recarga de página** → la clave persiste en `localStorage` y se reutiliza.

Un doble clic genera dos requests. Una recarga genera otro. Con la clave por par, ambos reutilizan la misma, y el backend —que devuelve el resultado cacheado de la primera— responde idéntico a los dos.

La comparación con la alternativa es lo que da valor a la decisión: si la clave fuera aleatoria en cada llamada, el doble clic crearía dos solicitudes con claves distintas, el backend las trataría como operaciones diferentes y **ambas podrían ocupar vacantes**. La clave aleatoria por llamada es exactamente el error que la idempotencia pretende evitar.

### 5.2 La máquina de estados que muestra el resultado

```js
estado:  inactivo -> enviando -> solicitada   (201)
                                   -> agotada    (otro 2xx, o ApiError 409)
                                   -> error       (cualquier otro)
```

Cada estado tiene su tratamiento visual, y el `409` —que es la respuesta de la carrera— se traduce a un mensaje de "no quedan vacantes" en lugar de un error técnico. El usuario no debería ver un `409 Conflict` por una acción legítima de su parte: si la mesa se llenó mientras miraba, lo que corresponde es un mensaje que lo diga.

La máquina tiene cinco estados y no un `loading` booleano, porque la diferencia entre "agotado" y "error" es información para el usuario, no un matiz: "agotado" es una respuesta válida del negocio y "error" es un fallo del sistema.

### 5.3 La evidencia de la carrera

`MesaDetailView` y `LlamadoCard` usan `useSolicitud`, de modo que el `201` y el `409` del backend son **visibles en la interfaz** en lugar de quedar como un detalle de la respuesta. La evidencia del comportamiento del backend está en `AE2/evidencias/carrera_antes_despues.png` y en `tests/test_idempotencia.py`; la captura del flujo de la interfaz es de la verificación E2E de §8.

---

## 6. Consumo de la asincronía del backend

*(criterios 5 y 6 de la rúbrica, del lado del cliente)*

Esta es la parte de mi trabajo donde se cruzan las dos capas. El backend resolvió concurrencia, caché, mensajería y artefactos asíncronos; el trabajo de la interfaz es **hacer visible y gestionable cada uno de esos contratos**. Un backend asíncrono con un cliente que muestra un spinner indefinido no seQEIFE Synchronous en la percepción del usuario.

### 6.1 Las dos estrategias de polling y por qué dos

| Comportamiento | Intervalo | Dónde | Qué refleja |
|---|---|---|---|
| Badge de notificaciones no leídas | 5 s | `useNotifications.js` | Efecto **asíncrono**: una notificación llega por un evento RabbitMQ consumido por `notif-api` |
| TTL del llamado de matchmaking | 2 s | `useLlamado.js` | **Estado efímero** en Redis: el TTL baja solo, sin que nadie lo escriba |

Las dos hacen polling, y aun así son formatos distintos porque los datos que persiguen tienen características distintas. Las notificaciones son un conjunto que cambia por evento: 5 s es un compromiso entre latencia percibida y carga. El TTL es un **contador regresivo de un valor que Redis ya tiene**: lo que importa es que no se vea congelado, y 2 s es suficiente para que un usuario no note la espera.

**Refcount y timer único.** `useNotifications` mantiene un `suscriptores` de referencia y un solo `setInterval` a nivel de módulo, con `arrancar()` idempotente. Si tres componentes llaman `arrancar()`, hay un solo timer, no tres. Es un detalle pequeño que evita una clase de bug difícil de diagnosticar: tres peticiones cada 5 s que nadie sabe de dónde vienen.

**Autocancelación del intervalo.** En `useLlamado`, el polling de 2 s se cancela solo al primer error (`try { await refrescar() } catch { clearInterval(timer) }`) y también cuando `ttl <= 0`. Un `setInterval` que sigue consultando después de saber que el recurso expiró es ruido de red y una fuente de estado inconsistente.

**Modo degradado.** `useNotifications` distingue fallo de "cero notificaciones": ante un error marca `desconectado = true` y el badge cambia a la icono `sim-bell-off` con el texto "sin conexión a avisos". Esta distinción la aprendí de un caso concreto: la primera versión trataba un fallo de red como "no hay notificaciones", que es la forma más engañosa de mentirle a un usuario.

### 6.2 El `X-Correlation-Id` conecta la UI con los logs

Cada request de `api()` lleva un `X-Correlation-Id` aleatorio. Ese identificador viaja al log del backend, al cuerpo del evento y al log del consumidor.

Para el usuario, esto no es visible. Para el soporte, es la diferencia entre "reportó que no le llegó la notificación" y poder reconstruct el recorrido entero. Es la misma decisión que defendí en backend §8.2 desde el otro lado: **un identificador de correlación que el cliente no genera existe solo para el servidor, y uno que el cliente genera permite diagnosticar desde el navegador**.

### 6.3 El PDF asíncrono: una máquina de estados, no un spinner

F07 implementa la máquina completa del contrato `202` del backend:

```text
inactivo -> enviando  ->  POST .../pdf
                     ->  202 { documento_id }   -> en_cola
                     ->  GET /pdf/{id}/estado   (consulta hasta resolver)
                     ->  listo    -> botón de descarga
                     ->  error    -> "Falló la generación: <motivo>" + reintentar
```

El detalle que importa es el estado `error` con su motivo. El backend marca `documento = 'error'` y **relanza** la excepción para que el mecanismo de reintentos la capture; sin ese relanzamiento, el documento quedaría en `en_proceso` para siempre y la interfaz mostraría un spinner que no termina nunca. Que la UI pueda distinguir "falló" de "todavía no" es consecuencia directa de que el backend tenga tres estados y no dos.

### 6.4 El QR single-use y el `409` que significa algo

`SesionQrView` implementa el par emisión/validación con la cuenta regresiva de 10 minutos y el `409` de uso único.

El `409` es el comportamiento correcto del backend y la UI lo muestra como tal: un `409` en la validación del QR **no es un error**, es la confirmación de que el mecanismo funciona —el QR ya se usó, no se puede reutilizar—. La pantalla dice exactamente eso. Mostrar un `409` como fallo de red habría hecho que un usuario que actúa correctamente creyera que la aplicación se rompió.

### 6.5 La evidencia de la caché, y lo que realmente mide

F03 y F05 muestran un chip de "caché ~X ms", alimentado por `performance.now()` alrededor de la llamada en `src/services/mesas.js`.

Aquí tengo que ser preciso, porque es el punto donde la UI podría dar una impresión engañosa: **ese número no es evidencia del tier de caché**. Mide el tiempo total de la llamada desde el navegador, que incluye red, backend, consulta a Redis o a PostgreSQL, y el proxy. En un `hit` de Redis y en un `miss` con consulta a la base, la diferencia es de milisegundos dentro de un número que domina el tiempo de red.

Lo que sí es evidencia del tier es el header `X-Cache-Tier` que devuelve el backend, y ese dato **se captura y no se muestra** (brecha L12). El chip visible es una medición client-side, útil paraXBILLER ver "responde rápido" pero no para afirmar "esto vino de Redis". La evidencia real del comportamiento de caché está en `tests/test_cache.py`, que cuenta las consultas a la base con un spy, y en `AE2/evidencias/redis_ttl.png`. Dejo la distinción explícita para que el número no se lea como algo que no es.

---

## 7. Testing y deuda técnica

### 7.1 Las 22 pruebas del frontend

| Suite | Casos | Qué cubre |
|---|---|---|
| `tests/unit/feature-gating.spec.js` | 6 | Matriz de `resolveGuard`: feature desactivada, activada, sin backend, sin roles, invitado → login con `redirect`, admin en ruta de invitado |
| `tests/unit/components.spec.js` | 5 | `EmptyState`, `ErrorState` (emite `retry`), `LoadingState` (`role="status"`), `MesaCard`, `BaseModal` (slot) |
| `tests/unit/inventory.spec.js` | 4 | Humo: todos los componentes, vistas, composables y servicios importan y están definidos |
| `tests/integration/http.spec.js` | 2 | `api()` inyecta `Authorization`, `Idempotency-Key` y `X-Correlation-Id`; un `409` se traduce en `ApiError` con `codigo` |
| `tests/integration/services.spec.js` | 5 | `mesas` y `auth` reales: normalización snake→camel, login→`me`→`logout`, notificaciones, `marcarLeida`, propagación de errores |

```bash
cd tfinder-vue
npm run test:unit -- --run            # 15
npm run test:integration -- --run     # 7
npm run lint && npm run type-check    # 0 errores
```

El patrón de `services.spec.js` —`vi.mock` de los endpoints y luego `await import()` del módulo bajo prueba— es necesario por el hoisting de ESM: los mocks se registran antes de que el módulo los importe. Sin eso, el módulo bajo pruebaAgarra la implementación real.

`inventory.spec.js` cumple una función específica: usa `import.meta.glob` con `eager: true` para recorrer todos los módulos y afirmar que cada uno está definido. No prueba comportamiento, pero **detecta un archivo que se rompió al importarse**, que es la clase de fallo que ninguna otra prueba cubre.

### 7.2 La deuda técnica que dejo declarada

| # | Deuda | Impacto | Por qué no la corregí |
|---|---|---|---|
| L9 | **Sin refresh de token.** El `refresh_token` se persiste y nunca se usa; ante un `401` hay redirección dura | El usuario pierde el estado de navegación en cada expiración. El endpoint de refresh existe en el backend (B03) | Es un flujo completo —refresh, rotación, reintento, cuidado con endpoints no idempotentes— y un refresh mal implementado es peor que una redirección clara. Es alcance de AE4 |
| L10 | **Dos implementaciones de "unirse".** `useSolicitud.unirse` (la viva) y `useMesas.unirse` (sin llamadores) | Código muerto con mensajes al usuario distintos | Quedó de una iteración previa a F04. Lo dejo declarado en vez de borrarlo sin verificar que ninguna vista lo use |
| L11 | **14 de 21 features desactivadas**, incluidas las 6 pestañas de `MesaGestionShell`, que llegan a renderizar cero | Vistas inaccesibles por navegación | Es el comportamiento buscado del gate, pero el efecto sobre `tabsVisibles` no lo anticipé y es visible |
| L12 | **`X-Cache-Tier` capturado y no renderizado**; el chip visible es `performance.now()` | La UI no muestra el tier real de caché | Explicado en §6.5. El chip es correcto; lo que no debe hacer es leerse como evidencia del tier |
| — | **`@testing-library/vue` reducido a `cleanup()`**; todos los componentes se montan con `@vue/test-utils` | Los tests no usan queries por rol o texto accesible | Se siguió el estilo del proyecto (test-utils) sin adoptar el segundo. Funciona; es una inconsistencia de enfoque |
| — | **Sin `test:watch`**, sin umbrales de cobertura, sin tests de composables con polling | Falta cobertura sobre el timer de 2 s y la redirección por `401` | Añadidos en AE4 |
| — | **Docs desfasadas**: `ENTREGA.md` dice 44 rutas (hay 46) y muestra el servicio leyendo `mesas.json`; `GUIA_USO.md` §2 instruye escribir `tfinder-rol` en `localStorage`, que ya no existe | Un lector que siga la guía no puede reproducir el estado de sesión | No las actualicé al cierre de AE2. Es la deuda más fácil de corregir de la lista |

La última es la que más lamento, porque una documentación que describe cómo hacer algo que ya no funciona es peor que no tener documentación: hace perder tiempo con seguridad.

---

## 8. Trazabilidad individual

### 8.1 Rama y commits

```bash
git log --oneline origin/A2-Frontend
```

```text
bf3774c  feat(web): capa HTTP unificada con auth, idempotencia y correlation id (F01)      #26
ed696f2  feat(web): auth real contra mesas-api (tokens access/refresh, registro, recuperar) (F02)   #27
229fee5  feat(web): mesas reales contra mesas-api con evidencia de cach Redis (F03)       #28
a44264b  feat(web): unirse a mesa real con carrera de vacantes e idempotencia (F04)       #29
f76e883  feat(web): matchmaking real contra mesas-api con TTL Redis en vivo (F05)       #30
31bd32f  feat(frontend): sesión en curso con QR de asistencia single-use y validación del GM (F06)  #31
2c57f14  feat(frontend): exportar PDF async real (202 en cola → listo) (F07)              #32
1b13721  feat(notif): notificaciones en vivo vía polling 5s + PATCH leída (F08)            #33
4dcba75  feat(admin): observabilidad real (live/ready), DLQ con reintento/descarte (F09)   #34
dd7674e  feat(web): feature gating con ComingSoon y suite vitest para el frontend
```

F01–F05 se desarrollaron en `origin/A2-Frontend` como rama propia, separada de la rama de desarrollo. F06–F09 y el feature gating se integraron en la rama de integración, que es donde se conectaron con los endpoints del backend que los soportan. La trazabilidad por issue está en el sufijo del commit y en las tareas de `openspec/changes/`.

### 8.2 OpenSpec

Cada bloque F01–F09 tiene un cambio en `openspec/changes/` con su `proposal.md` y sus `tasks.md`, y su capacidad publicada en `openspec/specs/`. Los requirements están en formato GIVEN/WHEN/THEN, lo que hace que cada comportamiento de interfaz sea verificable.

### 8.3 Evidencias

Las evidencias de los comportamientos que la interfaz expone están en `AE2/evidencias/`, generadas por `python scripts/generar_evidencias.py`:

| Evidencia | Criterio | Qué muestra la interfaz |
|---|---|---|
| `redis_ttl.png` | 6 | Que el listado responde con evidencia del tier de caché |
| `carrera_antes_despues.png` | 7 | El `201` y el `409` de la carrera de vacantes |
| `qr_single_use.png` | 9 | La validación `200` y luego `409` del QR de un solo uso |
| `pdf_202_y_ficha.png` | 9 | El `202` con `documento_id` y la descarga `200 application/pdf` |
| `sse_notificaciones.png` | 8 | El consumo de notificaciones en vivo |
| `email_mailhog.png` | 9 | El email que el usuario recibe tras unirse |
| `ready_live.png` / `ready_degradado.png` | 13 | El panel de observabilidad con los cuatro servicios |

---

## 9. Fundamentación

### 9.1 Las decisiones de este alcance

| Decisión | Alternativa descartada | Por qué |
|---|---|---|
| Un solo `api()` para toda la red | `fetch` en cada componente | Agregar un header, un timeout o un manejo de `401` en quince componentes es quince lugares donde olvidarse. El punto único hace que esas tres cosas se cambien en un archivo |
| `fetch` nativo | Axios / ky | Axios agrega transformadores de request y response que no se usan, e interceptores que el diseño descarta (no hay refresh). Se paga una dependencia por funcionalidad no usada |
| Sin Pinia | Store global | Siete piezas de estado no justifican la librería. El singleton de módulo cumple la misma función sin la dependencia |
| `resolveGuard` como función pura | Lógica dentro del `beforeEach` | Permite probar la matriz de acceso completa sin montar un router, y hace la guarda refactorizable |
| `Idempotency-Key` en `localStorage` por par (mesa, usuario) | Clave aleatoria por llamada | La clave por llamada es exactamente lo que rompe la idempotencia: un doble clic crearía dos operaciones distintas y ambos podrían ocupar vacantes |
| `provide`/`inject` en `MesaGestionShell` | Singleton de módulo | El estado de gestión es jerárquico, y `provide` expresa esa relación mejor que un store al que todas las vistas podrían alcanzar |
| Base URL por `ARG` de build | Config en runtime | `import.meta.env` no existe en runtime. El costo es que cambiar la URL exige reconstruir la imagen; se acepta con URL fija por ambiente |
| Feature gate antes que auth en el guard | Auth primero | Pedir autenticación para comprobar que una función no existe es fricción sin propósito. El invitado debe ver "Próximamente", no el login |

### 9.2 El criterio que las atraviesa

Las ocho decisiones se pueden resumir en una: **la respuesta a la pregunta "¿qué pasa cuando esto falla?"**.

- ¿El servicio no responde? → timeout de 8 s con mensaje que dice qué servicio y en qué puerto.
- ¿La sesión expiró? → limpieza y redirección con el destino preservado, sin dejar la interfaz en un estado intermedio.
- ¿La mesa se llenó? → `409` traducido a "no quedan vacantes", que es una respuesta del negocio y no un fallo.
- ¿El PDF falló? → estado `error` con el motivo y botón de reintentar, no un spinner infinito.
- ¿Las notificaciones no llegan? → modo degradado explícito, no "cero notificaciones".
- ¿El QR ya se usó? → mensaje que dice que el QR fue usado, no un error de red.

El patrón común es **no presentar un fallo técnico como si fuera un estado normal, ni un estado normal como si fuera un fallo**. En una interfaz con estos contratos, esa distinción es casi toda la diferencia entre una aplicación que se siente confiable y una que parece rota.

---

## 10. Conclusión

Mi alcance en AE2 fue llevar el frontend de TFinder de un prototipo con datos incrustados y una sesión simulada a una aplicación Vue 3 con 46 rutas, una capa HTTP única con autenticación, idempotencia y correlación reales, y la capacidad de hacer **visible en la interfaz** los contratos que el backend resolvió: la carrera por la última vacante, el TTL en Redis, el PDF asíncrono, el QR de un solo uso y el modo degradado de notificaciones.

Lo que más rescato del trabajo:

**Hacer visible lo que el backend resolvió.** Un backend que resuelve la concurrencia correctamente no se percibe desde la interfaz si esta muestra siempre un spinner. El trabajo de hacer tangible el `201`, el `409`, el `202` y el `en_proceso` es tan parte del contrato como el endpoint mismo.

**Un solo punto de paso hacia la red.** Es la decisión de la que más dependió todo lo demás: sin ella, el `X-Correlation-Id`, el timeout, el manejo de `401` y la idempotencia habrían sido quince decisiones en quince archivos.

**Persistir la clave de idempotencia por par (mesa, usuario).** Es un detalle pequeño que cierra el circuito de la concurrencia de extremo a extremo: la garantía del backend es que la misma clave devuelve el mismo resultado, y sin reutilizar la clave en el cliente, esa garantía nunca se ejerce.

**Ser explícito sobre lo que un número no mide.** El chip de "caché ~X ms" es una medición real y útil, pero no es evidencia del tier de caché. Preferí dejarlo declarado a presentarlo como si lo fuera.

Las deudas de §7.2 están declaradas con su impacto. La de refresh de token (L9) es la primera corrección de AE4, porque el endpoint ya existe en el backend y es trabajo puramente del cliente.
