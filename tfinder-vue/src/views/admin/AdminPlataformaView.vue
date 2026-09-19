<script setup>
import { ref, onMounted } from 'vue'
import { getPlataforma } from '@/services/admin.js'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'

const kpis = ref([])
const accesos = ref([])
const cargando = ref(true)
const fallo = ref(null)

const tonoKpi = {
  oro: 'text-[#D4AF37]',
  verde: 'text-[#6B8E23]',
  cobre: 'text-[#8B5A2B]'
}

const iconos = {
  traza: '<path d="M9 6h11M9 12h11M9 18h11M4 6h.01M4 12h.01M4 18h.01" stroke-linecap="round" stroke-linejoin="round"/>',
  pulso: '<path d="M3 12h4l3 8 4-16 3 8h4" stroke-linecap="round" stroke-linejoin="round"/>',
  cola: '<path d="M12 2 2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke-linecap="round" stroke-linejoin="round"/>',
  escudo: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke-linecap="round" stroke-linejoin="round"/>',
  balanza: '<path d="M12 3v18M7 7l-4 6h8l-4-6zM17 7l-4 6h8l-4-6zM8 21h8" stroke-linecap="round" stroke-linejoin="round"/>',
  grafico: '<path d="M3 3v18h18M8 17V9m5 8V5m5 12v-6" stroke-linecap="round" stroke-linejoin="round"/>'
}

async function cargar() {
  cargando.value = true
  fallo.value = null
  try {
    const data = await getPlataforma()
    kpis.value = data.kpis
    accesos.value = data.accesos
  } catch (e) {
    fallo.value = e.message || 'La administración integral no respondió.'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
</script>

<template>
  <main class="tfinder-shell">
    <nav class="flex items-center justify-between gap-2 text-[11px] font-tarzana font-semibold tracking-wider uppercase mb-4" aria-label="Migas de pan">
      <div class="flex items-center gap-2 text-[#8B7D6B]">
        <RouterLink to="/dashboard" class="hover:text-[#8B5A2B]">Inicio</RouterLink>
        <span>/</span>
        <span>Administración</span>
        <span>/</span>
        <span class="text-[#D4AF37]">Panel de Administración Integral</span>
      </div>
      <span class="hidden sm:block text-[10px] text-[#8B7D6B]">Códice de gobernanza técnica OGL v1.0a</span>
    </nav>

    <header class="mb-6">
      <h1 class="font-mason text-3xl font-bold text-[#8B5A2B] tracking-wide">✦ Panel de Administración Integral</h1>
      <p class="font-minion italic text-[#5C4633] mt-1">
        Visión consolidada del cónclave: comunidad, servicios y gobernanza técnica en un solo códice.
      </p>
    </header>

    <LoadingState v-if="cargando" message="Consolidando el códice de gobernanza…" />

    <ErrorState v-else-if="fallo" title="El códice no pudo abrirse" :message="fallo" @retry="cargar" />

    <template v-else>
      <div class="grid sm:grid-cols-3 gap-4 mb-6">
        <div v-for="kpi in kpis" :key="kpi.label" class="card-parchment rounded-sm px-4 py-5 text-center">
          <p class="font-mason text-4xl font-bold" :class="tonoKpi[kpi.tono]">{{ kpi.valor }}</p>
          <p class="font-tarzana text-[0.7rem] uppercase tracking-widest text-[#8B7D6B] mt-1">{{ kpi.label }}</p>
        </div>
      </div>

      <h2 class="font-mason text-lg font-bold text-[#8B5A2B] mb-3">Accesos directos de gobierno</h2>
      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <RouterLink
          v-for="acceso in accesos"
          :key="acceso.to"
          :to="acceso.to"
          class="card-parchment corner rounded-sm p-4 flex items-start gap-3 focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/60"
        >
          <span class="w-9 h-9 shrink-0 rounded-sm bg-[#F4EAD6] border border-[#C2A980] flex items-center justify-center text-[#8B5A2B]">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24" aria-hidden="true" v-html="iconos[acceso.icono]"></svg>
          </span>
          <span class="min-w-0">
            <span class="block font-tarzana font-bold text-[#1A1A1A]">{{ acceso.titulo }}</span>
            <span class="block font-minion italic text-xs text-[#8B7D6B]">{{ acceso.subtitulo }}</span>
          </span>
        </RouterLink>
      </div>
    </template>
  </main>
</template>
