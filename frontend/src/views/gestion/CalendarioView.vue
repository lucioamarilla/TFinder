<script setup>
// D-05: el GM elige dia y hora con inputs reales y se envia ISO (el backend
// lo valida con _parsear). Las marcas del cuadrante se calculan por la fecha
// de cada sesion/propuesta (no existe selloNum en el contrato). La capacidad
// proviene de la mesa (jugadores_max), nunca queda 'null'.
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from '@/composables/useToast.js'
import { getMesa } from '@/services/mesas.js'
import { getSesiones } from '@/services/sesiones.js'
import { getVotaciones, votar, proponerFecha, confirmarFecha } from '@/services/votaciones.js'
import Aviso from '@/components/Aviso.vue'

const props = defineProps({ mesaId: { type: String, required: true } })

const toast = useToast()

const MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
// versión abreviada para la cuadrícula en pantallas chicas (ver .dias-corto)
const DIAS_CORTOS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
const HOY = new Date()

const anio = ref(HOY.getFullYear())
const mes = ref(HOY.getMonth())
const sesiones = ref([])
const votaciones = ref([])
const capacidadRef = ref(null)
const abrirFormulario = ref(false)
const nueva = ref({ fecha: '', hora: '' })
const errorPropuesta = ref(null)

const nombreMes = computed(() => `${MESES[mes.value]} ${anio.value}`)

const capacidad = computed(() => capacidadRef.value)

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

// dia real de la fecha ISO 'YYYY-MM-DD[THH:mm]' sin aritmetica de zonas.
function diaDe(iso) {
  const m = String(iso ?? '').match(/^(\d{4})-(\d{2})-(\d{2})/)
  if (!m) return null
  if (Number(m[1]) !== anio.value || Number(m[2]) !== mes.value + 1) return null
  return Number(m[3])
}

function marcaDe(dia) {
  if (!dia) return null
  const sesionesDelDia = sesiones.value.filter((s) => diaDe(s.fecha) === dia)
  if (sesionesDelDia.length > 0) {
    return { marcador: 'sesion', texto: 'Sesión', titulo: sesionesDelDia.map((s) => `${s.fecha}`).join(' | ') }
  }
  const propuestasDelDia = votaciones.value.filter((v) => diaDe(v.fecha) === dia)
  if (propuestasDelDia.length === 0) return null
  const principal = propuestasDelDia[0]
  if (principal.confirmada) {
    return { marcador: 'sesion', texto: 'Confirmada', titulo: principal.fecha }
  }
  return { marcador: 'propuesta', texto: 'Propuesta', titulo: principal.fecha }
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
  if (!total) return 'Aún no hay cupo definido para esta mesa.'
  const quorum = Math.max(3, Math.ceil(total * 0.6))
  return `Los miembros de la mesa votan su disponibilidad. El quórum actual es de ${quorum} de ${total} aventureros.`
})

function textoVotos(arrays) {
  if (arrays.length === 0) return 'Ninguno'
  return arrays.join(', ')
}

function circulo(direccion, votacion) {
  return votacion.miVoto === direccion
}

async function cargar() {
  const [lista, votos] = await Promise.all([
    getSesiones(props.mesaId),
    getVotaciones(props.mesaId)
  ])
  sesiones.value = lista
  votaciones.value = votos
  // D-05: capacidad real de la mesa (jugadores_max), nunca null.
  try {
    const mesa = await getMesa(props.mesaId)
    capacidadRef.value = mesa?.plazas ?? capacidadRef.value
  } catch {
    /* capacidad queda en el valor previo; el quorum lo informa amable */
  }
}

onMounted(cargar)
watch(() => props.mesaId, cargar)

async function emitirVoto(votacion, direccion) {
  const actualizada = await votar(props.mesaId, votacion.id, direccion)
  const idx = votaciones.value.findIndex((v) => v.id === votacion.id)
  if (idx >= 0) votaciones.value[idx] = actualizada
  toast.ok(actualizada.miVoto ? (actualizada.miVoto === 'favor' ? 'Tu voto quedó A FAVOR de la propuesta.' : 'Tu voto quedó EN CONTRA de la propuesta.') : 'Eliminaste tu voto.')
}

async function proponer() {
  errorPropuesta.value = null
  if (!nueva.value.fecha) {
    errorPropuesta.value = 'Elegí una fecha con el selector.'
    return
  }
  try {
    await proponerFecha(props.mesaId, { ...nueva.value })
    votaciones.value = await getVotaciones(props.mesaId)
    nueva.value = { fecha: '', hora: '' }
    abrirFormulario.value = false
    toast.ok('Propuesta convocada al tribunal de fechas · avisamos a los aventureros.')
  } catch (e) {
    errorPropuesta.value = e?.message || 'No se pudo proponer la fecha.'
  }
}

async function confirmar(votacion) {
  await confirmarFecha(props.mesaId, votacion.id)
  votaciones.value = await getVotaciones(props.mesaId)
  toast.ok('Fecha oficial fijada · la sesión queda en el calendario.')
}
</script>

<template>
      <div class="cald">
      <!-- Cabecera del calendario -->
      <div class="cald-cabecera">
        <div>
          <h2 class="titulo-seccion">Calendario &amp; Votación</h2>
          <p class="label">El día y la hora se eligen en el selector; el resto queda a votos de la mesa.</p>
        </div>
        <div class="cald-leyenda-flechas">
          <div class="leyenda">
            <span class="leyenda-aviso leyenda-aviso--sesion"></span>
            <span class="label">Sesión / Confirmada</span>
            <span class="leyenda-aviso leyenda-aviso--propuesta"></span>
            <span class="label">Propuesta activa</span>
          </div>
          <div class="flechas">
            <button type="button" class="flecha-btn" aria-label="Mes anterior" data-test="mes-anterior" @click="mesAnterior">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="15 18 9 12 15 6" /></svg>
            </button>
            <span class="num nombre-mes">{{ nombreMes }}</span>
            <button type="button" class="flecha-btn" aria-label="Mes siguiente" data-test="mes-siguiente" @click="mesSiguiente">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9 18 15 12 9 6" /></svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Cuadrícula del mes -->
      <div class="cuadricula">
        <div class="dias">
          <div v-for="(d, i) in DIAS" :key="d" class="label">
            <span class="dias-largo">{{ d }}</span>
            <span class="dias-corto" :title="d">{{ DIAS_CORTOS[i] }}</span>
          </div>
        </div>
        <div class="celdas">
          <div
            v-for="(celda, i) in celdas"
            :key="i"
            :data-celda="celda.dia ?? undefined"
            class="celda"
            :class="celda.hoy ? 'celda--hoy' : celda.enMes ? '' : 'celda--fuera'"
          >
            <span v-if="celda.dia !== null" class="num dia" :class="celda.hoy ? 'dia--hoy' : ''">{{ celda.dia }}</span>
            <div v-else class="dia-vacio"></div>
            <div v-if="celda.hoy && !marcaDe(celda.dia)" class="anillo-hoy" aria-label="Hoy"></div>
            <div v-if="marcaDe(celda.dia)" class="marca" :title="marcaDe(celda.dia).titulo">
              <span class="punto" :class="`punto--${marcaDe(celda.dia).marcador}`"></span>
              <span class="label señal" :class="`señal--${marcaDe(celda.dia).marcador}`">{{ marcaDe(celda.dia).texto }}</span>
            </div>
            <template v-else-if="celda.hoy">
              <span class="label señal señal--hoy">Hoy</span>
            </template>
            <div v-else class="dia-vacio"></div>
          </div>
        </div>
      </div>

      <!-- Propuestas activas -->
      <section class="propuestas">
        <div class="propuestas-cabecera">
          <div>
            <h2 class="titulo-seccion">Propuestas activas de sesión</h2>
            <p class="label">{{ quorumTexto }}</p>
          </div>

          <button
            type="button"
            data-test="btn-abrir-proponer"
            class="btn"
            @click="abrirFormulario = !abrirFormulario"
          >
            Proponer fecha (GM)
          </button>
        </div>

        <!-- Formulario de propuesta: dia + hora reales (D-05) -->
        <form
          v-if="abrirFormulario"
          data-test="form-proponer"
          class="card form-proponer"
          novalidate
          @submit.prevent="proponer"
        >
          <div class="field">
            <label class="label" for="pro-fecha">Día</label>
            <input id="pro-fecha" data-test="input-fecha" v-model="nueva.fecha" type="date" class="input" />
          </div>
          <div class="field">
            <label class="label" for="pro-hora">Hora</label>
            <input id="pro-hora" data-test="input-hora" v-model="nueva.hora" type="time" value="20:00" class="input" />
          </div>
          <Aviso v-if="errorPropuesta" tipo="error" data-test="error-proponer">{{ errorPropuesta }}</Aviso>
          <div class="form-proponer-envio">
            <button type="submit" data-test="btn-proponer" class="btn">Convocar propuesta</button>
          </div>
        </form>

        <div class="lista-propuestas">
          <div
            v-for="votacion in votaciones"
            :key="votacion.id"
            data-test="propuesta-votacion"
            class="card propuesta"
          >
            <div class="propuesta-identidad">
              <span class="num propuesta-fecha">{{ votacion.fecha }}</span>
              <span class="tag" :class="votacion.confirmada ? 'tag--acid' : 'tag--ink'">{{ votacion.tipo }}</span>
            </div>
            <p class="propuesta-resumen">
              <strong>Sesión {{ votacion.sesionNumero }}:</strong>
              <em>{{ votacion.titulo }}</em> · {{ votacion.resumen }}
            </p>
            <div class="propuesta-votos-info">
              <span class="label">Votaron a favor: <span class="ok num">{{ textoVotos(votacion.favor) }}</span></span>
              <span class="label">Votos en contra: <span class="contra num">{{ textoVotos(votacion.contra) }}</span></span>
            </div>

            <div class="propuesta-acciones">
              <div class="votecell vote">
                <button
                  type="button"
                  class="voto-btn"
                  :class="circulo('favor', votacion) ? 'voto-btn--activa' : ''"
                  :aria-pressed="circulo('favor', votacion)"
                  :title="votacion.miVoto === 'favor' ? 'Tu voto actual: A favor de esta fecha' : 'Votar a favor de esta fecha'"
                  @click="emitirVoto(votacion, 'favor')"
                >
                  <span class="ok">▲</span>
                  <span class="num">{{ votacion.favor.length }}</span>
                </button>

                <button
                  type="button"
                  class="voto-btn"
                  :class="circulo('contra', votacion) ? 'voto-btn--activa' : ''"
                  :aria-pressed="circulo('contra', votacion)"
                  :title="votacion.miVoto === 'contra' ? 'Tu voto actual: En contra' : 'Votar en contra / No disponible'"
                  @click="emitirVoto(votacion, 'contra')"
                >
                  <span class="contra">▼</span>
                  <span class="num">{{ votacion.contra.length }}</span>
                </button>
              </div>

              <button
                type="button"
                class="btn btn--secondary btn--sm"
                :disabled="votacion.confirmada"
                title="Fijar como fecha oficial definitiva"
                @click="confirmar(votacion)"
              >
                {{ votacion.confirmada ? 'Fecha confirmada' : 'Confirmar fecha' }}
              </button>
            </div>
          </div>

          <div v-if="votaciones.length === 0" class="card vacio" data-test="sin-propuestas">
            No hay propuestas abiertas. El Director de Juego puede convocar una nueva fecha para la mesa.
          </div>
        </div>
      </section>
    </div>
</template>

<style scoped>
.cald { display: grid; gap: var(--space-lg); }
.titulo-seccion { margin: 0; font-size: var(--text-title); color: var(--color-ink); }
.cald-cabecera { display: flex; flex-direction: column; gap: var(--space-sm); flex-wrap: wrap; }
.cald-leyenda-flechas { display: flex; align-items: center; justify-content: space-between; gap: var(--space-md); flex-wrap: wrap; }
.leyenda { display: flex; gap: var(--space-sm); align-items: center; flex-wrap: wrap; }
.leyenda-aviso { width: 10px; height: 10px; border-radius: 999px; display: inline-block; border: var(--rule-hair) solid var(--color-rule); }
.leyenda-aviso--sesion { background: var(--color-accent-2); }
.leyenda-aviso--propuesta { background: var(--color-accent); }
.flechas { display: inline-flex; align-items: center; gap: var(--space-2xs); }
.flecha-btn { min-width: 32px; min-height: 32px; display: grid; place-items: center; background: var(--color-paper-2); border: var(--rule-bar) solid var(--color-rule); border-radius: var(--radius-card); color: var(--color-ink); cursor: pointer; transition: border-color var(--dur-micro) var(--ease-out), color var(--dur-micro) var(--ease-out); }
.flecha-btn:hover { border-color: var(--color-focus); color: var(--color-accent-2); }
.nombre-mes { font-size: var(--text-sm); color: var(--color-ink); min-width: 12ch; text-align: center; }
.cuadricula { border: var(--rule-hair) solid var(--color-rule); background: var(--color-paper-2); overflow: hidden; }
.dias, .celdas { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); }
.dias { border-bottom: var(--rule-hair) solid var(--color-rule); background: var(--color-paper-3); text-align: center; }
.dias .label { padding-block: var(--space-2xs); }
/* día de semana: nombre completo ≥40rem, abreviado debajo; a la vez se compacta
   la celda y la marca queda solo como punto (el detalle sigue en la leyenda y
   en la lista de propuestas de abajo) */
.dias-largo { display: none; }
.dias-corto { display: inline; }
@media (min-width: 40rem) { .dias-largo { display: inline; } .dias-corto { display: none; } }
.celdas { border-top: var(--rule-hair) solid var(--color-rule); }
.celda { min-height: 5.5rem; padding: var(--space-2xs); border-right: var(--rule-hair) solid var(--color-rule); border-bottom: var(--rule-hair) solid var(--color-rule); display: flex; flex-direction: column; justify-content: space-between; align-items: center; gap: var(--space-3xs); }
.celda--fuera { color: var(--color-muted); background: var(--color-paper-3); }
.celda--hoy { background: var(--color-paper-3); }
.dia { font-size: var(--text-sm); color: var(--color-ink); }
.dia--hoy { color: var(--color-accent-2); }
.dia-vacio { height: var(--space-md); }
.anillo-hoy { width: 28px; height: 28px; border: 2px solid var(--color-accent-2); border-radius: 999px; }
.marca { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.punto { width: 10px; height: 10px; border-radius: 999px; display: inline-block; border: var(--rule-hair) solid var(--color-paper); }
.punto--sesion { background: var(--color-accent-2); }
.punto--propuesta { background: var(--color-accent); }
.señal { font-size: 10px; font-weight: 700; }
.señal--sesion { color: var(--color-accent-2); }
.señal--propuesta { color: var(--color-accent); }
.señal--hoy { color: var(--color-accent-2); }
.propuestas { display: grid; gap: var(--space-md); }
.propuestas-cabecera { display: flex; align-items: center; justify-content: space-between; gap: var(--space-md); flex-wrap: wrap; border-bottom: var(--rule-hair) solid var(--color-rule); padding-bottom: var(--space-sm); }
.form-proponer { display: grid; gap: var(--space-sm); grid-template-columns: repeat(2, minmax(0, 1fr)); }
.form-proponer-envio { display: flex; justify-content: flex-end; grid-column: 1 / -1; }
.lista-propuestas { display: grid; gap: var(--space-sm); }
.propuesta { display: flex; flex-direction: column; gap: var(--space-2xs); }
.propuesta-identidad { display: flex; align-items: center; gap: var(--space-2xs); flex-wrap: wrap; }
.propuesta-fecha { font-size: var(--text-md); color: var(--color-ink); }
.propuesta-resumen { margin: 0; font-size: var(--text-sm); color: var(--color-ink-2); }
.propuesta-votos-info { display: flex; gap: var(--space-md); flex-wrap: wrap; }
.ok { color: var(--color-accent-2); }
.contra { color: var(--color-error); }
.propuesta-acciones { display: flex; align-items: center; justify-content: space-between; gap: var(--space-md); flex-wrap: wrap; }
.votecell { display: flex; align-items: center; gap: var(--space-sm); }
.voto-btn { background: var(--color-paper-3); border: var(--rule-bar) solid var(--color-rule); border-radius: var(--radius-card); padding: var(--space-2xs) var(--space-sm); display: inline-flex; align-items: center; gap: var(--space-2xs); cursor: pointer; font-weight: 700; color: var(--color-ink-2); transition: border-color var(--dur-micro) var(--ease-out), color var(--dur-micro) var(--ease-out); }
.voto-btn:hover { color: var(--color-ink); border-color: var(--color-muted); }
.voto-btn--activa { border-color: var(--color-accent); background: var(--color-paper); color: var(--color-ink); }
@media (max-width: 40rem) { .celda { min-height: 4.25rem; } .señal { display: none; } .punto { width: 12px; height: 12px; } }
.vacio { text-align: center; color: var(--color-ink-2); padding: var(--space-lg); }
@media (max-width: 60rem) { .form-proponer { grid-template-columns: minmax(0, 1fr); } }
</style>
