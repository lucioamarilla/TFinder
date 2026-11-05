<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast.js'
import MesaGestionShell from '@/components/mesa/MesaGestionShell.vue'
import { getSesion, guardarDiario } from '@/services/sesiones.js'
import { getMiembros } from '@/services/jugadores.js'

const props = defineProps({ mesaId: { type: String, required: true }, sesionId: { type: String, required: true } })

const router = useRouter()
const toast = useToast()

const sesion = ref(null)
const falta = ref(false)
const miembros = ref([])
const presentes = ref({})
const tituloCapitulo = ref('')
const recompensas = ref('')
const contenido = ref('')
const guardando = ref(false)

const esPendiente = computed(() => sesion.value?.pendienteDiario)

async function cargar() {
  try {
    const [detalle, jugadores] = await Promise.all([getSesion(props.mesaId, props.sesionId), getMiembros(props.mesaId)])
    sesion.value = detalle
    miembros.value = jugadores.miembros.filter((m) => m.rol === 'Jugador')
    presentes.value = miembros.value.reduce((acc, m) => ({ ...acc, [m.id]: m.estado === 'Activo' }), {})
    tituloCapitulo.value = detalle.titulo
    recompensas.value = detalle.estado === 'ejecutada' ? '+1.800 PX • 650 po repartidas' : ''
    contenido.value = detalle.diario || ''
  } catch {
    falta.value = true
  }
}

onMounted(cargar)
watch(() => props.sesionId, cargar)

function cancelar() {
  router.push(`/mesas/${props.mesaId}/sesiones`)
}

async function guardar() {
  if (!contenido.value.trim()) {
    toast.error('El resumen del diario no puede quedar en blanco.')
    return
  }
  guardando.value = true
  try {
    await guardarDiario(props.mesaId, props.sesionId, contenido.value.trim())
    toast.ok(`Diario de la sesión ${sesion.value.numero} registrado en el archivo de campaña.`)
    router.push(`/mesas/${props.mesaId}/sesiones`)
  } catch (e) {
    toast.error(e.message || 'No pudimos guardar el diario.')
  } finally {
    guardando.value = false
  }
}
</script>

<template>
  <MesaGestionShell :mesa-id="mesaId">
    <div v-if="falta" class="text-center py-16 font-minion text-[#5C4A32]">
      No encontramos esa sesión en el archivo de la campaña.
      <RouterLink :to="`/mesas/${mesaId}/sesiones`" class="block mt-3 font-tarzana font-bold text-[#8B5A2B] hover:underline">← Volver al historial</RouterLink>
    </div>

    <div v-else-if="sesion" class="space-y-6">
      <div class="space-y-1">
        <RouterLink
          :to="`/mesas/${mesaId}/sesiones`"
          class="inline-flex items-center gap-1.5 font-tarzana text-xs font-bold text-[#8B5A2B] hover:text-[#5C3817] uppercase tracking-wider"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
          </svg>
          VOLVER AL HISTORIAL DE SESIONES
        </RouterLink>
        <p class="font-minion text-sm text-[#5C4A32]">
          Sesión {{ sesion.numero }} · {{ sesion.fechaGolarion }} • Estado:
          <strong :class="esPendiente ? 'text-[#8B5A2B]' : 'text-[#6B8E23]'">
            {{ esPendiente ? 'Pendiente de Diario' : 'Diario cargado' }}
          </strong>
        </p>
      </div>

      <h2 class="font-mason text-[1.5rem] font-bold text-[#8B5A2B] tracking-wide flex items-center gap-2 border-b-2 border-[#C2A980] pb-3">
        <span>✒</span> {{ esPendiente ? 'Registrar Sesión' : 'Editar Diario' }} — {{ sesion.fechaGolarion }}
      </h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <label class="block">
          <span class="block font-mason text-xs font-bold text-[#8B5A2B] uppercase tracking-wider mb-1">Título del Capítulo</span>
          <input
            v-model="tituloCapitulo"
            type="text"
            class="w-full bg-[#FDF8EE] border border-[#C2A980] text-sm font-minion px-3 py-2 rounded text-[#1A1A1A] focus:outline-none focus:border-[#8B5A2B]"
          />
        </label>
        <label class="block">
          <span class="block font-mason text-xs font-bold text-[#8B5A2B] uppercase tracking-wider mb-1">XP / Tesoro (opcional)</span>
          <input
            v-model="recompensas"
            type="text"
            placeholder="Ej. +1.800 PX • 650 po repartidas"
            class="w-full bg-[#FDF8EE] border border-[#C2A980] text-sm font-minion px-3 py-2 rounded text-[#1A1A1A] placeholder-[#8B7D6B] focus:outline-none focus:border-[#8B5A2B]"
          />
        </label>
      </div>

      <label class="block">
        <span class="block font-mason text-xs font-bold text-[#8B5A2B] uppercase tracking-wider mb-1">
          Resumen de la Sesión <span class="text-[#8B1A1A]">*</span>
        </span>
        <textarea
          v-model="contenido"
          rows="12"
          placeholder="Narra lo ocurrido: decisiones, combates, descubrimientos y ganchos pendientes…"
          class="w-full bg-[#FDF8EE] border border-[#C2A980] text-[0.95rem] font-minion px-4 py-3 rounded text-[#1A1A1A] placeholder-[#8B7D6B] leading-relaxed focus:outline-none focus:border-[#8B5A2B] resize-y"
        ></textarea>
        <span class="block mt-1 text-xs font-minion italic text-[#8B7D6B]">
          Autoguardado local activo · los cambios se conservan en el grimorio de la mesa.
        </span>
      </label>

      <section v-if="miembros.length" class="bg-[#FBF4E6] border border-[#E8DCC8] rounded p-4">
        <h3 class="block font-mason text-xs font-bold text-[#8B5A2B] uppercase tracking-wider mb-2">Personajes Presentes en la Mesa</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <label v-for="m in miembros" :key="m.id" class="flex items-center gap-2 font-minion text-sm text-[#1A1A1A] cursor-pointer">
            <input v-model="presentes[m.id]" type="checkbox" class="accent-[#8B5A2B]" />
            <span>{{ m.personaje }}</span>
            <span class="font-tarzana text-[0.65rem] text-[#8B7D6B]">({{ m.clase }} Nvl {{ m.nivel }})</span>
          </label>
        </div>
        <p class="mt-3 text-xs font-minion text-[#5A4A36]">
          <strong>Asistencia registrada:</strong> {{ sesion.asistencias }} · {{ sesion.quorum }}
        </p>
      </section>

      <div class="flex items-center gap-2 justify-end pt-1">
        <button type="button" class="btn-copper-outline px-5 py-2.5 rounded font-tarzana text-xs font-bold" @click="cancelar">
          CANCELAR
        </button>
        <button type="button" :disabled="guardando" class="btn-gold-emboss px-6 py-2.5 rounded font-tarzana text-xs font-bold" @click="guardar">
          {{ guardando ? 'GUARDANDO…' : 'GUARDAR DIARIO' }}
        </button>
      </div>
    </div>
  </MesaGestionShell>
</template>