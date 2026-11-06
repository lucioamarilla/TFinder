<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { getWiki } from '@/services/wiki.js'

const props = defineProps({ mesaId: { type: String, required: true } })

const wiki = ref({ carpetas: [], paginas: [], total: 0 })
const carpetasAbiertas = ref({})
const carpetaActiva = ref(null)
const tipoActivo = ref('TODOS')
const busqueda = ref('')

const FILTROS = ['TODOS', 'LUGARES', 'PERSONAJES', 'CRIATURAS', 'NOTAS']

const TIPO_TAG = { LUGAR: 'tag--ember', NPC: 'tag--ink', CRIATURA: 'tag--ember', NOTA: 'tag--acid' }

const ICONOS = {
  user: 'M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z',
  map: 'M20.5 3l-.16.03L15 5.1 9 3 3.36 4.9c-.21.07-.36.25-.36.48V20.5c0 .28.22.5.5.5l.16-.03L9 18.9l6 2.1 5.64-1.9c.21-.07.36-.25.36-.48V3.5c0-.28-.22-.5-.5-.5zM15 19l-6-2.11V5l6 2.11V19z',
  claw: 'M12 2C9.5 2 7 3.8 6 6c-.8 1.8-.4 4 1 5.5-1.5.5-2.8 1.8-3 3.5-.3 2.5 1.5 4.8 4 5 1.5.1 3-.5 4-1.5 1 1 2.5 1.6 4 1.5 2.5-.2 4.3-2.5 4-5-.2-1.7-1.5-3-3-3.5 1.4-1.5 1.8-3.7 1-5.5-1-2.2-3.5-4-6-4zm-3.5 6c.8 0 1.5.7 1.5 1.5S9.3 11 8.5 11 7 10.3 7 9.5 7.7 8 8.5 8zm7 0c.8 0 1.5.7 1.5 1.5s-.7 1.5-1.5 1.5-1.5-.7-1.5-1.5.7-1.5 1.5-1.5.5 0 .5 0zM12 14c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2z',
  scroll: 'M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10H7v-2h10v2zm0-4H7V7h10v2z'
}

function matchTipo(pagina) {
  if (tipoActivo.value === 'TODOS') return true
  if (tipoActivo.value === 'LUGARES') return pagina.tipo === 'LUGAR'
  if (tipoActivo.value === 'PERSONAJES') return pagina.tipo === 'NPC'
  if (tipoActivo.value === 'CRIATURAS') return pagina.tipo === 'CRIATURA'
  if (tipoActivo.value === 'NOTAS') return pagina.tipo === 'NOTA'
  return true
}

const paginasFiltradas = computed(() => {
  let lista = wiki.value.paginas
  if (carpetaActiva.value) lista = lista.filter((p) => p.carpeta === carpetaActiva.value)
  lista = lista.filter(matchTipo)
  if (busqueda.value.trim()) {
    const q = busqueda.value.trim().toLowerCase()
    lista = lista.filter((p) => p.titulo.toLowerCase().includes(q) || p.resumen.toLowerCase().includes(q))
  }
  return lista
})

const carpetasConCount = computed(() =>
  wiki.value.carpetas.map((c) => ({
    ...c,
    count: wiki.value.paginas.filter((p) => p.carpeta === c.id).length
  }))
)

const tituloSeccion = computed(() => {
  const carpeta = wiki.value.carpetas.find((c) => c.id === carpetaActiva.value)
  return carpeta ? `Páginas de ${carpeta.nombre.replace(' & ', ' y ')}` : 'Páginas del Códice de Campaña'
})

function toggleCarpeta(id) {
  carpetasAbiertas.value[id] = !carpetasAbiertas.value[id]
}

function seleccionarCarpeta(id) {
  carpetaActiva.value = id
  carpetasAbiertas.value[id] = true
}

function seleccionarTipo(tipo) {
  tipoActivo.value = tipo
}

async function cargar() {
  wiki.value = await getWiki(props.mesaId)
  carpetasAbiertas.value = wiki.value.carpetas.reduce((acc, c) => ({ ...acc, [c.id]: c.abierta }), {})
}

onMounted(cargar)
watch(() => props.mesaId, cargar)
</script>

<template>
      <div class="codice">
      <!-- Sidebar árbol -->
      <aside class="card arbol">
        <div class="total">
          <h3 class="rotulo">Índice del Códice</h3>
          <span class="label">{{ wiki.total }} artículos</span>
        </div>

        <div class="ramas">
          <div v-for="carpeta in carpetasConCount" :key="carpeta.id">
            <div
              role="button"
              tabindex="0"
              class="rama"
              :class="carpetaActiva === carpeta.id ? 'rama--activa' : ''"
              @click="seleccionarCarpeta(carpeta.id)"
              @keydown.enter="seleccionarCarpeta(carpeta.id)"
            >
              <span class="rama-ident">
                <span class="flecha" :class="carpetasAbiertas[carpeta.id] ? '' : 'flecha--abierta'">▼</span>
                <svg class="glifo" viewBox="0 0 24 24" fill="currentColor">
                  <path :d="ICONOS[carpeta.icono] || ICONOS.scroll"></path>
                </svg>
                <span>{{ carpeta.nombre }}</span>
              </span>
              <span class="label rama-count">({{ carpeta.count }})</span>
            </div>

            <div v-if="carpetasAbiertas[carpeta.id]" class="hojas">
              <RouterLink
                v-for="pagina in wiki.paginas.filter((p) => p.carpeta === carpeta.id)"
                :key="pagina.id"
                :to="`/mesas/${mesaId}/wiki/${pagina.id}`"
                class="hoja"
                :class="carpetaActiva === carpeta.id ? 'hoja--activa' : ''"
              >
                {{ pagina.titulo.split(' (')[0] }}
              </RouterLink>
            </div>
          </div>
        </div>

        <div class="arbol-pie">
          <span>Total: <strong>{{ wiki.total }} artículos</strong></span>
          <button class="text-link" type="button" @click="carpetaActiva = null">
            ✚ VER TODAS
          </button>
        </div>
      </aside>

      <!-- Columna principal -->
      <section class="principal">
        <div class="principal-cabecera">
          <div>
            <div class="titulo-fila">
              <span class="titulo">{{ tituloSeccion }}</span>
              <span class="tag tag--ink">{{ paginasFiltradas.length }} artículos</span>
            </div>
            <p class="label">Códice topográfico, asentamientos y registros de la crónica; mantenido por la mesa.</p>
          </div>

          <RouterLink :to="`/mesas/${mesaId}/wiki/nueva`" class="btn btn--sm">
            + Crear página
          </RouterLink>
        </div>

        <div class="filtros-fila">
          <div class="filtros">
            <span class="label filtros-etiqueta">FILTRAR TIPO:</span>
            <button
              v-for="filtro in FILTROS"
              :key="filtro"
              type="button"
              class="btn btn--sm"
              :class="tipoActivo === filtro ? '' : 'btn--secondary'"
              @click="seleccionarTipo(filtro)"
            >
              {{ filtro }}
            </button>
          </div>
          <div class="label conteo">
            Mostrando {{ paginasFiltradas.length }} de {{ wiki.total }} registros
          </div>
        </div>

        <div class="buscador">
          <input v-model="busqueda" type="text" placeholder="Filtrar páginas del código…" class="input" />
        </div>

        <div class="datos">
          <table class="tf-table">
            <thead>
              <tr>
                <th>TÍTULO</th>
                <th>TIPO</th>
                <th>FECHA MODIFICACIÓN</th>
                <th class="centrado">ACCIÓN</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="pagina in paginasFiltradas" :key="pagina.id">
                <td>
                  <div class="titulo-pagina">
                    <svg class="glifo" viewBox="0 0 24 24" fill="currentColor">
                      <path :d="ICONOS.map"></path>
                    </svg>
                    <RouterLink :to="`/mesas/${mesaId}/wiki/${pagina.id}`" class="text-link">
                      {{ pagina.titulo }}
                    </RouterLink>
                  </div>
                  <div class="label resumen">
                    {{ pagina.resumen }}
                  </div>
                </td>
                <td>
                  <span class="tag" :class="TIPO_TAG[pagina.tipo] || 'tag--acid'">
                    {{ pagina.tipo }}
                  </span>
                </td>
                <td class="label">{{ pagina.fecha }}</td>
                <td class="centrado">
                  <RouterLink
                    :to="`/mesas/${mesaId}/wiki/${pagina.id}/editar`"
                    class="text-link"
                    title="Editar entrada"
                  >
                    ✎
                  </RouterLink>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="paginasFiltradas.length === 0" class="vacio">
            <p class="label">El código no registra páginas con estos criterios.</p>
            <p class="label">Ajusta el filtro o crea una entrada nueva.</p>
          </div>
        </div>
      </section>
    </div>
</template>

<style scoped>
.codice { display: grid; gap: var(--space-md); grid-template-columns: minmax(0, 1fr); }
@media (min-width: 60rem) { .codice { grid-template-columns: minmax(0, 3fr) minmax(0, 7fr); gap: var(--space-lg); } }
.arbol { padding: var(--space-md); display: flex; flex-direction: column; justify-content: space-between; min-height: 26rem; gap: var(--space-sm); }
.total { display: flex; align-items: center; justify-content: space-between; gap: var(--space-2xs); margin-bottom: var(--space-sm); padding-bottom: var(--space-2xs); border-bottom: var(--rule-hair) solid var(--color-rule); }
.rotulo { margin: 0; font-size: var(--text-md); font-weight: 700; color: var(--color-ink); text-transform: uppercase; letter-spacing: .04em; }
.ramas { display: grid; gap: var(--space-3xs); }
.rama { display: flex; align-items: center; justify-content: space-between; gap: var(--space-2xs); padding: var(--space-3xs) var(--space-2xs); cursor: pointer; color: var(--color-ink); font-weight: 700; text-align: left; }
.rama:hover { color: var(--color-accent-2); }
.rama--activa { background: var(--color-paper-3); color: var(--color-accent-2); }
.rama-ident { display: inline-flex; align-items: center; gap: var(--space-2xs); min-width: 0; }
.flecha { font-size: 10px; color: var(--color-muted); }
.flecha--abierta { transform: rotate(-90deg); }
.glifo { width: 16px; height: 16px; color: var(--color-accent-2); flex-shrink: 0; }
.rama-count { font-size: var(--text-xs); color: var(--color-muted); }
.hojas { padding-left: var(--space-md); margin-left: var(--space-2xs); border-left: var(--rule-hair) solid var(--color-rule); display: grid; gap: 2px; margin-top: 2px; }
.hoja { display: block; padding: var(--space-3xs) var(--space-2xs); color: var(--color-ink-2); text-decoration: none; font-size: var(--text-sm); }
.hoja:hover { color: var(--color-accent-2); background: var(--color-paper-3); }
.hoja--activa { border-left: var(--rule-bar) solid var(--color-accent-2); background: var(--color-paper-3); color: var(--color-accent-2); font-weight: 700; }
.arbol-pie { display: flex; align-items: center; justify-content: space-between; gap: var(--space-2xs); padding-top: var(--space-sm); border-top: var(--rule-hair) solid var(--color-rule); color: var(--color-ink-2); font-size: var(--text-xs); }
.principal { display: flex; flex-direction: column; gap: var(--space-md); min-width: 0; }
.principal-cabecera { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--space-md); flex-wrap: wrap; border-bottom: var(--rule-bar) solid var(--color-rule); padding-bottom: var(--space-sm); }
.titulo-fila { display: flex; align-items: center; gap: var(--space-2xs); flex-wrap: wrap; }
.titulo { font-size: var(--text-md); font-weight: 700; color: var(--color-ink); }
.filtros-fila { display: flex; align-items: center; justify-content: space-between; gap: var(--space-sm); flex-wrap: wrap; }
.filtros { display: flex; align-items: center; gap: var(--space-3xs); flex-wrap: wrap; }
.filtros .btn { padding-block: 2px; }
.conteo { color: var(--color-ink-2); font-style: italic; }
.buscador { display: block; }
.datos { border: var(--rule-hair) solid var(--color-rule); overflow-x: auto; }
.centrado { text-align: center; }
.titulo-pagina { display: flex; align-items: center; gap: var(--space-2xs); }
.resumen { font-style: italic; padding-left: var(--space-md); margin-top: 2px; }
.vacio { padding: var(--space-lg); text-align: center; display: grid; gap: var(--space-3xs); }
</style>
