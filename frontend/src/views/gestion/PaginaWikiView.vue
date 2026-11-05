<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from '@/composables/useToast.js'
import MesaGestionShell from '@/components/mesa/MesaGestionShell.vue'
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

const TIPOS_BADGE = { LUGAR: 'badge-place', NPC: 'badge-npc', CRIATURA: 'badge-creature', NOTA: 'badge-note' }

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
  <MesaGestionShell :mesa-id="mesaId">
    <div v-if="cargando" class="text-center py-16 font-tarzana text-xs uppercase tracking-widest text-[#8B7D6B]">
      Abriendo la página del código…
    </div>

    <div v-else-if="falta" class="text-center py-16 font-minion text-[#5C4A32]">
      Esta página fue borrada del grimorio.
      <RouterLink :to="`/mesas/${mesaId}/wiki`" class="block mt-3 font-tarzana font-bold text-[#8B5A2B] hover:underline">← Volver al Códice</RouterLink>
    </div>

    <div v-else-if="pagina" class="grid grid-cols-1 md:grid-cols-10 gap-6">
      <!-- Índice lateral -->
      <aside class="md:col-span-3">
        <div class="bg-[#F6EDDC] border border-[#C2A980] rounded p-4 sticky top-24">
          <h2 class="font-mason text-[1.05rem] font-bold text-[#8B5A2B] uppercase tracking-wide mb-3">Índice del Códice</h2>
          <div class="relative mb-3">
            <svg class="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-[#8B7D6B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
            <input
              v-model="busqueda"
              type="text"
              placeholder="Filtrar notas, lugares, PNJs..."
              class="w-full bg-[#FDF8EE] border border-[#C2A980] text-xs font-minion px-3 py-1.5 pl-8 rounded text-[#1A1A1A] placeholder-[#8B7D6B] focus:outline-none focus:border-[#8B5A2B]"
            />
          </div>
          <nav class="space-y-0.5 max-h-[520px] overflow-y-auto pr-1">
            <RouterLink
              v-for="p in indiceFiltrado"
              :key="p.id"
              :to="`/mesas/${mesaId}/wiki/${p.id}`"
              class="block px-2 py-1.5 text-[0.88rem] rounded transition border-l-2"
              :class="p.id === pagina.id
                ? 'bg-[#FDF8EE]/90 border-[#8B5A2B] text-[#8B5A2B] font-semibold'
                : 'border-transparent text-[#1A1A1A] hover:bg-[#FDF8EE]/80 hover:text-[#8B5A2B]'"
            >
              {{ p.titulo.split(' (')[0] }}
            </RouterLink>
          </nav>
        </div>
      </aside>

      <!-- Artículo -->
      <article class="md:col-span-7">
        <RouterLink
          :to="`/mesas/${mesaId}/wiki`"
          class="inline-flex items-center gap-1.5 font-tarzana text-xs font-bold text-[#8B5A2B] hover:text-[#5C3817] uppercase tracking-wider mb-3"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
          </svg>
          Volver a la Lista
        </RouterLink>

        <div class="flex flex-wrap items-center gap-2 mb-1">
          <span class="font-tarzana text-[0.7rem] px-2 py-0.5 rounded" :class="TIPOS_BADGE[pagina.tipo] || 'badge-note'">
            {{ pagina.tipo }}
          </span>
          <span class="font-tarzana text-xs text-[#8B7D6B]">Carpeta: {{ pagina.carpeta }}</span>
        </div>
        <h1 class="font-mason text-2xl md:text-3xl text-[#8B5A2B] font-bold tracking-wide mb-2">
          {{ pagina.titulo }}
        </h1>
        <p class="font-minion italic text-sm text-[#736351] mb-6">{{ pagina.resumen }}</p>

        <div class="space-y-5">
          <template v-for="(bloque, i) in pagina.contenido" :key="i">
            <p v-if="bloque.tipo === 'parrafo'" class="font-minion text-[1rem] text-[#1A1A1A] leading-relaxed">
              {{ bloque.texto }}
            </p>
            <h2 v-else-if="bloque.tipo === 'subtitle'" class="font-mason text-[1.4rem] text-[#8B5A2B] font-bold pt-2 border-b border-[#C2A980]/50 pb-1">
              {{ bloque.texto }}
            </h2>
            <p v-else-if="bloque.tipo === 'cita'" class="font-minion italic text-[0.95rem] text-[#5C4A32] border-l-4 border-[#C2A980] bg-[#F6EDDC]/60 pl-4 py-2 rounded-r">
              {{ bloque.texto }}
            </p>
            <div v-else-if="bloque.tipo === 'lista'">
              <h3 class="font-mason text-[1.1rem] text-[#8B5A2B] font-bold pt-1 mb-1.5">{{ bloque.titulo }}</h3>
              <ul class="list-disc pl-6 space-y-1 font-minion text-[0.98rem] text-[#1A1A1A]">
                <li v-for="(item, k) in bloque.items" :key="k">{{ item }}</li>
              </ul>
            </div>
          </template>
        </div>

        <div class="mt-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-4 border-t border-[#C2A980]/50">
          <span class="font-minion text-xs text-[#8B7D6B] italic">
            Última edición: <strong class="text-[#5C4A32]">{{ pagina.fecha }}</strong> por Aldren (GM)
          </span>
          <RouterLink
            :to="`/mesas/${mesaId}/wiki/${pagina.id}/editar`"
            class="btn-copper-outline px-4 py-2 rounded font-tarzana text-xs font-bold flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
            EDITAR PÁGINA
          </RouterLink>
        </div>

        <!-- Discusión -->
        <section class="mt-8">
          <h2 class="font-mason text-[1rem] font-bold text-[#8B5A2B] uppercase tracking-wider mb-3">
            Discusión del Códice ({{ comentarios.length }})
          </h2>
          <div class="space-y-3">
            <div v-for="(c, i) in comentarios" :key="i" class="flex gap-3 bg-[#FBF4E6] border border-[#E8DCC8] rounded p-3.5">
              <div class="w-8 h-8 rounded-full bg-[#8B5A2B] text-[#FDF8EE] flex items-center justify-center font-mason text-[0.65rem] font-bold shrink-0">
                {{ c.avatar }}
              </div>
              <div>
                <div class="text-xs font-tarzana font-bold text-[#8B5A2B]">
                  {{ c.autor }}
                  <span class="font-normal text-[#8B7D6B]">· {{ c.fecha }}</span>
                </div>
                <p class="text-sm font-minion text-[#1A1A1A] mt-0.5">{{ c.texto }}</p>
              </div>
            </div>

            <form class="flex gap-2" @submit.prevent="publicar">
              <input
                v-model="nuevoComentario"
                type="text"
                placeholder="Aporta una anotación al códice…"
                class="flex-1 bg-[#FDF8EE] border border-[#C2A980] text-sm font-minion px-3 py-2 rounded text-[#1A1A1A] placeholder-[#8B7D6B] focus:outline-none focus:border-[#8B5A2B]"
              />
              <button type="submit" class="btn-gold-emboss px-4 py-2 rounded font-tarzana text-xs font-bold">PUBLICAR</button>
            </form>
          </div>
        </section>
      </article>
    </div>
  </MesaGestionShell>
</template>