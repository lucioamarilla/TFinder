<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast.js'
import MesaGestionShell from '@/components/mesa/MesaGestionShell.vue'
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
  <MesaGestionShell :mesa-id="mesaId">
    <div class="space-y-5">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b-2 border-[#C2A980] pb-4">
        <div>
          <h2 class="font-mason text-xl font-bold text-[#8B5A2B] uppercase tracking-wide flex items-center gap-2">
            <span>✒</span> {{ esNueva ? 'Nueva Página del Códice' : 'Editar Página del Códice' }}
          </h2>
          <p class="font-minion italic text-xs text-[#736351] mt-0.5">
            Formato ligero: líneas normales son párrafos, «## » encabeza, «- » crea listas y «&gt; » es citado.
          </p>
        </div>
      </div>

      <!-- Metadatos -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 bg-[#FBF4E6] border border-[#E8DCC8] rounded p-4">
        <label class="md:col-span-2 block">
          <span class="font-tarzana text-xs font-bold text-[#8B5A2B] uppercase tracking-wide">Título de la Página *</span>
          <input
            v-model="titulo"
            type="text"
            placeholder="Ej. Ruinas del Fuerte Virmar"
            class="mt-1 w-full bg-[#FDF8EE] border border-[#C2A980] text-sm font-minion px-3 py-2 rounded text-[#1A1A1A] placeholder-[#8B7D6B] focus:outline-none focus:border-[#8B5A2B]"
          />
        </label>

        <label class="block">
          <span class="font-tarzana text-xs font-bold text-[#8B5A2B] uppercase tracking-wide">Tipo de Entrada</span>
          <select
            v-model="tipo"
            class="mt-1 w-full bg-[#FDF8EE] border border-[#C2A980] text-sm font-minion px-3 py-2 rounded text-[#1A1A1A] focus:outline-none focus:border-[#8B5A2B]"
          >
            <option v-for="t in TIPOS" :key="t" :value="t">{{ t }}</option>
          </select>
        </label>

        <label class="block">
          <span class="font-tarzana text-xs font-bold text-[#8B5A2B] uppercase tracking-wide">Carpeta Padre</span>
          <select
            v-model="carpeta"
            class="mt-1 w-full bg-[#FDF8EE] border border-[#C2A980] text-sm font-minion px-3 py-2 rounded text-[#1A1A1A] focus:outline-none focus:border-[#8B5A2B]"
          >
            <option v-for="c in carpetas" :key="c.id" :value="c.id">{{ c.nombre }}</option>
          </select>
        </label>

        <label class="md:col-span-3 block">
          <span class="font-tarzana text-xs font-bold text-[#8B5A2B] uppercase tracking-wide">Resumen / Vista previa en listado</span>
          <input
            v-model="resumen"
            type="text"
            placeholder="Una línea que resuma la entrada para el índice…"
            class="mt-1 w-full bg-[#FDF8EE] border border-[#C2A980] text-sm font-minion px-3 py-2 rounded text-[#1A1A1A] placeholder-[#8B7D6B] focus:outline-none focus:border-[#8B5A2B]"
          />
        </label>
      </div>

      <!-- Barra de formato -->
      <div class="flex flex-wrap items-center gap-1 bg-[#E8DCC8] border border-[#C2A980] rounded p-1.5">
        <span class="font-tarzana text-[0.7rem] font-bold text-[#8B7D6B] px-2">HERRAMIENTAS:</span>
        <button type="button" class="px-2 py-1 hover:bg-[#DFCDB4] rounded text-[#8B5A2B] font-bold text-sm" title="Encabezado H2" @click="insertar('## ')">H2</button>
        <button type="button" class="px-2 py-1 hover:bg-[#DFCDB4] rounded text-[#8B5A2B] font-bold text-sm" title="Encabezado H3" @click="insertar('### ')">H3</button>
        <button type="button" class="px-2 py-1 hover:bg-[#DFCDB4] rounded text-[#8B5A2B] font-bold text-sm" title="Lista de viñetas" @click="insertar('lista')">• Lista</button>
        <button type="button" class="px-2 py-1 hover:bg-[#DFCDB4] rounded text-[#8B5A2B] font-bold text-sm" title="Cita / leyenda" @click="insertar('> ')">&gt; Cita</button>
        <span class="flex-1"></span>
        <span class="font-tarzana text-[0.7rem] text-[#8B7D6B]">{{ bloquesParseados.length }} bloques detectados</span>
      </div>

      <textarea
        ref="area"
        v-model="contenido"
        rows="16"
        placeholder="Escribe la entrada. Ej.:\n## Historia\nRavengro es una pequeña comunidad agrícola fundada en 4588 CA…\n- Punto uno\n- Punto dos"
        class="w-full bg-[#FDF8EE] border border-[#C2A980] text-[0.95rem] font-minion px-4 py-3 rounded text-[#1A1A1A] placeholder-[#8B7D6B] leading-relaxed focus:outline-none focus:border-[#8B5A2B] resize-y"
      ></textarea>

      <!-- Barra de acciones -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
        <button
          v-if="!esNueva"
          type="button"
          class="self-start sm:self-auto font-tarzana text-xs font-bold text-[#8B1A1A] hover:underline flex items-center gap-1.5"
          @click="confirmarBorrado = true"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
          </svg>
          Eliminar página
        </button>
        <div class="flex items-center gap-2 sm:ml-auto">
          <button type="button" class="btn-copper-outline px-5 py-2.5 rounded font-tarzana text-xs font-bold" @click="cancelar">
            CANCELAR
          </button>
          <button type="button" :disabled="guardando" class="btn-gold-emboss px-6 py-2.5 rounded font-tarzana text-xs font-bold" @click="guardar">
            {{ guardando ? 'GUARDANDO…' : 'GUARDAR PÁGINA' }}
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
  </MesaGestionShell>
</template>