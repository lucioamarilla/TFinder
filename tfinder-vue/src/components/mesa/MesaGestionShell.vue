<script setup>
import { ref, computed, provide, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getMesa } from '@/services/mesas.js'
import { getMembresias } from '@/services/membresias.js'
import { getWiki } from '@/services/wiki.js'
import { getSesiones } from '@/services/sesiones.js'
import { getMiembros } from '@/services/jugadores.js'
import { useToast } from '@/composables/useToast.js'

const props = defineProps({ mesaId: { type: String, required: true } })

const route = useRoute()
const toast = useToast()

const mesa = ref(null)
const cargando = ref(true)
const noEncontrada = ref(false)
const wikiCount = ref(0)
const sesionesCount = ref(0)
const ocupacion = ref({ miembros: 0, capacidad: 5 })
const esGM = ref(false)

const TABS = [
  { segmento: 'gestion', etiqueta: 'Resumen', glyph: '◆', flora: true },
  { segmento: 'wiki', etiqueta: 'Wiki', glyph: '', flora: false },
  { segmento: 'calendario', etiqueta: 'Calendario & Votación', glyph: '', flora: false },
  { segmento: 'sesiones', etiqueta: 'Sesiones', glyph: '', flora: false },
  { segmento: 'jugadores', etiqueta: 'Jugadores', glyph: '', flora: false },
  { segmento: 'builds', etiqueta: 'Builds', glyph: '', flora: false }
]

const rutaBase = computed(() => `/mesas/${props.mesaId}`)

function tabActiva(tab) {
  const base = tab.segmento === 'gestion' ? `${rutaBase.value}/gestion` : `${rutaBase.value}/${tab.segmento}`
  return tab.segmento === 'gestion'
    ? route.path === base
    : route.path.startsWith(base)
}

function contador(tab) {
  if (tab.segmento === 'wiki') return wikiCount.value
  if (tab.segmento === 'sesiones') return sesionesCount.value
  if (tab.segmento === 'jugadores') return `${ocupacion.value.miembros}/${ocupacion.value.capacidad}`
  return null
}

const estadoBadge = computed(() => {
  const estado = (mesa.value?.estado || '').toLowerCase()
  if (estado.includes('abiert') || estado.includes('reclut')) {
    return { texto: 'ABIERTA', cls: 'bg-[#6B8E23] text-[#FDF8EE]', pulso: true }
  }
  if (estado.includes('pausa')) {
    return { texto: 'EN PAUSA', cls: 'bg-[#8B7D6B] text-[#FDF8EE]', pulso: false }
  }
  return { texto: 'CERRADA', cls: 'bg-[#4A3228] text-[#FDF8EE]', pulso: false }
})

async function cargar() {
  cargando.value = true
  noEncontrada.value = false
  try {
    const [detalle, wiki, sesiones, membresias, jugadores] = await Promise.all([
      getMesa(props.mesaId),
      getWiki(props.mesaId),
      getSesiones(props.mesaId),
      getMembresias(),
      getMiembros(props.mesaId)
    ])
    mesa.value = detalle
    wikiCount.value = wiki.total
    sesionesCount.value = sesiones.length
    ocupacion.value = { miembros: jugadores.miembros.length, capacidad: jugadores.capacidad }
    esGM.value = membresias.some((m) => m.id === props.mesaId && m.rol === 'gm')
  } catch {
    noEncontrada.value = true
  } finally {
    cargando.value = false
  }
}

function invitarJugador() {
  toast.ok('Enlace de invitación copiado al portapapeles (simulado).')
}

onMounted(cargar)
watch(() => props.mesaId, cargar)

provide('mesaGestion', { mesa, cargando, wikiCount, sesionesCount, ocupacion, esGM })
</script>

<template>
  <div v-if="noEncontrada" class="bg-[#FDF8EE] border border-[#C2A980] rounded-lg p-10 text-center font-minion text-[#5C4A32]">
    No encontramos la mesa que buscas. Quizá fue archivada por el Director de Juego.
    <RouterLink to="/mis-mesas" class="block mt-3 font-tarzana font-bold text-[#8B5A2B] hover:underline">← Volver a Mis Mesas</RouterLink>
  </div>

  <div v-else-if="cargando" class="flex flex-col items-center justify-center py-16 text-[#8B7D6B]">
    <span class="w-8 h-8 border-2 border-[#C2A980] border-t-[#8B5A2B] rounded-full animate-spin"></span>
    <span class="mt-3 font-tarzana text-xs uppercase tracking-widest">Abriendo el grimorio de campaña…</span>
  </div>

  <div v-else-if="mesa">
    <!-- Miga de pan -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-2 font-tarzana text-xs text-[#8B7D6B] uppercase tracking-wider">
        <RouterLink to="/mis-mesas" class="hover:text-[#8B5A2B] transition-colors">Mis Mesas</RouterLink>
        <span>/</span>
        <span class="text-[#8B5A2B] font-semibold">Gestión de Campaña</span>
        <span>/</span>
        <span class="text-[#1A1A1A]">{{ mesa.nombre }}</span>
      </div>
      <div class="flex items-center space-x-2 bg-[#8B5A2B]/10 border border-[#8B5A2B]/30 px-2.5 py-0.5 rounded text-xs font-tarzana text-[#8B5A2B]">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
        </svg>
        <span class="font-semibold uppercase tracking-wider">Modo Director de Juego (GM)</span>
      </div>
    </div>

    <!-- Cabecera de la mesa -->
    <section class="bg-[#FDF8EE]/95 border border-[#C2A980] rounded-t-lg p-6 sm:p-8 shadow-lg relative">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div class="space-y-2">
          <div class="flex flex-wrap items-center gap-3">
            <h1 class="font-mason text-2xl sm:text-3xl lg:text-[2rem] font-bold text-[#8B5A2B] leading-tight drop-shadow-sm">
              {{ mesa.nombre }}
            </h1>
            <span class="px-2.5 py-0.5 bg-[#1A1A1A] text-[#FDF8EE] font-tarzana font-bold text-xs rounded border border-[#8B7D6B] tracking-wider">
              {{ mesa.sistema || 'PF1e' }}
            </span>
            <span
              :class="`px-2.5 py-0.5 font-tarzana font-bold text-xs rounded tracking-wider shadow-sm flex items-center space-x-1 ${estadoBadge.cls}`"
            >
              <span :class="`w-1.5 h-1.5 rounded-full bg-white ${estadoBadge.pulso ? 'animate-pulse' : ''}`"></span>
              <span>{{ estadoBadge.texto }}</span>
            </span>
          </div>
          <p class="font-minion italic text-[#5C4A32] text-base">
            {{ mesa.lore }}
          </p>
        </div>

        <div v-if="esGM" class="flex items-center space-x-3 self-start md:self-center">
          <RouterLink
            :to="`${rutaBase}/editar`"
            class="flex items-center space-x-2 px-4 py-2 bg-[#FDF8EE] hover:bg-[#E8DCC8] border border-[#8B5A2B] rounded shadow-sm text-[#8B5A2B] hover:text-[#5C3817] font-tarzana font-semibold text-sm transition-all duration-150 active:scale-95 group"
          >
            <svg class="w-4 h-4 text-[#8B5A2B] group-hover:scale-110 transition-transform" fill="currentColor" viewBox="0 0 24 24">
              <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"></path>
            </svg>
            <span>EDITAR MESA</span>
          </RouterLink>

          <button
            type="button"
            class="btn-gold-emboss px-4 py-2 rounded text-[#1A1A1A] font-tarzana font-bold text-sm flex items-center space-x-1.5"
            @click="invitarJugador"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path>
            </svg>
            <span>INVITAR JUGADOR</span>
          </button>
        </div>
      </div>
    </section>

    <!-- Tabs horizontales -->
    <nav class="flex border-x border-b border-[#C2A980] bg-[#E8DCC8]/90 overflow-x-auto shadow-sm">
      <RouterLink
        v-for="tab in TABS"
        :key="tab.segmento"
        :to="tab.segmento === 'gestion' ? `${rutaBase}/gestion` : `${rutaBase}/${tab.segmento}`"
        :class="tabActiva(tab) ? 'tab-active' : 'tab-inactive'"
        class="px-6 py-3 font-mason font-bold text-sm sm:text-[1rem] flex items-center space-x-2 whitespace-nowrap transition-colors uppercase"
      >
        <span v-if="tab.glyph" class="text-[#D4AF37]">{{ tab.glyph }}</span>
        <span>{{ tab.etiqueta }}</span>
        <span
          v-if="contador(tab) !== null"
          :class="tab.segmento === 'jugadores'
            ? 'text-[0.7rem] bg-[#6B8E23] text-white px-1.5 py-0.2 rounded font-tarzana font-bold'
            : 'text-[0.7rem] bg-[#8B7D6B]/30 px-1.5 py-0.2 rounded font-tarzana text-[#5C4A32]'"
        >{{ contador(tab) }}</span>
      </RouterLink>
    </nav>

    <!-- Contenido de la pestaña -->
    <div class="bg-[#FDF8EE] border-x border-b border-[#C2A980] rounded-b-lg p-6 sm:p-8 shadow-xl">
      <slot />
    </div>
  </div>
</template>