<script setup>
import { ref, computed, inject, onMounted, watch } from 'vue'
import { useToast } from '@/composables/useToast.js'
import MesaGestionShell from '@/components/mesa/MesaGestionShell.vue'
import ModalAsociarBuild from '@/components/modals/ModalAsociarBuild.vue'
import { getBuilds, miBuildActivo, vincularBuild } from '@/services/builds.js'
import { getMiembros } from '@/services/jugadores.js'
import { getMesas } from '@/services/mesas.js'

const props = defineProps({ mesaId: { type: String, required: true } })

const toast = useToast()
const gestion = inject('mesaGestion')

const builds = ref([])
const equipo = ref({ miembros: [], capacidad: 5 })
const miBuild = ref(null)
const mesas = ref([])
const modalAbierto = ref(false)

const libres = computed(() => Math.max(0, equipo.value.capacidad - equipo.value.miembros.length))
const conBuild = computed(() => builds.value.filter((b) => b.protagonista).length)

const ICONOS_CLASE = {
  Guerrero: 'M6.92 3.75L12 8.83l5.08-5.08 1.42 1.42L13.42 10.25 18.5 15.33l-1.42 1.42L12 11.67l-5.08 5.08-1.42-1.42 5.08-5.08L5.5 5.17z',
  Paladín: 'M12 2l8 4v6c0 5-3.4 8.5-8 10-4.6-1.5-8-5-8-10V6l8-4zm-1 12l5-5-1.4-1.4L11 11.2 9.4 9.6 8 11l3 3z',
  Mago: 'M12 2l1.8 5.2L19 9l-5.2 1.8L12 16l-1.8-5.2L5 9l5.2-1.8L12 2z',
  Explorador: 'M12 2l9 5v10l-9 5-9-5V7l9-5zm0 4.5L6 9.7v5.6l6 3.2 6-3.2V9.7l-6-3.2z'
}

async function cargar() {
  const [lista, jugadores, todas] = await Promise.all([getBuilds(props.mesaId), getMiembros(props.mesaId), getMesas()])
  builds.value = lista
  equipo.value = jugadores
  mesas.value = todas.map((m) => ({ id: m.id, nombre: m.nombre, estado: m.estado }))
  miBuild.value = await miBuildActivo()
}

onMounted(cargar)
watch(() => props.mesaId, cargar)

function abrirModal() {
  modalAbierto.value = true
}

async function asociar(mesaDestinoId) {
  modalAbierto.value = false
  if (!mesaDestinoId) return
  const destino = mesas.value.find((m) => m.id === mesaDestinoId)
  await vincularBuild(miBuild.value.id, mesaDestinoId)
  toast.ok(`Build vinculado a «${destino?.nombre || 'la mesa'}».`)
}
</script>

<template>
  <MesaGestionShell :mesa-id="mesaId">
    <div class="space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b-2 border-[#C2A980] pb-4">
        <div>
          <h2 class="font-mason text-xl font-bold text-[#8B5A2B] uppercase tracking-wide flex items-center gap-2">
            <span>✦</span> Builds Asociados a la Campaña
          </h2>
          <p class="font-minion italic text-sm text-[#736351] mt-0.5">
            {{ conBuild }} de {{ equipo.miembros.length }} jugadores activos tienen un build enlazado.
          </p>
        </div>
        <button
          type="button"
          class="btn-gold-emboss px-5 py-2.5 rounded font-tarzana text-xs font-bold flex items-center gap-2 self-start sm:self-auto"
          @click="abrirModal"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
          </svg>
          Asociar mi Build
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <article
          v-for="build in builds"
          :key="build.id"
          class="bg-[#FDF8EE] border border-[#C2A980] border-l-4 border-l-[#8B5A2B] rounded p-4 shadow-sm flex flex-col justify-between gap-3 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start gap-3">
            <div class="w-11 h-11 rounded bg-[#1A1A1A] border border-[#D4AF37] flex items-center justify-center shrink-0">
              <svg class="w-6 h-6 text-[#D4AF37]" viewBox="0 0 24 24" fill="currentColor">
                <path :d="ICONOS_CLASE[build.clase] || ICONOS_CLASE.Guerrero"></path>
              </svg>
            </div>
            <div class="min-w-0">
              <h3 class="font-mason text-lg font-bold text-[#8B5A2B] leading-tight">{{ build.nombre }}</h3>
              <p class="font-tarzana text-xs font-bold text-[#5C4A32] uppercase tracking-wider">
                {{ build.clase }} · Nivel {{ build.nivel }}
              </p>
            </div>
          </div>

          <p class="font-minion text-sm text-[#5C4A32] italic">{{ build.detalle }}</p>

          <div class="flex items-center justify-between pt-2 border-t border-[#C2A980]/50">
            <span class="font-minion text-xs text-[#736351]">Jugador: {{ build.persona }} <span class="text-[#8B7D6B]">({{ build.handle }})</span></span>
            <RouterLink
              :to="`/builds/${build.id}`"
              class="font-tarzana text-xs font-bold text-[#8B5A2B] hover:underline decoration-[#D4AF37] underline-offset-4"
            >
              Ver Ficha →
            </RouterLink>
          </div>
        </article>

        <!-- Ranura vacante -->
        <article
          v-for="n in libres"
          :key="`vacante-${n}`"
          class="bg-[#FBF4E6]/60 border border-dashed border-[#C2A980] rounded p-6 flex flex-col items-center justify-center text-center gap-2 min-h-[170px]"
        >
          <span class="text-[#8B7D6B] text-2xl">＋</span>
          <p class="font-minion italic text-sm text-[#736351] max-w-[240px]">
            La campaña tiene espacio para un aventurero adicional. Una vez aceptada una solicitud, su build aparecerá aquí.
          </p>
          <RouterLink :to="`/mesas/${mesaId}/jugadores`" class="font-tarzana text-xs font-bold text-[#8B5A2B] hover:underline uppercase tracking-wider">
            + Invitar a Jugador
          </RouterLink>
        </article>
      </div>

      <p class="font-minion italic text-xs text-[#8B7D6B] border-t border-[#C2A980]/50 pt-4">
        Los builds asociados se recalculan automáticamente al subir de nivel en la campaña. Los jugadores pueden importar fichas en formato JSON desde Pathbuilder 1e o exportar su bloque de estadísticas OGL para imprimir en mesa.
      </p>
    </div>

    <ModalAsociarBuild
      :open="modalAbierto"
      :build="{ nombre: miBuild?.nombre || '', detalle: miBuild?.detalle || '' }"
      :mesas="mesas"
      @close="modalAbierto = false"
      @accepted="asociar"
    />
  </MesaGestionShell>
</template>