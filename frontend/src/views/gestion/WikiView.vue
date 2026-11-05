<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import MesaGestionShell from '@/components/mesa/MesaGestionShell.vue'
import { getWiki } from '@/services/wiki.js'

const props = defineProps({ mesaId: { type: String, required: true } })

const wiki = ref({ carpetas: [], paginas: [], total: 0 })
const carpetasAbiertas = ref({})
const carpetaActiva = ref(null)
const tipoActivo = ref('TODOS')
const busqueda = ref('')

const FILTROS = ['TODOS', 'LUGARES', 'PERSONAJES', 'CRIATURAS', 'NOTAS']

const TIPOS_BADGE = { LUGAR: 'badge-place', NPC: 'badge-npc', CRIATURA: 'badge-creature', NOTA: 'badge-note' }

const ICONOS = {
  user: 'M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z',
  map: 'M20.5 3l-.16.03L15 5.1 9 3 3.36 4.9c-.21.07-.36.25-.36.48V20.5c0 .28.22.5.5.5l.16-.03L9 18.9l6 2.1 5.64-1.9c.21-.07.36-.25.36-.48V3.5c0-.28-.22-.5-.5-.5zM15 19l-6-2.11V5l6 2.11V19z',
  claw: 'M12 2C9.5 2 7 3.8 6 6c-.8 1.8-.4 4 1 5.5-1.5.5-2.8 1.8-3 3.5-.3 2.5 1.5 4.8 4 5 1.5.1 3-.5 4-1.5 1 1 2.5 1.6 4 1.5 2.5-.2 4.3-2.5 4-5-.2-1.7-1.5-3-3-3.5 1.4-1.5 1.8-3.7 1-5.5-1-2.2-3.5-4-6-4zm-3.5 6c.8 0 1.5.7 1.5 1.5S9.3 11 8.5 11 7 10.3 7 9.5 7.7 8 8.5 8zm7 0c.8 0 1.5.7 1.5 1.5s-.7 1.5-1.5 1.5-1.5-.7-1.5-1.5.7-1.5 1.5-1.5.5 0 .5 0zM12 14c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2z',
  scroll: 'M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10H7v-2h10v2zm0-4H7V7h10v2z'
}

function matchTipo(pagina) {
  if (tipoActivo.value === 'TODOS') return true
  if (tipoActivo.value === 'LUGARES') return pagina.tipo === 'LUGAR'
  if (tipoActivo.value === 'PERSONAJES') return pagina.tipo === 'NPC'
  if (tipoActivo.value === 'CRIATURAS') return pagina.tipo === 'CRIATURA'
  if (tipoActivo.value === 'NOTAS') return pagina.tipo === 'NOTA'
  return true
}

const paginasFiltradas = computed(() => {
  let lista = wiki.value.paginas
  if (carpetaActiva.value) lista = lista.filter((p) => p.carpeta === carpetaActiva.value)
  lista = lista.filter(matchTipo)
  if (busqueda.value.trim()) {
    const q = busqueda.value.trim().toLowerCase()
    lista = lista.filter((p) => p.titulo.toLowerCase().includes(q) || p.resumen.toLowerCase().includes(q))
  }
  return lista
})

const carpetasConCount = computed(() =>
  wiki.value.carpetas.map((c) => ({
    ...c,
    count: wiki.value.paginas.filter((p) => p.carpeta === c.id).length
  }))
)

const tituloSeccion = computed(() => {
  const carpeta = wiki.value.carpetas.find((c) => c.id === carpetaActiva.value)
  return carpeta ? `Páginas de ${carpeta.nombre.replace(' & ', ' y ')}` : 'Páginas del Códice de Campaña'
})

function toggleCarpeta(id) {
  carpetasAbiertas.value[id] = !carpetasAbiertas.value[id]
}

function seleccionarCarpeta(id) {
  carpetaActiva.value = id
  carpetasAbiertas.value[id] = true
}

function seleccionarTipo(tipo) {
  tipoActivo.value = tipo
}

async function cargar() {
  wiki.value = await getWiki(props.mesaId)
  carpetasAbiertas.value = wiki.value.carpetas.reduce((acc, c) => ({ ...acc, [c.id]: c.abierta }), {})
}

onMounted(cargar)
watch(() => props.mesaId, cargar)
</script>

<template>
  <MesaGestionShell :mesa-id="mesaId">
    <div class="grid grid-cols-1 md:grid-cols-10 gap-6">
      <!-- Sidebar árbol -->
      <aside class="md:col-span-3 bg-[#F6EDDC] border border-[#C2A980] rounded p-4 flex flex-col justify-between min-h-[420px]">
        <div>
          <div class="flex items-center justify-between mb-3 pb-2 border-b border-[#C2A980]/60">
            <span class="font-mason text-[1.05rem] font-bold text-[#8B5A2B] uppercase tracking-wide">Índice del Códice</span>
            <span class="font-tarzana text-[0.65rem] text-[#8B7D6B]">{{ wiki.total }} artículos</span>
          </div>

          <div class="space-y-1.5">
            <div v-for="carpeta in carpetasConCount" :key="carpeta.id">
              <div
                role="button"
                tabindex="0"
                class="w-full flex items-center justify-between px-2 py-1.5 rounded text-left hover:text-[#8B5A2B] transition group cursor-pointer"
                :class="carpetaActiva === carpeta.id ? 'bg-[#FDF8EE]/80 text-[#8B5A2B]' : ''"
                @click="seleccionarCarpeta(carpeta.id)"
                @keydown.enter="seleccionarCarpeta(carpeta.id)"
              >
                <span class="flex items-center space-x-1.5 font-bold text-[#1A1A1A] group-hover:text-[#8B5A2B]">
                  <span class="text-xs text-[#8B7D6B] transition-transform" :class="carpetasAbiertas[carpeta.id] ? '' : '-rotate-90'">▼</span>
                  <svg class="w-4 h-4 text-[#8B5A2B]" viewBox="0 0 24 24" fill="currentColor">
                    <path :d="ICONOS[carpeta.icono] || ICONOS.scroll"></path>
                  </svg>
                  <span class="text-[0.92rem]">{{ carpeta.nombre }}</span>
                </span>
                <span class="font-tarzana text-[0.65rem] text-[#8B7D6B]">({{ carpeta.count }})</span>
              </div>

              <div v-if="carpetasAbiertas[carpeta.id]" class="pl-6 space-y-0.5 border-l border-[#8B5A2B]/40 ml-3 mt-1">
                <RouterLink
                  v-for="pagina in wiki.paginas.filter((p) => p.carpeta === carpeta.id)"
                  :key="pagina.id"
                  :to="`/mesas/${mesaId}/wiki/${pagina.id}`"
                  class="block px-2 py-1 text-[0.88rem] rounded text-[#1A1A1A] hover:text-[#8B5A2B] hover:bg-[#FDF8EE]/80 transition"
                  :class="carpetaActiva === carpeta.id ? 'border-l-2 border-[#8B5A2B] bg-[#FDF8EE]/90 text-[#8B5A2B] font-semibold' : ''"
                >
                  {{ pagina.titulo.split(' (')[0] }}
                </RouterLink>
              </div>
            </div>
          </div>
        </div>

        <div class="pt-4 mt-4 border-t border-[#C2A980]/70 text-[0.75rem] font-minion text-[#554737] flex items-center justify-between">
          <span>Total: <strong>{{ wiki.total }} artículos</strong></span>
          <button class="font-tarzana text-[0.7rem] text-[#8B5A2B] hover:underline font-bold" @click="carpetaActiva = null">
            ✚ VER TODAS
          </button>
        </div>
      </aside>

      <!-- Columna principal -->
      <section class="md:col-span-7 flex flex-col">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b-2 border-[#C2A980] pb-4 mb-5">
          <div>
            <div class="flex items-center space-x-2">
              <span class="font-mason text-[1.2rem] font-bold text-[#8B5A2B]">{{ tituloSeccion }}</span>
              <span class="font-tarzana text-xs bg-[#E8DCC8] text-[#8B5A2B] px-2 py-0.5 rounded border border-[#C2A980] font-bold">
                {{ paginasFiltradas.length }} artículos
              </span>
            </div>
            <p class="font-minion italic text-xs text-[#736351] mt-0.5">
              Códice topográfico, asentamientos y registros de la crónica; mantenido por la mesa.
            </p>
          </div>

          <RouterLink
            :to="`/mesas/${mesaId}/wiki/nueva`"
            class="gold-emboss-btn px-4 py-2 rounded-sm font-tarzana text-xs font-bold flex items-center space-x-2 shadow self-start sm:self-auto"
          >
            <span class="text-sm font-bold leading-none">+</span>
            <span>CREAR PÁGINA</span>
          </RouterLink>
        </div>

        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
          <div class="flex items-center space-x-2 font-tarzana text-xs flex-wrap">
            <span class="text-[#8B7D6B]">FILTRAR TIPO:</span>
            <button
              v-for="filtro in FILTROS"
              :key="filtro"
              type="button"
              class="px-2 py-0.5 rounded transition font-bold"
              :class="tipoActivo === filtro ? 'bg-[#8B5A2B] text-[#FDF8EE]' : 'hover:bg-[#E8DCC8] text-[#554737]'"
              @click="seleccionarTipo(filtro)"
            >
              {{ filtro }}
            </button>
          </div>
          <div class="text-xs font-minion text-[#8B7D6B] italic">
            Mostrando {{ paginasFiltradas.length }} de {{ wiki.total }} registros
          </div>
        </div>

        <div class="relative mb-4">
          <svg class="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-[#8B7D6B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
          <input
            v-model="busqueda"
            type="text"
            placeholder="Filtrar páginas del código…"
            class="w-full bg-[#FDF8EE] border border-[#C2A980] text-xs font-minion px-3 py-2 pl-8 rounded text-[#1A1A1A] placeholder-[#8B7D6B] focus:outline-none focus:border-[#8B5A2B]"
          />
        </div>

        <div class="border border-[#C2A980] rounded-sm overflow-hidden shadow-sm bg-white/40">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-[#E8DCC8] border-b border-[#C2A980] font-tarzana text-xs text-[#8B5A2B]">
                <th class="py-2.5 px-4 font-bold border-r border-[#C2A980]/60">TÍTULO</th>
                <th class="py-2.5 px-4 font-bold border-r border-[#C2A980]/60 w-[110px]">TIPO</th>
                <th class="py-2.5 px-4 font-bold w-[170px]">FECHA MODIFICACIÓN</th>
                <th class="py-2.5 px-3 font-bold w-[70px] text-center">ACCIÓN</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#C2A980]/60 font-minion text-sm">
              <tr v-for="pagina in paginasFiltradas" :key="pagina.id" class="transition-colors">
                <td class="py-3 px-4 border-r border-[#C2A980]/40">
                  <div class="flex items-center space-x-2.5">
                    <svg class="w-4 h-4 text-[#8B5A2B] flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
                      <path :d="ICONOS.map"></path>
                    </svg>
                    <RouterLink :to="`/mesas/${mesaId}/wiki/${pagina.id}`" class="font-mason font-bold text-[#8B5A2B] hover:underline text-[0.95rem]">
                      {{ pagina.titulo }}
                    </RouterLink>
                  </div>
                  <div class="text-xs text-[#736351] italic pl-6 mt-0.5">
                    {{ pagina.resumen }}
                  </div>
                </td>
                <td class="py-3 px-4 border-r border-[#C2A980]/40">
                  <span
                    class="font-tarzana text-[0.7rem] px-2 py-0.5 rounded"
                    :class="TIPOS_BADGE[pagina.tipo] || 'badge-note'"
                  >
                    {{ pagina.tipo }}
                  </span>
                </td>
                <td class="py-3 px-4 font-tarzana text-xs text-[#8B7D6B]">
                  {{ pagina.fecha }}
                </td>
                <td class="py-3 px-3 text-center">
                  <RouterLink
                    :to="`/mesas/${mesaId}/wiki/${pagina.id}/editar`"
                    class="text-[#8B5A2B] hover:text-[#1A1A1A] transition p-1 inline-flex"
                    title="Editar entrada"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                  </RouterLink>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="paginasFiltradas.length === 0" class="p-10 text-center">
            <p class="font-tarzana text-sm text-[#8B7D6B]">El código no registra páginas con estos criterios.</p>
            <p class="font-minion italic text-xs text-[#8B7D6B] mt-1">Ajusta el filtro o crea una entrada nueva.</p>
          </div>
        </div>
      </section>
    </div>
  </MesaGestionShell>
</template>