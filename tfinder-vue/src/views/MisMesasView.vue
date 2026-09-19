<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMembresias } from '@/services/membresias'

const router = useRouter()
const membresias = ref([])
const isLoading = ref(true)
const error = ref(null)

const rolTab = ref('gm')
const busqueda = ref('')
const estadoFiltro = ref('Todas')

const opcionesEstado = ['Todas', 'Abiertas', 'En Pausa', 'Cerradas']

async function load() {
  isLoading.value = true
  error.value = null
  try {
    membresias.value = await getMembresias()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Ocurrió un error inesperado.'
  } finally {
    isLoading.value = false
  }
}

const rolGm = computed(() => membresias.value.filter((m) => m.rol === 'gm'))
const rolJugador = computed(() => membresias.value.filter((m) => m.rol === 'jugador'))

const visibles = computed(() => {
  const base = rolTab.value === 'gm' ? rolGm.value : rolJugador.value
  const q = busqueda.value.trim().toLowerCase()
  return base.filter((m) => {
    const coincideTexto =
      !q || [m.nombre, m.capitulo, m.personaje].filter(Boolean).join(' ').toLowerCase().includes(q)
    const coincideEstado = estadoFiltro.value === 'Todas' || m.estado === estadoFiltro.value
    return coincideTexto && coincideEstado
  })
})

const opsAplicadas = computed(() => Boolean(busqueda.value.trim()) || estadoFiltro.value !== 'Todas')

function limpiarFiltros() {
  busqueda.value = ''
  estadoFiltro.value = 'Todas'
}

const colorEstado = (estado) => {
  if (estado === 'Abierta') return 'bg-[#6B8E23] text-[#FDF8EE]'
  if (estado === 'Cerrada') return 'bg-[#8B1A1A] text-[#FDF8EE]'
  return 'bg-[#8B7D6B] text-[#FDF8EE]'
}

const dataAccion = (m) => {
  if (m.estado === 'Cerrada') {
    return { texto: 'Ver Archivo', destino: `/mesas/${m.id}`, muted: true }
  }
  if (m.rol === 'gm') {
    return { texto: 'Administrar', destino: `/mesas/${m.id}/gestion`, muted: false }
  }
  return { texto: 'Entrar', destino: `/mesas/${m.id}`, muted: false }
}

onMounted(() => load())
</script>

<template>
  <main class="flex-grow w-full max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-10">
    <div class="bg-[#FDF8EE] border border-[#B8A68B] rounded-sm shadow-xl overflow-hidden p-6 md:p-8">
      <div v-if="isLoading" class="py-16 flex flex-col items-center gap-4" role="status" aria-live="polite">
        <div class="animate-pulse space-y-3 w-full max-w-md">
          <div class="h-4 bg-[#C2A980]/40 rounded w-2/3"></div>
          <div class="h-2.5 bg-[#C2A980]/25 rounded w-full"></div>
          <div class="h-2.5 bg-[#C2A980]/25 rounded w-1/2"></div>
        </div>
        <p class="font-tarzana text-xs uppercase tracking-widest text-[#8B7D6B]">Consultando el registro...</p>
      </div>

      <div v-else-if="error" class="py-16 text-center" role="alert">
        <p class="font-tarzana uppercase tracking-widest text-xs text-[#8B1A1A] font-bold mb-1">Error al cargar tus campañas</p>
        <p class="font-minion text-[#5A4A3A]">{{ error }}</p>
        <button type="button" class="btn-gold mt-4 px-6 py-2 font-tarzana font-bold uppercase tracking-wider text-sm" @click="load">Reintentar</button>
      </div>

      <template v-else>
        <!-- Cabecera -->
        <div class="flex flex-col md:flex-row md:items-center justify-between border-b border-[#B8A68B]/60 pb-6 gap-4">
          <div>
            <div class="flex items-center space-x-2.5">
              <span class="text-[#8B5A2B] text-lg select-none">◆</span>
              <h1 class="font-mason text-3xl font-bold text-[#8B5A2B] tracking-wide leading-tight">Mis Campañas</h1>
            </div>
            <p class="font-minion italic text-[#8B7D6B] text-base mt-1">
              Registro de crónicas activas y expediciones en los Reinos de Golarion
            </p>
          </div>
          <button
            type="button"
            class="btn-gold text-[#1A1A1A] font-mason font-bold text-base px-5 py-2.5 rounded-sm flex items-center justify-center space-x-2 active:scale-95 transition"
            @click="router.push('/mesas/nueva')"
          >
            <span class="text-lg leading-none font-black">+</span>
            <span>Crear Mesa</span>
          </button>
        </div>

        <!-- Tabs de rol + filtros -->
        <div class="mt-6 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 border-b border-[#B8A68B]/70">
          <div class="flex space-x-2 -mb-[1px]" role="tablist" aria-label="Filtrar por rol">
            <button
              type="button"
              role="tab"
              :aria-selected="rolTab === 'gm'"
              :class="rolTab === 'gm'
                ? 'bg-[#FDF8EE] border-b-[3px] border-[#D4AF37] text-[#8B5A2B]'
                : 'bg-[#E8DCC8]/60 hover:bg-[#E8DCC8] text-[#8B7D6B] hover:text-[#8B5A2B] border-b-[3px] border-transparent'"
              class="font-mason font-bold text-sm md:text-base px-5 py-2.5 flex items-center space-x-2 cursor-pointer transition-all"
              @click="rolTab = 'gm'"
            >
              <span>Como GM</span>
              <span class="font-tarzana text-xs font-semibold px-2 py-0.5 rounded-full bg-[#8B5A2B]/10 text-[#8B5A2B]">({{ rolGm.length }})</span>
            </button>
            <button
              type="button"
              role="tab"
              :aria-selected="rolTab === 'jugador'"
              :class="rolTab === 'jugador'
                ? 'bg-[#FDF8EE] border-b-[3px] border-[#D4AF37] text-[#8B5A2B]'
                : 'bg-[#E8DCC8]/60 hover:bg-[#E8DCC8] text-[#8B7D6B] hover:text-[#8B5A2B] border-b-[3px] border-transparent'"
              class="font-mason font-bold text-sm md:text-base px-5 py-2.5 flex items-center space-x-2 cursor-pointer transition-all"
              @click="rolTab = 'jugador'"
            >
              <span>Como Jugador</span>
              <span class="font-tarzana text-xs font-semibold px-2 py-0.5 rounded-full bg-[#1A1A1A]/10 text-[#8B7D6B]">({{ rolJugador.length }})</span>
            </button>
          </div>

          <div class="flex items-center space-x-3 pb-2 sm:pb-0">
            <div class="relative w-full sm:w-60">
              <input
                v-model="busqueda"
                type="search"
                class="w-full text-xs font-tarzana py-1.5 pl-8 pr-2.5 bg-[#FAF3E0] border border-[#C2A980] text-[#5c3b1c] placeholder-[#8B7D6B] rounded-sm focus:ring-1 focus:ring-[#D4AF37] focus:border-[#D4AF37] outline-none"
                placeholder="Buscar campaña o diario..."
              />
              <svg class="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-[#8B7D6B]" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
            </div>
            <div class="relative shrink-0">
              <select v-model="estadoFiltro" class="text-xs font-tarzana py-1.5 pl-3 pr-7 bg-[#FAF3E0] border border-[#C2A980] text-[#8B7D6B] rounded-sm focus:ring-1 focus:ring-[#D4AF37] focus:border-[#D4AF37] outline-none cursor-pointer">
                <option v-for="opcion in opcionesEstado" :key="opcion" :value="opcion">Estado: {{ opcion }}</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Listado -->
        <div class="mt-6 space-y-3.5">
          <article
            v-for="m in visibles"
            :key="m.mesaId"
            class="bg-[#FDF8EE] border border-[#C2A980] rounded-sm p-4 md:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4"
          >
            <div class="space-y-1.5 flex-1 min-w-0">
              <div class="flex flex-wrap items-center gap-2.5">
                <h2 class="font-mason font-bold text-[#8B5A2B] text-lg leading-tight">{{ m.nombre }}</h2>
                <span class="font-tarzana text-[0.7rem] uppercase px-2 py-0.5 bg-[#1A1A1A] text-[#FDF8EE] rounded-sm font-semibold tracking-wider">{{ m.sistema }}</span>
                <span class="font-tarzana text-[0.7rem] uppercase px-2 py-0.5 rounded-sm font-semibold tracking-wide" :class="colorEstado(m.estado)">{{ m.estado }}</span>
              </div>
              <div class="flex flex-wrap items-center text-sm gap-y-1 gap-x-3">
                <p class="font-minion italic text-[#8B7D6B] text-sm font-semibold">
                  Rol: <span class="font-normal text-[#1A1A1A]">{{ m.rol === 'gm' ? 'Director de Juego (GM)' : `Jugador (${m.personaje})` }}</span>
                </p>
                <span v-if="m.capitulo" class="text-[#C2A980] hidden sm:inline">•</span>
                <p v-if="m.capitulo" class="font-tarzana text-xs text-[#5c3b1c] font-medium">{{ m.capitulo }}</p>
                <span class="text-[#C2A980] hidden sm:inline">•</span>
                <span class="font-tarzana text-xs text-[#8B7D6B] bg-[#E8DCC8]/50 px-1.5 py-0.5 rounded">
                  {{ m.jugadores >= m.plazas && m.plazas > 0 ? `${m.jugadores}/${m.plazas} (Completo)` : `${m.jugadores}/${m.plazas} Jugadores` }}
                </span>
              </div>
              <div v-if="m.ultimaSesion" class="flex items-center space-x-1.5 text-[#8B7D6B] text-xs font-tarzana pt-0.5">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <circle cx="12" cy="12" r="9" stroke-width="1.8"></circle>
                  <path d="M12 7v5l3 3" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"></path>
                </svg>
                <span>Última sesión: {{ m.ultimaSesion }}</span>
              </div>
            </div>

            <div class="shrink-0 flex items-center md:self-center border-t md:border-t-0 border-[#C2A980]/50 pt-3 md:pt-0">
              <RouterLink
                :to="dataAccion(m).destino"
                :class="dataAccion(m).muted
                  ? 'text-[#8B7D6B] hover:text-[#8B5A2B] border-[#8B7D6B]/30 bg-[#FDF8EE]/30 hover:bg-[#FDF8EE]/70'
                  : 'text-[#8B5A2B] hover:text-[#5c3b1c] border-[#8B5A2B]/30 bg-[#FDF8EE]/60 hover:bg-[#FDF8EE]'"
                class="inline-flex items-center space-x-1 font-tarzana font-bold text-sm px-3.5 py-1.5 rounded border transition-colors group"
              >
                <span>{{ dataAccion(m).texto }}</span>
                <span class="transition-transform group-hover:translate-x-0.5">→</span>
              </RouterLink>
            </div>
          </article>

          <div v-if="visibles.length === 0" class="py-12 text-center" role="status">
            <div class="text-3xl mb-2 select-none" aria-hidden="true">🗝️</div>
            <h3 class="font-mason font-bold text-xl text-[#8B5A2B]">No hay campañas que coincidan</h3>
            <p class="font-minion text-[#5A4A3A] mt-1">Ajustá la búsqueda o los filtros para volver a ver tus {{ rolTab === 'gm' ? 'crónicas' : 'expediciones' }}.</p>
            <button v-if="opsAplicadas" type="button" class="btn-copper-outline mt-5 px-6 py-2.5 font-tarzana font-bold uppercase tracking-wider text-sm" @click="limpiarFiltros">
              Limpiar filtros
            </button>
          </div>
        </div>

        <!-- Inscripción de pie -->
        <div class="mt-8 pt-4 border-t border-[#C2A980]/40 flex flex-col sm:flex-row items-center justify-between text-xs font-tarzana text-[#8B7D6B] uppercase tracking-wider">
          <span>Sistema d20 • Pathfinder RPG 1e</span>
          <span class="mt-1 sm:mt-0 font-minion normal-case italic text-[#8B7D6B]">Total: {{ membresias.length }} crónicas registradas bajo tu regencia</span>
        </div>
      </template>
    </div>
  </main>
</template>