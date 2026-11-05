<template>
  <div class="app-grid">
    <template v-if="cargando">
      <main><p class="label">Cargando…</p></main>
    </template>
    <template v-else-if="!mesa">
      <main>
        <article class="card" style="padding: var(--space-xl); text-align: center;">
          <h2>Mesa no encontrada</h2>
          <RouterLink class="btn btn--secondary" to="/mesas" style="margin-top: var(--space-md);">Ver las mesas abiertas</RouterLink>
        </article>
      </main>
    </template>
    <template v-else>
      <main>
        <div style="display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: var(--space-sm);">
          <div>
            <h2>Calendario · votación de fechas</h2>
            <p class="label">{{ mesa.nombre }} · RN-06: un voto por jugador, actualizable; el GM propone y confirma</p>
          </div>
          <RouterLink class="btn btn--secondary" :to="`/mesas/${mesa.id}`">Volver a la mesa</RouterLink>
        </div>

        <form v-if="esGM" class="card" style="padding: var(--space-md); display: grid; gap: var(--space-sm);" data-test="form-proponer" novalidate @submit.prevent="proponer">
          <h3>Proporner nueva sesión</h3>
          <div class="grid-2" style="gap: var(--space-md);">
            <div class="field">
              <label class="label" for="c-fecha">Fecha</label>
              <input class="input" id="c-fecha" data-test="input-fecha" v-model="nueva.fecha" type="date" :min="hoyISO" />
            </div>
            <div class="field">
              <label class="label" for="c-numero">Sesión</label>
              <input class="input" id="c-numero" v-model="nueva.sesionNumero" placeholder="#45" />
            </div>
          </div>
          <div class="field">
            <label class="label" for="c-titulo">Título</label>
            <input class="input" id="c-titulo" v-model="nueva.titulo" placeholder="Sesión: la cripta se abre" />
          </div>
          <p class="hint-error" v-if="errorPropuesta" role="alert" data-test="error-fecha">{{ errorPropuesta }}</p>
          <button class="btn btn--sm" type="submit" data-test="btn-proponer">Proponer fecha</button>
        </form>

        <p class="hint-error" v-if="errorVoto" role="alert" data-test="error-calendario">{{ errorVoto }}</p>

        <div class="card" style="padding: var(--space-md);">
          <h3>Propuestas</h3>
          <div v-if="propuestas.length === 0" style="font-size: var(--text-sm); color: var(--color-ink-2);">Nadie propuso fechas todavía.</div>
          <article v-for="p in propuestas" :key="p.id" class="propuesta-row" data-test="propuesta-fecha">
            <div class="votecell vote">
              <button data-test="voto-favor" :aria-pressed="miVoto(p) === 'favor'" :disabled="!puedoVotar" @click="votar(p, 'favor')">▲</button>
              <span class="count">{{ conteo(p, 'favor') }}</span>
              <button data-test="voto-contra" :aria-pressed="miVoto(p) === 'contra'" :disabled="!puedoVotar" @click="votar(p, 'contra')">▼</button>
            </div>
            <div style="flex: 1; min-width: 220px;">
              <p style="margin: 0; font-weight: 700; font-size: var(--text-sm);">{{ p.sesionNumero }} · {{ p.titulo }}</p>
              <p class="label" style="margin: 0;">
                <span class="num">{{ fmt(p.fecha) }}</span>
                <span v-if="p.confirmada" class="tag tag--acid" style="margin-left: var(--space-2xs);">Confirmada</span>
              </p>
            </div>
            <button v-if="esGM" class="btn btn--secondary btn--sm" :disabled="p.confirmada" @click="confirmar(p)">
              {{ p.confirmada ? 'Confirmada' : 'Confirmar fecha' }}
            </button>
          </article>
        </div>
      </main>

      <aside>
        <div class="well" style="padding: var(--space-lg);">
          <p class="label" style="margin-bottom: var(--space-2xs);">Reglas del calendario</p>
          <p style="font-size: var(--text-sm); color: var(--color-ink-2);">
            Un voto a favor/en contra por jugador por propuesta, actualizable (RN-06). El director propone y confirma; no vota (RN-17).
          </p>
        </div>
      </aside>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { getMesa } from '@/services/mesas'
import { getVotaciones, votar as votarApi, proponerFecha as proponerApi, confirmarFecha as confirmarApi } from '@/services/votaciones'
import { getMiembros } from '@/services/jugadores'

const route = useRoute()
const { user } = useAuth()

const mesa = ref(null)
const cargando = ref(true)
const propuestas = ref([])
const esMiembro = ref(false)
const nueva = ref({ fecha: '', sesionNumero: '', titulo: '' })
const errorPropuesta = ref(null)
const errorVoto = ref(null)

const hoyISO = computed(() => new Date().toISOString().slice(0, 10))

const esGM = computed(() => !!mesa.value && !!user.value && mesa.value.gmId === Number(user.value?.id ?? user.value?.sub))
const puedoVotar = computed(() => esMiembro.value && !esGM.value)

onMounted(async () => {
  try {
    mesa.value = await getMesa(route.params.id)
    const miembros = await getMiembros(mesa.value.id)
    esMiembro.value = (miembros?.miembros ?? []).some((m) => m.email === user.value?.email)
    propuestas.value = await getVotaciones(mesa.value.id)
  } catch (e) {
    mesa.value = null
  } finally {
    cargando.value = false
  }
})

function fmt(f) {
  if (!f) return ''
  const [y, m, d] = String(f).split('-')
  return `${d}/${m}/${y}`
}

function miVoto(p) {
  return p.miVoto || null
}
function conteo(p, dir) {
  return dir === 'favor' ? (p.favor?.length ?? 0) : (p.contra?.length ?? 0)
}

async function proponer() {
  errorPropuesta.value = null
  try {
    await proponerApi(mesa.value.id, { ...nueva.value })
    propuestas.value = await getVotaciones(mesa.value.id)
    nueva.value = { fecha: '', sesionNumero: '', titulo: '' }
  } catch (e) {
    errorPropuesta.value = e?.message || 'No se pudo proponer la fecha.'
  }
}

async function votar(p, dir) {
  errorVoto.value = null
  try {
    await votarApi(mesa.value.id, p.id, dir)
    propuestas.value = await getVotaciones(mesa.value.id)
  } catch (e) {
    errorVoto.value = e?.message || 'No se pudo registrar el voto.'
  }
}

async function confirmar(p) {
  try {
    await confirmarApi(mesa.value.id, p.id)
    propuestas.value = await getVotaciones(mesa.value.id)
  } catch (e) {
    errorVoto.value = e?.message || 'No se pudo confirmar la fecha.'
  }
}
</script>

<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: minmax(0, 1fr) 312px; gap: var(--space-lg); align-items: start; }
.propuesta-row { display: flex; align-items: center; gap: var(--space-md); padding-block: var(--space-sm); border-bottom: var(--rule-hair) solid var(--color-rule); flex-wrap: wrap; }
.propuesta-row:last-child { border-bottom: none; }
.propuesta-row .votecell { min-width: 72px; }
@media (max-width: 75rem) { .app-grid { grid-template-columns: minmax(0, 1fr); } }
@media (max-width: 60rem) { .app-grid { padding-top: 120px; } }
</style>