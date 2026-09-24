<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { mesasApi } from '@/api/endpoints'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const toast = useToast()

const mesas = ref([])
const cargando = ref(true)
const error = ref('')
const cacheOrigen = ref('')
const cacheTier = ref('')
const refKey = ref('')

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const resp = await mesasApi.listar()
    mesas.value = resp.datos || []
    const h = resp.encabezados || {}
    cacheOrigen.value = h['x-cache'] || (h['x-served-from'] ? 'redis' : '')
    cacheTier.value = h['x-cache-tier'] || ''
    refKey.value = h['x-ref-key'] || ''
  } catch (e) {
    mesas.value = []
    error.value = e?.mensaje || e?.message || 'No pudimos abrir el archivo de mesas.'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)

const vacantes = computed(() =>
  mesas.value.map((m) => ({ id: m.id, nombre: m.nombre, libres: Math.max(m.plazas - (m.jugadores || 0), 0), plazas: m.plazas || 0 }))
)
</script>

<template>
  <main class="max-w-7xl mx-auto px-6 py-10">
    <header class="mb-8 border-b border-[#8B5A2B]/40 pb-4">
      <span class="font-stat uppercase text-xs tracking-widest text-[#8B5A2B] font-bold">Archivo de Partidas</span>
      <h1 class="font-mason text-3xl md:text-4xl font-bold text-[#8B5A2B] mt-1">Explorar Mesas</h1>
      <p class="font-narrative italic text-lg text-[#5A4A3A] mt-1">
        Busca la aventura perfecta entre las mesas activas de la comunidad de PF1e.
      </p>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-8 items-start">
      <!-- SIDEBAR DE FILTROS -->
      <aside class="lg:sticky lg:top-24 card-parchment p-5 rounded-[2px] book-spine-accent pl-6">
        <h2 class="font-mason font-bold text-lg text-[#8B5A2B] mb-4 flex items-center gap-2">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
          Filtros
        </h2>

        <label class="block mb-3">
          <span class="font-stat uppercase text-xs font-bold tracking-wider text-[#8B7D6B]">Búsqueda</span>
          <input
            v-model="busqueda"
            type="search"
            class="parchment-input mt-1 w-full px-3 py-2 font-narrative text-sm rounded-[2px] placeholder:text-[#8B7D6B] placeholder:italic"
            placeholder="Senda, GM, estilo..."
          />
        </label>

        <label class="block mb-3">
          <span class="font-stat uppercase text-xs font-bold tracking-wider text-[#8B7D6B]">Sistema</span>
          <select v-model="sistema" class="select-parchment mt-1 w-full px-3 py-2 font-stat text-sm font-semibold rounded-[2px]">
            <option v-for="s in opcionesSistemas" :key="s" :value="s">{{ s }}</option>
          </select>
        </label>

        <label class="block mb-3">
          <span class="font-stat uppercase text-xs font-bold tracking-wider text-[#8B7D6B]">Modalidad</span>
          <select v-model="modalidad" class="select-parchment mt-1 w-full px-3 py-2 font-stat text-sm font-semibold rounded-[2px]">
            <option v-for="m in opcionesModalidad" :key="m" :value="m">{{ m }}</option>
          </select>
        </label>

        <label class="block mb-5">
          <span class="font-stat uppercase text-xs font-bold tracking-wider text-[#8B7D6B]">Disponibilidad</span>
          <select v-model="disponibilidad" class="select-parchment mt-1 w-full px-3 py-2 font-stat text-sm font-semibold rounded-[2px]">
            <option v-for="d in opcionesDisponibilidad" :key="d" :value="d">{{ d }}</option>
          </select>
        </label>

        <div class="flex items-center gap-2">
          <button type="button" class="btn-gold flex-1 px-4 py-2.5 font-stat font-bold uppercase tracking-wider text-sm rounded-[2px]" @click="retry">
            Aplicar
          </button>
          <button
            type="button"
            class="font-stat text-xs font-bold uppercase tracking-wider text-[#8B5A2B] underline underline-offset-2 hover:text-[#8B1A1A]"
            @click="limpiarFiltros"
          >
            Limpiar
          </button>
        </div>
      </aside>

      <!-- RESULTADOS -->
      <section aria-label="Listado de mesas">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-5 border border-[#8B5A2B]/25 bg-[#FDF8EE]/80 px-4 py-2.5 rounded-[2px]">
          <span class="font-stat text-sm font-bold text-[#8B5A2B] uppercase tracking-wider">
            <span class="text-[#D4AF37] text-base">☩</span>
            {{ filtradas.length }} {{ filtradas.length === 1 ? 'mesa activa' : 'mesas activas' }}
            <span v-if="opsAplicadas" class="text-[#8B7D6B] normal-case font-semibold">(con filtros)</span>
          </span>
          <label class="flex items-center gap-2">
            <span class="font-stat uppercase text-xs font-bold tracking-wider text-[#8B7D6B]">Ordenar</span>
            <select v-model="orden" class="select-parchment px-3 py-1.5 font-stat text-sm font-semibold rounded-[2px]">
              <option v-for="o in opcionesOrden" :key="o.valor" :value="o.valor">{{ o.etiqueta }}</option>
            </select>
          </label>
        </div>

        <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 justify-items-center" role="status" aria-live="polite">
          <div v-for="n in 6" :key="n" class="card-parchment w-full max-w-[340px] min-h-[240px] p-4 rounded-[2px] animate-pulse">
            <div class="w-2/3 h-4 bg-[#C2A980]/40 rounded mb-3"></div>
            <div class="w-full h-2 bg-[#C2A980]/25 rounded mb-2"></div>
            <div class="w-full h-2 bg-[#C2A980]/25 rounded mb-2"></div>
            <div class="w-1/2 h-2 bg-[#C2A980]/25 rounded"></div>
          </div>
        </div>

        <div v-else-if="error" class="card-parchment p-8 text-center max-w-xl mx-auto" role="alert">
          <p class="font-stat uppercase tracking-widest text-xs text-[#8B1A1A] font-bold mb-1">Error al cargar mesas</p>
          <p class="font-narrative text-[#5A4A3A]">{{ error }}</p>
          <button type="button" class="btn-gold mt-4 px-6 py-2 font-stat font-bold uppercase tracking-wider text-sm" @click="retry">Reintentar</button>
        </div>

        <div v-else-if="filtradas.length === 0" class="card-parchment p-10 text-center max-w-xl mx-auto" role="status">
          <div class="text-4xl mb-3 select-none" aria-hidden="true">🗝️</div>
          <h3 class="font-mason font-bold text-xl text-[#8B5A2B]">No se encontraron mesas</h3>
          <p class="font-narrative text-[#5A4A3A] mt-2">
            Ajustá los filtros del grimorio o limpiá la búsqueda para volver a ver las partidas activas.
          </p>
          <button type="button" class="btn-copper-outline mt-5 px-6 py-2.5 font-stat font-bold uppercase tracking-wider text-sm" @click="limpiarFiltros">
            Limpiar filtros
          </button>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 justify-items-center">
          <MesaCard v-for="mesa in filtradas" :key="mesa.id" :mesa="mesa" />
        </div>
      </section>
    </div>
  </main>
</template>