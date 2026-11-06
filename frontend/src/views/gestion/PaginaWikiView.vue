<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from '@/composables/useToast.js'
import { getWiki, getPagina } from '@/services/wiki.js'

const props = defineProps({ mesaId: { type: String, required: true }, paginaId: { type: String, required: true } })

const toast = useToast()

const pagina = ref(null)
const cargando = ref(true)
const falta = ref(false)
const indice = ref([])
const busqueda = ref('')
const comentarios = ref([
  {
    autor: 'Kaelen Valeros',
    avatar: 'KV',
    fecha: 'Hace 2 días',
    texto: '¿El herrero local afila armas de hierro frío o tendremos que esperar a llegar a Lepidstadt? Si vamos a entrar a Harrowstone necesitaremos bonus contra espectros.'
  },
  {
    autor: 'Aldren Valeros',
    avatar: 'AV',
    fecha: 'Hace 1 día • GM',
    texto: 'Sí: Baltor Tabbard afila hierro frío por 8 po en 3 horas. Las armas de plata las tendrás que encargar en Caliphas.'
  }
])
const nuevoComentario = ref('')

const indiceFiltrado = computed(() => {
  if (!busqueda.value.trim()) return indice.value
  const q = busqueda.value.trim().toLowerCase()
  return indice.value.filter((p) => p.titulo.toLowerCase().includes(q))
})

const TIPO_TAG = { LUGAR: 'tag--ember', NPC: 'tag--ink', CRIATURA: 'tag--ember', NOTA: 'tag--acid' }

function publicar() {
  const texto = nuevoComentario.value.trim()
  if (!texto) return
  comentarios.value.push({ autor: 'Aldren Valeros', avatar: 'AV', fecha: 'Justo ahora', texto })
  nuevoComentario.value = ''
  toast.ok('Comentario publicado en la página del código.')
}

async function cargar() {
  cargando.value = true
  falta.value = false
  try {
    const [pag, wiki] = await Promise.all([getPagina(props.mesaId, props.paginaId), getWiki(props.mesaId)])
    pagina.value = pag
    indice.value = wiki.paginas
  } catch {
    falta.value = true
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
watch(() => props.paginaId, cargar)
</script>

<template>
      <div v-if="cargando" class="label central">
      Abriendo la página del código…
    </div>

    <div v-else-if="falta" class="falta">
      Esta página fue borrada del grimorio.
      <RouterLink :to="`/mesas/${mesaId}/wiki`" class="text-link">← Volver al Códice</RouterLink>
    </div>

    <div v-else-if="pagina" class="pagina">
      <!-- Índice lateral -->
      <aside>
        <div class="card arbol">
          <h2 class="rotulo">Índice del Códice</h2>
          <input v-model="busqueda" type="text" placeholder="Filtrar notas, lugares, PNJs..." class="input buscador" />
          <nav class="ramas">
            <RouterLink
              v-for="p in indiceFiltrado"
              :key="p.id"
              :to="`/mesas/${mesaId}/wiki/${p.id}`"
              class="rama"
              :class="p.id === pagina.id ? 'rama--activa' : ''"
            >
              {{ p.titulo.split(' (')[0] }}
            </RouterLink>
          </nav>
        </div>
      </aside>

      <!-- Artículo -->
      <article class="articulo">
        <RouterLink :to="`/mesas/${mesaId}/wiki`" class="text-link volver">← Volver a la Lista</RouterLink>

        <div class="cabeza">
          <span class="tag" :class="TIPO_TAG[pagina.tipo] || 'tag--acid'">{{ pagina.tipo }}</span>
          <span class="label">Carpeta: {{ pagina.carpeta }}</span>
        </div>
        <h1 class="titulo">{{ pagina.titulo }}</h1>
        <p class="subtitulo">{{ pagina.resumen }}</p>

        <div class="cuerpo">
          <template v-for="(bloque, i) in pagina.contenido" :key="i">
            <p v-if="bloque.tipo === 'parrafo'" class="parrafo">{{ bloque.texto }}</p>
            <h2 v-else-if="bloque.tipo === 'subtitle'" class="sub-bloque">{{ bloque.texto }}</h2>
            <p v-else-if="bloque.tipo === 'cita'" class="cita">{{ bloque.texto }}</p>
            <div v-else-if="bloque.tipo === 'lista'">
              <h3 class="sub-bloque sub-bloque--tercer">{{ bloque.titulo }}</h3>
              <ul class="lista">
                <li v-for="(item, k) in bloque.items" :key="k">{{ item }}</li>
              </ul>
            </div>
          </template>
        </div>

        <div class="pie">
          <span class="label">Última edición: <strong>{{ pagina.fecha }}</strong> por Aldren (GM)</span>
          <RouterLink :to="`/mesas/${mesaId}/wiki/${pagina.id}/editar`" class="btn btn--secondary btn--sm">
            Editar página
          </RouterLink>
        </div>

        <!-- Discusión -->
        <section class="discusion">
          <h2 class="rotulo">Discusión del Códice ({{ comentarios.length }})</h2>
          <div class="comentarios">
            <div v-for="(c, i) in comentarios" :key="i" class="card comentario">
              <div class="crt avatar">{{ c.avatar }}</div>
              <div>
                <div class="autor">{{ c.autor }} <span class="label">· {{ c.fecha }}</span></div>
                <p class="comentario-texto">{{ c.texto }}</p>
              </div>
            </div>

            <form class="formulario" @submit.prevent="publicar">
              <input v-model="nuevoComentario" type="text" placeholder="Aporta una anotación al códice…" class="input" />
              <button type="submit" class="btn btn--sm">Publicar</button>
            </form>
          </div>
        </section>
      </article>
    </div>
</template>

<style scoped>
.pagina { display: grid; gap: var(--space-md); grid-template-columns: minmax(0, 1fr); }
@media (min-width: 60rem) { .pagina { grid-template-columns: minmax(0, 3fr) minmax(0, 7fr); gap: var(--space-lg); } }
.central { text-align: center; padding-block: var(--space-xl); }
.falta { text-align: center; padding-block: var(--space-xl); display: grid; gap: var(--space-sm); justify-items: center; color: var(--color-ink-2); }
.arbol { padding: var(--space-md); display: grid; gap: var(--space-sm); align-content: start; position: sticky; top: 96px; }
.rotulo { margin: 0; font-size: var(--text-md); font-weight: 700; color: var(--color-ink); text-transform: uppercase; letter-spacing: .04em; }
.buscador { font-size: var(--text-sm); }
.ramas { display: grid; gap: 2px; max-height: 32rem; overflow-y: auto; padding-right: var(--space-3xs); }
.rama { display: block; padding: var(--space-3xs) var(--space-2xs); border-left: var(--rule-bar) solid transparent; color: var(--color-ink-2); text-decoration: none; font-size: var(--text-sm); }
.rama:hover { color: var(--color-accent-2); background: var(--color-paper-3); }
.rama--activa { border-left-color: var(--color-accent-2); background: var(--color-paper-3); color: var(--color-accent-2); font-weight: 700; }
.articulo { min-width: 0; display: grid; gap: var(--space-sm); align-content: start; }
.volver { font-weight: 700; font-size: var(--text-sm); }
.cabeza { display: flex; align-items: center; gap: var(--space-2xs); flex-wrap: wrap; }
.titulo { margin: 0; font-size: var(--text-display-s); color: var(--color-ink); }
.subtitulo { margin: 0; color: var(--color-ink-2); font-style: italic; font-size: var(--text-sm); }
.cuerpo { display: grid; gap: var(--space-md); }
.parrafo { margin: 0; color: var(--color-ink); line-height: 1.6; }
.sub-bloque { margin: 0; padding-bottom: var(--space-3xs); border-bottom: var(--rule-hair) solid var(--color-rule); font-size: var(--text-title); color: var(--color-ink); font-weight: 700; }
.sub-bloque--tercer { font-size: var(--text-md); }
.cita { margin: 0; color: var(--color-ink-2); font-style: italic; border-left: var(--rule-bar) solid var(--color-rule); background: var(--color-paper-3); padding: var(--space-2xs) var(--space-sm); }
.lista { margin: 0; padding-left: var(--space-lg); display: grid; gap: var(--space-3xs); color: var(--color-ink); }
.pie { display: flex; align-items: center; justify-content: space-between; gap: var(--space-md); padding-top: var(--space-sm); border-top: var(--rule-hair) solid var(--color-rule); flex-wrap: wrap; }
.discusion { display: grid; gap: var(--space-sm); border-top: var(--rule-hair) solid var(--color-rule); padding-top: var(--space-md); }
.comentarios { display: grid; gap: var(--space-sm); }
.comentario { display: flex; gap: var(--space-sm); padding: var(--space-sm) var(--space-md); align-items: flex-start; }
.avatar { width: 32px; height: 32px; display: grid; place-content: center; border-radius: 999px; background: var(--color-accent-2); color: var(--color-paper); font-weight: 700; font-size: var(--text-xs); flex-shrink: 0; }
.autor { font-weight: 700; color: var(--color-ink); font-size: var(--text-sm); }
.comentario-texto { margin: 2px 0 0; font-size: var(--text-sm); color: var(--color-ink); }
.formulario { display: flex; gap: var(--space-2xs); flex-wrap: wrap; }
.formulario .input { flex: 1; min-width: 12rem; }
</style>
