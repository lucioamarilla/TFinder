<script setup>
// D-04: la vista vive sobre SesionOut del backend:
//   { id, mesa_id, estado: 'abierta' | 'cerrada', fecha, confirmada_at }
// No existen numero/titulo/asistencias/quorum/diario en el contrato: el
// ordinal se deriva del orden cronologico y el diario se administra en
// /gestion/sesiones/:id/diario (feed-api) tras cerrar la sesion.
import { ref, computed, onMounted, watch } from 'vue'
import { getSesiones } from '@/services/sesiones.js'
import Aviso from '@/components/Aviso.vue'

const props = defineProps({ mesaId: { type: String, required: true } })

const sesiones = ref([])
const cargando = ref(true)
const error = ref(null)

const ETIQUETAS_ESTADO = {
  abierta: { texto: 'Abierta', cls: 'tag--acid' },
  cerrada: { texto: 'Cerrada', cls: 'tag--ember' }
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
  const crudo = String(estado ?? '')
  const capitalizado = crudo.charAt(0).toUpperCase() + crudo.slice(1)
  return ETIQUETAS_ESTADO[estado] ?? { texto: capitalizado, cls: 'tag--ink' }
}

function fmt(fecha) {
  if (!fecha) return 'Fecha por definir'
  const m = String(fecha).match(/^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2}))?/)
  if (!m) return String(fecha)
  const [, y, mes, d, hh, mm] = m
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
      <div class="sesv">
      <div class="sesv-cabecera">
        <div>
          <h2 class="titulo-seccion">Historial de Sesiones</h2>
          <p class="label">Convocatorias oficiales de la mesa; el diario de cada sesión vive en su propia página.</p>
        </div>
        <span class="tag tag--ink">{{ resumen }}</span>
      </div>

      <Aviso v-if="error" tipo="error" banner data-test="error-sesiones">
        {{ error }}
        <div class="aviso-acciones">
          <button class="btn btn--sm" type="button" @click="cargar">Reintentar</button>
        </div>
      </Aviso>

      <div v-if="!cargando && !error && orden.length === 0" class="card vacio" data-test="sin-sesiones">
        Aún no hay sesiones convocadas. Proponé una fecha en el Calendario y confirmala para abrirla aquí.
      </div>

      <div class="sesiones">
        <article
          v-for="(sesion, i) in orden"
          :key="sesion.id"
          data-test="sesion-fila"
          :data-sesion-id="String(sesion.id)"
          :data-estado="sesion.estado"
          class="card fila"
          :class="sesion.estado === 'cerrada' ? 'fila--cerrada' : ''"
        >
          <div class="fila-ident">
            <div class="crt bloque">
              <span class="label">Ordinal</span>
              <span class="num ordinal">{{ ordinal(i) }}</span>
            </div>
            <div>
              <div class="titulos">
                <span class="fecha">{{ fmt(sesion.fecha) }}</span>
                <span class="tag" :class="etiqueta(sesion.estado).cls">{{ etiqueta(sesion.estado).texto }}</span>
              </div>
              <p v-if="sesion.confirmadaAt" class="label">Confirmada {{ fmt(sesion.confirmadaAt) }}</p>
            </div>
          </div>

          <div class="acciones">
            <RouterLink
              data-test="bitacora-link"
              :to="`/mesas/${mesaId}/gestion/sesiones/${sesion.id}/bitacora`"
              class="btn btn--secondary btn--sm"
            >
              Bitácora
            </RouterLink>


          </div>
        </article>
      </div>
    </div>
</template>

<style scoped>
.sesv { display: grid; gap: var(--space-md); }
.titulo-seccion { margin: 0; font-size: var(--text-title); color: var(--color-ink); }
.sesv-cabecera { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--space-md); flex-wrap: wrap; border-bottom: var(--rule-hair) solid var(--color-rule); padding-bottom: var(--space-sm); }
.sesiones { display: grid; gap: var(--space-sm); }
.fila { display: flex; align-items: center; justify-content: space-between; gap: var(--space-md); padding: var(--space-sm) var(--space-md); flex-wrap: wrap; }
.fila--cerrada { opacity: .85; }
.fila-ident { display: flex; align-items: center; gap: var(--space-sm); min-width: 0; }
.bloque { width: 56px; height: 56px; display: grid; place-content: center; text-align: center; gap: 2px; background: var(--color-paper-3); border: var(--rule-hair) solid var(--color-rule); }
.ordinal { font-size: var(--text-md); color: var(--color-ink); }
.titulos { display: flex; align-items: center; gap: var(--space-2xs); flex-wrap: wrap; }
.fecha { font-weight: 700; color: var(--color-ink); }
.acciones { display: flex; align-items: center; gap: var(--space-2xs); flex-wrap: wrap; justify-content: flex-end; }
.vacio { text-align: center; color: var(--color-ink-2); padding: var(--space-lg); }
</style>
