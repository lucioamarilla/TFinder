<script setup>
import { ref, computed, inject, onMounted, watch } from 'vue'
import { useToast } from '@/composables/useToast.js'
import MesaGestionShell from '@/components/mesa/MesaGestionShell.vue'
import ModalExpulsar from '@/components/modals/ModalExpulsar.vue'
import { getMiembros, getSolicitudes, aceptarSolicitud, rechazarSolicitud, expulsarMiembro } from '@/services/jugadores.js'

const props = defineProps({ mesaId: { type: String, required: true } })

const toast = useToast()
const gestion = inject('mesaGestion')

const miembros = ref([])
const solicitudes = ref([])
const capacidad = ref(5)
const expulsarAbierto = ref(false)
const candidatoExpulsar = ref(null)
const procesando = ref(false)

const nombreMesa = computed(() => gestion?.mesa.value?.nombre || 'la mesa')
const jugadorModal = computed(() => {
  if (!candidatoExpulsar.value) return { nombre: '', rol: '', chip: '' }
  const m = candidatoExpulsar.value
  return { nombre: m.nombre, rol: m.rol, chip: `${m.personaje} · ${m.clase} Nvl ${m.nivel}` }
})

const ESTADOS = { Activo: 'bg-[#6B8E23]/15 text-[#556B2F] border-[#6B8E23]/50', 'En pausa': 'bg-[#8B7D6B]/15 text-[#5C4A32] border-[#8B7D6B]/50' }

async function cargar() {
  const [equipo, pendientes] = await Promise.all([getMiembros(props.mesaId), getSolicitudes(props.mesaId)])
  miembros.value = equipo.miembros
  capacidad.value = equipo.capacidad
  solicitudes.value = pendientes
}

onMounted(cargar)
watch(() => props.mesaId, cargar)

async function aceptar(solicitud) {
  await aceptarSolicitud(props.mesaId, solicitud.id)
  toast.ok('Solicitud aceptada · nuevo héroe en la mesa.')
  await cargar()
}

async function rechazar(solicitud) {
  await rechazarSolicitud(props.mesaId, solicitud.id)
  toast.info('Solicitud rechazada · se notificó al aventurero.')
  await cargar()
}

function abrirExpulsar(miembro) {
  candidatoExpulsar.value = miembro
  expulsarAbierto.value = true
}

async function confirmarExpulsion() {
  procesando.value = true
  try {
    const expulsado = await expulsarMiembro(props.mesaId, candidatoExpulsar.value.id)
    toast.ok(`${expulsado.nombre} fue expulsado de ${nombreMesa.value}.`)
    await cargar()
  } catch (e) {
    toast.error(e.message || 'No pudimos expulsar al miembro.')
  } finally {
    procesando.value = false
    expulsarAbierto.value = false
  }
}
</script>

<template>
  <MesaGestionShell :mesa-id="mesaId">
    <div class="space-y-8">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b-2 border-[#C2A980] pb-4">
        <h2 class="font-mason text-xl font-bold text-[#8B5A2B] uppercase tracking-wide flex items-center gap-2">
          <span>✦</span> Jugadores &amp; Solicitudes
          <span class="text-xs bg-[#6B8E23] text-white px-1.5 py-0.2 rounded font-tarzana">{{ miembros.length }}/{{ capacidad }}</span>
        </h2>
      </div>

      <!-- Solicitudes pendientes -->
      <section v-if="solicitudes.length" aria-labelledby="heading-solicitudes">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-[#D4AF37]">◆</span>
          <h3 id="heading-solicitudes" class="font-tarzana text-sm font-bold text-[#8B5A2B] uppercase tracking-wider">
            Solicitudes Pendientes de Ingreso ({{ solicitudes.length }})
          </h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
          <article
            v-for="solicitud in solicitudes"
            :key="solicitud.id"
            class="bg-[#FDF8EE] border border-[#C2A980] rounded p-4 flex flex-col justify-between gap-3 shadow-sm"
          >
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 rounded-full bg-[#6B8E23] text-[#FDF8EE] flex items-center justify-center font-mason text-sm font-bold shrink-0">
                {{ solicitud.avatar }}
              </div>
              <div class="min-w-0">
                <h4 class="font-mason font-bold text-[#8B5A2B] leading-tight">{{ solicitud.nombre }}</h4>
                <p class="font-tarzana text-xs text-[#5C4A32]">{{ solicitud.personaje }} · {{ solicitud.clase }} Nvl {{ solicitud.nivel }}</p>
                <p class="font-minion italic text-xs text-[#736351] mt-1">{{ solicitud.nota }}</p>
              </div>
            </div>
            <div class="flex items-center justify-between">
              <span class="font-minion text-[0.7rem] text-[#8B7D6B]">{{ solicitud.fecha }}</span>
              <div class="flex items-center gap-2">
                <button
                  type="button"
                  class="font-tarzana text-xs font-bold px-3 py-1.5 rounded flex items-center gap-1.5 bg-[#8B1A1A]/10 border border-[#8B1A1A]/50 text-[#8B1A1A] hover:bg-[#8B1A1A] hover:text-white transition-colors"
                  title="Rechazar solicitud"
                  @click="rechazar(solicitud)"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                  Rechazar
                </button>
                <button
                  type="button"
                  class="font-tarzana text-xs font-bold px-3 py-1.5 rounded flex items-center gap-1.5 bg-[#6B8E23]/10 border border-[#6B8E23]/50 text-[#556B2F] hover:bg-[#6B8E23] hover:text-white transition-colors"
                  title="Aceptar e incorporar a la campaña"
                  @click="aceptar(solicitud)"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  Aceptar
                </button>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- Miembros -->
      <section aria-labelledby="heading-miembros">
        <h3 id="heading-miembros" class="font-mason text-lg font-bold text-[#8B5A2B] mb-3">
          Mesa de Aventureros ({{ miembros.length }} de {{ capacidad }} plazas)
        </h3>

        <div class="border border-[#C2A980] rounded-sm overflow-hidden shadow-sm bg-white/40 overflow-x-auto">
          <table class="w-full text-left border-collapse min-w-[640px]">
            <thead>
              <tr class="bg-[#E8DCC8] border-b border-[#C2A980] font-tarzana text-xs text-[#8B5A2B]">
                <th class="py-3 px-4 font-bold border-r border-[#C2A980]/60">MIEMBRO</th>
                <th class="py-3 px-4 font-bold border-r border-[#C2A980]/60">PERSONAJE ACTIVO</th>
                <th class="py-3 px-4 font-bold border-r border-[#C2A980]/60 w-[120px]">ESTADO</th>
                <th class="py-3 px-4 font-bold border-r border-[#C2A980]/60 w-[140px]">INGRESO</th>
                <th class="py-3 px-3 font-bold w-[110px] text-center">ACCIÓN</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#C2A980]/60 font-minion text-sm">
              <tr v-for="miembro in miembros" :key="miembro.id" class="hover:bg-[#FBF4E6]/60 transition-colors">
                <td class="py-3 px-4 border-r border-[#C2A980]/40">
                  <div class="flex items-center gap-2.5">
                    <div class="w-8 h-8 rounded-full bg-[#8B5A2B] text-[#FDF8EE] flex items-center justify-center font-mason text-[0.7rem] font-bold shrink-0">
                      {{ miembro.avatar }}
                    </div>
                    <div>
                      <div class="font-mason font-bold text-[#1A1A1A]">{{ miembro.nombre }}</div>
                      <div class="text-xs text-[#8B7D6B]">{{ miembro.handle || miembro.rol }}</div>
                    </div>
                  </div>
                </td>
                <td class="py-3 px-4 border-r border-[#C2A980]/40">
                  <div class="font-minion text-[#1A1A1A] font-semibold">{{ miembro.personaje }}</div>
                  <div class="text-xs text-[#736351]">{{ miembro.clase }} Nvl {{ miembro.nivel }}</div>
                </td>
                <td class="py-3 px-4 border-r border-[#C2A980]/40">
                  <span class="font-tarzana text-[0.7rem] px-2 py-0.5 rounded border font-bold" :class="ESTADOS[miembro.estado] || ESTADOS['Activo']">
                    {{ miembro.estado.toUpperCase() }}
                  </span>
                </td>
                <td class="py-3 px-4 border-r border-[#C2A980]/40 font-tarzana text-xs text-[#8B7D6B]">
                  {{ miembro.fecha }}
                </td>
                <td class="py-3 px-3 text-center">
                  <button
                    type="button"
                    class="font-tarzana text-[0.7rem] font-bold px-2.5 py-1 rounded border border-[#8B1A1A]/50 text-[#8B1A1A] hover:bg-[#8B1A1A] hover:text-[#FDF8EE] transition-colors"
                    @click="abrirExpulsar(miembro)"
                  >
                    EXPULSAR
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>

    <ModalExpulsar
      :open="expulsarAbierto"
      :jugador="jugadorModal"
      :mesa-nombre="nombreMesa"
      @close="expulsarAbierto = false"
      @accepted="confirmarExpulsion"
    />
  </MesaGestionShell>
</template>