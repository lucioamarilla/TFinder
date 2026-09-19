<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import { getFeedPosts } from '@/services/feed.js'
import { getMisBuilds } from '@/services/builds.js'
import ModalCambioPassword from '@/components/modals/ModalCambioPassword.vue'

const router = useRouter()
const toast = useToast()
const { user } = useAuth()

const STATS = [
  { valor: 5, label: 'Mesas en Juego' },
  { valor: 12, label: 'Builds Forjados' },
  { valor: 348, label: 'Seguidores' },
  { valor: 89, label: 'Seguidos' }
]

const ETIQUETAS = {
  'Guía de Build': 'bg-[#D4AF37]/20 border-[#D4AF37] text-[#8B5A2B]',
  'Debate Táctico': 'bg-[#9C6734]/15 border-[#9C6734] text-[#8B5A2B]',
  'Debate de Reglas': 'bg-[#9C6734]/15 border-[#9C6734] text-[#8B5A2B]',
  'Entrada de Wiki': 'bg-[#6B8E23]/15 border-[#6B8E23] text-[#556B2F]',
  'Crónica de Sesión': 'bg-[#8B1A1A]/10 border-[#8B1A1A] text-[#8B1A1A]',
  'Pregunta de Reglas OGL': 'bg-[#8B5A2B]/15 border-[#8B5A2B] text-[#8B5A2B]'
}

const pestana = ref('publicaciones')
const orden = ref('recientes')
const modalClave = ref(false)
const posts = ref([])
const builds = ref([])
const cargando = ref(true)

const postsOrdenados = computed(() => {
  const copia = [...posts.value]
  if (orden.value === 'valorados') return copia.sort((a, b) => b.votos - a.votos)
  if (orden.value === 'comentados') return copia.sort((a, b) => b.totalComentarios - a.totalComentarios)
  return copia.sort((a, b) => a.horas - b.horas)
})

const compendio = computed(() => builds.value.slice(0, 4))

function etiquetaClase(post) {
  return ETIQUETAS[post.etiqueta] || ETIQUETAS['Debate Táctico']
}

function esPublico(build) {
  return build.privacidad === 'publico'
}

function atributosDe(build) {
  const rasgos = build.ficha?.rasgos
  if (!rasgos?.length) return build.detalle || build.arquetipo
  return rasgos.map((r) => `${r.etiqueta} ${r.valor} (${r.mod})`).join(' • ')
}

function dotesDe(build) {
  const dotes = build.ficha?.dotes
  if (!dotes?.length) return build.detalle || 'Sin dotes registradas.'
  return dotes.map((d) => d.nombre).join(', ')
}

onMounted(async () => {
  try {
    const [publicaciones, misBuilds] = await Promise.all([
      getFeedPosts({ autorId: 'aldren' }),
      getMisBuilds()
    ])
    posts.value = publicaciones
    builds.value = misBuilds
  } catch (e) {
    toast.error(e.message || 'No pudimos cargar tu perfil.')
  } finally {
    cargando.value = false
  }
})
</script>

<template>
  <main class="flex-grow w-full max-w-5xl mx-auto px-4 py-8">
    <nav class="flex items-center justify-between gap-2 text-[11px] font-tarzana font-semibold tracking-wider uppercase mb-4">
      <div class="flex items-center gap-2 text-[#8B7D6B]">
        <RouterLink to="/dashboard" class="hover:text-[#8B5A2B]">Inicio</RouterLink>
        <span>/</span>
        <span>Perfil</span>
        <span>/</span>
        <span class="text-[#D4AF37]">{{ user?.nombre }}</span>
      </div>
      <span class="hidden sm:block text-[10px] text-[#8B7D6B]">Libramiento del Gremio de Exploradores</span>
    </nav>

    <div class="bg-[#FDF8EE] border border-[#C2A980] shadow-sm rounded-md overflow-hidden">
      <section class="relative">
        <div
          class="h-32 border-b-2 border-[#D4AF37] relative flex items-end justify-end p-3"
          style="background-color:#1A1A1A;background-image:radial-gradient(#2B2319 1px, transparent 1px),radial-gradient(#2B2319 1px, #1A1A1A 1px);background-size:20px 20px;background-position:0 0,10px 10px"
        >
          <span class="text-[10px] font-tarzana text-[#D4AF37]/60 tracking-widest hidden sm:block">LIBRAMIENTO DEL GREMIO DE EXPLORADORES</span>
        </div>

        <div class="relative -mt-12 flex justify-center">
          <div class="relative">
            <div class="w-24 h-24 rounded-full bg-[#2B2319] border-[3px] border-[#D4AF37] shadow-lg flex items-center justify-center p-1.5 ring-4 ring-[#FDF8EE]">
              <div class="w-full h-full rounded-full border border-[#573312]/60 bg-gradient-to-br from-stone-800 to-[#1e1710] flex flex-col items-center justify-center text-[#D4AF37] shadow-inner">
                <span class="font-mason font-black text-2xl tracking-tighter">{{ user?.iniciales || 'AV' }}</span>
                <span class="font-tarzana text-[7px] text-[#E6CA65]/80 -mt-1 tracking-widest">NVL 4</span>
              </div>
            </div>
            <div class="absolute bottom-1 right-2 w-4 h-4 bg-[#6B8E23] rounded-full border-2 border-[#FDF8EE]" title="Aventurero Activo"></div>
          </div>
        </div>

        <div class="px-6 pt-3 pb-6 text-center">
          <h1 class="font-mason font-bold text-2xl md:text-3xl text-[#8B5A2B] tracking-wide">{{ user?.nombre || 'Aldren Valeros' }}</h1>
          <p class="font-tarzana text-xs font-semibold text-[#8B7D6B] tracking-widest uppercase mt-0.5">
            Guerrero Humano Nvl 4 • Maestro Forjador de Campañas
          </p>
          <div class="max-w-2xl mx-auto mt-4 px-4">
            <p class="font-minion italic text-[#332517] text-base md:text-[1.05rem] leading-relaxed">
              «El filo de una espada forjada en Ustalav vale más que diez discursos vacíos en Absalom.» Veterano de la Corona de Carroña y compilador de dotes tácticas para aventureros de Pathfinder 1e. Cronista en activo en 3 mesas de campaña.
            </p>
          </div>
          <div class="mt-5 flex items-center justify-center flex-wrap gap-4">
            <button
              type="button"
              class="px-4 py-1.5 border-[1.5px] border-[#8B5A2B] text-[#8B5A2B] hover:bg-[#8B5A2B] hover:text-[#FDF8EE] rounded text-xs font-tarzana font-bold transition-all flex items-center gap-1.5 shadow-sm"
              @click="toast.info('Formulario de perfil (simulado).')"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
              </svg>
              Editar Perfil
            </button>
            <button
              type="button"
              class="px-3 py-1.5 text-[#8B5A2B] hover:text-[#523315] hover:underline text-xs font-tarzana font-bold transition-colors flex items-center gap-1.5"
              @click="modalClave = true"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
              </svg>
              Cambiar Contraseña
            </button>
          </div>
        </div>
      </section>

      <section class="bg-[#F4EAD6] border-y border-[#E5D7C0] py-4 px-4">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center max-w-4xl mx-auto">
          <div v-for="(stat, i) in STATS" :key="stat.label" class="py-1" :class="i < STATS.length - 1 ? 'sm:border-r border-[#E5D7C0]' : ''">
            <div class="font-mason font-bold text-2xl text-[#8B5A2B] leading-none">{{ stat.valor }}</div>
            <div class="font-tarzana text-[10px] font-semibold text-[#8B7D6B] tracking-widest mt-1 uppercase">{{ stat.label }}</div>
          </div>
        </div>
      </section>

      <section class="p-6 md:p-8">
        <div class="flex items-center justify-between border-b border-[#E5D7C0] pb-px mb-6 flex-wrap gap-4">
          <div class="flex gap-3">
            <button
              type="button"
              class="font-mason text-sm md:text-base pb-2.5 px-2 border-b-[3px] -mb-px flex items-center gap-1.5 transition-colors"
              :class="pestana === 'publicaciones' ? 'font-bold text-[#8B5A2B] border-[#D4AF37]' : 'font-semibold text-[#8B7D6B] hover:text-[#8B5A2B] border-transparent'"
              @click="pestana = 'publicaciones'"
            >
              Publicaciones
              <span class="font-tarzana text-xs px-1.5 py-0.5 rounded font-semibold" :class="pestana === 'publicaciones' ? 'bg-[#E6CA65]/30 text-[#523315]' : 'bg-stone-200/50 text-[#8B7D6B]'">({{ posts.length }})</span>
            </button>
            <button
              type="button"
              class="font-mason text-sm md:text-base pb-2.5 px-2 border-b-[3px] -mb-px flex items-center gap-1.5 transition-colors"
              :class="pestana === 'builds' ? 'font-bold text-[#8B5A2B] border-[#D4AF37]' : 'font-semibold text-[#8B7D6B] hover:text-[#8B5A2B] border-transparent'"
              @click="pestana = 'builds'"
            >
              Builds
              <span class="font-tarzana text-xs px-1.5 py-0.5 rounded font-semibold" :class="pestana === 'builds' ? 'bg-[#E6CA65]/30 text-[#523315]' : 'bg-stone-200/50 text-[#8B7D6B]'">({{ builds.length }})</span>
            </button>
          </div>
          <div class="flex items-center gap-2 text-xs font-tarzana">
            <label class="text-[#8B7D6B]" for="sortFilter">ORDEN:</label>
            <select
              id="sortFilter"
              v-model="orden"
              class="bg-[#FDF8EE] border border-[#E5D7C0] text-[#332517] text-xs rounded py-1 px-2.5 focus:outline-none focus:border-[#D4AF37] focus:ring-1 focus:ring-[#D4AF37]"
            >
              <option value="recientes">Más recientes</option>
              <option value="valorados">Mejor valorados</option>
              <option value="comentados">Más comentados</option>
            </select>
          </div>
        </div>

        <div v-if="cargando" class="space-y-4" role="status" aria-live="polite">
          <div v-for="n in 2" :key="n" class="card-parchment p-4 rounded-md animate-pulse space-y-3">
            <div class="h-4 bg-[#C2A980]/40 rounded w-24"></div>
            <div class="h-5 bg-[#C2A980]/40 rounded w-3/4"></div>
            <div class="h-3 bg-[#C2A980]/25 rounded w-full"></div>
          </div>
        </div>

        <div v-else-if="pestana === 'publicaciones'" class="space-y-6">
          <p v-if="posts.length === 0" class="py-12 text-center font-minion text-[#6B5B4B] italic">
            Todavía no publicaste nada en el tablón.
          </p>
          <article v-for="post in postsOrdenados" :key="post.id" class="bg-[#FCF6EB] border border-[#E5D7C0] rounded-md p-4 md:p-5 shadow-sm hover:border-[#D4AF37]/70 transition-colors">
            <div class="flex items-start gap-3 md:gap-4">
              <div class="flex flex-col items-center justify-center bg-[#F4EAD6] border border-[#E5D7C0] rounded px-2 py-2 min-w-[48px]">
                <span class="text-[#6B8E23]" aria-hidden="true">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path clip-rule="evenodd" fill-rule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" />
                  </svg>
                </span>
                <span class="font-mason font-bold text-sm text-[#332517] my-1">+{{ post.votos }}</span>
                <span class="text-[#8B7D6B]" aria-hidden="true">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path clip-rule="evenodd" fill-rule="evenodd" d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z" />
                  </svg>
                </span>
              </div>
              <div class="flex-grow min-w-0">
                <div class="flex items-center flex-wrap gap-2 text-xs font-tarzana mb-1">
                  <span class="px-2 py-0.5 border rounded font-bold text-[10px] uppercase" :class="etiquetaClase(post)">{{ post.etiqueta }}</span>
                  <span class="text-[#8B7D6B]">Publicado {{ post.tiempo }} por ti</span>
                </div>
                <h2 class="font-mason font-bold text-lg text-[#8B5A2B] leading-snug mb-2">{{ post.titulo }}</h2>
                <p class="font-minion text-[#332517] text-sm md:text-base leading-relaxed mb-3">{{ post.cuerpo }}</p>

                <div v-if="post.embed" class="bg-[#FDF8EE] border-2 border-dashed border-[#D4AF37]/70 rounded p-3 mb-3 flex items-center justify-between flex-wrap gap-3">
                  <div class="flex items-center gap-3 min-w-0">
                    <div class="w-8 h-8 rounded bg-[#2B2319] text-[#D4AF37] flex items-center justify-center font-mason font-bold text-xs border border-[#D4AF37] flex-shrink-0">
                      {{ post.embed.icono }}
                    </div>
                    <div class="min-w-0">
                      <div class="font-mason font-bold text-xs text-[#332517] truncate">{{ post.embed.eyebrow }}: {{ post.embed.titulo }}</div>
                      <div class="font-tarzana text-[10px] text-[#8B7D6B]">{{ post.embed.meta }}</div>
                    </div>
                  </div>
                  <button
                    type="button"
                    class="font-tarzana text-xs font-bold text-[#1A1A1A] bg-[#D4AF37] hover:bg-[#E6CA65] transition-colors px-3 py-1 rounded shadow-sm whitespace-nowrap"
                    @click="router.push(post.embed.ruta)"
                  >
                    {{ post.embed.boton }}
                  </button>
                </div>

                <div class="flex items-center gap-4 text-xs font-tarzana text-[#8B7D6B] pt-2 border-t border-[#E5D7C0]">
                  <span>{{ post.totalComentarios }} Comentarios</span>
                  <button type="button" class="hover:text-[#332517]" @click="toast.info('Enlace de la publicación copiado.')">Compartir</button>
                  <RouterLink to="/feed" class="text-[#8B5A2B] font-bold hover:underline">Ver en el feed →</RouterLink>
                </div>
              </div>
            </div>
          </article>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="build in builds" :key="build.id" class="bg-[#F4EAD6] border border-[#E5D7C0] rounded p-4 flex flex-col justify-between">
            <div>
              <div class="flex justify-between items-start gap-2 mb-2">
                <span class="font-mason font-bold text-sm text-[#8B5A2B]">{{ build.display || build.nombre }}</span>
                <span
                  class="font-tarzana text-[9px] font-bold px-2 py-0.5 border rounded whitespace-nowrap"
                  :class="esPublico(build) ? 'bg-[#6B8E23]/20 text-[#556B2F] border-[#6B8E23]/40' : 'bg-[#8B1A1A]/15 text-[#8B1A1A] border-[#8B1A1A]/40'"
                >
                  {{ esPublico(build) ? 'PÚBLICO' : 'PRIVADO / EN MESA' }}
                </span>
              </div>
              <div class="font-tarzana text-xs text-[#332517] font-semibold mb-1">
                {{ build.clase }} {{ build.raza }} Nvl {{ build.nivel }} • {{ build.arquetipo }}
              </div>
              <div class="text-xs font-minion text-[#8B7D6B] mb-3">Atributos: {{ atributosDe(build) }}</div>
              <div class="text-[11px] font-tarzana text-[#332517] bg-[#FDF8EE] p-2 rounded border border-[#E5D7C0]">
                Dotes: {{ dotesDe(build) }}
              </div>
            </div>
            <div class="mt-4 pt-2 border-t border-[#E5D7C0] flex justify-between items-center text-xs font-tarzana">
              <span class="text-[#8B7D6B] text-[10px]">{{ build.actualizado || 'Borrador sin actualizar' }}</span>
              <button type="button" class="font-bold text-[#8B5A2B] hover:underline" @click="router.push(`/builds/${build.id}`)">Abrir Ficha »</button>
            </div>
          </div>
        </div>

        <div v-if="!cargando" class="mt-10 pt-6 border-t border-[#E5D7C0]">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h3 class="font-mason font-bold text-base text-[#8B5A2B] tracking-wide">Compendio de Fichas Recientes</h3>
              <p class="font-minion text-xs text-[#8B7D6B] italic">Construcciones optimizadas según reglas OGL Pathfinder v1.0a</p>
            </div>
            <button type="button" class="font-tarzana text-xs font-bold text-[#8B5A2B] hover:underline flex items-center gap-1" @click="router.push('/builds')">
              Ver todas las {{ builds.length }} fichas <span>→</span>
            </button>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="build in compendio" :key="build.id" class="bg-[#F4EAD6] border border-[#E5D7C0] rounded p-4 flex flex-col justify-between">
              <div>
                <div class="flex justify-between items-start gap-2 mb-2">
                  <span class="font-mason font-bold text-sm text-[#8B5A2B]">{{ build.display || build.nombre }}</span>
                  <span
                    class="font-tarzana text-[9px] font-bold px-2 py-0.5 border rounded whitespace-nowrap"
                    :class="esPublico(build) ? 'bg-[#6B8E23]/20 text-[#556B2F] border-[#6B8E23]/40' : 'bg-[#8B1A1A]/15 text-[#8B1A1A] border-[#8B1A1A]/40'"
                  >
                    {{ esPublico(build) ? 'PÚBLICO' : 'PRIVADO / EN MESA' }}
                  </span>
                </div>
                <div class="font-tarzana text-xs text-[#332517] font-semibold mb-1">
                  {{ build.clase }} {{ build.raza }} Nvl {{ build.nivel }} • {{ build.arquetipo }}
                </div>
                <div class="text-xs font-minion text-[#8B7D6B] mb-3">Atributos: {{ atributosDe(build) }}</div>
                <div class="text-[11px] font-tarzana text-[#332517] bg-[#FDF8EE] p-2 rounded border border-[#E5D7C0]">
                  Dotes: {{ dotesDe(build) }}
                </div>
              </div>
              <div class="mt-4 pt-2 border-t border-[#E5D7C0] flex justify-between items-center text-xs font-tarzana">
                <span class="text-[#8B7D6B] text-[10px]">{{ build.actualizado || 'Borrador sin actualizar' }}</span>
                <button type="button" class="font-bold text-[#8B5A2B] hover:underline" @click="router.push(`/builds/${build.id}`)">Abrir Ficha »</button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <ModalCambioPassword :open="modalClave" @close="modalClave = false" />
  </main>
</template>
