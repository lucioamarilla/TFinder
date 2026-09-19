<script setup>
import { ref, computed, inject, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import MesaGestionShell from '@/components/mesa/MesaGestionShell.vue'
import ConfirmModal from '@/components/modals/ConfirmModal.vue'
import { getSesiones } from '@/services/sesiones.js'
import { eliminarMesa } from '@/services/mesas.js'
import { useToast } from '@/composables/useToast.js'

const props = defineProps({ mesaId: { type: String, required: true } })

const router = useRouter()
const toast = useToast()

const gestion = inject('mesaGestion')
const mesa = computed(() => gestion?.mesa.value)
const esGM = computed(() => gestion?.esGM.value ?? false)

const sesiones = ref([])
const confirmarEliminar = ref(false)
const eliminando = ref(false)

const proximasSesiones = computed(() =>
  sesiones.value
    .filter((s) => ['confirmada', 'borrador', 'tentativa'].includes(s.estado))
    .slice(0, 3)
)

const ESTADOS = {
  confirmada: { texto: 'CONFIRMADA', cls: 'bg-[#D4AF37]/20 border-[#D4AF37] text-[#8B5A2B]' },
  borrador: { texto: 'BORRADOR', cls: 'bg-[#8B7D6B]/20 text-[#5C4A32]' },
  tentativa: { texto: 'TENTATIVA', cls: 'bg-[#8B7D6B]/20 text-[#5C4A32]' }
}

async function cargarSesiones() {
  sesiones.value = await getSesiones(props.mesaId)
}

onMounted(cargarSesiones)
watch(() => props.mesaId, cargarSesiones)

async function confirmarBaja() {
  eliminando.value = true
  try {
    await eliminarMesa(props.mesaId)
    toast.ok('Campaña disuelta · la crónica quedó archivada en el Cónclave.')
    router.push('/mis-mesas')
  } catch (e) {
    toast.error(e.message || 'No pudimos archivar la campaña.')
  } finally {
    eliminando.value = false
    confirmarEliminar.value = false
  }
}

const parametros = computed(() => {
  if (!mesa.value) return { izquierda: [], derecha: [] }
  return {
    izquierda: [
      { k: 'Sistema y Reglas:', v: 'Pathfinder 1ª Edición (OGL v1.0a)' },
      { k: 'Aventura Oficial / AP:', v: mesa.value.tono },
      { k: 'Nivel de Personajes:', v: mesa.value.rangoNivel },
      { k: 'Modalidad:', v: mesa.value.modalidad },
      { k: 'Frecuencia / Horario:', v: mesa.value.frecuencia }
    ],
    derecha: [
      { k: 'Director de Juego (GM):', v: 'Aldren Valeros', tu: true },
      { k: 'Ocupación de Mesa:', v: mesa.value.ocurrenciasPlazas },
      { k: 'Plataforma VTT & Voz:', v: mesa.value.ubicacion },
      { k: 'Tono de la Crónica:', v: mesa.value.tono },
      { k: 'Visibilidad Pública:', v: 'Listada en el Buscador de Mesas TFinder', verde: true }
    ]
  }
})
</script>

<template>
  <MesaGestionShell :mesa-id="mesaId">
    <div class="space-y-8">
      <!-- Parámetros de campaña -->
      <div>
        <div class="flex items-center space-x-2 mb-4 pb-2 border-b border-[#C2A980]/60">
          <span class="text-[#8B5A2B] text-lg font-mason">❖</span>
          <h2 class="font-mason text-lg text-[#8B5A2B] font-bold uppercase tracking-wide">
            Parámetros de Campaña y Crónica
          </h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-10 gap-y-5 bg-[#FBF4E6] p-5 rounded border border-[#E8DCC8]">
          <div class="space-y-4">
            <div
              v-for="item in parametros.izquierda"
              :key="item.k"
              class="flex flex-col sm:flex-row sm:items-baseline justify-between pb-2 border-b border-[#8B7D6B]/20 last:border-b-0"
            >
              <span class="font-tarzana text-[0.9rem] font-bold text-[#8B5A2B] uppercase tracking-wide">{{ item.k }}</span>
              <span class="font-minion text-[1rem] text-[#1A1A1A]">{{ item.v }}</span>
            </div>
          </div>
          <div class="space-y-4">
            <div
              v-for="item in parametros.derecha"
              :key="item.k"
              class="flex flex-col sm:flex-row sm:items-baseline justify-between pb-2 border-b border-[#8B7D6B]/20 last:border-b-0"
            >
              <span class="font-tarzana text-[0.9rem] font-bold text-[#8B5A2B] uppercase tracking-wide">{{ item.k }}</span>
              <div class="flex items-center space-x-1.5">
                <span :class="`font-minion text-[1rem] ${item.verde ? 'text-[#6B8E23] font-semibold' : 'text-[#1A1A1A]'}`">{{ item.v }}</span>
                <span v-if="item.tu" class="text-xs bg-[#8B5A2B] text-white px-1.5 py-0.2 rounded font-tarzana">Tú</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sinopsis -->
      <div class="bg-[#FDF8EE] p-5 rounded border border-[#C2A980]/80">
        <div class="flex items-center justify-between mb-2">
          <span class="font-tarzana text-[0.9rem] font-bold text-[#8B5A2B] uppercase tracking-wide">Sinopsis de la Mesa:</span>
          <span class="font-tarzana text-xs text-[#8B7D6B]">Visible para aspirantes a jugadores</span>
        </div>
        <p class="font-minion text-[1rem] text-[#1A1A1A] leading-relaxed italic">
          "{{ mesa?.descripcion }}"
        </p>
      </div>

      <!-- Próximas sesiones -->
      <div>
        <div class="flex items-center justify-between mb-4 pb-2 border-b border-[#C2A980]/60">
          <div class="flex items-center space-x-2">
            <span class="text-[#8B5A2B] text-lg font-mason">✦</span>
            <h2 class="font-mason text-lg text-[#8B5A2B] font-bold uppercase tracking-wide">
              Próximas Sesiones Programadas
            </h2>
          </div>
          <RouterLink
            :to="`/mesas/${mesaId}/calendario`"
            class="font-tarzana font-semibold text-xs text-[#8B5A2B] hover:text-[#5C3817] flex items-center space-x-1"
          >
            <span>+ Convocar nueva fecha</span>
          </RouterLink>
        </div>

        <div class="space-y-3">
          <div
            v-for="(sesion, idx) in proximasSesiones"
            :key="sesion.id"
            class="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-[#FBF4E6] border-l-4 rounded shadow-sm hover:bg-[#F3E8D0] transition-colors"
            :class="idx === 0 ? 'border-[#D4AF37] border-y border-r border-[#C2A980]' : 'border-[#8B7D6B] border-y border-r border-[#C2A980]/80'"
          >
            <div class="flex items-start sm:items-center space-x-4 mb-2 sm:mb-0">
              <div
                class="w-12 h-12 rounded flex flex-col items-center justify-center text-[#FDF8EE] border shrink-0"
                :class="idx === 0 ? 'bg-[#1A1A1A] border-[#D4AF37]' : 'bg-[#3A3228] border-[#8B7D6B]'"
              >
                <span :class="`font-tarzana text-[0.7rem] uppercase leading-none ${idx === 0 ? 'text-[#D4AF37]' : 'text-[#C2A980]'}`">{{ sesion.selloDia }}</span>
                <span class="font-mason font-bold text-base leading-none mt-1">{{ sesion.selloNum }}</span>
              </div>
              <div>
                <div class="flex items-center space-x-2">
                  <span class="font-mason text-base font-bold text-[#8B5A2B]">Sesión {{ sesion.numero.replace('#', '') }}: {{ sesion.titulo }}</span>
                  <span
                    :class="`px-2 py-0.2 font-tarzana text-[0.75rem] font-bold rounded ${ESTADOS[sesion.estado]?.cls || 'bg-[#8B7D6B]/20 text-[#5C4A32]'}`"
                  >{{ ESTADOS[sesion.estado]?.texto || sesion.estado }}</span>
                </div>
                <p class="font-minion text-sm text-[#5C4A32]">
                  Fecha Golarion: {{ sesion.fechaGolarion }} • Horario: {{ sesion.horario }}
                </p>
              </div>
            </div>
            <div class="flex items-center space-x-3 text-right font-tarzana text-xs text-[#8B7D6B]">
              <div v-if="sesion.estado === 'confirmada'" class="hidden md:block">
                <div class="text-[#1A1A1A] font-semibold">{{ sesion.asistencias }} Asistencias</div>
                <div class="text-[#6B8E23]">{{ sesion.quorum }}</div>
              </div>
              <RouterLink
                :to="`/mesas/${mesaId}/sesiones`"
                class="px-3 py-1.5 bg-[#FDF8EE] border border-[#8B7D6B] hover:border-[#8B5A2B] text-[#8B5A2B] rounded font-tarzana text-xs font-semibold"
              >
                {{ sesion.estado === 'confirmada' ? 'Gestionar Hoja de Ruta' : 'Editar Convocatoria' }}
              </RouterLink>
            </div>
          </div>
        </div>
      </div>

      <!-- Zona peligrosa -->
      <div class="pt-6 border-t-2 border-[#8B7D6B]/30">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between bg-[#F7EBEB] border border-[#8B1A1A]/30 p-5 rounded-lg">
          <div class="mb-4 sm:mb-0 pr-4">
            <div class="flex items-center space-x-2 text-[#8B1A1A] font-tarzana font-bold text-sm tracking-wider uppercase">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
              <span>Zona Peligrosa de Campaña</span>
            </div>
            <p class="font-minion text-sm text-[#5C3232] mt-1">
              La disolución de la mesa archivará permanentemente las notas de la crónica, foros tácticos y desvinculará las fichas de los jugadores.
            </p>
          </div>

          <button
            type="button"
            class="shrink-0 flex items-center space-x-2 px-5 py-2.5 bg-transparent hover:bg-[#8B1A1A] text-[#8B1A1A] hover:text-[#FDF8EE] border-2 border-[#8B1A1A] rounded font-tarzana font-bold text-[1rem] uppercase tracking-wider transition-all duration-150 shadow-sm active:scale-95"
            @click="confirmarEliminar = true"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
            <span>Eliminar Mesa</span>
          </button>
        </div>
      </div>
    </div>

    <ConfirmModal
      :open="confirmarEliminar"
      :titulo="`¿Disolver «${mesa?.nombre}»?`"
      chip="Acción irreversible de archivo"
      mensaje="La campaña desaparecerá del buscador y sus notas de crónica quedarán selladas. ¿Continuar?"
      variante="danger"
      etiqueta-ok="Eliminar Mesa"
      @close="confirmarEliminar = false"
      @accept="confirmarBaja"
    />
  </MesaGestionShell>
</template>