<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMisBuilds } from '@/services/builds.js'
import { crearPost } from '@/services/feed.js'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const toast = useToast()
const { user } = useAuth()

const MAX_TITULO = 180

const PESTANAS = [
  { id: 'post', label: 'Post', etiqueta: 'Debate Táctico' },
  { id: 'build', label: 'Compartir Build', etiqueta: 'Guía de Build' },
  { id: 'wiki', label: 'Compartir Wiki', etiqueta: 'Entrada de Wiki' }
]

const FLAIRS = ['Debate Táctico', 'Guía de Build', 'Entrada de Wiki', 'Pregunta de Reglas OGL']

const WIKIS = [
  {
    id: 'wiki-harrowstone',
    icono: '📜',
    eyebrow: 'Página de Wiki',
    meta: 'Campaña: La Corona de Carroña',
    titulo: 'Harrowstone: Crónica de la Ruina',
    texto: 'Tablas de DC para investigación y objetos encantados recuperables.',
    boton: 'Leer Wiki',
    ruta: '/builds'
  },
  {
    id: 'wiki-criptas',
    icono: '🗺️',
    eyebrow: 'Página de Wiki',
    meta: 'Wiki de mesa',
    titulo: 'Mapa de las Criptas de Everflame',
    texto: 'Pasajes inundados, trampas de foso y la cámara del celador.',
    boton: 'Leer Wiki',
    ruta: '/builds'
  }
]

const pestana = ref('post')
const titulo = ref('')
const etiqueta = ref('Debate Táctico')
const cuerpo = ref('')
const recursoId = ref('')
const misBuilds = ref([])
const publicando = ref(false)
const areaRef = ref(null)

const opciones = computed(() => {
  if (pestana.value === 'wiki') return WIKIS
  return misBuilds.value.map((b) => ({
    id: b.id,
    icono: '⚔️',
    eyebrow: 'Build Asociado',
    meta: `${b.clase} Nvl ${b.nivel} · PF1e OGL SRD`,
    titulo: b.display || b.nombre,
    texto: b.detalle || b.arquetipo,
    boton: 'Ver Ficha OGL',
    ruta: `/builds/${b.id}`
  }))
})

const recurso = computed(() => opciones.value.find((o) => o.id === recursoId.value) || null)

function cambiarPestana(id) {
  if (pestana.value === id) return
  pestana.value = id
  etiqueta.value = PESTANAS.find((p) => p.id === id)?.etiqueta || etiqueta.value
  recursoId.value = ''
}

function envolver(prefijo, sufijo = prefijo) {
  const el = areaRef.value
  if (!el) {
    cuerpo.value += `${prefijo}${sufijo}`
    return
  }
  const inicio = el.selectionStart
  const fin = el.selectionEnd
  const seleccion = cuerpo.value.slice(inicio, fin)
  cuerpo.value = `${cuerpo.value.slice(0, inicio)}${prefijo}${seleccion}${sufijo}${cuerpo.value.slice(fin)}`
  requestAnimationFrame(() => {
    el.focus()
    el.setSelectionRange(inicio + prefijo.length, inicio + prefijo.length + seleccion.length)
  })
}

function insertarTexto(texto) {
  const el = areaRef.value
  if (!el) {
    cuerpo.value += texto
    return
  }
  const inicio = el.selectionStart
  cuerpo.value = `${cuerpo.value.slice(0, inicio)}${texto}${cuerpo.value.slice(el.selectionEnd)}`
  requestAnimationFrame(() => {
    el.focus()
    el.setSelectionRange(inicio + texto.length, inicio + texto.length)
  })
}

async function publicar() {
  if (!titulo.value.trim()) {
    toast.error('La publicación necesita un título.')
    return
  }
  publicando.value = true
  try {
    const embed = recurso.value
      ? {
          icono: recurso.value.icono,
          eyebrow: recurso.value.eyebrow,
          meta: recurso.value.meta,
          titulo: recurso.value.titulo,
          texto: recurso.value.texto,
          boton: recurso.value.boton,
          ruta: recurso.value.ruta
        }
      : null
    await crearPost({
      titulo: titulo.value,
      cuerpo: cuerpo.value,
      etiqueta: etiqueta.value,
      tipo: pestana.value === 'post' ? 'post' : pestana.value,
      embed,
      autor: {
        id: 'aldren',
        handle: 'Valeros_ElTemerario',
        nombre: user.value?.nombre || 'Valeros el Temerario',
        iniciales: user.value?.iniciales || 'AV',
        tono: 'oro'
      }
    })
    toast.ok('Publicación añadida al tablón del cónclave.')
    router.push('/feed')
  } catch (e) {
    toast.error(e.message || 'No pudimos publicar tu mensaje.')
  } finally {
    publicando.value = false
  }
}

onMounted(async () => {
  try {
    misBuilds.value = await getMisBuilds()
  } catch {
    misBuilds.value = []
  }
})
</script>

<template>
  <main class="flex-grow w-full max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-10">
    <nav class="flex items-center gap-2 text-[11px] font-tarzana tracking-wider uppercase mb-4 text-[#8B7D6B]">
      <RouterLink to="/dashboard" class="hover:text-[#8B5A2B]">Inicio</RouterLink>
      <span>/</span>
      <RouterLink to="/feed" class="hover:text-[#8B5A2B]">Feed de la Comunidad</RouterLink>
      <span>/</span>
      <span class="text-[#8B5A2B] font-bold">Crear Publicación</span>
    </nav>

    <article class="parchment-sheet border border-[#C2A980] rounded-sm p-6 md:p-8 relative">
      <header class="text-center mb-6">
        <div class="flex items-center justify-center gap-2 mb-1">
          <span class="text-[#D4AF37] text-xs">✦</span>
          <h1 class="font-mason text-[1.7rem] font-bold text-[#8B5A2B] tracking-wider uppercase leading-tight">Crear Publicación</h1>
          <span class="text-[#D4AF37] text-xs">✦</span>
        </div>
        <p class="font-minion italic text-[#6B5B4B] text-[0.95rem] leading-relaxed max-w-md mx-auto">
          Comparte crónicas, debates de reglas o vincula tus fichas de personaje y páginas de wiki con el cónclave.
        </p>
        <div class="w-full h-px bg-gradient-to-r from-transparent via-[#C2A980] to-transparent mt-4"></div>
      </header>

      <nav class="flex border-b border-[#C2A980] mb-6" aria-label="Tipo de publicación">
        <button
          v-for="opcion in PESTANAS"
          :key="opcion.id"
          type="button"
          class="flex-1 py-2.5 text-center font-mason text-sm tracking-wide border-b-[3px] transition-colors"
          :class="pestana === opcion.id
            ? 'font-bold text-[#8B5A2B] border-[#D4AF37] bg-[#FAF2DE]/50'
            : 'font-semibold text-[#8B7D6B] border-transparent hover:text-[#8B5A2B] hover:bg-black/5'"
          @click="cambiarPestana(opcion.id)"
        >
          {{ opcion.label }}
        </button>
      </nav>

      <form class="space-y-5" @submit.prevent="publicar">
        <div>
          <div class="flex justify-between items-center mb-1.5">
            <label class="font-tarzana text-xs uppercase font-bold text-[#8B5A2B] tracking-wider" for="post-title">
              Título de la Publicación *
            </label>
            <span class="font-minion text-xs" :class="titulo.length >= MAX_TITULO ? 'text-[#8B1A1A] font-bold' : 'text-[#8B7D6B]'">
              {{ titulo.length }}/{{ MAX_TITULO }}
            </span>
          </div>
          <input
            id="post-title"
            v-model="titulo"
            type="text"
            :maxlength="MAX_TITULO"
            placeholder="¿Qué tema quieres discutir o presentar a los aventureros?"
            class="w-full bg-white border border-[#8B7D6B] rounded-none px-3.5 py-2.5 font-minion text-base text-[#1A1A1A] placeholder-[#8B7D6B]/70 focus:outline-none focus:border-[#D4AF37] focus:ring-1 focus:ring-[#D4AF37] shadow-inner"
          />
        </div>

        <div>
          <label class="block font-tarzana text-xs uppercase font-bold text-[#8B5A2B] tracking-wider mb-2">
            Etiqueta del Cónclave (Flair)
          </label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="flair in FLAIRS"
              :key="flair"
              type="button"
              class="px-3 py-1 text-xs font-tarzana uppercase rounded transition-colors border"
              :class="etiqueta === flair
                ? 'bg-[#EAD9B8] border-[#8B5A2B] text-[#8B5A2B] font-semibold shadow-sm'
                : 'text-[#8B7D6B] bg-white/80 border-[#C2A980] hover:border-[#8B5A2B] hover:text-[#8B5A2B]'"
              @click="etiqueta = flair"
            >
              <span v-if="etiqueta === flair">✓ </span>{{ flair }}
            </button>
          </div>
        </div>

        <div>
          <label class="block font-tarzana text-xs uppercase font-bold text-[#8B5A2B] tracking-wider mb-1.5" for="post-content">
            Cuerpo del Mensaje
          </label>
          <div class="flex flex-wrap items-center gap-1 bg-[#EFE4D0] border-t border-l border-r border-[#8B7D6B] px-2.5 py-1.5 text-xs text-[#8B5A2B]">
            <button type="button" class="px-2 py-1 hover:bg-[#DFCDB1] rounded font-bold font-serif" title="Negrita" @click="envolver('**')">B</button>
            <button type="button" class="px-2 py-1 hover:bg-[#DFCDB1] rounded italic font-serif" title="Cursiva" @click="envolver('*')">I</button>
            <span class="text-[#C2A980] mx-1">|</span>
            <button type="button" class="px-2 py-1 hover:bg-[#DFCDB1] rounded font-minion font-semibold" title="Cita OGL" @click="insertarTexto('«cita OGL»')">“ ” OGL</button>
            <button type="button" class="px-2 py-1 hover:bg-[#DFCDB1] rounded font-tarzana" title="Enlace" @click="insertarTexto('[enlace](url)')">🔗 Enlace</button>
            <button type="button" class="px-2 py-1 hover:bg-[#DFCDB1] rounded font-serif" title="Lista de viñetas" @click="insertarTexto('- ')">• Lista</button>
            <span class="text-[#C2A980] mx-1">|</span>
            <button type="button" class="px-2 py-1 hover:bg-[#DFCDB1] rounded font-mono text-[11px] bg-white/50 border border-[#C2A980]/60" title="Código de Regla" @click="insertarTexto('`<Regla/>`')">&lt;Regla/&gt;</button>
          </div>
          <textarea
            id="post-content"
            ref="areaRef"
            v-model="cuerpo"
            class="w-full h-[200px] bg-white border border-[#8B7D6B] rounded-none p-3.5 font-minion text-base text-[#1A1A1A] placeholder-[#8B7D6B]/70 leading-relaxed focus:outline-none focus:border-[#D4AF37] focus:ring-1 focus:ring-[#D4AF37] resize-none shadow-inner"
            placeholder="¿Qué quieres compartir con la comunidad?"
          ></textarea>
        </div>

        <div class="border border-dashed border-[#C2A980] bg-[#F5EEDD]/60 p-4 rounded-sm">
          <label class="block font-tarzana text-xs uppercase font-bold text-[#8B5A2B] tracking-wider mb-2" for="resource-selector">
            Vincular Ficha de Build o Wiki (Opcional)
          </label>
          <div class="relative mb-3">
            <select
              id="resource-selector"
              v-model="recursoId"
              class="w-full bg-white border border-[#8B7D6B] rounded-none py-2 px-3 pr-8 font-minion text-base text-[#1A1A1A] focus:outline-none focus:border-[#D4AF37] focus:ring-1 focus:ring-[#D4AF37] cursor-pointer appearance-none"
            >
              <option value="">Seleccionar uno de tus recursos guardados...</option>
              <option v-for="opcion in opciones" :key="opcion.id" :value="opcion.id">
                {{ opcion.icono }} {{ opcion.titulo }} ({{ opcion.meta }})
              </option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-[#8B5A2B]">
              <svg class="h-4 w-4 fill-current" viewBox="0 0 20 20" aria-hidden="true">
                <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
              </svg>
            </div>
          </div>

          <div v-if="recurso" class="border border-[#D4AF37] bg-[#FDF8EE] p-3 rounded shadow-sm flex items-start gap-3">
            <div class="w-10 h-10 border border-[#8B5A2B] bg-[#EFE3CF] flex-shrink-0 flex items-center justify-center text-[#8B5A2B] text-lg rounded-sm shadow-inner">
              {{ recurso.icono }}
            </div>
            <div class="flex-grow min-w-0">
              <div class="flex items-baseline justify-between gap-2">
                <h4 class="font-mason font-bold text-sm text-[#8B5A2B] truncate">{{ recurso.titulo }}</h4>
                <span class="text-[10px] font-tarzana text-[#D4AF37] font-bold uppercase tracking-wider bg-[#2B2319] px-1.5 py-0.5 rounded whitespace-nowrap">
                  PF1e OGL
                </span>
              </div>
              <p class="font-minion text-xs text-[#332517]/90 mt-0.5 leading-snug">{{ recurso.texto }}</p>
            </div>
          </div>
          <p v-else-if="opciones.length === 0" class="font-minion text-xs italic text-[#8B7D6B]">
            No tenés recursos guardados de este tipo todavía.
          </p>
        </div>

        <div class="pt-2 flex items-center justify-end gap-3 border-t border-[#C2A980]/60">
          <button
            type="button"
            class="px-5 py-2 border border-[#8B7D6B] font-tarzana uppercase text-sm font-semibold text-[#8B5A2B] hover:bg-[#EFE4D0] transition-colors rounded-none"
            @click="router.push('/feed')"
          >
            Cancelar
          </button>
          <button
            type="submit"
            class="btn-gold-emboss px-7 py-2.5 font-tarzana uppercase font-bold text-[#1A1A1A] text-base tracking-wider flex items-center gap-1.5 rounded-none"
            :disabled="publicando"
          >
            <span>✦</span>
            <span>{{ publicando ? 'Publicando…' : 'Publicar' }}</span>
          </button>
        </div>
      </form>
    </article>
  </main>
</template>
