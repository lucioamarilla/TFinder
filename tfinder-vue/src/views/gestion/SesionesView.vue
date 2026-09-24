<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import MesaGestionShell from '@/components/mesa/MesaGestionShell.vue'
import { getSesiones } from '@/services/sesiones.js'

const props = defineProps({ mesaId: { type: String, required: true } })

const sesiones = ref([])

const pendientes = computed(() => sesiones.value.filter((s) => s.pendienteDiario))
const orden = computed(() => {
  const num = (s) => parseInt(s.numero.replace('#', ''), 10)
  return [...sesiones.value].sort((a, b) => {
    const futA = ['confirmada', 'borrador', 'tentativa'].includes(a.estado)
    const futB = ['confirmada', 'borrador', 'tentativa'].includes(b.estado)
    if (futA !== futB) return futA ? -1 : 1
    return num(b) - num(a)
  })
})

const ETIQUETAS_ESTADO = {
  confirmada: { texto: 'CONFIRMADA', cls: 'text-[#6B8E23]', tachado: false },
  borrador: { texto: 'BORRADOR', cls: 'text-[#8B7D6B]', tachado: false },
  tentativa: { texto: 'TENTATIVA', cls: 'text-[#8B7D6B]', tachado: false },
  ejecutada: { texto: 'Realizada', cls: 'text-[#6B8E23]', tachado: false },
  suspendida: { texto: 'Desconvocada', cls: 'text-[#8B1A1A]', tachado: true }
}

function accionDe(sesion) {
  if (sesion.estado !== 'ejecutada') return { tipo: 'convocatoria', texto: 'Editar Convocatoria' }
  if (sesion.pendienteDiario) return { tipo: 'registrar', texto: 'Registrar Diario' }
  return { tipo: 'ver', texto: 'Ver Diario →' }
}

async function cargar() {
  sesiones.value = await getSesiones(props.mesaId)
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
            <span>✦</span> Historial de Sesiones y Diarios
          </h2>
          <p class="font-minion italic text-sm text-[#736351] mt-0.5">
            Crónicas de campaña, actas de combate y diarios de expedición de los aventureros.
          </p>
        </div>
        <span
          v-if="pendientes.length"
          class="self-start sm:self-auto px-3 py-1 rounded border text-xs font-tarzana font-bold uppercase tracking-wider"
          :class="pendientes.length > 0 ? 'bg-[#D4AF37]/15 border-[#D4AF37] text-[#8B5A2B]' : ''"
        >
          Pendientes de Diario ({{ pendientes.length }})
        </span>
      </div>

      <div class="space-y-3">
        <article
          v-for="sesion in orden"
          :key="sesion.id"
          class="p-3.5 transition-all flex flex-col md:flex-row md:items-center justify-between gap-3 border rounded-xs"
          :class="sesion.estado === 'suspendida' ? 'bg-[#F7F2E7]/80 opacity-90 border-[#C2A980]' : 'border-[#C2A980] hover:border-[#8B5A2B]'"
        >
          <div class="flex items-start sm:items-center space-x-4">
            <div class="shrink-0 w-16 text-center border-r border-[#C2A980]/70 pr-3">
              <span class="block text-xs font-tarzana uppercase font-bold text-[#8B7D6B]">Ordinal</span>
              <span
                class="block text-base font-mason font-bold"
                :class="sesion.estado === 'suspendida' ? 'text-[#8B1A1A]' : 'text-[#8B5A2B]'"
              >{{ sesion.numero }}</span>
            </div>
            <div class="space-y-1">
              <div class="flex flex-wrap items-center gap-x-3 gap-y-1">
                <h3 class="text-base font-mason font-bold" :class="ETIQUETAS_ESTADO[sesion.estado]?.tachado ? 'text-[#8B7D6B] line-through' : 'text-[#8B5A2B]'">
                  {{ sesion.fechaGolarion }}
                </h3>
                <span class="text-xs font-minion text-[#8B7D6B]">({{ sesion.selloDia }} {{ sesion.selloNum }})</span>
                <span class="inline-flex items-center space-x-1 text-xs font-tarzana font-bold uppercase" :class="ETIQUETAS_ESTADO[sesion.estado]?.cls || ''">
                  <svg v-if="sesion.estado === 'ejecutada'" class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                    <path clip-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" fill-rule="evenodd"></path>
                  </svg>
                  <svg v-else-if="sesion.estado === 'suspendida'" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                  <span>{{ ETIQUETAS_ESTADO[sesion.estado]?.texto }}</span>
                </span>
              </div>
              <p class="text-sm font-minion text-[#1A1A1A] italic">
                {{ sesion.titulo }} — {{ sesion.resumen }}
              </p>
              <div class="text-xs font-minion text-[#5A4A36] flex flex-wrap items-center gap-x-4">
                <span><strong>Asistencia:</strong> {{ sesion.asistencias }} · {{ sesion.quorum }}</span>
                <span class="text-[#8B5A2B]">✦ {{ sesion.horario }}</span>
              </div>
            </div>
          </div>

          <div class="shrink-0 flex items-center justify-end gap-2 pl-2">
            <RouterLink
              v-if="['confirmada', 'ejecutada', 'abierta', 'en_curso'].includes(sesion.estado)"
              :to="`/mesas/${mesaId}/sesiones/${sesion.id}/qr`"
              class="inline-flex items-center space-x-1.5 text-xs font-tarzana font-bold uppercase tracking-wider text-[#6B8E23] hover:text-[#4A6B17] border-[1.5px] border-[#6B8E23]/50 hover:border-[#6B8E23] rounded-xs px-3 py-1.5 transition-colors"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 17m-1 0a1 1 0 114 0 1 1 0 01-4 0zm12 0a1 1 0 114 0 1 1 0 01-4 0z"></path>
              </svg>
              <span>Asistencia (QR)</span>
            </RouterLink>
            <RouterLink
              v-if="accionDe(sesion).tipo === 'ver'"
              :to="`/mesas/${mesaId}/sesiones/${sesion.id}/diario`"
              class="inline-flex items-center space-x-1.5 text-sm font-minion font-semibold text-[#8B5A2B] hover:text-[#5A4A36] underline decoration-[#D4AF37] underline-offset-4 transition-colors"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              <span>{{ accionDe(sesion).texto }}</span>
            </RouterLink>

            <button
              v-else-if="accionDe(sesion).tipo === 'registrar'"
              type="button"
              class="px-3.5 py-1.5 border-[1.5px] border-[#D4AF37] bg-[#D4AF37]/10 hover:bg-[#D4AF37]/25 text-[#8B5A2B] text-xs font-tarzana uppercase font-bold tracking-wider rounded-xs transition-colors flex items-center space-x-1.5"
              @click="$router.push(`/mesas/${mesaId}/sesiones/${sesion.id}/diario`)"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
              </svg>
              <span>Registrar Diario</span>
            </button>

            <span
              v-else-if="accionDe(sesion).tipo === 'convocatoria'"
              class="text-xs font-tarzana uppercase text-[#8B7D6B] italic"
            >{{ sesion.estado === 'suspendida' ? 'Sin Diario Registrado' : 'Convocatoria en el calendario' }}</span>
          </div>
        </article>
      </div>
    </div>
  </MesaGestionShell>
</template>