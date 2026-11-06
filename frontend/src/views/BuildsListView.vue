<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth.js'
import { getMisBuilds, getBuildsPublicos, forkBuild } from '@/services/builds.js'

const router = useRouter()
const { isAuthenticated } = useAuth()

const pestaña = ref('mis')
const buscador = ref('')
const orden = ref('recientes')
const tipoFiltro = ref('todos')
const mios = ref([])
const publicos = ref([])
const cargando = ref(true)
const fallo = ref(null)

const ordenadoMios = computed(() => ordenar(mios.value))
const ordenadoPublicos = computed(() => ordenar(publicos.value))

const visibles = computed(() => {
  const base = pestaña.value === 'mios' ? ordenadoMios.value : ordenadoPublicos.value
  let resultado = base
  if (tipoFiltro.value !== 'todos') {
    resultado = resultado.filter((b) => (b.tipo || 'personaje') === tipoFiltro.value)
  }
  const termino = buscador.value.trim().toLowerCase()
  if (!termino) return resultado
  return resultado.filter((b) => `${b.nombre} ${b.clase} ${b.arquetipo} ${b.detalle} ${b.tipo}`.toLowerCase().includes(termino))
})

const MIS_SLOTS = 6

function ordenar(lista) {
  const copia = [...lista]
  if (orden.value === 'nivel') return copia.sort((a, b) => b.nivel - a.nivel)
  if (orden.value === 'valorados') return copia.sort((a, b) => b.favoritos - a.favoritos)
  return copia
}

async function cargar() {
  cargando.value = true
  fallo.value = null
  try {
    const [mis, publ] = await Promise.all([getMisBuilds(), getBuildsPublicos()])
    mios.value = mis
    publicos.value = publ
  } catch (e) {
    fallo.value = e.message || 'No pudimos cargar la biblioteca de builds.'
  } finally {
    cargando.value = false
  }
}

onMounted(() => {
  pestaña.value = isAuthenticated.value ? 'mios' : 'publicos'
  cargar()
})

async function crearPropia(id) {
  try {
    const nuevo = await forkBuild(id)
    router.push(`/builds/${nuevo.id}/editar`)
  } catch (e) {
    console.error(e)
  }
}
</script>

<template>
  <div class="app-grid">
    <aside class="sidebar">
      <div class="well">
        <p class="label" style="margin-bottom: var(--space-2xs);">Tipo</p>
        <select class="input" v-model="tipoFiltro" aria-label="Filtrar por tipo">
          <option value="todos">Todos</option>
          <option value="personaje">Personaje</option>
          <option value="objeto">Objeto</option>
          <option value="lugar">Lugar</option>
          <option value="criatura">Criatura</option>
          <option value="nota">Nota</option>
        </select>
        <p class="label" style="margin-block: var(--space-2xs);">Orden</p>
        <select class="input" v-model="orden" aria-label="Ordenar builds">
          <option value="recientes">Más recientes</option>
          <option value="nivel">Mayor nivel</option>
          <option value="valorados">Mejor valorados</option>
        </select>
        <p class="label" style="margin-block: var(--space-2xs);">Buscar</p>
        <input class="input" v-model="buscador" type="search" placeholder="nombre, clase, dote…" aria-label="Buscar builds" />
      </div>
    </aside>
    <main>
      <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: var(--space-sm); margin-bottom: var(--space-md);">
        <div>
          <h2><span>✦</span> Mis Builds</h2>
          <p class="label">Gestiona tus hojas de ruta tácticas, progresiones y arquetipos de Pathfinder 1e, o explora la biblioteca comunitaria.</p>
        </div>
        <button v-if="isAuthenticated" type="button" class="btn" @click="router.push('/builds/asistente')">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round"></path>
          </svg>
          <span>Crear Build</span>
        </button>
      </div>

      <div style="display: flex; gap: var(--space-2xs); flex-wrap: wrap; margin-bottom: var(--space-md);">
        <button type="button" class="filtro-btn" :aria-pressed="pestaña === 'publicos'" @click="pestaña = 'publicos'">Explorar públicas</button>
        <button v-if="isAuthenticated" type="button" class="filtro-btn" :aria-pressed="pestaña === 'mios'" @click="pestaña = 'mios'">Mis builds</button>
      </div>

      <div class="card" style="padding: var(--space-md);">
        <h3 style="margin: 0 0 var(--space-md);">{{ pestaña === 'mios' ? 'Mis builds' : 'Builds públicos' }}</h3>

        <div v-if="cargando" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5" role="status" aria-live="polite">
          <div v-for="n in 4" :key="n" class="card" style="padding: var(--space-md);">
            <div class="skel" style="height: 14px; width: 40%; margin-bottom: var(--space-2xs);"></div>
            <div class="skel" style="height: 18px; width: 75%; margin-bottom: var(--space-2xs);"></div>
            <div class="skel" style="height: 12px; width: 50%; margin-bottom: var(--space-2xs);"></div>
            <div class="skel" style="height: 12px; width: 66%;"></div>
          </div>
        </div>

        <div v-else-if="fallo" style="padding: var(--space-xl); text-align: center;" role="alert">
          <p class="label" style="color: var(--color-error); margin-bottom: var(--space-2xs);">La biblioteca está oculta</p>
          <p style="color: var(--color-ink-2);">{{ fallo }}</p>
          <button type="button" class="btn btn--secondary" style="margin-top: var(--space-md);" @click="cargar">Reintentar</button>
        </div>

        <div v-else-if="visibles.length === 0" style="padding: var(--space-xl); text-align: center;">
          <h3>Ningún pergamino coincide</h3>
          <p class="label" style="margin-top: var(--space-2xs);">
            {{ pestaña === 'mios' ? 'Crea tu primer héroe o ajusta el filtro de búsqueda.' : 'La búsqueda no encontró builds públicos.' }}
          </p>
        </div>

        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <article v-for="build in visibles" :key="build.id" class="card" style="padding: var(--space-md); display: flex; flex-direction: column; justify-content: space-between; position: relative;">
            <div>
              <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-2xs);">
                <span v-if="(build.tipo || 'personaje') === 'personaje'" class="tag tag--ink">Nivel {{ build.nivel }}</span>
                <span class="tag tag--acid" style="margin-left: var(--space-2xs);">{{ (build.tipo || 'personaje') }}</span>
                <div style="display: flex; align-items: center; color: var(--color-muted);" :title="build.privacidad === 'privado' || build.privacidad === 'borrador' ? 'Privado' : 'Público'">
                  <svg v-if="build.privacidad === 'privado' || build.privacidad === 'borrador'" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" stroke-linecap="round" stroke-linejoin="round"></path>
                  </svg>
                  <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"></path>
                  </svg>
                </div>
              </div>
              <h3 style="margin: 0; font-size: var(--text-md);">{{ build.display }}</h3>
              <p style="font-size: var(--text-sm); font-weight: 700; color: var(--color-ink-2); margin-top: var(--space-3xs);">{{ build.clase }} ({{ build.arquetipo }})</p>
              <p class="label" style="margin-top: var(--space-3xs);">Por {{ build.autor }}</p>
              <div style="margin-top: var(--space-sm); padding-top: var(--space-2xs); border-top: var(--rule-hair) solid var(--color-rule); font-size: var(--text-xs); display: grid; gap: var(--space-3xs);">
                <div style="display: flex; justify-content: space-between;">
                  <span class="label">ROL:</span>
                  <span style="font-weight: 700;">{{ build.rol }}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                  <span class="label">ALINEAMIENTO:</span>
                  <span style="font-weight: 700;">{{ build.alineamiento }}</span>
                </div>
              </div>
            </div>
            <div style="margin-top: var(--space-md); padding-top: var(--space-2xs); border-top: var(--rule-hair) solid var(--color-rule); display: flex; align-items: center; justify-content: space-between;">
              <span class="label">{{ build.actualizado }}</span>
              <div style="display: flex; gap: var(--space-2xs);">
                <button
                  v-if="isAuthenticated && pestaña === 'publicos' && (build.privacidad === 'publico')"
                  type="button"
                  class="btn btn--secondary btn--sm"
                  @click="crearPropia(build.id)"
                >
                  Crear propia
                </button>
                <button
                  type="button"
                  class="btn btn--secondary btn--sm"
                  @click="router.push(`/builds/${build.id}`)"
                >
                  <span v-if="build.privacidad === 'privado' || build.privacidad === 'borrador'">Editar Build</span>
                  <span v-else>Ver Ficha</span> →
                </button>
              </div>
            </div>
          </article>

          <RouterLink
            v-if="pestaña === 'mios' && mios.length < MIS_SLOTS"
            to="/builds/asistente"
            class="card"
            style="padding: var(--space-md); border-style: dashed; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; min-height: 220px; text-decoration: none; color: inherit;"
          >
            <div style="width: 48px; height: 48px; border-radius: var(--radius-card); background: var(--color-paper-3); border: var(--rule-hair) solid var(--color-rule); display: grid; place-items: center; color: var(--color-muted); margin-bottom: var(--space-sm);">
              <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round"></path>
              </svg>
            </div>
            <span style="font-weight: 700;">Crear Nuevo Build</span>
            <p class="label" style="margin-top: var(--space-2xs); max-width: 190px;">Importar desde Pathbuilder 1e o diseñar una progresión de niveles desde cero.</p>
          </RouterLink>
        </div>

        <div style="margin-top: var(--space-lg); padding-top: var(--space-sm); border-top: var(--rule-hair) solid var(--color-rule); display: flex; flex-direction: column; gap: var(--space-2xs); font-size: var(--text-xs); color: var(--color-muted);">
          <span>{{ visibles.length }} ficha{{ visibles.length === 1 ? '' : 's' }} · página 1 de 1</span>
          <span>{{ pestaña === 'mios' ? `Slot de personaje: ${mios.length}/${MIS_SLOTS}` : 'Biblioteca comunitaria PF1e · OGL v1.0a' }}</span>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: 240px minmax(0, 1fr); gap: var(--space-lg); align-items: start; }
.sidebar .well { padding: var(--space-md); margin-bottom: var(--space-md); }
.sidebar .side-item { display: flex; align-items: center; gap: var(--space-2xs); padding: var(--space-2xs) var(--space-sm); border-radius: var(--radius-card); font-size: var(--text-sm); font-weight: 700; color: var(--color-ink-2); text-decoration: none; }
.sidebar .side-link { background: none; border: 0; width: 100%; text-align: left; cursor: pointer; }
.sidebar .side-link:hover { background: var(--color-paper-3); }
.sidebar .side-link[aria-pressed="true"] { background: var(--color-accent); color: var(--color-accent-ink); }
@media (max-width: 75rem) { .app-grid { grid-template-columns: minmax(0, 1fr); } .sidebar { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--space-md); } .sidebar .well { margin-bottom: 0; } }
@media (max-width: 60rem) { .app-grid { grid-template-columns: minmax(0, 1fr); padding-top: 120px; } .sidebar { grid-template-columns: minmax(0, 1fr); } }
</style>