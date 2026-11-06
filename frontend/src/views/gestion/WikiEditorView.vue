<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast.js'
import ConfirmModal from '@/components/modals/ConfirmModal.vue'
import { getWiki, getPagina, crearPagina, actualizarPagina, eliminarPagina } from '@/services/wiki.js'

const props = defineProps({ mesaId: { type: String, required: true }, paginaId: { type: String, required: true } })

const esNueva = computed(() => props.paginaId === 'nueva')

const router = useRouter()
const toast = useToast()

const carpetas = ref([])
const titulo = ref('')
const tipo = ref('LUGAR')
const carpeta = ref('lugares')
const resumen = ref('')
const contenido = ref('')
const area = ref(null)
const guardando = ref(false)
const confirmarBorrado = ref(false)

const TIPOS = ['LUGAR', 'NPC', 'CRIATURA', 'NOTA']

function serializar(pagina) {
  const lineas = []
  for (const bloque of pagina.contenido) {
    if (bloque.tipo === 'parrafo') lineas.push(bloque.texto, '')
    else if (bloque.tipo === 'cita') lineas.push(`> ${bloque.texto}`, '')
    else if (bloque.tipo === 'subtitle') lineas.push(`## ${bloque.texto}`, '')
    else if (bloque.tipo === 'lista') {
      lineas.push(`### ${bloque.titulo || 'Lista'}`, '')
      for (const item of bloque.items) lineas.push(`- ${item}`, '')
    }
  }
  return lineas.join('\n').replace(/\n{3,}/g, '\n\n').trim()
}

function parsear(markdown) {
  const bloques = []
  const grupos = markdown.split(/\n\s*\n/)
  for (const grupo of grupos) {
    const lineas = grupo.split('\n').filter((linea) => linea.trim().length > 0)
    if (lineas.length === 0) continue
    const esLista = lineas.every((linea) => /^-\s+/.test(linea))
    if (esLista) {
      bloques.push({ tipo: 'lista', titulo: '', items: lineas.map((linea) => linea.replace(/^-\s+/, '')) })
      continue
    }
    const encabezado = lineas.findIndex((linea) => /^#{2,3}\s+/.test(linea))
    if (encabezado === 0 && lineas.length === 1) {
      bloques.push({ tipo: 'subtitle', texto: lineas[0].replace(/^#{2,3}\s+/, '') })
      continue
    }
    if (/^>\s+/.test(lineas[0]) && lineas.length === 1) {
      bloques.push({ tipo: 'cita', texto: lineas[0].replace(/^>\s+/, '') })
      continue
    }
    bloques.push({ tipo: 'parrafo', texto: lineas.join(' ').trim() })
  }
  return bloques
}

const bloquesParseados = computed(() => parsear(contenido.value))

async function cargar() {
  const wiki = await getWiki(props.mesaId)
  carpetas.value = wiki.carpetas
  if (!esNueva.value) {
    const pagina = await getPagina(props.mesaId, props.paginaId)
    titulo.value = pagina.titulo
    tipo.value = pagina.tipo
    carpeta.value = pagina.carpeta
    resumen.value = pagina.resumen
    contenido.value = serializar(pagina)
  }
}

function insertar(prefijo) {
  const el = area.value
  if (!el) return
  const inicio = el.selectionStart
  const fin = el.selectionEnd
  const seleccion = contenido.value.slice(inicio, fin)
  const texto = prefijo === 'lista'
    ? (seleccion.split('\n').map((s) => `- ${s}`).join('\n'))
    : `${prefijo}${seleccion}`
  contenido.value = contenido.value.slice(0, inicio) + texto + contenido.value.slice(fin)
  requestAnimationFrame(() => {
    el.focus()
    el.setSelectionRange(inicio, inicio + texto.length)
  })
}

async function guardar() {
  if (!titulo.value.trim()) {
    toast.error('El título de la página es obligatorio.')
    return
  }
  guardando.value = true
  try {
    const entrada = {
      titulo: titulo.value.trim(),
      tipo: tipo.value,
      carpeta: carpeta.value,
      resumen: resumen.value.trim(),
      contenido: bloquesParseados.value
    }
    if (esNueva.value) {
      const creada = await crearPagina(props.mesaId, entrada)
      toast.ok(`Página «${creada.titulo}» añadida al código de campaña.`)
      router.push(`/mesas/${props.mesaId}/wiki/${creada.id}`)
    } else {
      const actualizada = await actualizarPagina(props.mesaId, props.paginaId, entrada)
      toast.ok(`Página «${actualizada.titulo}» guardada en el grimorio.`)
      router.push(`/mesas/${props.mesaId}/wiki/${props.paginaId}`)
    }
  } catch (e) {
    toast.error(e.message || 'No pudimos guardar la página.')
  } finally {
    guardando.value = false
  }
}

async function borrar() {
  try {
    await eliminarPagina(props.mesaId, props.paginaId)
    toast.ok('La página fue eliminada del código de campaña.')
    router.push(`/mesas/${props.mesaId}/wiki`)
  } finally {
    confirmarBorrado.value = false
  }
}

function cancelar() {
  const destino = esNueva.value
    ? `/mesas/${props.mesaId}/wiki`
    : `/mesas/${props.mesaId}/wiki/${props.paginaId}`
  router.push(destino)
}

onMounted(cargar)
</script>

<template>
      <div class="editor">
      <div class="editor-cabecera">
        <div>
          <h2 class="titulo-seccion">✒ {{ esNueva ? 'Nueva Página del Códice' : 'Editar Página del Códice' }}</h2>
          <p class="label">Formato ligero: líneas normales son párrafos, «## » encabeza, «- » crea listas y «&gt; » es citado.</p>
        </div>
      </div>

      <!-- Metadatos -->
      <div class="card meta">
        <label class="field span2">
          <span class="label">Título de la Página *</span>
          <input v-model="titulo" type="text" placeholder="Ej. Ruinas del Fuerte Virmar" class="input" />
        </label>

        <label class="field">
          <span class="label">Tipo de Entrada</span>
          <select v-model="tipo" class="input">
            <option v-for="t in TIPOS" :key="t" :value="t">{{ t }}</option>
          </select>
        </label>

        <label class="field">
          <span class="label">Carpeta Padre</span>
          <select v-model="carpeta" class="input">
            <option v-for="c in carpetas" :key="c.id" :value="c.id">{{ c.nombre }}</option>
          </select>
        </label>

        <label class="field span3">
          <span class="label">Resumen / Vista previa en listado</span>
          <input v-model="resumen" type="text" placeholder="Una línea que resuma la entrada para el índice…" class="input" />
        </label>
      </div>

      <!-- Barra de formato -->
      <div class="herramientas">
        <span class="label herramientas-etiqueta">HERRAMIENTAS:</span>
        <button type="button" class="her" title="Encabezado H2" @click="insertar('## ')">H2</button>
        <button type="button" class="her" title="Encabezado H3" @click="insertar('### ')">H3</button>
        <button type="button" class="her" title="Lista de viñetas" @click="insertar('lista')">• Lista</button>
        <button type="button" class="her" title="Cita / leyenda" @click="insertar('> ')">&gt; Cita</button>
        <span class="herramientas-espacio"></span>
        <span class="label">{{ bloquesParseados.length }} bloques detectados</span>
      </div>

      <textarea
        ref="area"
        v-model="contenido"
        rows="16"
        placeholder='Escribe la entrada. Ej.:\n## Historia\nRavengro es una pequeña comunidad agrícola fundada en 4588 CA…\n- Punto uno\n- Punto dos'
        class="input area"
      ></textarea>

      <!-- Barra de acciones -->
      <div class="acciones">
        <button
          v-if="!esNueva"
          type="button"
          class="enlace-peligro"
          @click="confirmarBorrado = true"
        >
          Eliminar página
        </button>
        <div class="acciones-finales">
          <button type="button" class="btn btn--secondary" @click="cancelar">
            Cancelar
          </button>
          <button type="button" :disabled="guardando" class="btn" @click="guardar">
            {{ guardando ? 'Guardando…' : 'Guardar página' }}
          </button>
        </div>
      </div>
    </div>

    <ConfirmModal
      :open="confirmarBorrado"
      titulo="¿Eliminar esta página?"
      chip="Se retirará del índice del código"
      mensaje="Los enlaces que apunten a esta entrada dejarán de resolver. Esta acción no se puede deshacer."
      variante="danger"
      etiqueta-ok="Eliminar página"
      @close="confirmarBorrado = false"
      @accept="borrar"
    />
</template>

<style scoped>
.editor { display: grid; gap: var(--space-md); }
.editor-cabecera { display: flex; flex-direction: column; gap: var(--space-2xs); border-bottom: var(--rule-bar) solid var(--color-rule); padding-bottom: var(--space-sm); }
.titulo-seccion { margin: 0; font-size: var(--text-title); color: var(--color-ink); }
.meta { display: grid; gap: var(--space-sm); grid-template-columns: minmax(0, 1fr); padding: var(--space-md); align-content: start; }
@media (min-width: 60rem) { .meta { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
.field { display: grid; gap: var(--space-3xs); }
.span2 { grid-column: 1 / -1; }
.span3 { grid-column: 1 / -1; }
@media (min-width: 60rem) { .span2 { grid-column: span 2; } .span3 { grid-column: 1 / -1; } }
.herramientas { display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-3xs); border: var(--rule-hair) solid var(--color-rule); background: var(--color-paper-3); padding: var(--space-3xs) var(--space-sm); }
.herramientas-etiqueta { color: var(--color-muted); }
.herramientas-espacio { flex: 1; }
.her { background: transparent; border: 0; cursor: pointer; color: var(--color-accent-2); font-weight: 700; font-size: var(--text-sm); padding: var(--space-3xs) var(--space-2xs); }
.her:hover { background: var(--color-paper-2); }
.area { min-height: 20rem; resize: vertical; line-height: 1.6; font-family: var(--font-body); }
.acciones { display: flex; align-items: center; justify-content: space-between; gap: var(--space-2xs); flex-wrap: wrap; }
.acciones-finales { display: flex; align-items: center; gap: var(--space-2xs); margin-left: auto; }
.enlace-peligro { background: transparent; border: 0; color: var(--color-error); font-weight: 700; cursor: pointer; font-size: var(--text-sm); display: inline-flex; gap: var(--space-3xs); align-items: center; }
.enlace-peligro:hover { text-decoration: underline; }
</style>
