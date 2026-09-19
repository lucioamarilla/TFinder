<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMisBuilds, getBuildsPublicos } from '@/services/builds.js'

const router = useRouter()

const pestaña = ref('mios')
const buscador = ref('')
const orden = ref('recientes')
const mios = ref([])
const publicos = ref([])
const cargando = ref(true)
const fallo = ref(null)

const ordenadoMios = computed(() => ordenar(mios.value))
const ordenadoPublicos = computed(() => ordenar(publicos.value))

const visibles = computed(() => {
  const base = pestaña.value === 'mios' ? ordenadoMios.value : ordenadoPublicos.value
  const termino = buscador.value.trim().toLowerCase()
  if (!termino) return base
  return base.filter((b) => `${b.nombre} ${b.clase} ${b.arquetipo} ${b.detalle}`.toLowerCase().includes(termino))
})

const MIS_SLOTS = 6

function ordenar(lista) {
  const copia = [...lista]
  if (orden.value === 'nivel') return copia.sort((a, b) => b.nivel - a.nivel)
  if (orden.value === 'valorados') return copia.sort((a, b) => b.favoritos - a.favoritos)
  return copia
}

const paletaAlineamiento = {
  verde: 'text-[#6B8E23]',
  rojo: 'text-[#8B1A1A]',
  neutral: 'text-[#6E4520]'
}

async function cargar() {
  cargando.value = true
  fallo.value = null
  try {
    const [mis, publ] = await Promise.all([getMisBuilds(), getBuildsPublicos()])
    mios.value = mis
    publicos.value = publ
  } catch (e) {
    fallo.value = e.message || 'No pudimos cargar la biblioteca de builds.'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
</script>

<template>
  <main class="flex-grow w-full max-w-7xl mx-auto px-6 py-8">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="font-mason text-2xl md:text-3xl font-bold text-[#8B5A2B] tracking-wide flex items-center gap-2">
          <span>✦</span> Mis Personajes
        </h1>
        <p class="font-minion text-base mt-1">
          Gestiona tus hojas de ruta tácticas, progresiones y arquetipos de Pathfinder 1e, o explora la biblioteca comunitaria.
        </p>
      </div>
      <button type="button" class="btn-gold-emboss self-start md:self-auto px-5 py-2.5 rounded text-[#1A1A1A] font-tarzana font-extrabold text-xs tracking-widest uppercase flex items-center space-x-2 transition-all" @click="router.push('/builds/nuevo')">
        <svg class="w-4 h-4 font-bold" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round"></path>
        </svg>
        <span>Crear Build</span>
      </button>
    </div>

    <div class="parchment-sheet rounded-sm p-6 relative border border-[#C2A980] bg-[#FBF4E6] shadow-sm">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[#C2A980] gap-4 pb-0 mb-6">
        <div class="flex items-center space-x-2">
          <button
            type="button"
            class="font-mason font-bold px-6 py-3 rounded-t-sm flex items-center space-x-2 shadow-sm transition-colors"
            :class="pestaña === 'mios' ? 'bg-[#FDF8EE] text-[#8B5A2B] border-t-2 border-x border-b-0 border-t-[#D4AF37] border-x-[#C2A980] relative -mb-[1px]' : 'bg-[#F5EAD9] hover:bg-[#ebd9bd] text-[#8B7D6B] hover:text-[#8B5A2B] border border-[#C2A980] border-b-0'"
            @click="pestaña = 'mios'"
          >
            <span class="tracking-wide">Mis Builds</span>
            <span class="bg-[#8B5A2B] text-[#FDF8EE] font-tarzana text-xs px-2 py-0.5 rounded-full font-bold">{{ mios.length }}</span>
          </button>
          <button
            type="button"
            class="font-mason font-medium px-6 py-3 rounded-t-sm flex items-center space-x-2 transition-colors"
            :class="pestaña === 'publicos' ? 'bg-[#FDF8EE] text-[#8B5A2B] border-t-2 border-x border-b-0 border-t-[#D4AF37] border-x-[#C2A980] relative -mb-[1px]' : 'bg-[#F5EAD9] hover:bg-[#ebd9bd] text-[#8B7D6B] hover:text-[#8B5A2B] border border-[#C2A980] border-b-0'"
            @click="pestaña = 'publicos'"
          >
            <span class="tracking-wide">Explorar Públicos</span>
            <span class="bg-[#C2A980] text-[#1A1A1A] font-tarzana text-xs px-2 py-0.5 rounded-full font-bold">{{ publicos.length }}</span>
          </button>
        </div>

        <div class="flex flex-wrap items-center gap-3 pb-2 sm:pb-0">
          <div class="relative min-w-[240px]">
            <input
              v-model="buscador"
              type="text"
              placeholder="Filtrar por nombre, clase, dote..."
              class="w-full bg-[#F5EAD9] border border-[#C2A980] text-xs font-minion placeholder-[#8B7D6B] py-1.5 pl-8 pr-3 rounded focus:outline-none focus:border-[#8B5A2B] focus:ring-1 focus:ring-[#8B5A2B] shadow-inner text-[#1A1A1A]"
            />
            <svg class="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-[#8B7D6B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
            </svg>
          </div>
          <select v-model="orden" class="bg-[#F5EAD9] border border-[#C2A980] text-xs font-tarzana py-1.5 px-3 rounded focus:outline-none focus:border-[#8B5A2B] text-[#4A3B2C]">
            <option value="recientes">Más recientes</option>
            <option value="nivel">Mayor nivel</option>
            <option value="valorados">Mejor valorados</option>
          </select>
        </div>
      </div>

      <div v-if="cargando" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5" role="status" aria-live="polite">
        <div v-for="n in 4" :key="n" class="card-parchment p-3.5 rounded animate-pulse space-y-3">
          <div class="h-4 bg-[#C2A980]/40 rounded w-16"></div>
          <div class="h-5 bg-[#C2A980]/40 rounded w-3/4"></div>
          <div class="h-3 bg-[#C2A980]/25 rounded w-1/2"></div>
          <div class="h-3 bg-[#C2A980]/25 rounded w-2/3"></div>
        </div>
      </div>

      <div v-else-if="fallo" class="py-16 text-center" role="alert">
        <p class="font-tarzana uppercase tracking-widest text-xs text-[#8B1A1A] font-bold mb-1">La biblioteca está oculta</p>
        <p class="font-minion text-[#5A4A3A]">{{ fallo }}</p>
        <button type="button" class="btn-gold mt-4 px-6 py-2 font-tarzana font-bold uppercase tracking-wider text-sm" @click="cargar">Reintentar</button>
      </div>

      <div v-else-if="visibles.length === 0" class="py-16 text-center">
        <p class="font-mason text-xl text-[#8B5A2B] font-bold">Ningún pergamino coincide</p>
        <p class="font-minion text-sm text-[#6B5B4B] italic mt-1">
          {{ pestaña === 'mios' ? 'Crea tu primer héroe o ajusta el filtro de búsqueda.' : 'La búsqueda no encontró builds públicos.' }}
        </p>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <article v-for="build in visibles" :key="build.id" class="card-parchment p-3.5 rounded flex flex-col justify-between relative shadow-sm">
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="bg-[#F4EAD9] border border-[#C2A980] text-[#8B5A2B] font-mason text-[11px] font-bold px-2 py-0.5 rounded">Nivel {{ build.nivel }}</span>
              <div class="flex items-center text-[#8B7D6B]" :title="build.privacidad === 'privado' || build.privacidad === 'borrador' ? 'Privado' : 'Público'">
                <svg v-if="build.privacidad === 'privado' || build.privacidad === 'borrador'" class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" stroke-linecap="round" stroke-linejoin="round"></path>
                </svg>
                <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                  <path d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"></path>
                </svg>
              </div>
            </div>
            <h2 class="font-mason text-[15px] font-bold text-[#8B5A2B] leading-snug">{{ build.display }}</h2>
            <p class="font-tarzana text-xs text-[#332517] font-semibold mt-0.5">{{ build.clase }} ({{ build.arquetipo }})</p>
            <p class="font-minion italic text-[11px] text-[#6B5B4B] mt-0.5">Por {{ build.autor }}</p>
            <div class="mt-3 pt-2.5 border-t border-[#E5D7C0] text-[11px] font-tarzana space-y-1">
              <div class="flex justify-between">
                <span class="text-[#8B7D6B]">ROL:</span>
                <span class="text-[#1A1A1A] font-bold">{{ build.rol }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-[#8B7D6B]">ALINEAMIENTO:</span>
                <span class="font-bold" :class="paletaAlineamiento[build.alineamientoColor] || 'text-[#6E4520]'">{{ build.alineamiento }}</span>
              </div>
            </div>
          </div>
          <div class="mt-4 pt-2 border-t border-[#E5D7C0] flex items-center justify-between">
            <span class="text-[10px] font-tarzana text-[#8B7D6B]">{{ build.actualizado }}</span>
            <button
              type="button"
              class="font-tarzana text-xs font-bold text-[#8B5A2B] hover:text-[#523315] inline-flex items-center gap-1 transition-colors"
              @click="router.push(`/builds/${build.id}`)"
            >
              <span v-if="build.privacidad === 'privado' || build.privacidad === 'borrador'">Editar Build</span>
              <span v-else>Ver Ficha</span> <span>→</span>
            </button>
          </div>
        </article>

        <RouterLink
          v-if="pestaña === 'mios' && mios.length < MIS_SLOTS"
          to="/builds/nuevo"
          class="border-2 border-dashed border-[#C2A980] hover:border-[#D4AF37] hover:bg-[#F9F2E2] p-5 rounded flex flex-col items-center justify-center text-center transition-all group min-h-[220px]"
        >
          <div class="w-12 h-12 rounded-full bg-[#EFE3CF] group-hover:bg-[#D4AF37] border border-[#C2A980] flex items-center justify-center text-[#8B5A2B] group-hover:text-[#1A1A1A] mb-3 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round"></path>
            </svg>
          </div>
          <span class="font-mason font-bold text-sm text-[#8B5A2B] group-hover:text-[#5A3815] tracking-wide">Crear Nuevo Build</span>
          <p class="font-minion text-xs text-[#8B7D6B] mt-1.5 max-w-[190px]">Importar desde Pathbuilder 1e o diseñar una progresión de niveles desde cero.</p>
        </RouterLink>
      </div>

      <div class="mt-8 pt-5 border-t border-[#C2A980] flex flex-col sm:flex-row items-center justify-between gap-4 font-tarzana text-xs tracking-wider">
        <span class="text-[#8B7D6B]">{{ visibles.length }} ficha{{ visibles.length === 1 ? '' : 's' }} · página 1 de 1</span>
        <span class="text-[#8B7D6B]">{{ pestaña === 'mios' ? `Slot de personaje: ${mios.length}/${MIS_SLOTS}` : 'Biblioteca comunitaria PF1e · OGL v1.0a' }}</span>
      </div>
    </div>
  </main>
</template>