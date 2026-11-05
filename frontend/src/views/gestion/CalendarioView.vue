<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from '@/composables/useToast.js'
import MesaGestionShell from '@/components/mesa/MesaGestionShell.vue'
import ModalDatePicker from '@/components/modals/ModalDatePicker.vue'
import { getSesiones } from '@/services/sesiones.js'
import { getMiembros } from '@/services/jugadores.js'
import { getVotaciones, votar, proponerFecha, confirmarFecha } from '@/services/votaciones.js'

const props = defineProps({ mesaId: { type: String, required: true } })

const toast = useToast()

const MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
const DIAS = ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'DOMINGO']
const HOY = new Date()

const anio = ref(HOY.getFullYear())
const mes = ref(HOY.getMonth())
const sesiones = ref([])
const votaciones = ref([])
const capacidad = ref(4)
const abrirPicker = ref(false)

const nombreMes = computed(() => `${MESES[mes.value].toUpperCase()} ${anio.value}`)

const celdas = computed(() => {
  const primerDia = new Date(anio.value, mes.value, 1)
  const offset = (primerDia.getDay() + 6) % 7
  const total = new Date(anio.value, mes.value + 1, 0).getDate()
  const celdasLista = []
  for (let i = 0; i < offset; i++) celdasLista.push({ dia: null, enMes: false })
  for (let d = 1; d <= total; d++) celdasLista.push({ dia: d, enMes: true, hoy: esHoy(d) })
  while (celdasLista.length % 7 !== 0) celdasLista.push({ dia: null, enMes: false })
  return celdasLista
})

function esHoy(dia) {
  return anio.value === HOY.getFullYear() && mes.value === HOY.getMonth() && dia === HOY.getDate()
}

function marcaDe(dia) {
  if (!dia) return null
  const coincidencias = sesiones.value.filter((s) => String(dia) === String(parseInt(s.selloNum, 10)))
  if (coincidencias.length === 0) return null
  const iconos = { confirmada: 'CONFIRMADA', ejecutada: 'ACTA LISTA', borrador: 'PROPUESTA', tentativa: 'PROPUESTA', suspendida: 'SIN QUÓRUM' }
  const colores = { confirmada: '#6B8E23', ejecutada: '#6B8E23', borrador: '#D4AF37', tentativa: '#D4AF37', suspendida: '#8B7D6B' }
  const principal = coincidencias[0]
  return {
    color: colores[principal.estado] || '#8B7D6B',
    texto: iconos[principal.estado] || 'SESIÓN',
    titulo: coincidencias.map((s) => `${s.numero}: ${s.titulo}`).join(' | ')
  }
}

function mesAnterior() {
  mes.value = mes.value === 0 ? 11 : mes.value - 1
  if (mes.value === 11) anio.value -= 1
}

function mesSiguiente() {
  mes.value = mes.value === 11 ? 0 : mes.value + 1
  if (mes.value === 0) anio.value += 1
}

const quorumTexto = computed(() => {
  const total = capacidad.value
  const quorum = Math.max(3, Math.ceil(total * 0.6))
  return `Los miembros de la mesa votan su disponibilidad. El quórum actual es de ${quorum} de ${total} aventureros.`
})

const candidatosFechas = computed(() => {
  const lista = []
  const hoy = new Date()
  const sabado = hoy.getDay() === 6 ? hoy.getDate() : hoy.getDate() + ((6 - hoy.getDay() + 7) % 7)
  for (let semana = 0; semana < 4 && lista.length < 4; semana++) {
    const fecha = new Date(hoy.getFullYear(), hoy.getMonth(), sabado + semana * 7)
    const dia = fecha.getDate()
    const etiqueta = `${MESES[fecha.getMonth()].slice(0, 3)}`
    const label = `Sábado ${dia} de ${etiqueta} de ${fecha.getFullYear()}`
    lista.push({ value: label, label, detalle: '18:00 a 22:00 (GMT+1)' })
  }
  return lista
})

function textoVotos(arrays) {
  if (arrays.length === 0) return 'Ninguno'
  return arrays.join(', ')
}

function circulo(direccion, votacion) {
  return votacion.miVoto === direccion
}

async function cargar() {
  const [lista, jugadores, votos] = await Promise.all([
    getSesiones(props.mesaId),
    getMiembros(props.mesaId),
    getVotaciones(props.mesaId)
  ])
  sesiones.value = lista
  capacidad.value = jugadores.capacidad
  votaciones.value = votos
}

onMounted(cargar)
watch(() => props.mesaId, cargar)

async function emitirVoto(votacion, direccion) {
  const actualizada = await votar(props.mesaId, votacion.id, direccion)
  const idx = votaciones.value.findIndex((v) => v.id === votacion.id)
  if (idx >= 0) votaciones.value[idx] = actualizada
  toast.ok(actualizada.miVoto ? (actualizada.miVoto === 'favor' ? 'Tu voto quedó A FAVOR de la propuesta.' : 'Tu voto quedó EN CONTRA de la propuesta.') : 'Eliminaste tu voto.')
}

async function proponer(seleccion) {
  abrirPicker.value = false
  if (!seleccion) return
  const nueva = await proponerFecha(props.mesaId, { fecha: seleccion, sesionNumero: '#30', titulo: 'Sesión Extraordinaria' })
  votaciones.value.unshift(nueva)
  toast.ok('Propuesta convocada al tribunal de fechas · avisamos a los aventureros.')
}

async function confirmar(votacion) {
  await confirmarFecha(props.mesaId, votacion.id)
  votaciones.value = votaciones.value.filter((v) => v.id !== votacion.id)
  toast.ok(`Fecha oficial fijada · «${votacion.titulo}» queda en el calendario.`)
}
</script>

<template>
  <MesaGestionShell :mesa-id="mesaId">
    <div class="space-y-8">
      <!-- Cabecera del calendario -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div class="space-y-1">
          <h2 class="font-mason text-xl font-bold text-[#8B5A2B] uppercase tracking-wide">✦ Calendario &amp; Votación</h2>
          <p class="font-minion italic text-sm text-[#554a3e]">Cronología golariana de la mesa; los sábados son el día canónico.</p>
        </div>
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-3 font-tarzana text-xs text-[#554737]">
            <div class="flex items-center gap-1.5">
              <span class="w-2.5 h-2.5 rounded-full bg-[#6B8E23] shadow-sm"></span>
              <span>SESIÓN CONFIRMADA</span>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="w-2.5 h-2.5 rounded-full bg-[#D4AF37] shadow-sm"></span>
              <span>PROPUESTA ACTIVA</span>
            </div>
          </div>
          <div class="flex items-center gap-1 bg-[#E8DCC8] p-0.5 rounded border border-[#C2A980]">
            <button class="px-2.5 py-1 text-[#8B5A2B] hover:bg-[#FDF8EE] rounded font-mason text-xs font-bold transition-colors" title="Mes anterior" @click="mesAnterior">
              «
            </button>
            <span class="px-2 font-tarzana text-xs font-bold text-[#1A1A1A]">{{ nombreMes }}</span>
            <button class="px-2.5 py-1 text-[#8B5A2B] hover:bg-[#FDF8EE] rounded font-mason text-xs font-bold transition-colors" title="Mes siguiente" @click="mesSiguiente">
              »
            </button>
          </div>
        </div>
      </div>

      <!-- Cuadrícula del mes -->
      <div class="border border-[#C2A980] rounded bg-[#FDF8EE]/90 overflow-hidden shadow-sm">
        <div class="grid grid-cols-7 bg-[#E8DCC8] border-b border-[#C2A980] text-center font-tarzana text-xs font-bold text-[#8B5A2B] py-2.5">
          <div v-for="d in DIAS" :key="d" :class="d === 'SÁBADO' ? 'bg-[#ded0ba]/60' : ''">{{ d }}</div>
        </div>
        <div class="grid grid-cols-7 divide-x divide-y divide-[#C2A980]/50 text-center">
          <div
            v-for="(celda, i) in celdas"
            :key="i"
            class="h-20 sm:h-24 p-2 flex flex-col justify-between items-center hover:bg-[#FAF2DF] transition-colors"
            :class="celda.hoy ? 'bg-[#F4ECD8]/70' : celda.enMes ? '' : 'bg-[#E8DCC8]/40 text-[#8B7D6B]'"
          >
            <span
              v-if="celda.dia !== null"
              class="font-mason text-sm sm:text-base font-bold"
              :class="celda.hoy ? 'text-[#8B5A2B]' : celda.enMes ? 'text-[#1A1A1A]' : 'text-[#8B7D6B]/60'"
            >{{ celda.dia }}</span>
            <div v-else class="h-4"></div>
            <div v-if="celda.hoy" class="w-8 h-8 rounded border-2 border-[#8B5A2B] flex items-center justify-center bg-[#FDF8EE] shadow-sm pointer-events-none" />
            <div v-if="marcaDe(celda.dia)" class="flex flex-col items-center pointer-events-auto" :title="marcaDe(celda.dia).titulo">
              <span class="rounded-full ring-2 ring-[#FDF8EE] shadow-sm" :class="marcaDe(celda.dia).color === '#6B8E23' ? 'w-3 h-3 bg-[#6B8E23]' : 'w-2.5 h-2.5 bg-[#D4AF37]'" v-if="marcaDe(celda.dia).color === '#6B8E23' || marcaDe(celda.dia).color === '#D4AF37'"></span>
              <span class="w-2.5 h-2.5 rounded-full bg-[#8B7D6B] shadow-sm" v-else></span>
              <span class="font-tarzana text-[10px] font-bold mt-0.5 hidden sm:inline" :style="{ color: marcaDe(celda.dia).color }">{{ marcaDe(celda.dia).texto }}</span>
            </div>
            <template v-else-if="celda.hoy">
              <span class="font-tarzana text-[10px] text-[#8B5A2B] font-extrabold uppercase">HOY</span>
            </template>
            <div v-else class="h-4"></div>
          </div>
        </div>
      </div>

      <!-- Propuestas activas -->
      <section class="space-y-4 pt-1">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-[#C2A980] gap-4">
          <div>
            <h3 class="font-mason text-xl font-bold text-[#8B5A2B] flex items-center gap-2">
              <span>✦</span> PROPUESTAS ACTIVAS DE SESIÓN
            </h3>
            <p class="font-minion italic text-sm text-[#554a3e]">{{ quorumTexto }}</p>
          </div>

          <button
            type="button"
            class="btn-gold px-5 py-2.5 rounded font-tarzana text-sm font-bold uppercase tracking-wider flex items-center justify-center gap-2 self-start sm:self-auto shrink-0"
            @click="abrirPicker = true"
          >
            <svg class="w-4 h-4 text-[#1A1A1A]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
            </svg>
            PROPONER FECHA (GM)
          </button>
        </div>

        <div class="space-y-3.5">
          <div
            v-for="votacion in votaciones"
            :key="votacion.id"
            class="bg-[#FDF8EE] border border-[#C2A980] hover:border-[#8B5A2B] p-4 sm:p-5 rounded transition-all duration-150 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4"
          >
            <div class="space-y-1">
              <div class="flex flex-wrap items-center gap-2 sm:gap-3">
                <span class="font-mason text-base sm:text-lg font-bold text-[#8B5A2B]">
                  {{ votacion.fecha }}
                </span>
                <span class="px-2 py-0.5 bg-[#D4AF37]/20 border border-[#D4AF37] font-tarzana text-xs font-bold text-[#8B5A2B] rounded">
                  {{ votacion.tipo }}
                </span>
              </div>
              <p class="font-minion text-sm text-[#554a3e]">
                <strong class="text-[#1A1A1A]">Sesión {{ votacion.sesionNumero }}:</strong>
                <em>{{ votacion.titulo }}</em> — {{ votacion.resumen }}
              </p>
              <div class="font-tarzana text-xs text-[#8B7D6B] flex items-center gap-3 pt-1">
                <span>Votaron a favor: <strong class="text-[#6B8E23]">{{ textoVotos(votacion.favor) }}</strong></span>
                <span>•</span>
                <span>Votos en contra: <strong class="text-[#8B1A1A]">{{ textoVotos(votacion.contra) }}</strong></span>
              </div>
            </div>

            <div class="flex items-center gap-4 shrink-0 self-end md:self-center">
              <div class="flex items-center gap-2 bg-[#E8DCC8]/70 px-3 py-1.5 rounded-full border border-[#C2A980]">
                <button
                  type="button"
                  class="p-1.5 flex items-center gap-1.5 transition-transform active:scale-95 rounded-full"
                  :class="circulo('favor', votacion) ? 'ring-2 ring-[#D4AF37] bg-[#FDF8EE]' : 'text-[#8B7D6B] hover:text-[#6B8E23]'"
                  :title="votacion.miVoto === 'favor' ? 'Tu voto actual: A favor de esta fecha' : 'Votar a favor de esta fecha'"
                  @click="emitirVoto(votacion, 'favor')"
                >
                  <svg class="w-5 h-5 text-[#6B8E23]" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                  </svg>
                  <span class="font-mason text-base font-bold text-[#1A1A1A] pr-1">{{ votacion.favor.length }}</span>
                </button>

                <div class="h-4 w-px bg-[#C2A980]"></div>

                <button
                  type="button"
                  class="p-1.5 flex items-center gap-1.5 text-[#8B7D6B] hover:text-[#8B1A1A] transition-colors rounded-full"
                  :class="circulo('contra', votacion) ? 'ring-2 ring-[#D4AF37] bg-[#FDF8EE]' : ''"
                  :title="votacion.miVoto === 'contra' ? 'Tu voto actual: En contra' : 'Votar en contra / No disponible'"
                  @click="emitirVoto(votacion, 'contra')"
                >
                  <svg class="w-5 h-5 text-[#8B1A1A]" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                  <span class="font-mason text-base font-bold text-[#1A1A1A] pr-1">{{ votacion.contra.length }}</span>
                </button>
              </div>

              <button
                type="button"
                class="px-3.5 py-1.5 rounded font-tarzana text-xs font-bold uppercase tracking-wider border-[#6B8E23] text-[#6B8E23] hover:bg-[#6B8E23] hover:text-white transition-colors border-0"
                :style="{ border: '1.5px solid #6B8E23' }"
                title="Fijar como fecha oficial definitiva"
                @click="confirmar(votacion)"
              >
                CONFIRMAR FECHA
              </button>
            </div>
          </div>

          <div v-if="votaciones.length === 0" class="bg-[#FBF4E6] border border-dashed border-[#C2A980] rounded p-8 text-center font-minion italic text-[#736351]">
            No hay propuestas abiertas. El Director de Juego puede convocar una nueva fecha para la mesa.
          </div>
        </div>
      </section>
    </div>

    <ModalDatePicker
      :open="abrirPicker"
      chip="Proponer fecha GM"
      :candidatos="candidatosFechas"
      @close="abrirPicker = false"
      @accepted="proponer"
    />
  </MesaGestionShell>
</template>