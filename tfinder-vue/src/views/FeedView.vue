<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getFeedPosts, votarPost, toggleGuardarPost } from '@/services/feed.js'
import { useToast } from '@/composables/useToast'
import FeedComment from '@/components/feed/FeedComment.vue'

const router = useRouter()
const toast = useToast()

const ORDENES = [
  { id: 'hot', label: 'Hot' },
  { id: 'nuevo', label: 'Nuevo' },
  { id: 'top', label: 'Top' }
]

const ETIQUETAS = {
  'Guía de Build': { chip: 'bg-[#D4AF37]/20 border-[#D4AF37] text-[#8B5A2B]', avatar: 'bg-[#D4AF37] text-[#1A1A1A] border-[#8B5A2B]' },
  'Debate Táctico': { chip: 'bg-[#9C6734]/15 border-[#9C6734] text-[#8B5A2B]', avatar: 'bg-[#9C6734] text-[#FDF8EE] border-[#573312]' },
  'Debate de Reglas': { chip: 'bg-[#9C6734]/15 border-[#9C6734] text-[#8B5A2B]', avatar: 'bg-[#9C6734] text-[#FDF8EE] border-[#573312]' },
  'Entrada de Wiki': { chip: 'bg-[#6B8E23]/15 border-[#6B8E23] text-[#556B2F]', avatar: 'bg-[#6B8E23] text-[#FDF8EE] border-[#4F6A19]' },
  'Crónica de Sesión': { chip: 'bg-[#8B1A1A]/10 border-[#8B1A1A] text-[#8B1A1A]', avatar: 'bg-[#8B1A1A] text-[#FDF8EE] border-[#5E0F0F]' },
  'Pregunta de Reglas OGL': { chip: 'bg-[#8B5A2B]/15 border-[#8B5A2B] text-[#8B5A2B]', avatar: 'bg-[#8B5A2B] text-[#FDF8EE] border-[#573312]' }
}

const TENDENCIAS = [
  { titulo: 'Seelah Hermana de Armas', meta: 'Paladín Defensiva', votos: 94 },
  { titulo: 'Cripta de Everflame (Wiki)', meta: 'Guía para GM', votos: 76 },
  { titulo: 'Merisiel Sombra Veloz', meta: 'Pícaro Elfo Nvl 7', votos: 58 }
]

const REGLAS = [
  { lead: 'Fidelidad OGL v1.0a:', texto: 'Citá las fuentes del SRD y respetá los términos de la licencia.' },
  { lead: 'Spoilers de Campañas:', texto: 'Etiquetá las tramas de mesas activas antes de narrarlas.' },
  { lead: 'Enlaces a Builds:', texto: 'Compartí fichas completas enlazadas para facilitar el debate.' },
  { lead: 'Caballerosidad de Taberna:', texto: 'El cónclave premia la crítica argumentada, no el desdén.' }
]

const orden = ref('hot')
const posts = ref([])
const cargando = ref(true)
const fallo = ref(null)
const hilosAbiertos = ref([])

const PERFILES_CONOCIDOS = ['seelah', 'ezren']

async function cargar() {
  cargando.value = true
  fallo.value = null
  try {
    posts.value = await getFeedPosts({ orden: orden.value })
  } catch (e) {
    fallo.value = e.message || 'No pudimos abrir el tablón de aventureros.'
  } finally {
    cargando.value = false
  }
}

function cambiarOrden(id) {
  if (orden.value === id) return
  orden.value = id
  cargar()
}

function etiquetaDe(post) {
  return ETIQUETAS[post.etiqueta] || ETIQUETAS['Debate Táctico']
}

function reemplazar(actualizado) {
  const i = posts.value.findIndex((p) => p.id === actualizado.id)
  if (i >= 0) posts.value.splice(i, 1, actualizado)
}

async function votar(post, direccion) {
  try {
    reemplazar(await votarPost(post.id, direccion))
  } catch (e) {
    toast.error(e.message)
  }
}

async function guardar(post) {
  try {
    const actualizado = await toggleGuardarPost(post.id)
    reemplazar(actualizado)
    toast.info(actualizado.guardado ? 'Publicación guardada en tu compendio.' : 'Publicación retirada de tu compendio.')
  } catch (e) {
    toast.error(e.message)
  }
}

function alternarHilo(post) {
  if (!post.comentarios.length) {
    toast.info(`Esta publicación acumula ${post.totalComentarios} comentarios en el hilo del cónclave.`)
    return
  }
  const i = hilosAbiertos.value.indexOf(post.id)
  if (i >= 0) hilosAbiertos.value.splice(i, 1)
  else hilosAbiertos.value.push(post.id)
}

onMounted(cargar)
</script>

<template>
  <main class="flex-grow w-full max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-10">
    <nav class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[11px] font-tarzana tracking-wider uppercase mb-4">
      <div class="flex items-center gap-2 text-[#8B7D6B]">
        <RouterLink to="/dashboard" class="hover:text-[#8B5A2B]">Inicio</RouterLink>
        <span>/</span>
        <span>Tablón de Aventureros</span>
        <span>/</span>
        <span class="text-[#8B5A2B] font-bold">Feed de la Comunidad</span>
      </div>
      <div class="flex items-center gap-3 text-[#8B7D6B]">
        <span class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-[#6B8E23]"></span> 142 Aventureros Conectados
        </span>
        <span>•</span>
        <span>Reglas Canónicas Paizo OGL v1.0a</span>
      </div>
    </nav>

    <div class="bg-[#FDF8EE]/90 border border-[#C2A980] rounded-sm px-4 sm:px-5 py-3 mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <h1 class="font-mason text-xl md:text-2xl font-bold text-[#8B5A2B] tracking-wide flex items-center gap-2">
        <span class="text-[#D4AF37]">✦</span> Comunidad
      </h1>
      <div class="flex items-center gap-4 flex-wrap">
        <div class="flex items-center gap-1 font-mason text-sm font-semibold">
          <button
            v-for="opcion in ORDENES"
            :key="opcion.id"
            type="button"
            class="px-3 py-1.5 border-b-[3px] transition-colors"
            :class="orden === opcion.id ? 'text-[#8B5A2B] border-[#D4AF37]' : 'text-[#8B7D6B] border-transparent hover:text-[#8B5A2B]'"
            @click="cambiarOrden(opcion.id)"
          >
            {{ opcion.label }}
          </button>
        </div>
        <button
          type="button"
          class="btn-gold-emboss px-4 py-2 rounded text-[#1A1A1A] font-tarzana font-extrabold text-xs tracking-widest uppercase flex items-center gap-1.5"
          @click="router.push('/feed/nuevo')"
        >
          <span>+</span> Crear Publicación
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_300px] gap-6 items-start">
      <section aria-label="Publicaciones de la comunidad">
        <div v-if="cargando" class="space-y-4" role="status" aria-live="polite">
          <div v-for="n in 3" :key="n" class="card-parchment p-4 rounded-sm animate-pulse space-y-3">
            <div class="h-4 bg-[#C2A980]/40 rounded w-32"></div>
            <div class="h-5 bg-[#C2A980]/40 rounded w-4/5"></div>
            <div class="h-3 bg-[#C2A980]/25 rounded w-full"></div>
            <div class="h-3 bg-[#C2A980]/25 rounded w-2/3"></div>
          </div>
        </div>

        <div v-else-if="fallo" class="parchment-sheet border border-[#C2A980] rounded-sm py-14 text-center" role="alert">
          <p class="font-tarzana uppercase tracking-widest text-xs text-[#8B1A1A] font-bold mb-1">El tablón está en silencio</p>
          <p class="font-minion text-[#5A4A3A]">{{ fallo }}</p>
          <button type="button" class="btn-gold mt-4 px-6 py-2 font-tarzana font-bold uppercase tracking-wider text-sm" @click="cargar">Reintentar</button>
        </div>

        <div v-else-if="posts.length === 0" class="parchment-sheet border border-[#C2A980] rounded-sm py-14 text-center">
          <p class="font-mason text-xl text-[#8B5A2B] font-bold">Ningún pergamino en el tablón</p>
          <p class="font-minion text-sm text-[#6B5B4B] italic mt-1">Sé el primero en compartir una crónica, duda o ficha.</p>
        </div>

        <div v-else class="space-y-5">
          <article v-for="post in posts" :key="post.id" class="card-parchment p-4 rounded-sm shadow-sm">
            <div class="flex gap-4">
              <div class="flex flex-col items-center bg-[#F4EAD6] border border-[#E5D7C0] rounded px-2 py-2 min-w-[48px] h-fit">
                <button
                  type="button"
                  class="transition-transform hover:scale-110"
                  :class="post.miVoto === 'up' ? 'text-[#D4AF37]' : 'text-[#6B8E23]'"
                  aria-label="Voto positivo"
                  @click="votar(post, 'up')"
                >
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                    <path clip-rule="evenodd" fill-rule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" />
                  </svg>
                </button>
                <span class="font-mason font-bold text-sm text-[#332517] my-1">{{ post.votos }}</span>
                <button
                  type="button"
                  class="transition-colors"
                  :class="post.miVoto === 'down' ? 'text-[#8B1A1A]' : 'text-[#8B7D6B] hover:text-[#8B1A1A]'"
                  aria-label="Voto negativo"
                  @click="votar(post, 'down')"
                >
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                    <path clip-rule="evenodd" fill-rule="evenodd" d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z" />
                  </svg>
                </button>
              </div>

              <div class="flex-grow min-w-0">
                <div class="flex items-center gap-2 mb-1.5">
                  <span
                    class="w-7 h-7 rounded-full border flex items-center justify-center font-mason text-[10px] font-bold flex-shrink-0"
                    :class="etiquetaDe(post).avatar"
                  >
                    {{ post.iniciales }}
                  </span>
                  <RouterLink
                    v-if="PERFILES_CONOCIDOS.includes(post.autorId)"
                    :to="`/usuarios/${post.autorId}`"
                    class="font-tarzana text-xs text-[#8B5A2B] font-semibold hover:underline"
                  >
                    {{ post.autor }}
                  </RouterLink>
                  <span v-else class="font-tarzana text-xs text-[#332517] font-semibold">{{ post.autor }}</span>
                  <span class="font-minion text-[11px] text-[#8B7D6B]">• {{ post.tiempo }}</span>
                </div>

                <span
                  class="inline-block px-2 py-0.5 border rounded font-tarzana font-bold text-[10px] uppercase tracking-wide mb-2"
                  :class="etiquetaDe(post).chip"
                >
                  {{ post.etiqueta }}
                </span>

                <h2 class="font-mason font-bold text-lg text-[#8B5A2B] leading-snug mb-2">{{ post.titulo }}</h2>
                <p class="font-minion text-[15px] text-[#332517] leading-relaxed">{{ post.cuerpo }}</p>

                <div v-if="post.embed" class="bg-[#FDF8EE] border-2 border-dashed border-[#D4AF37]/70 rounded p-3 mt-3 flex items-center justify-between flex-wrap gap-3">
                  <div class="flex items-center gap-3 min-w-0">
                    <span class="w-8 h-8 rounded bg-[#2B2319] text-[#D4AF37] flex items-center justify-center text-base border border-[#D4AF37] flex-shrink-0">
                      {{ post.embed.icono }}
                    </span>
                    <div class="min-w-0">
                      <div class="font-tarzana text-[10px] uppercase tracking-wider text-[#8B7D6B]">
                        {{ post.embed.eyebrow }} · {{ post.embed.meta }}
                      </div>
                      <div class="font-mason font-bold text-xs text-[#332517] truncate">{{ post.embed.titulo }}</div>
                      <div class="font-minion italic text-[11px] text-[#6B5B4B] leading-snug">{{ post.embed.texto }}</div>
                    </div>
                  </div>
                  <button
                    type="button"
                    class="font-tarzana text-xs font-bold text-[#1A1A1A] bg-[#D4AF37] hover:bg-[#E6CA65] transition-colors px-3 py-1 rounded shadow-sm whitespace-nowrap"
                    @click="router.push(post.embed.ruta)"
                  >
                    {{ post.embed.boton }} →
                  </button>
                </div>

                <div class="flex items-center flex-wrap gap-4 text-xs font-tarzana text-[#8B7D6B] pt-2.5 mt-3 border-t border-[#E5D7C0]">
                  <button type="button" class="flex items-center gap-1.5 hover:text-[#8B5A2B] transition-colors" @click="alternarHilo(post)">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                    <span :class="{ 'text-[#8B5A2B] font-bold': post.comentarios.length }">{{ post.totalComentarios }} Comentarios</span>
                  </button>
                  <button type="button" class="flex items-center gap-1.5 hover:text-[#8B5A2B] transition-colors" @click="toast.info('Enlace de la publicación copiado al portapapeles.')">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                    Compartir
                  </button>
                  <button
                    type="button"
                    class="flex items-center gap-1.5 transition-colors"
                    :class="post.guardado ? 'text-[#8B5A2B] font-bold' : 'hover:text-[#8B5A2B]'"
                    @click="guardar(post)"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L7 21V5z" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                    {{ post.guardado ? 'Guardado' : 'Guardar' }}
                  </button>
                </div>

                <div v-if="hilosAbiertos.includes(post.id) && post.comentarios.length" class="mt-3 pt-3 border-t border-[#E5D7C0]">
                  <div class="flex items-center justify-between mb-3">
                    <h3 class="font-mason font-bold text-sm text-[#8B5A2B]">Hilo de Respuestas del Cónclave</h3>
                    <span class="font-tarzana text-[10px] uppercase tracking-wider text-[#8B7D6B]">ordenado por votos</span>
                  </div>
                  <div class="space-y-3">
                    <FeedComment
                      v-for="comentario in post.comentarios"
                      :key="comentario.id"
                      :comentario="comentario"
                    />
                  </div>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>

      <aside class="space-y-5">
        <div class="parchment-sheet border border-[#C2A980] rounded-sm p-4">
          <h2 class="font-mason font-bold text-sm text-[#8B5A2B] tracking-wide mb-2">✦ Acerca de la Comunidad</h2>
          <p class="font-minion text-xs text-[#6B5B4B] leading-relaxed mb-3">
            El Tablón de Aventureros de TFinder reúne a cronistas de Pathfinder 1e para compartir fichas, resolver dudas canónicas y narrar sus sesiones.
          </p>
          <div class="grid grid-cols-2 gap-2 text-center mb-3">
            <div class="bg-[#F4EAD6] border border-[#E5D7C0] rounded py-2">
              <div class="font-mason font-bold text-lg text-[#8B5A2B]">1,840</div>
              <div class="font-tarzana text-[9px] uppercase tracking-widest text-[#8B7D6B]">Miembros</div>
            </div>
            <div class="bg-[#F4EAD6] border border-[#E5D7C0] rounded py-2">
              <div class="font-mason font-bold text-lg text-[#8B5A2B]">142</div>
              <div class="font-tarzana text-[9px] uppercase tracking-widest text-[#8B7D6B]">En Campaña</div>
            </div>
          </div>
          <button
            type="button"
            class="btn-gold w-full px-4 py-2 font-tarzana font-bold uppercase tracking-wider text-xs"
            @click="router.push('/feed/nuevo')"
          >
            + Publicar Crónica o Duda
          </button>
        </div>

        <div class="parchment-sheet border border-[#C2A980] rounded-sm p-4">
          <h2 class="font-mason font-bold text-sm text-[#8B5A2B] tracking-wide mb-2">Reglas del Cónclave OGL</h2>
          <ol class="space-y-2 font-minion text-xs text-[#6B5B4B] leading-relaxed list-decimal list-inside">
            <li v-for="regla in REGLAS" :key="regla.lead">
              <b class="text-[#332517]">{{ regla.lead }}</b> {{ regla.texto }}
            </li>
          </ol>
        </div>

        <div class="parchment-sheet border border-[#C2A980] rounded-sm p-4">
          <h2 class="font-mason font-bold text-sm text-[#8B5A2B] tracking-wide mb-3">Tendencias en Golarion</h2>
          <ul class="space-y-2.5">
            <li v-for="t in TENDENCIAS" :key="t.titulo" class="flex items-center justify-between gap-2">
              <div class="min-w-0">
                <div class="font-tarzana text-xs font-bold text-[#332517] truncate">{{ t.titulo }}</div>
                <div class="font-minion text-[10px] text-[#8B7D6B]">{{ t.meta }}</div>
              </div>
              <span class="font-tarzana text-[11px] font-bold text-[#556B2F] whitespace-nowrap">{{ t.votos }} votos</span>
            </li>
          </ul>
        </div>
      </aside>
    </div>
  </main>
</template>
