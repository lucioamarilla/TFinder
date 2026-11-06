<script setup>
// D-04: la vista vive sobre SesionOut del backend:
//   { id, mesa_id, estado: 'abierta' | 'cerrada', fecha, confirmada_at }
// No existen numero/titulo/asistencias/quorum/diario en el contrato: el
// ordinal se deriva del orden cronologico y el diario se administra en
// /gestion/sesiones/:id/diario (feed-api) tras cerrar la sesion.
import { ref, computed, onMounted, watch } from 'vue'
import MesaGestionShell from '@/components/mesa/MesaGestionShell.vue'
import { getSesiones } from '@/services/sesiones.js'

const props = defineProps({ mesaId: { type: String, required: true } })

const sesiones = ref([])
const cargando = ref(true)
const error = ref(null)

const ETIQUETAS_ESTADO = {
  abierta: { texto: 'ABIERTA', cls: 'text-[#6B8E23]' },
  cerrada: { texto: 'CERRADA', cls: 'text-[#8B7D6B]' }
}

// La mas reciente siempre arriba; la fecha real ordena (no hay numero en el
// contrato) y el ordinal derivado representa el orden cronologico.
const orden = computed(() =>
  [...sesiones.value].sort((a, b) => String(b.fecha).localeCompare(String(a.fecha)))
)

function ordinal(indice) {
  return `#${orden.value.length - indice}`
}

function etiqueta(estado) {
  return ETIQUETAS_ESTADO[estado] ?? { texto: String(estado ?? '').toUpperCase(), cls: 'text-[#8B7D6B]' }
}

function fmt(fecha) {
  if (!fecha) return 'Fecha por definir'
  const m = String(fecha).match(/^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2}))?/)
  if (!m) return String(fecha)
  const [, y, mes, d, hh, mm] = m
  return fmtDmy(d, mes, y, hh, mm)
}

function fmtDmy(d, mes, y, hh, mm) {
  const base = `${d}/${mes}/${y}`
  return hh ? `${base} · ${hh}:${mm}` : base
}

const resumen = computed(() => {
  const n = sesiones.value.length
  const cerradas = sesiones.value.filter((s) => s.estado === 'cerrada').length
  return `Sesiones registradas: ${n}. Aun por jugar: ${n - cerradas}.`
})

async function cargar() {
  cargando.value = true
  error.value = null
  try {
    sesiones.value = await getSesiones(props.mesaId)
  } catch (e) {
    sesiones.value = []
    error.value = e?.message || 'No se pudieron cargar las sesiones.'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
watch(() => props.mesaId, cargar)
</script>

<template>
  <MesaGestionShell :mesa-id="mesaId">
    <div class="space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b-2 border-[#C2A980] pb-4">
        <div>
          <h2 class="font-mason text-xl font-bold text-[#8B5A2B] uppercase tracking-wide flex items-center gap-2">
            <span>✦</span> Historial de Sesiones
          </h2>
          <p class="font-minion italic text-sm text-[#736351] mt-0.5">
            Convocatorias oficiales de la mesa; el diario de cada sesión vive en su propia página.
          </p>
        </div>
        <span
          class="self-start sm:self-auto px-3 py-1 rounded border text-xs font-tarzana font-bold uppercase tracking-wider border-[#C2A980] text-[#5C4A32]"
        >{{ resumen }}</span>
      </div>

      <p v-if="error" class="hint-error" role="alert" data-test="error-sesiones">{{ error }}</p>

      <div v-if="!cargando && !error && orden.length === 0" class="bg-[#FBF4E6] border border-dashed border-[#C2A980] rounded p-8 text-center font-minion italic text-[#736351]" data-test="sin-sesiones">
        Aún no hay sesiones convocadas. Proponé una fecha en el Calendario y confirmala para abrirla aquí.
      </div>

      <div class="space-y-3">
        <article
          v-for="(sesion, i) in orden"
          :key="sesion.id"
          data-test="sesion-fila"
          :data-sesion-id="String(sesion.id)"
          :data-estado="sesion.estado"
          class="p-3.5 transition-all flex flex-col md:flex-row md:items-center justify-between gap-3 border rounded-xs"
          :class="sesion.estado === 'cerrada' ? 'bg-[#F7F2E7]/80 opacity-90 border-[#C2A980]' : 'border-[#C2A980] hover:border-[#8B5A2B]'"
        >
          <div class="flex items-start sm:items-center space-x-4">
            <div class="shrink-0 w-16 text-center border-r border-[#C2A980]/70 pr-3">
              <span class="block text-xs font-tarzana uppercase font-bold text-[#8B7D6B]">Ordinal</span>
              <span
                class="block text-base font-mason font-bold"
                :class="sesion.estado === 'cerrada' ? 'text-[#8B7D6B]' : 'text-[#8B5A2B]'"
              >{{ ordinal(i) }}</span>
            </div>
            <div class="space-y-1">
              <div class="flex flex-wrap items-center gap-x-3 gap-y-1">
                <h3 class="text-base font-mason font-bold text-[#8B5A2B]">
                  {{ fmt(sesion.fecha) }}
                </h3>
                <span
                  class="inline-flex items-center space-x-1 text-xs font-tarzana font-bold uppercase"
                  :class="etiqueta(sesion.estado).cls"
                >
                  <svg v-if="sesion.estado === 'cerrada'" class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                    <path clip-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" fill-rule="evenodd"></path>
                  </svg>
                  <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                  <span>{{ etiqueta(sesion.estado).texto }}</span>
                </span>
                <span v-if="sesion.confirmadaAt" class="text-xs font-minion text-[#8B7D6B]">
                  Confirmada {{ fmt(sesion.confirmadaAt) }}
                </span>
              </div>
            </div>
          </div>

          <div class="shrink-0 flex items-center justify-end gap-2 pl-2">
            <RouterLink
              v-if="sesion.estado === 'abierta'"
              data-test="qr-link"
              :to="`/mesas/${mesaId}/gestion/sesiones/${sesion.id}/qr`"
              class="inline-flex items-center space-x-1.5 text-xs font-tarzana font-bold uppercase tracking-wider text-[#6B8E23] hover:text-[#4A6B17] border-[1.5px] border-[#6B8E23]/50 hover:border-[#6B8E23] rounded-xs px-3 py-1.5 transition-colors"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 17m-1 0a1 1 0 114 0 1 1 0 01-4 0zm12 0a1 1 0 114 0 1 1 0 01-4 0z"></path>
              </svg>
              <span>Asistencia (QR)</span>
            </RouterLink>

            <RouterLink
              data-test="bitacora-link"
              :to="`/mesas/${mesaId}/gestion/sesiones/${sesion.id}/bitacora`"
              class="inline-flex items-center space-x-1.5 text-xs font-tarzana font-bold uppercase tracking-wider text-[#3C6E71] hover:text-[#2C5658] border-[1.5px] border-[#3C6E71]/50 hover:border-[#3C6E71] rounded-xs px-3 py-1.5 transition-colors"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
              </svg>
              <span>Bitácora</span>
            </RouterLink>

            <RouterLink
              data-test="diario-link"
              :to="`/mesas/${mesaId}/gestion/sesiones/${sesion.id}/diario`"
              class="inline-flex items-center space-x-1.5 text-sm font-minion font-semibold text-[#8B5A2B] hover:text-[#5A4A36] underline decoration-[#D4AF37] underline-offset-4 transition-colors"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              <span>Diario de sesión</span>
            </RouterLink>
          </div>
        </article>
      </div>
    </div>
  </MesaGestionShell>
</template>
