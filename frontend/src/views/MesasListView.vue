<template>
  <div class="app-grid">
    <aside class="sidebar">
      <div class="well">
        <p class="label" style="margin-bottom: var(--space-3xs);">Estado</p>
        <select class="input" v-model="filtroEstado" aria-label="Filtrar por estado">
          <option v-for="o in estados" :key="o.v" :value="o.v">{{ o.l }}</option>
        </select>
        <p class="label" style="margin-block: var(--space-3xs);">Nivel inicial</p>
        <select class="input" v-model="filtroNivel" aria-label="Filtrar por nivel">
          <option v-for="o in niveles" :key="o.v" :value="o.v">{{ o.l }}</option>
        </select>
      </div>
    </aside>

    <main>
      <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: var(--space-sm); margin-bottom: var(--space-md);">
        <div>
          <h2>Mesas activas</h2>
          <p class="label" data-test="contador-mesas">{{ mesasFiltradas.length }} mesas</p>
        </div>
        <RouterLink class="btn" to="/mesas/nueva">Publicá tu campaña</RouterLink>
      </div>
      <div class="busqueda">
        <input class="input" v-model="q" type="search" placeholder="Buscar por mesa, GM o lugar…" style="max-width: 420px;" />
      </div>
      <div v-if="cargando" class="label">Cargando…</div>
      <div v-else-if="mesasFiltradas.length === 0" class="card" style="padding: var(--space-xl); text-align: center; grid-column: 1 / -1;">
        <p>Ninguna mesa coincide con el filtro.</p>
        <button class="btn btn--secondary" style="margin-top: var(--space-md);" @click="limpiar">Limpiar filtros</button>
      </div>
      <div class="mesa-grid">
        <article v-for="m in mesasFiltradas" :key="m.id" class="card mesa-card">
          <div class="crt-cover"><span class="figure-lg" :class="completa(m) ? 'ember' : 'acid'" style="font-size: 40px;">{{ m.nivel ?? '—' }}</span></div>
          <div style="display: flex; gap: var(--space-2xs); flex-wrap: wrap; margin-bottom: var(--space-2xs);">
            <span class="tag tag--ink">PF1e</span>
            <span class="tag" :class="etiquetaTono(m)">{{ etiquetaEstado(m) }}</span>
            <span v-if="m.estado === 'abierta' && mesaCompleta(m)" class="tag tag--ember">Completa</span>
            <span class="tag tag--ink">{{ m.horario || 'A coordinar' }}</span>
          </div>
          <h3 style="margin: 0;"><RouterLink class="mesa-link" :to="`/mesas/${m.id}`" data-test="mesa-link">{{ m.nombre }}</RouterLink></h3>
          <p style="font-size: var(--text-sm); color: var(--color-ink-2); margin-block: var(--space-2xs) var(--space-sm);">
            Dirigida por {{ m.gm || 'su master' }}<span v-if="m.ubicacion">, {{ m.ubicacion }}</span>
          </p>
          <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: var(--space-2xs);">
              <span class="seats" role="img" :aria-label="ocupacionNormalizada(m) + ' de ' + (cupoDe(m) ?? '∞') + ' asientos'">
                <i v-for="i in ocupacionNormalizada(m)" :key="'on' + m.id + i"></i>
                <i v-for="i in Math.max(0, (cupoDe(m) ?? 0) - ocupacionNormalizada(m))" :key="'off' + m.id + i" class="off"></i>
              </span>
              <span class="num" style="font-size: var(--text-sm);">{{ ocupacionNormalizada(m) }}/{{ cupoDe(m) ?? '∞' }}</span>
            </div>
            <button v-if="!esMasterDe(m)" class="btn btn--sm" :disabled="!puedoPedir(m) || postuladas.has(m.id) || postulandoId === m.id" @click="unirse(m)">{{ etiquetaBoton(m) }}</button>
          </div>
        </article>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { getMesas } from '@/services/mesas'
import { mesasApi } from '@/api/endpoints'
import { useToast } from '@/composables/useToast'
// sin demo

const { user, isAuthenticated } = useAuth()
const router = useRouter()
const toast = useToast()
const postuladas = ref(new Set())
const postulandoId = ref(null)

const q = ref('')
const filtroEstado = ref('todas')
const filtroNivel = ref('todos')
const mesasApiLista = ref([])
const cargando = ref(true)

onMounted(async () => {
  try {
    mesasApiLista.value = await getMesas()
  } catch {
    mesasApiLista.value = []
  } finally {
    cargando.value = false
  }
})

const niveles = [{ v: 'todos', l: 'Todos' }, { v: '1-5', l: '1 a 5' }, { v: '6-9', l: '6 a 9' }, { v: '10-12', l: '10 a 12' }]

const rango = (niv) => { const [a] = niv.split('-').map(Number); return a >= 10 ? '10-12' : a >= 6 ? '6-9' : '1-5' }

function cupoDe(m) { return m.plazas ?? m.cupo ?? null }
function ocupacionNormalizada(m) { return m.jugadores ?? 0 }
function completa(m) { return m.plazas != null && m.jugadores >= m.plazas }
function estadoCrudo(m) { return String(m.estado ?? '').toLowerCase() }

const mesasFiltradas = computed(() => {
  const texto = q.value.trim().toLowerCase()
  return mesasApiLista.value.filter((m) =>
    (filtroEstado.value === 'todas' ||
      (filtroEstado.value === 'abierta' ? estadoCrudo(m) === 'abierta' && !completa(m) : estadoCrudo(m) === 'abierta' && completa(m))) &&
    (filtroNivel.value === 'todos' || rango(String(m.nivel ?? '')) === filtroNivel.value) &&
    (!texto || (m.nombre + ' ' + (m.gm || '') + ' ' + (m.ubicacion || '')).toLowerCase().includes(texto))
  )
})

const estados = [
  { v: 'todas', l: 'Todas las mesas' },
  { v: 'abierta', l: 'Con vacante' },
  { v: 'completa', l: 'Completas' }
]

function etiquetaEstado(m) { return completa(m) ? 'Completa' : (estadoCrudo(m) === 'abierta' ? 'Abierta' : 'Cerrada') }
function etiquetaTono(m) {
  if (completa(m)) return 'tag--ember'
  if (estadoCrudo(m) === 'abierta') return 'tag--acid'
  return 'tag--ink'
}
function mesaCompleta(m) { return completa(m) }

function esMasterDe(m) {
  return !!user.value && Number(m?.gmId ?? m?.gm_id) === Number(user.value?.id ?? user.value?.sub)
}
function puedoPedir(m) {
  return isAuthenticated.value && !esMasterDe(m) && estadoCrudo(m) === 'abierta' && !completa(m)
}

function etiquetaBoton(m) {
  if (postuladas.value.has(m.id)) return 'Postulado ✓'
  if (!isAuthenticated.value) return 'Postularme'
  if (estadoCrudo(m) !== 'abierta') return 'Cerrada'
  if (completa(m)) return 'Completa'
  if (postulandoId.value === m.id) return 'Enviando…'
  return 'Postularme'
}

async function unirse(m) {
  if (!isAuthenticated.value) { router.push({ path: '/login', query: { redirect: '/mesas' } }); return }
  if (postuladas.value.has(m.id) || postulandoId.value === m.id) return
  postulandoId.value = m.id
  try {
    await mesasApi.solicitarUnion(m.id, {})
    postuladas.value = new Set([...postuladas.value, m.id])
    toast.ok('Postulación enviada · el GM revisará tu solicitud.')
  } catch (e) {
    toast.error(e?.message || 'No se pudo enviar la postulación. Intentá de nuevo.')
  } finally {
    postulandoId.value = null
  }
}

function limpiar() { q.value = ''; filtroEstado.value = 'todas'; filtroNivel.value = 'todos' }
</script>

<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: 240px minmax(0, 1fr); gap: var(--space-lg); align-items: start; }
.sidebar { display: grid; gap: var(--space-md); }
.mesa-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: var(--space-md); }
.mesa-card { padding: var(--space-md); display: grid; gap: var(--space-2xs); }
.crt-cover { aspect-ratio: 16/9; background: var(--color-paper-3); border: var(--rule-hair) solid var(--color-rule); display: grid; place-items: center; margin-bottom: var(--space-2xs); }
.mesa-link { color: inherit; text-decoration: none; }
.mesa-link:hover { color: var(--color-accent-2); }
@media (max-width: 60rem) { .app-grid { grid-template-columns: minmax(0, 1fr); } }
</style>