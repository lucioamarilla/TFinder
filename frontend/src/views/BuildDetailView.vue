<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast.js'
import { getBuild, vincularBuild } from '@/services/builds.js'
import { getMesas } from '@/services/mesas.js'
import { wikiApi } from '@/api/endpoints.js'
import { feedApi } from '@/api/endpoints.js'
import { useAuth } from '@/composables/useAuth.js'
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

async function vincular(mesaId) {
 if (!build.value) return
 try {
 const salida = await vincularBuild(build.value.id, mesaId)
 if (salida?.build) build.value = salida.build
 toast.ok('Build vinculado a la mesa.')
 } catch (e) {
 toast.error(e?.message || 'No se pudo vincular el build.')
 } finally {
 abrirAsociar.value = false
 }
}

function alternarMeGusta() {
 megusta.value = !megusta.value
 likes.value += megusta.value ? 1 : -1
 toast.ok(megusta.value ? '¡Te gusta este build!' : 'Me gusta retirado.')
}

async function agregarAWiki() {
 if (!build.value?.mesaId) {
 toast.error('Vinculá el build a una mesa primero para agregarlo a su wiki.')
 return
 }
 try {
 await wikiApi.crear(build.value.mesaId, {
 titulo: build.value.nombre || build.value.display,
 tipo: 'Nota',
 cuerpo: build.value.detalle || '',
 visibilidad: 'jugadores'
 })
 toast.ok('Build agregado a la wiki de la campaña.')
 } catch (e) {
 toast.error(e?.mensaje || e?.message || 'No se pudo agregar a la wiki.')
 }
}

async function publicarEnForo() {
 if (build.value?.privacidad !== 'publico') {
 toast.error('Solo los builds públicos se pueden publicar en el foro.')
 return
 }
 try {
 await feedApi.crear({
 titulo: build.value.nombre || build.value.display,
 cuerpo: build.value.detalle || '',
 tipo: 'build',
 embed: { build_id: build.value.id }
 })
 toast.ok('Build publicado en el foro.')
 } catch (e) {
 toast.error(e?.mensaje || e?.message || 'No se pudo publicar en el foro.')
 }
}

function ponerEnBitacora() {
 toast.info('Creá una sesión en la mesa y anotá el build desde la bitácora de esa sesión.')
}
</script>

<template>
 <div class="app-grid">
    <main class="stack">
 <div v-if="cargando" class="py-16 flex flex-col items-center gap-4" role="status" aria-live="polite">
 <div class="animate-pulse space-y-3 w-full max-w-md">
 <div class="h-5 bg-[#C2A980]/40 rounded w-2/3"></div>
 <div class="h-3 bg-[#C2A980]/25 rounded w-full"></div>
 <div class="h-3 bg-[#C2A980]/25 rounded w-1/2"></div>
 </div>
 <p class=" text-xs uppercase tracking-widest text-[var(--color-muted)]">Cargando el pergamino del héroe...</p>
 </div>

 <div v-else-if="error" class="py-16 text-center" role="alert">
 <p class=" uppercase tracking-widest text-xs text-[var(--color-error)] font-bold mb-1">Ficha no encontrada</p>
 <p class=" text-[var(--color-muted)]">{{ error }}</p>
 <RouterLink to="/builds" class="btn-copper-outline inline-block mt-5 px-5 py-2 font-bold uppercase tracking-wider text-sm">← Volver a la biblioteca</RouterLink>
 </div>

 <template v-else-if="build">
 <div class="mb-4 flex flex-col sm:flex-row sm:items-center gap-2 justify-between">
 <RouterLink to="/builds" class="inline-flex items-center gap-1.5 text-xs font-bold text-[var(--color-accent)] hover:text-[#5C3817] uppercase tracking-wider">
 <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
 </svg>
 VOLVER AL LISTADO
 </RouterLink>
 <RouterLink :to="`/builds/${build.id}/historial`" class=" text-xs font-bold text-[var(--color-accent)] hover:underline uppercase tracking-wider">
 Historial y versionado →
 </RouterLink>
 </div>

 <div class="relative bg-[var(--color-paper-2)] border-2 border-[var(--color-rule)] rounded-sm p-6 md:p-8 shadow-xl">
 <div class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-[var(--color-accent)]"></div>
 <div class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-[var(--color-accent)]"></div>
 <div class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-[var(--color-accent)]"></div>
 <div class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-[var(--color-accent)]"></div>

 <div class="border-b border-[var(--color-rule)]/70 pb-3 mb-4">
 <h1 class=" text-[1.8rem] text-[var(--color-accent)] font-bold leading-tight tracking-wide uppercase">
 {{ build.display }}
 </h1>
 <div class=" text-[1rem] text-[var(--color-ink)] font-bold tracking-wide mt-1 flex flex-wrap items-center gap-2">
 <span>{{ build.clase }} {{ build.raza }}</span>
 <span class="text-[var(--color-accent)]">•</span>
 <span class="bg-[var(--color-paper)] px-2 py-0.5 border border-[var(--color-rule)] rounded text-xs text-[var(--color-accent)]">Nivel {{ build.nivel }}</span>
 <span class="text-[var(--color-accent)]">•</span>
 <span class="text-[var(--color-muted)] italic font-semibold">{{ build.arquetipo }}</span>
 </div>
 <div class=" italic text-xs text-[var(--color-muted)] mt-1 flex flex-wrap items-center justify-between gap-2">
 <span>Alineamiento: {{ build.alineamiento === 'CB' ? 'Caótico Bueno' : build.alineamiento }}</span>
 <span>Deidad: {{ build.ficha?.deidad || 'Sin deidad asignada' }}</span>
 </div>
 </div>

 <div v-if="!build.ficha" class="grid grid-cols-1 md:grid-cols-[35%_1fr] gap-6">
 <div class="max-w-sm">
 <div class=" text-xs uppercase tracking-widest text-[var(--color-accent)] font-bold mb-2">Rol Táctico</div>
 <div class="bg-[var(--color-paper)] border border-[var(--color-rule)] rounded-sm p-4 space-y-2 text-xs ">
 <div class="flex justify-between"><span class="text-[var(--color-muted)]">ROL:</span><strong class="text-[var(--color-ink)]">{{ build.rol }}</strong></div>
 <div class="flex justify-between"><span class="text-[var(--color-muted)]">ALINEAMIENTO:</span><strong>{{ build.alineamiento }}</strong></div>
 <div class="flex justify-between"><span class="text-[var(--color-muted)]">PRIVACIDAD:</span><strong class="uppercase">{{ build.privacidad }}</strong></div>
 </div>
 </div>
 <div class="space-y-4">
 <p class=" text-[var(--color-ink)] italic">{{ build.detalle }}</p>
 <div class="bg-[var(--color-paper)] border-l-2 border-[var(--color-accent)] p-3 text-xs text-[var(--color-ink)] italic">
 La ficha OGL completa de este personaje aún no se ha publicado. Podés editarlo para completar dotes, conjuros y equipo táctico.
 </div>
 </div>
 </div>

 <div v-else class="grid grid-cols-1 lg:grid-cols-[35%_1fr] gap-6">
 <aside class="w-full">
 <div class=" text-[0.75rem] uppercase tracking-widest text-[var(--color-accent)] font-bold mb-2">
 Puntuaciones de Característica
 </div>
 <div class="grid grid-cols-6 gap-2 bg-[var(--color-paper)] p-2.5 border border-[var(--color-rule)] rounded-sm">
 <div v-for="rasgo in build.ficha.rasgos" :key="rasgo.etiqueta" class="flex flex-col items-center text-center min-w-0">
 <span class=" text-[0.8rem] text-[var(--color-accent)] font-bold uppercase leading-none">{{ rasgo.etiqueta }}</span>
 <span class=" text-[1.5rem] text-[var(--color-ink)] font-black leading-none my-1">{{ rasgo.valor }}</span>
 <span class=" text-[0.7rem] text-[var(--color-muted)] font-bold leading-none mb-1">{{ rasgo.mod }}</span>
 <div class="w-full stat-bar-bg h-1.5 rounded-full overflow-hidden">
 <div class="stat-bar-fill h-full" :style="{ width: rasgo.ancho + '%' }"></div>
 </div>
 </div>
 </div>

 <div class="ogl-divider"><div class="ogl-divider-header">DEFENSA</div><div class="ogl-divider-line"></div></div>
 <div class="space-y-1.5 text-xs text-[var(--color-ink)]">
 <div>
 <strong class=" font-bold text-[var(--color-accent)] uppercase">CA:</strong>
 <span class="font-semibold text-sm">{{ build.ficha.defensa.ca }}</span>, {{ build.ficha.defensa.caDetalle }}
 </div>
 <div>
 <strong class=" font-bold text-[var(--color-accent)] uppercase">PG:</strong>
 <span class="font-semibold text-sm text-[var(--color-error)]">{{ build.ficha.defensa.pg }}</span> ({{ build.ficha.defensa.pgDetalle }})
 </div>
 <div class="flex justify-between items-center bg-[var(--color-paper)] px-2 py-1 border border-[var(--color-rule)] rounded">
 <span class=" font-bold text-[var(--color-accent)]">SALVACIONES:</span>
 <div class="space-x-3 text-xs">
 <span v-for="s in build.ficha.defensa.salvaciones" :key="s.sigla"><strong>{{ s.sigla }}</strong> {{ s.valor }}</span>
 </div>
 </div>
 <div class="text-[11px] text-[var(--color-muted)] italic">
 <strong>Capacidades defensivas:</strong> {{ build.ficha.defensa.capacidades }}
 </div>
 </div>

 <div class="ogl-divider"><div class="ogl-divider-header">ATAQUE</div><div class="ogl-divider-line"></div></div>
 <div class="space-y-1.5 text-xs text-[var(--color-ink)]">
 <div><strong class=" font-bold text-[var(--color-accent)] uppercase">Velocidad:</strong> {{ build.ficha.ataque.velocidad }}</div>
 <div>
 <strong class=" font-bold text-[var(--color-accent)] uppercase">Cuerpo a cuerpo (Principal):</strong>
 <span class="font-semibold">{{ build.ficha.ataque.cuerpo.arma }}</span> {{ build.ficha.ataque.cuerpo.bonificador }} ({{ build.ficha.ataque.cuerpo.daño }})
 </div>
 <div>
 <strong class=" font-bold text-[var(--color-accent)] uppercase">Dos Armas:</strong>
 {{ build.ficha.ataque.dosArmas.principal.arma }} {{ build.ficha.ataque.dosArmas.principal.bonificador }} ({{ build.ficha.ataque.dosArmas.principal.daño }}) y {{ build.ficha.ataque.dosArmas.secundaria.arma }} {{ build.ficha.ataque.dosArmas.secundaria.bonificador }} ({{ build.ficha.ataque.dosArmas.secundaria.daño }})
 </div>
 <div>
 <strong class=" font-bold text-[var(--color-accent)] uppercase">A distancia:</strong>
 {{ build.ficha.ataque.distancia.arma }} {{ build.ficha.ataque.distancia.bonificador }} ({{ build.ficha.ataque.distancia.daño }})
 </div>
 <div class="text-[11px] text-[var(--color-muted)] italic">{{ build.ficha.ataque.especiales }}</div>
 </div>

 <div class="ogl-divider"><div class="ogl-divider-header">ESTADÍSTICAS</div><div class="ogl-divider-line"></div></div>
 <div class="space-y-1.5 text-xs text-[var(--color-ink)]">
 <div class="grid grid-cols-2 gap-2 bg-[var(--color-paper)] p-1.5 border border-[var(--color-rule)] rounded">
 <div><strong class=" font-bold text-[var(--color-accent)]">Ataque Base (BAB):</strong> {{ build.ficha.estadisticas.bab }}</div>
 <div><strong class=" font-bold text-[var(--color-accent)]">BMC:</strong> {{ build.ficha.estadisticas.bmc }} | <strong class=" font-bold text-[var(--color-accent)]">DMC:</strong> {{ build.ficha.estadisticas.dmc }}</div>
 </div>
 <div><strong class=" font-bold text-[var(--color-accent)] uppercase">Iniciativa:</strong> {{ build.ficha.estadisticas.iniciativa }}</div>
 <div><strong class=" font-bold text-[var(--color-accent)] uppercase">Sentidos:</strong> {{ build.ficha.estadisticas.sentidos }}</div>
 <div><strong class=" font-bold text-[var(--color-accent)] uppercase">Idiomas:</strong> {{ build.ficha.estadisticas.idiomas }}</div>
 <div class="pt-2 border-t border-[var(--color-rule)]/60 text-[11px] text-[var(--color-muted)] flex justify-between items-center">
 <span>ID de Build: {{ build.ficha.idBuild }}</span>
 <span class="text-[var(--color-success,#6B8E23)] font-bold">● Compatible Bestiario OGL</span>
 </div>
 </div>
 </aside>

 <section class="w-full space-y-5">
 <div class="bg-[var(--color-paper-2)] border-2 border-[var(--color-rule)] rounded-sm p-4 shadow-md flex flex-wrap items-center justify-between gap-4">
 <div class="flex flex-wrap items-center gap-3">
 <button type="button" class="btn-bronze px-4 py-2 rounded text-xs font-bold tracking-wider uppercase flex items-center space-x-2" @click="router.push(`/builds/${build.id}/editar`)">
 <svg class="w-4 h-4 text-[#FDF8EE]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
 </svg>
 <span>Editar</span>
 </button>
 <button type="button" class="btn-gold-relief px-4 py-2 rounded text-xs font-extrabold tracking-wider uppercase flex items-center space-x-2" @click="router.push('/feed/nuevo')">
 <svg class="w-4 h-4 text-[var(--color-ink)]" fill="currentColor" viewBox="0 0 20 20">
 <path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z"></path>
 </svg>
 <span>Publicar en Feed</span>
 </button>
 <button type="button" class="btn-gold-relief px-4 py-2 rounded text-xs font-extrabold tracking-wider uppercase flex items-center space-x-2" @click="publicarEnForo">
 <span>Publicar en Foro</span>
 </button>
 <button type="button" class="btn-bronze px-4 py-2 rounded text-xs font-bold tracking-wider uppercase flex items-center space-x-2" @click="agregarAWiki">
 <span>Agregar a Wiki</span>
 </button>
 <button type="button" class="btn-bronze px-4 py-2 rounded text-xs font-bold tracking-wider uppercase flex items-center space-x-2" @click="ponerEnBitacora">
 <span>Bitácora</span>
 </button>
 <button type="button" class="btn-bronze px-4 py-2 rounded text-xs font-bold tracking-wider uppercase flex items-center space-x-2" @click="abrirAsociar = true">
 <svg class="w-4 h-4 text-[#FDF8EE]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
 </svg>
 <span>{{ build.mesaId ? 'Cambiar Mesa' : 'Asociar a Mesa' }}</span>
 </button>
 </div>

 <button type="button" class="btn-like px-3.5 py-2 rounded flex items-center space-x-2.5 shadow-sm group" :class="{ 'sim-votado': megusta }" @click="alternarMeGusta">
 <svg class="w-5 h-5 text-[var(--color-accent)] group-hover:scale-110 transition-transform" fill="currentColor" viewBox="0 0 24 24">
 <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"></path>
 </svg>
 <span class=" text-xs font-bold text-[var(--color-accent)] uppercase tracking-wider">Me gusta</span>
 <span class=" text-[1.15rem] font-bold text-[var(--color-ink)] pl-1 border-l border-[var(--color-rule)]">{{ likes }}</span>
 </button>
 </div>

 <div class="bg-[var(--color-paper-2)] border-2 border-[var(--color-rule)] rounded-sm p-5 shadow-md">
 <div class="flex items-center justify-between border-b border-[var(--color-rule)] pb-2 mb-3">
 <h2 class=" text-lg text-[var(--color-accent)] font-bold tracking-wide flex items-center gap-2">
 <span>✦</span> DOTES SELECCIONADAS ({{ build.ficha.dotes.length }})
 </h2>
 <span class=" text-xs text-[var(--color-muted)] uppercase">Progresión Nivel {{ build.nivel }} {{ build.clase }}</span>
 </div>
 <div class="flex flex-wrap gap-2.5">
 <div v-for="dote in build.ficha.dotes" :key="dote.nombre" class="pf-tag px-3 py-1.5 rounded text-xs flex items-center space-x-2 shadow-xs cursor-pointer">
 <span class="font-bold text-[var(--color-accent)]">{{ dote.nombre }}</span>
 <span class="text-[10px] bg-[var(--color-paper)] px-1.5 py-0.2 rounded text-[var(--color-ink)]">{{ dote.fuente }}</span>
 </div>
 </div>
 <div class="mt-3 bg-[var(--color-paper)] p-2.5 border-l-2 border-[var(--color-accent)] text-xs text-[var(--color-ink)] italic">
 <strong>Estrategia táctica:</strong> {{ build.ficha.estrategia }}
 </div>
 </div>

 <div class="bg-[var(--color-paper-2)] border-2 border-[var(--color-rule)] rounded-sm p-5 shadow-md">
 <div class="flex items-center justify-between border-b border-[var(--color-rule)] pb-2 mb-3">
 <h2 class=" text-lg text-[var(--color-accent)] font-bold tracking-wide flex items-center gap-2">
 <span>✦</span> CONJUROS, RUNAS &amp; APTITUDES MÁGICAS
 </h2>
 <span class=" text-xs text-[var(--color-muted)] uppercase">Capacidades Arcanas / Objetos Activables</span>
 </div>
 <p class=" text-xs text-[var(--color-muted)] italic mb-3">{{ build.ficha.magia.intro }}</p>
 <div class="flex flex-wrap gap-2.5">
 <div v-for="item in build.ficha.magia.items" :key="item.nombre" class="pf-tag px-3 py-1.5 rounded text-xs flex items-center space-x-2 shadow-xs">
 <span class="font-bold" :class="item.destacado ? 'text-[var(--color-error)]' : 'text-[var(--color-accent)]'">{{ item.nombre }}</span>
 <span class="text-[10px] bg-[var(--color-paper)] px-1.5 py-0.5 rounded text-[var(--color-ink)]">{{ item.fuente }}</span>
 </div>
 </div>
 </div>

 <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
 <div class="bg-[var(--color-paper-2)] border-2 border-[var(--color-rule)] rounded-sm p-5 shadow-md flex flex-col justify-between">
 <div>
 <div class="flex items-center justify-between border-b border-[var(--color-rule)] pb-2 mb-3">
 <h2 class=" text-lg text-[var(--color-accent)] font-bold tracking-wide flex items-center gap-2">
 <span>✦</span> EQUIPO TÁCTICO
 </h2>
 <span class=" text-xs text-[var(--color-muted)] uppercase">{{ build.ficha.pesoCarga }}</span>
 </div>
 <ul class=" text-sm text-[var(--color-ink)] space-y-2 divide-y divide-[#C2A980]/30">
 <li v-for="pieza in build.ficha.equipo" :key="pieza.nombre" class="pt-1 flex items-start justify-between gap-3">
 <div>
 <span class="font-bold text-[var(--color-accent)]">{{ pieza.nombre }}</span>
 <p class="text-xs text-[var(--color-muted)] italic">{{ pieza.detalle }}</p>
 </div>
 <span class=" text-xs font-bold text-[var(--color-ink)] shrink-0">{{ pieza.precio }}</span>
 </li>
 </ul>
 </div>
 <div class="mt-4 pt-2 border-t border-[var(--color-rule)] flex justify-between items-center text-xs text-[var(--color-muted)]">
 <span>Riqueza líquida: <strong>{{ build.ficha.riquezaLiquida }}</strong></span>
 <span class="text-[var(--color-accent)] font-bold">Valor Total: {{ build.ficha.valorTotal }}</span>
 </div>
 </div>

 <div class="bg-[var(--color-paper-2)] border-2 border-[var(--color-rule)] rounded-sm p-5 shadow-md flex flex-col justify-between">
 <div>
 <div class="flex items-center justify-between border-b border-[var(--color-rule)] pb-2 mb-3">
 <h2 class=" text-lg text-[var(--color-accent)] font-bold tracking-wide flex items-center gap-2">
 <span>✦</span> HABILIDADES DE CLASE
 </h2>
 <span class=" text-xs text-[var(--color-muted)] uppercase">Rangos invertidos: {{ build.ficha.rangos }}</span>
 </div>
 <ul class=" text-sm text-[var(--color-ink)] space-y-2 divide-y divide-[#C2A980]/30">
 <li v-for="hab in build.ficha.habilidades" :key="hab.nombre" class="pt-1 flex items-center justify-between">
 <div class="flex items-center space-x-2">
 <span class="w-1.5 h-1.5 bg-[#8B5A2B] rounded-full"></span>
 <span class="font-semibold">{{ hab.nombre }}</span>
 <span class="text-[11px] text-[var(--color-muted)] italic">{{ hab.abrev }}</span>
 </div>
 <span class=" font-bold text-sm text-[var(--color-ink)] bg-[var(--color-paper)] px-2 py-0.5 border border-[var(--color-rule)] rounded">{{ hab.valor }}</span>
 </li>
 </ul>
 </div>
 <div class="mt-4 pt-2 border-t border-[var(--color-rule)] text-[11px] text-[var(--color-muted)] italic">{{ build.ficha.penalizadorArmadura }}</div>
 </div>
 </div>

 <div class="bg-[var(--color-paper-2)] border border-[var(--color-rule)] rounded-sm p-4 text-xs text-[var(--color-ink)] flex flex-wrap items-center justify-between gap-3 shadow-xs">
 <div class="flex items-center space-x-3">
 <span class=" font-bold text-[var(--color-accent)] uppercase">Campaña Activa:</span>
 <template v-if="campañaBanner">
 <span class="bg-[var(--color-paper)] px-2.5 py-1 border border-[var(--color-rule)] rounded text-[var(--color-ink)] font-semibold">{{ campañaBanner.nombre }}</span>
 <span class="text-[var(--color-success,#6B8E23)] font-bold">{{ campañaBanner.enlazadoPor }}</span>
 </template>
 <span v-else class="text-[var(--color-muted)] italic">Sin campaña vinculada todavía.</span>
 </div>
 <div class="flex items-center space-x-2">
 <span class="text-[var(--color-muted)]">Creado por:</span>
 <strong class=" text-[var(--color-ink)]">{{ build.autor }}</strong>
 <span class="text-[var(--color-muted)]">• Actualizado {{ build.historial[0]?.fecha || 'hace un momento' }}</span>
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
</div>
</template>
<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-lg); align-items: start; }
.stack { display: grid; gap: var(--space-lg); }
@media (max-width: 60rem) { .app-grid { padding-top: 120px; } }
</style>
