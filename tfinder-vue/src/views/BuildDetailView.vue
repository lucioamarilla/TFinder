<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast.js'
import { getBuild, vincularBuild } from '@/services/builds.js'
import { getMesas } from '@/services/mesas.js'
import ModalAsociarBuild from '@/components/modals/ModalAsociarBuild.vue'

const props = defineProps({ id: { type: String, required: true } })

const router = useRouter()
const toast = useToast()

const build = ref(null)
const mesas = ref([])
const cargando = ref(true)
const error = ref(null)
const megusta = ref(false)
const likes = ref(0)
const abrirAsociar = ref(false)

const campañaBanner = computed(() => {
  if (!build.value) return null
  if (build.value.ficha?.campaña) return build.value.ficha.campaña
  if (build.value.mesaId) {
    const mesa = mesas.value.find((m) => m.id === build.value.mesaId)
    if (mesa) return { nombre: mesa.nombre, enlazadoPor: '● Vincular Build' }
  }
  return null
})

async function cargar() {
  cargando.value = true
  error.value = null
  try {
    const [detalle, todas] = await Promise.all([getBuild(props.id), getMesas()])
    build.value = detalle
    mesas.value = todas.map((m) => ({ id: m.id, nombre: m.nombre, estado: m.estado }))
    likes.value = detalle.favoritos || 0
    megusta.value = false
  } catch (e) {
    error.value = e.message || 'No pudimos cargar la ficha.'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
watch(() => props.id, cargar)

function alternarMeGusta() {
  megusta.value = !megusta.value
  likes.value += megusta.value ? 1 : -1
  toast.ok(megusta.value ? '¡Te gusta este build!' : 'Me gusta retirado.')
}

async function vincular(mesaId) {
  abrirAsociar.value = false
  if (!mesaId) return
  const destino = mesas.value.find((m) => m.id === mesaId)
  const res = await vincularBuild(props.id, mesaId)
  build.value.mesaId = res.build.mesaId
  toast.ok(`Build vinculado a «${destino?.nombre || 'la mesa'}».`)
  if (res.mesaAnterior) toast.info(`Se desvinculó de la mesa anterior.`)
}
</script>

<template>
  <main class="flex-grow w-full max-w-7xl mx-auto px-6 py-8">
    <div v-if="cargando" class="py-16 flex flex-col items-center gap-4" role="status" aria-live="polite">
      <div class="animate-pulse space-y-3 w-full max-w-md">
        <div class="h-5 bg-[#C2A980]/40 rounded w-2/3"></div>
        <div class="h-3 bg-[#C2A980]/25 rounded w-full"></div>
        <div class="h-3 bg-[#C2A980]/25 rounded w-1/2"></div>
      </div>
      <p class="font-tarzana text-xs uppercase tracking-widest text-[#8B7D6B]">Cargando el pergamino del héroe...</p>
    </div>

    <div v-else-if="error" class="py-16 text-center" role="alert">
      <p class="font-tarzana uppercase tracking-widest text-xs text-[#8B1A1A] font-bold mb-1">Ficha no encontrada</p>
      <p class="font-minion text-[#5A4A3A]">{{ error }}</p>
      <RouterLink to="/builds" class="btn-copper-outline inline-block mt-5 px-5 py-2 font-tarzana font-bold uppercase tracking-wider text-sm">← Volver a la biblioteca</RouterLink>
    </div>

    <template v-else-if="build">
      <div class="mb-4 flex flex-col sm:flex-row sm:items-center gap-2 justify-between">
        <RouterLink to="/builds" class="inline-flex items-center gap-1.5 font-tarzana text-xs font-bold text-[#8B5A2B] hover:text-[#5C3817] uppercase tracking-wider">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
          </svg>
          VOLVER AL LISTADO
        </RouterLink>
        <RouterLink :to="`/builds/${build.id}/historial`" class="font-tarzana text-xs font-bold text-[#8B5A2B] hover:underline uppercase tracking-wider">
          Historial y versionado →
        </RouterLink>
      </div>

      <div class="relative bg-[#FDF8EE] border-2 border-[#C2A980] rounded-sm p-6 md:p-8 shadow-xl">
        <div class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-[#8B5A2B]"></div>
        <div class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-[#8B5A2B]"></div>
        <div class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-[#8B5A2B]"></div>
        <div class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-[#8B5A2B]"></div>

        <div class="border-b border-[#C2A980]/70 pb-3 mb-4">
          <h1 class="font-mason text-[1.8rem] text-[#8B5A2B] font-bold leading-tight tracking-wide uppercase">
            {{ build.display }}
          </h1>
          <div class="font-tarzana text-[1rem] text-[#1A1A1A] font-bold tracking-wide mt-1 flex flex-wrap items-center gap-2">
            <span>{{ build.clase }} {{ build.raza }}</span>
            <span class="text-[#8B5A2B]">•</span>
            <span class="bg-[#F5EFE0] px-2 py-0.5 border border-[#C2A980] rounded text-xs text-[#8B5A2B]">Nivel {{ build.nivel }}</span>
            <span class="text-[#8B5A2B]">•</span>
            <span class="text-[#6E4520] italic font-semibold">{{ build.arquetipo }}</span>
          </div>
          <div class="font-minion italic text-xs text-[#6B5B4B] mt-1 flex flex-wrap items-center justify-between gap-2">
            <span>Alineamiento: {{ build.alineamiento === 'CB' ? 'Caótico Bueno' : build.alineamiento }}</span>
            <span>Deidad: {{ build.ficha?.deidad || 'Sin deidad asignada' }}</span>
          </div>
        </div>

        <div v-if="!build.ficha" class="grid grid-cols-1 md:grid-cols-[35%_1fr] gap-6">
          <div class="max-w-sm">
            <div class="font-tarzana text-xs uppercase tracking-widest text-[#8B5A2B] font-bold mb-2">Rol Táctico</div>
            <div class="bg-[#F5EFE0] border border-[#C2A980] rounded-sm p-4 space-y-2 text-xs font-tarzana">
              <div class="flex justify-between"><span class="text-[#8B7D6B]">ROL:</span><strong class="text-[#1A1A1A]">{{ build.rol }}</strong></div>
              <div class="flex justify-between"><span class="text-[#8B7D6B]">ALINEAMIENTO:</span><strong>{{ build.alineamiento }}</strong></div>
              <div class="flex justify-between"><span class="text-[#8B7D6B]">PRIVACIDAD:</span><strong class="uppercase">{{ build.privacidad }}</strong></div>
            </div>
          </div>
          <div class="space-y-4">
            <p class="font-minion text-[#4A3E31] italic">{{ build.detalle }}</p>
            <div class="bg-[#F5EFE0] border-l-2 border-[#8B5A2B] p-3 text-xs font-minion text-[#4A3E31] italic">
              La ficha OGL completa de este personaje aún no se ha publicado. Podés editarlo para completar dotes, conjuros y equipo táctico.
            </div>
          </div>
        </div>

        <div v-else class="grid grid-cols-1 lg:grid-cols-[35%_1fr] gap-6">
          <aside class="w-full">
            <div class="font-tarzana text-[0.75rem] uppercase tracking-widest text-[#8B5A2B] font-bold mb-2">
              Puntuaciones de Característica
            </div>
            <div class="grid grid-cols-6 gap-2 bg-[#F5EFE0] p-2.5 border border-[#C2A980] rounded-sm">
              <div v-for="rasgo in build.ficha.rasgos" :key="rasgo.etiqueta" class="flex flex-col items-center text-center min-w-0">
                <span class="font-tarzana text-[0.8rem] text-[#8B5A2B] font-bold uppercase leading-none">{{ rasgo.etiqueta }}</span>
                <span class="font-mason text-[1.5rem] text-[#1A1A1A] font-black leading-none my-1">{{ rasgo.valor }}</span>
                <span class="font-tarzana text-[0.7rem] text-[#6E4520] font-bold leading-none mb-1">{{ rasgo.mod }}</span>
                <div class="w-full stat-bar-bg h-1.5 rounded-full overflow-hidden">
                  <div class="stat-bar-fill h-full" :style="{ width: rasgo.ancho + '%' }"></div>
                </div>
              </div>
            </div>

            <div class="ogl-divider"><div class="ogl-divider-header">DEFENSA</div><div class="ogl-divider-line"></div></div>
            <div class="space-y-1.5 text-xs font-minion text-[#1A1A1A]">
              <div>
                <strong class="font-tarzana font-bold text-[#8B5A2B] uppercase">CA:</strong>
                <span class="font-semibold text-sm">{{ build.ficha.defensa.ca }}</span>, {{ build.ficha.defensa.caDetalle }}
              </div>
              <div>
                <strong class="font-tarzana font-bold text-[#8B5A2B] uppercase">PG:</strong>
                <span class="font-semibold text-sm text-[#8B1A1A]">{{ build.ficha.defensa.pg }}</span> ({{ build.ficha.defensa.pgDetalle }})
              </div>
              <div class="flex justify-between items-center bg-[#F5EFE0] px-2 py-1 border border-[#C2A980] rounded">
                <span class="font-tarzana font-bold text-[#8B5A2B]">SALVACIONES:</span>
                <div class="space-x-3 font-tarzana text-xs">
                  <span v-for="s in build.ficha.defensa.salvaciones" :key="s.sigla"><strong>{{ s.sigla }}</strong> {{ s.valor }}</span>
                </div>
              </div>
              <div class="text-[11px] text-[#6B5B4B] italic">
                <strong>Capacidades defensivas:</strong> {{ build.ficha.defensa.capacidades }}
              </div>
            </div>

            <div class="ogl-divider"><div class="ogl-divider-header">ATAQUE</div><div class="ogl-divider-line"></div></div>
            <div class="space-y-1.5 text-xs font-minion text-[#1A1A1A]">
              <div><strong class="font-tarzana font-bold text-[#8B5A2B] uppercase">Velocidad:</strong> {{ build.ficha.ataque.velocidad }}</div>
              <div>
                <strong class="font-tarzana font-bold text-[#8B5A2B] uppercase">Cuerpo a cuerpo (Principal):</strong>
                <span class="font-semibold">{{ build.ficha.ataque.cuerpo.arma }}</span> {{ build.ficha.ataque.cuerpo.bonificador }} ({{ build.ficha.ataque.cuerpo.daño }})
              </div>
              <div>
                <strong class="font-tarzana font-bold text-[#8B5A2B] uppercase">Dos Armas:</strong>
                {{ build.ficha.ataque.dosArmas.principal.arma }} {{ build.ficha.ataque.dosArmas.principal.bonificador }} ({{ build.ficha.ataque.dosArmas.principal.daño }}) y {{ build.ficha.ataque.dosArmas.secundaria.arma }} {{ build.ficha.ataque.dosArmas.secundaria.bonificador }} ({{ build.ficha.ataque.dosArmas.secundaria.daño }})
              </div>
              <div>
                <strong class="font-tarzana font-bold text-[#8B5A2B] uppercase">A distancia:</strong>
                {{ build.ficha.ataque.distancia.arma }} {{ build.ficha.ataque.distancia.bonificador }} ({{ build.ficha.ataque.distancia.daño }})
              </div>
              <div class="text-[11px] text-[#6B5B4B] italic">{{ build.ficha.ataque.especiales }}</div>
            </div>

            <div class="ogl-divider"><div class="ogl-divider-header">ESTADÍSTICAS</div><div class="ogl-divider-line"></div></div>
            <div class="space-y-1.5 text-xs font-minion text-[#1A1A1A]">
              <div class="grid grid-cols-2 gap-2 bg-[#F5EFE0] p-1.5 border border-[#C2A980] rounded">
                <div><strong class="font-tarzana font-bold text-[#8B5A2B]">Ataque Base (BAB):</strong> {{ build.ficha.estadisticas.bab }}</div>
                <div><strong class="font-tarzana font-bold text-[#8B5A2B]">BMC:</strong> {{ build.ficha.estadisticas.bmc }} | <strong class="font-tarzana font-bold text-[#8B5A2B]">DMC:</strong> {{ build.ficha.estadisticas.dmc }}</div>
              </div>
              <div><strong class="font-tarzana font-bold text-[#8B5A2B] uppercase">Iniciativa:</strong> {{ build.ficha.estadisticas.iniciativa }}</div>
              <div><strong class="font-tarzana font-bold text-[#8B5A2B] uppercase">Sentidos:</strong> {{ build.ficha.estadisticas.sentidos }}</div>
              <div><strong class="font-tarzana font-bold text-[#8B5A2B] uppercase">Idiomas:</strong> {{ build.ficha.estadisticas.idiomas }}</div>
              <div class="pt-2 border-t border-[#C2A980]/60 text-[11px] text-[#6B5B4B] flex justify-between items-center">
                <span>ID de Build: {{ build.ficha.idBuild }}</span>
                <span class="text-[#6B8E23] font-tarzana font-bold">● Compatible Bestiario OGL</span>
              </div>
            </div>
          </aside>

          <section class="w-full space-y-5">
            <div class="bg-[#FDF8EE] border-2 border-[#C2A980] rounded-sm p-4 shadow-md flex flex-wrap items-center justify-between gap-4">
              <div class="flex flex-wrap items-center gap-3">
                <button type="button" class="btn-bronze px-4 py-2 rounded text-xs font-tarzana font-bold tracking-wider uppercase flex items-center space-x-2" @click="router.push(`/builds/${build.id}/editar`)">
                  <svg class="w-4 h-4 text-[#FDF8EE]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                  <span>Editar</span>
                </button>
                <button type="button" class="btn-gold-relief px-4 py-2 rounded text-xs font-tarzana font-extrabold tracking-wider uppercase flex items-center space-x-2" @click="router.push('/feed/nuevo')">
                  <svg class="w-4 h-4 text-[#1A1A1A]" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z"></path>
                  </svg>
                  <span>Publicar en Feed</span>
                </button>
                <button type="button" class="btn-bronze px-4 py-2 rounded text-xs font-tarzana font-bold tracking-wider uppercase flex items-center space-x-2" @click="abrirAsociar = true">
                  <svg class="w-4 h-4 text-[#FDF8EE]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
                  </svg>
                  <span>{{ build.mesaId ? 'Cambiar Mesa' : 'Asociar a Mesa' }}</span>
                </button>
              </div>

              <button type="button" class="btn-like px-3.5 py-2 rounded flex items-center space-x-2.5 shadow-sm group" :class="{ 'sim-votado': megusta }" @click="alternarMeGusta">
                <svg class="w-5 h-5 text-[#8B5A2B] group-hover:scale-110 transition-transform" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"></path>
                </svg>
                <span class="font-tarzana text-xs font-bold text-[#8B5A2B] uppercase tracking-wider">Me gusta</span>
                <span class="font-mason text-[1.15rem] font-bold text-[#1A1A1A] pl-1 border-l border-[#C2A980]">{{ likes }}</span>
              </button>
            </div>

            <div class="bg-[#FDF8EE] border-2 border-[#C2A980] rounded-sm p-5 shadow-md">
              <div class="flex items-center justify-between border-b border-[#C2A980] pb-2 mb-3">
                <h2 class="font-mason text-lg text-[#8B5A2B] font-bold tracking-wide flex items-center gap-2">
                  <span>✦</span> DOTES SELECCIONADAS ({{ build.ficha.dotes.length }})
                </h2>
                <span class="font-tarzana text-xs text-[#8B7D6B] uppercase">Progresión Nivel {{ build.nivel }} {{ build.clase }}</span>
              </div>
              <div class="flex flex-wrap gap-2.5">
                <div v-for="dote in build.ficha.dotes" :key="dote.nombre" class="pf-tag px-3 py-1.5 rounded text-xs font-tarzana flex items-center space-x-2 shadow-xs cursor-pointer">
                  <span class="font-bold text-[#8B5A2B]">{{ dote.nombre }}</span>
                  <span class="text-[10px] bg-[#E8DCC8] px-1.5 py-0.2 rounded text-[#1A1A1A]">{{ dote.fuente }}</span>
                </div>
              </div>
              <div class="mt-3 bg-[#F5EFE0] p-2.5 border-l-2 border-[#8B5A2B] text-xs font-minion text-[#4A3E31] italic">
                <strong>Estrategia táctica:</strong> {{ build.ficha.estrategia }}
              </div>
            </div>

            <div class="bg-[#FDF8EE] border-2 border-[#C2A980] rounded-sm p-5 shadow-md">
              <div class="flex items-center justify-between border-b border-[#C2A980] pb-2 mb-3">
                <h2 class="font-mason text-lg text-[#8B5A2B] font-bold tracking-wide flex items-center gap-2">
                  <span>✦</span> CONJUROS, RUNAS &amp; APTITUDES MÁGICAS
                </h2>
                <span class="font-tarzana text-xs text-[#8B7D6B] uppercase">Capacidades Arcanas / Objetos Activables</span>
              </div>
              <p class="font-minion text-xs text-[#6B5B4B] italic mb-3">{{ build.ficha.magia.intro }}</p>
              <div class="flex flex-wrap gap-2.5">
                <div v-for="item in build.ficha.magia.items" :key="item.nombre" class="pf-tag px-3 py-1.5 rounded text-xs font-tarzana flex items-center space-x-2 shadow-xs">
                  <span class="font-bold" :class="item.destacado ? 'text-[#8B1A1A]' : 'text-[#8B5A2B]'">{{ item.nombre }}</span>
                  <span class="text-[10px] bg-[#E8DCC8] px-1.5 py-0.5 rounded text-[#1A1A1A]">{{ item.fuente }}</span>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div class="bg-[#FDF8EE] border-2 border-[#C2A980] rounded-sm p-5 shadow-md flex flex-col justify-between">
                <div>
                  <div class="flex items-center justify-between border-b border-[#C2A980] pb-2 mb-3">
                    <h2 class="font-mason text-lg text-[#8B5A2B] font-bold tracking-wide flex items-center gap-2">
                      <span>✦</span> EQUIPO TÁCTICO
                    </h2>
                    <span class="font-tarzana text-xs text-[#8B7D6B] uppercase">{{ build.ficha.pesoCarga }}</span>
                  </div>
                  <ul class="font-minion text-sm text-[#1A1A1A] space-y-2 divide-y divide-[#C2A980]/30">
                    <li v-for="pieza in build.ficha.equipo" :key="pieza.nombre" class="pt-1 flex items-start justify-between gap-3">
                      <div>
                        <span class="font-bold text-[#8B5A2B]">{{ pieza.nombre }}</span>
                        <p class="text-xs text-[#6B5B4B] italic">{{ pieza.detalle }}</p>
                      </div>
                      <span class="font-tarzana text-xs font-bold text-[#1A1A1A] shrink-0">{{ pieza.precio }}</span>
                    </li>
                  </ul>
                </div>
                <div class="mt-4 pt-2 border-t border-[#C2A980] flex justify-between items-center text-xs font-tarzana text-[#6B5B4B]">
                  <span>Riqueza líquida: <strong>{{ build.ficha.riquezaLiquida }}</strong></span>
                  <span class="text-[#8B5A2B] font-bold">Valor Total: {{ build.ficha.valorTotal }}</span>
                </div>
              </div>

              <div class="bg-[#FDF8EE] border-2 border-[#C2A980] rounded-sm p-5 shadow-md flex flex-col justify-between">
                <div>
                  <div class="flex items-center justify-between border-b border-[#C2A980] pb-2 mb-3">
                    <h2 class="font-mason text-lg text-[#8B5A2B] font-bold tracking-wide flex items-center gap-2">
                      <span>✦</span> HABILIDADES DE CLASE
                    </h2>
                    <span class="font-tarzana text-xs text-[#8B7D6B] uppercase">Rangos invertidos: {{ build.ficha.rangos }}</span>
                  </div>
                  <ul class="font-minion text-sm text-[#1A1A1A] space-y-2 divide-y divide-[#C2A980]/30">
                    <li v-for="hab in build.ficha.habilidades" :key="hab.nombre" class="pt-1 flex items-center justify-between">
                      <div class="flex items-center space-x-2">
                        <span class="w-1.5 h-1.5 bg-[#8B5A2B] rounded-full"></span>
                        <span class="font-semibold">{{ hab.nombre }}</span>
                        <span class="text-[11px] text-[#8B7D6B] italic">{{ hab.abrev }}</span>
                      </div>
                      <span class="font-tarzana font-bold text-sm text-[#1A1A1A] bg-[#F5EFE0] px-2 py-0.5 border border-[#C2A980] rounded">{{ hab.valor }}</span>
                    </li>
                  </ul>
                </div>
                <div class="mt-4 pt-2 border-t border-[#C2A980] text-[11px] text-[#6B5B4B] italic">{{ build.ficha.penalizadorArmadura }}</div>
              </div>
            </div>

            <div class="bg-[#FDF8EE] border border-[#C2A980] rounded-sm p-4 text-xs font-minion text-[#4A3E31] flex flex-wrap items-center justify-between gap-3 shadow-xs">
              <div class="flex items-center space-x-3">
                <span class="font-tarzana font-bold text-[#8B5A2B] uppercase">Campaña Activa:</span>
                <template v-if="campañaBanner">
                  <span class="bg-[#F5EFE0] px-2.5 py-1 border border-[#C2A980] rounded text-[#1A1A1A] font-semibold">{{ campañaBanner.nombre }}</span>
                  <span class="text-[#6B8E23] font-tarzana font-bold">{{ campañaBanner.enlazadoPor }}</span>
                </template>
                <span v-else class="text-[#8B7D6B] italic">Sin campaña vinculada todavía.</span>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-[#8B7D6B]">Creado por:</span>
                <strong class="font-tarzana text-[#1A1A1A]">{{ build.autor }}</strong>
                <span class="text-[#8B7D6B]">• Actualizado {{ build.historial[0]?.fecha || 'hace un momento' }}</span>
              </div>
            </div>
          </section>
        </div>
      </div>
    </template>

    <ModalAsociarBuild
      :open="abrirAsociar"
      :build="{ nombre: `${build?.nombre} (${build?.clase} Nvl ${build?.nivel})` }"
      :mesas="mesas"
      @close="abrirAsociar = false"
      @accepted="vincular"
    />
  </main>
</template>