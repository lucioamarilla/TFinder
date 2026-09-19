# Entrega · Listado de mesas con datos reactivos (Vue 3)

**Materia:** Paradigmas III · **Proyecto:** TFinder (frontend)
**Carpeta del proyecto:** `tfinder-vue/`
**Objetivo de la consigna:** la plantilla del componente no debe contener datos
hardcodeados ni manipular el DOM de forma imperativa. El listado debe armarse
con directivas (`v-for`, `v-if`/`v-else`) y estado reactivo (`ref`), consumiendo
un JSON de prueba a través de un servicio.

---

## 1. Antes

Fuente: `tfinder-prototipo-nuevo/pantalla_2_listado_de_mesas_explorar/index.html`
(pantalla estática del prototipo). El listado se escribía a mano, repitiendo la
misma estructura de tarjeta **seis veces**, una por mesa, con los datos
incrustados directamente en el markup:

```html
<!-- GRID DE TARJETAS: 3 columnas -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-8">

  <!-- Tarjeta 1 -->
  <article class="card-parchment p-4 rounded-[2px] book-spine-accent pl-5 flex flex-col justify-between">
    <div>
      <div class="flex items-start justify-between gap-2 mb-1.5">
        <h3 class="font-mason text-[1.1rem] text-[#8B5A2B] font-bold leading-tight">
          La Corona de Carroña
        </h3>
        <div class="flex items-center gap-1 shrink-0">
          <span class="font-tarzana ... bg-[#1A1A1A] ...">PF1e</span>
          <span class="font-tarzana ... bg-[#6B8E23] ...">Abierta</span>
        </div>
      </div>
      <p class="font-minion italic ...">
        Dirigida por <span class="font-semibold text-[#8B5A2B]">Aldren van Richten</span>
      </p>
      <p class="font-minion text-xs ... line-clamp-3 mb-3">
        Investigación gótica en Ustalav. Buscamos personajes enfocados en religión,
        ocultismo y combate táctico metódico.
      </p>
    </div>
    <div class="pt-2 border-t border-[#C2A980]/50 flex items-center justify-between mt-2">
      <span class="font-tarzana ...">⚔ 4/6 Jugadores</span>
      <a href="#" class="font-tarzana ... btn-link-details uppercase tracking-wider">
        Ver detalles →
      </a>
    </div>
  </article>

  <!-- Tarjeta 2 ... repetida para cada mesa, con otros datos incrustados ... -->
  <!-- Tarjeta 3 ... -->
  <!-- Tarjeta 4 ... -->
  <!-- Tarjeta 5 ... -->
  <!-- Tarjeta 6 ... -->
</div>
```

**Problemas del enfoque "antes":**

- Cada mesa es **markup duplicado**: cambiar una tarjeta obliga a repetir el
  cambio seis veces.
- Los datos están **incrustados** en el HTML; cambiar un dato implica editar el
  documento, no el estado.
- No existe **estado** de carga, error ni vacío: si no hubiera mesas, no hay forma
  de representarlo sin borrar el bloque a mano.
- Los enlaces son `href="#"` (navegación simulada).

---

## 2. Después

El listado pasa a ser un único componente que **recorre el estado reactivo** y
delega la tarjeta en un componente presentacional.

### 2.1 Vista principal del listado

Archivo real: `tfinder-vue/src/views/MesasListView.vue`

```vue
<script setup>
import { computed, onMounted } from 'vue'
import { useMesas } from '@/composables/useMesas'
import MesaCard from '@/components/MesaCard.vue'
import LoadingState from '@/components/LoadingState.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'

const { mesas, isLoading, error, load, retry } = useMesas()

const hayMesas = computed(() => mesas.value.length > 0)
const resumen = computed(() => {
  if (isLoading.value) return 'Cargando…'
  return `${mesas.value.length} mesas disponibles`
})

onMounted(load)
</script>

<template>
  <div class="tf-container">
    <header class="tf-section-head">
      <div>
        <p class="tf-eyebrow">Explorar</p>
        <h1 class="tf-title">Mesas abiertas</h1>
      </div>
      <p class="tf-meta">{{ resumen }}</p>
    </header>

    <LoadingState v-if="isLoading" />

    <ErrorState v-else-if="error" :message="error" @retry="retry" />

    <EmptyState v-else-if="!hayMesas">
      <RouterLink class="tf-btn tf-btn--gold" to="/perfil">
        Crear una mesa
      </RouterLink>
    </EmptyState>

    <section v-else class="tf-grid" aria-label="Listado de mesas">
      <MesaCard v-for="mesa in mesas" :key="mesa.id" :mesa="mesa" />
    </section>
  </div>
</template>
```

### 2.2 Estado reactivo del listado

Archivo real: `tfinder-vue/src/composables/useMesas.js`

```js
import { ref } from 'vue'
import { getMesas } from '@/services/mesas'

export function useMesas() {
  const mesas = ref([])
  const isLoading = ref(true)
  const error = ref(null)

  async function load() {
    isLoading.value = true
    error.value = null
    try {
      mesas.value = await getMesas()
    } catch (err) {
      mesas.value = []
      error.value =
        err instanceof Error ? err.message : 'Ocurrió un error inesperado.'
    } finally {
      isLoading.value = false
    }
  }

  function retry() {
    return load()
  }

  return { mesas, isLoading, error, load, retry }
}
```

### 2.3 Servicio que consume el JSON de prueba

Archivo real: `tfinder-vue/src/services/mesas.js`

```js
import mesasData from '@/data/mesas.json'

const LATENCIA_SIMULADA_MS = 400

function esperar(ms = LATENCIA_SIMULADA_MS) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export async function getMesas() {
  await esperar()
  return mesasData.map((mesa) => ({ ...mesa, etiquetas: [...mesa.etiquetas] }))
}

export async function getMesa(id) {
  await esperar()
  const mesa = mesasData.find((item) => item.id === id)
  if (!mesa) {
    throw new Error(`No encontramos ninguna mesa con el identificador "${id}".`)
  }
  return { ...mesa, etiquetas: [...mesa.etiquetas] }
}
```

### 2.4 Tarjeta presentacional

Archivo real: `tfinder-vue/src/components/MesaCard.vue` (fragmento): recibe la
entidad por props y solo la muestra.

```vue
<script setup>
defineProps({
  mesa: { type: Object, required: true }
})
</script>

<template>
  <article class="tf-card tf-mesa-card">
    <p class="tf-meta">{{ mesa.sistema }}</p>
    <h3 class="tf-mesa-card__title">{{ mesa.nombre }}</h3>
    <p class="tf-mesa-card__lore">{{ mesa.lore }}</p>
    <!-- ... gm, nivel, frecuencia, cupos ... -->
    <ul class="tf-tags">
      <li v-for="etiqueta in mesa.etiquetas" :key="etiqueta" class="tf-badge">
        {{ etiqueta }}
      </li>
    </ul>
    <RouterLink class="tf-btn tf-btn--outline" :to="`/mesas/${mesa.id}`">
      Ver mesa
    </RouterLink>
  </article>
</template>
```

### 2.5 Origen de los datos

Archivo real: `tfinder-vue/src/data/mesas.json` — arreglo de 10 mesas, cada una
con `id`, `nombre`, `sistema`, `lore`, `gm`, `nivel`, `frecuencia`, `jugadores`,
`plazas`, `vacante` y `etiquetas`.

---

## 3. Explicación técnica

### 3.1 Template declarativo, sin datos incrustados

El único lugar con datos es `mesas.json`. El template **no menciona ninguna
mesa**: describe la *forma* de la lista. `v-for` proyecta la colección reactiva
y `:key="mesa.id"` da a Vue una identidad estable por fila (imprescindible para
un diff correcto y para evitar re-render innecesario).

### 3.2 Directivas usadas

| Directiva | Dónde | Para qué |
| --- | --- | --- |
| `v-for` + `:key` | grid de mesas y etiquetas | iterar la colección/atributos del estado |
| `v-if` / `v-else-if` / `v-else` | `MesasListView` | alternar carga / error / vacío / contenido |
| `:mesa`, `:to`, `:message` | `MesaCard`, `RouterLink`, `ErrorState` | pasar datos y rutas por binding, no por texto fijo |
| `@retry` | `ErrorState` | evento declarativo para reintentar |
| `{{ }}` | títulos y metadatos | interpolación segura (texto, sin `innerHTML`) |

No se usa ninguna API imperativa del DOM en todo `src/` (verificado por
búsqueda: `getElementById`, `querySelector`, `innerHTML`, `insertAdjacentHTML`,
`replaceChild`, `createElement` → 0 coincidencias). El navegador actualiza el
DOM porque Vue lo hace por nosotros a partir del estado.

### 3.3 Estado reactivo

`useMesas()` encapsula el estado del listado con `ref`:

- `mesas` → colección (arranca `[]`).
- `isLoading` → **arranca en `true`**, para que la UI muestre carga desde el
  primer render.
- `error` → mensaje de fallo o `null`.

`computed` (`hayMesas`, `resumen`) deriva valores sin duplicar estado: no
guardamos "hay mesas" ni "cuántas" por separado, se calculan.

### 3.4 Ciclo de vida y consumo del servicio

El fetch se dispara **una vez montado el componente**, no antes:

```js
onMounted(load)
```

`load()` es `async` y está envuelto en `try/catch/finally`. El `finally` pone
`isLoading` en `false` **siempre**, haya éxito, error o resultado vacío, de modo
que el flag de carga nunca queda colgado. El `error` se captura en el
`catch`, que además limpia la colección para no mostrar datos viejos.

### 3.5 Datos de prueba con latencia

`services/mesas.js` importa `mesas.json` **como módulo** (no hace red) y devuelve
`Promise`s con una espera de ~400 ms. Esa latencia existe para que el estado de
carga sea observable y la UI se comporte como lo hará con un backend real. Cambiar
a un backend más adelante es reemplazar el cuerpo del servicio, sin tocar la
vista.

### 3.6 Estados no nominales

- **Carga:** `LoadingState` (esqueletos + `role="status"`).
- **Error:** `ErrorState` con mensaje y botón *Reintentar* (`@retry` → `retry()`
  vuelve a ejecutar `load`).
- **Vacío:** `EmptyState` con un llamado a la acción.
- **Detalle inexistente:** `getMesa(id)` rechaza y `MesaDetailView` muestra el
  estado *not-found* con enlace de vuelta al listado.

### 3.7 Rutas de la entrega original (subconjunto)

Estas son las rutas mínimas de la consigna; el router completo de la app expandida
se documenta en la sección 4.6.

| Ruta | Vista |
| --- | --- |
| `/` | `LandingView` |
| `/mesas` | `MesasListView` (consigna) |
| `/mesas/:id` | `MesaDetailView` (con estado not-found) |
| `/perfil` | `PerfilView` |

### 3.8 Cómo ejecutar

```bash
cd tfinder-vue
npm install
npm run dev      # servidor de desarrollo
npm run build    # build de producción
```

### 3.9 Verificación realizada

- `npm run build` compila sin errores.
- Chequeo estático: 0 usos de APIs de DOM imperativo y 0 nombres de mesas fuera
  de `data/`.
- Chequeo de datos: 10 mesas, todos los campos presentes, `id` únicos.
- Chequeo de runtime del estado: `isLoading` arranca en `true` y termina en
  `false` una sola vez (éxito y reintento), la colección se puebla desde el
  servicio y `getMesa(id)` rechaza para un `id` inexistente.

---

## 4. Capa reactiva expandida (port completo)

La consigna original pedía una única vista reactiva (`/mesas`). El port posterior
llevó el mismo patrón a **toda la aplicación**, de modo que el entregable sigue
siendo la misma idea —*el template no contiene datos ni toca el DOM*— pero
aplicada a cada entidad del dominio.

### 4.1 Servicios por entidad

`tfinder-vue/src/services/` contiene **14 servicios**, cada uno responsable de
una entidad o capacidad. Todos comparten la misma forma: importan su JSON de
prueba, esperan una latencia simulada y devuelven copias (nunca la referencia
del módulo), de modo que mutar el resultado no corrompe el "catálogo".

| Servicio | Responsabilidad |
| --- | --- |
| `mesas.js` | listar/leer mesas, crear y eliminar |
| `membresias.js` | mesas a las que pertenece el usuario y su rol |
| `sesiones.js` | sesiones por mesa y diarios por sesión |
| `wiki.js` | árbol de páginas, lectura y guardado del editor |
| `jugadores.js` | miembros de una mesa y solicitudes |
| `votaciones.js` | votos de calendario (votar / desvotar) |
| `builds.js` | builds, versiones e historial |
| `feed.js` | feed social, votos, guardado y alta de posts |
| `usuarios.js` | padrón público de usuarios |
| `notificaciones.js` | bandeja, marcar leída / todas leídas |
| `actividad.js` / `eventos.js` | widgets del dashboard |
| `matchmaking.js` | candidatos, solicitudes y llamado abierto |
| `admin.js` | consola de administración (moderación, usuarios, telemetría, DLQ, resiliencia, Prometheus) |

Los errores se modelan lanzando `Error` cuando la entidad no existe o la entrada
es inválida (p. ej. `getMesa(id)` con `id` inexistente, `guardarResiliencia` fuera
de rango); las vistas los capturan y los convierten en estado de error.

### 4.2 Datos de prueba

`tfinder-vue/src/data/` reúne **23 archivos JSON** (incluyendo `admin/*.json`),
una fuente por servicio. El template nunca menciona nombres de dominio: recorre
la colección con `v-for` y `:key`.

### 4.3 Patrón de estados no nominales

Todas las vistas que consumen un servicio alternan los mismos cuatro estados:

| Estado | Cómo se representa |
| --- | --- |
| **Carga** | `LoadingState.vue`, o bien un bloque `v-if="isLoading"` con `role="status"` y `aria-live="polite"` |
| **Error** | `ErrorState.vue` (props `title`/`message`/`isNotFound`, emit `retry`) o bloque propio con botón *Reintentar* |
| **Vacío** | `EmptyState.vue` o bloque `v-if="…length === 0"` con llamado a la acción |
| **No encontrado** | `getX(id)` rechaza → vista de not-found con enlace de vuelta |

El flag de carga se resuelve siempre en `finally`, de modo que nunca queda
"colgado" tras un fallo; el `catch` limpia la colección para no mostrar datos
viejos.

### 4.4 Composables

- `useAuth.js` — sesión y roles (`guest`/`auth`/`admin`) para el guard de rutas.
- `useNotifications.js` — conteo de no leídas que alimenta el badge de la campana.
- `useToast.js` — cola de toasts (`ok`/`error`/`info`) con auto-cierre.
- `useShell.js` — estado del menú móvil.
- `useMesas.js` — estados del listado de la consigna original.

### 4.5 Shells por rol

`App.vue` elige el layout según el rol de la sesión; los tres envuelven
`AppShell` (cabecera, menú móvil, `ToastHost`, `<main class="tf-main">`, pie):

- `GuestLayout` — invitado (landing, login, registro).
- `AppLayout` — usuario autenticado.
- `AdminLayout` — administrador (consola `/admin/*`).

### 4.6 Cobertura de rutas

El router declara **44 rutas**: públicas, de autenticación, sociales
(feed/perfil/usuarios/notificaciones), mesas y su gestión por tabs
(`/mesas/:id/gestion|wiki|calendario|sesiones|jugadores|builds`), builds
(lista/ficha/editor/asistente/historial), tags, encuentros, matchmaking y las 10
rutas de la consola `/admin/*`.

### 4.7 Accesibilidad

- **Foco visible global:** regla `:focus-visible { outline: 2px solid var(--tf-gold) }`
  en `tokens.css`, más realce de borde/sombra en inputs de `crono.css`.
- **Targets táctiles ≥ 44 px:** botones de acción y paginación usan `min-h-[44px]`
  (y `min-w-[44px]` los cuadrados).
- **Señales no solo de color:** los estados de salud, nivel de log y estado de
  breaker combinan color **y** texto o glifo.
- **Etiquetado:** los botones solo-icono llevan `aria-label`/texto accesible; los
  overlays con `@click.self` cuentan con cierre por teclado.

### 4.8 Verificación del port

- `npm run build` en verde (43 vistas y 16 componentes en chunks separados).
- `rg` sobre `src/`: **0** usos de `getElementById`, `querySelector`, `innerHTML`,
  `insertAdjacentHTML`, `replaceChild` o `createElement`.
- Auditoría de estados: toda vista que importa un servicio expone carga y manejo
  de error; las sub-vistas de gestión heredan carga/not-found del
  `MesaGestionShell`.
- Auditoría de accesibilidad: 0 botones solo-icono sin etiqueta, 0 targets por
  debajo de 44 px, foco visible global.
