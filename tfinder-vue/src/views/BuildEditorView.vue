<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast.js'
import { getBuild, actualizarBuild } from '@/services/builds.js'

const props = defineProps({ id: { type: String, required: true } })

const router = useRouter()
const toast = useToast()

const cargando = ref(true)
const error = ref(null)
const guardando = ref(false)

const nombre = ref('')
const nivel = ref(1)
const clase = ref('Guerrero (Fighter)')
const arquetipo = ref('')

const base = [
  { etiqueta: 'FUE', valor: 10, fila: 0 },
  { etiqueta: 'DES', valor: 10, fila: 1 },
  { etiqueta: 'CON', valor: 10, fila: 2 },
  { etiqueta: 'INT', valor: 10, fila: 3 },
  { etiqueta: 'SAB', valor: 10, fila: 4 },
  { etiqueta: 'CAR', valor: 10, fila: 5 }
]
const rasgos = ref(base.map((r) => ({ ...r })))

const dotes = ref([])
const magia = ref([])

const busquedaDotes = ref('')
const busquedaMagia = ref('')

const COMPENDIO_DOTES = [
  { nombre: 'Ataque Poderoso', fuente: 'General' },
  { nombre: 'Esquiva', fuente: 'General' },
  { nombre: 'Soltura con un Arma', fuente: 'General' },
  { nombre: 'Combate con Dos Armas', fuente: 'General' },
  { nombre: 'Doble Tajo', fuente: 'General' },
  { nombre: 'Especialización en Armas', fuente: 'General' },
  { nombre: 'Arremetida Potente', fuente: 'Guerrero' },
  { nombre: 'Reflejos de Combate', fuente: 'General' },
  { nombre: 'Carga Alocada', fuente: 'General' },
  { nombre: 'Valentía', fuente: 'Guerrero' },
  { nombre: 'Esquiva Gigantes', fuente: 'General' },
  { nombre: 'Movilidad', fuente: 'General' },
  { nombre: 'Furtivo', fuente: 'General' },
  { nombre: 'Disparo a Bocajarro', fuente: 'General' }
]

const GRIMORIO = [
  { nombre: 'Varita de Curar Heridas Leves', fuente: 'Nivel 1 (28 cargas)' },
  { nombre: 'Aura de Valentía (Su)', fuente: 'Innato Guerrero' },
  { nombre: 'Aceite de Arma Mágica', fuente: '2 viales' },
  { nombre: 'Poción de Agrandar Persona', fuente: 'Nvl 1 Transmutación' },
  { nombre: 'Rayo de Debilitamiento', fuente: 'Nivel 1' },
  { nombre: 'Sanar Heridas Leves', fuente: 'Nivel 1' },
  { nombre: 'Fuego Fatuo', fuente: 'Nivel 1' }
]

const COSTO_POR_PUNTO = [0, 1, 1, 1, 2, 2, 3, 4]

function costoSobre10(valor) {
  let costo = 0
  for (let i = 11; i <= valor; i++) costo += COSTO_POR_PUNTO[i - 10]
  return costo
}

const puntosUsados = computed(() => rasgos.value.reduce((acc, r) => acc + costoSobre10(r.valor), 0))
const puntosRestantes = computed(() => Math.max(0, 20 - puntosUsados.value))

const sinCupo = computed(() => puntosRestantes.value === 0)

function mod(valor) {
  const m = Math.floor((valor - 10) / 2)
  return m >= 0 ? `+${m}` : `${m}`
}

function ajustar(fila, delta) {
  const r = rasgos.value.find((x) => x.fila === fila)
  const destino = r.valor + delta
  if (destino < 7 || destino > 20) return
  if (delta > 0 && sinCupo.value) {
    toast.info('No quedan puntos para este atributo (límite Buy 20).')
    return
  }
  r.valor = destino
}

const dotesFiltradas = computed(() => {
  const q = busquedaDotes.value.trim().toLowerCase()
  const presentes = new Set(dotes.value.map((d) => d.nombre))
  return COMPENDIO_DOTES.filter((d) => !presentes.has(d.nombre)).filter(
    (d) => !q || d.nombre.toLowerCase().includes(q) || d.fuente.toLowerCase().includes(q)
  )
})

const magiaFiltrada = computed(() => {
  const q = busquedaMagia.value.trim().toLowerCase()
  const presentes = new Set(magia.value.map((m) => m.nombre))
  return GRIMORIO.filter((m) => !presentes.has(m.nombre)).filter(
    (m) => !q || m.nombre.toLowerCase().includes(q) || m.fuente.toLowerCase().includes(q)
  )
})

function anadirDote({ nombre: n, fuente }) {
  if (dotes.value.length >= 5) {
    toast.info('Cupo de dotes completo (5/5).')
    return
  }
  dotes.value.push({ nombre: n, fuente })
}

function quitarDote(indice) {
  dotes.value.splice(indice, 1)
}

function anadirMagia({ nombre: n, fuente }) {
  magia.value.push({ nombre: n, fuente })
}

function quitarMagia(indice) {
  magia.value.splice(indice, 1)
}

const cupoDotes = computed(() => `${dotes.value.length}/5`)

async function cargar() {
  cargando.value = true
  error.value = null
  try {
    const b = await getBuild(props.id)
    nombre.value = b.nombre || b.display || ''
    nivel.value = b.nivel || 1
    clase.value = b.clase ? (b.clase.includes('(') ? b.clase : `${b.clase} (${b.clase})`) : 'Guerrero (Fighter)'
    arquetipo.value = b.arquetipo || ''
    if (b.ficha?.rasgos) {
      rasgos.value = b.ficha.rasgos.map((r, i) => ({
        etiqueta: r.etiqueta,
        valor: Number(r.valor) || 10,
        fila: i
      }))
    }
    dotes.value = (b.ficha?.dotes || []).map((d) => ({ nombre: d.nombre, fuente: d.fuente }))
    magia.value = (b.ficha?.magia?.items || []).map((m) => ({ nombre: m.nombre, fuente: m.fuente }))
  } catch (e) {
    error.value = e.message || 'No pudimos cargar la ficha para editar.'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)

async function publicarFicha() {
  guardando.value = true
  try {
    const b = await getBuild(props.id)
    const clave = clase.value.replace(/\s*\(.*\)$/, '').trim()
    const nuevaFicha = {
      ...(b.ficha || {}),
      rasgos: rasgos.value.map((r) => ({
        etiqueta: r.etiqueta,
        valor: r.valor,
        mod: mod(r.valor),
        ancho: Math.min(100, Math.round(((r.valor - 7) / 13) * 100))
      })),
      dotes: dotes.value.map((d) => ({ nombre: d.nombre, fuente: d.fuente })),
      magia: {
        intro: 'Capacidades arcanas y objetos activables registrados en la hoja.',
        items: magia.value.map((m) => ({ nombre: m.nombre, fuente: m.fuente, destacado: false }))
      }
    }
    const cambios = {
      nombre: nombre.value.trim(),
      display: nombre.value.trim() || 'Personaje sin nombre',
      nivel: Number(nivel.value),
      clase: clave,
      arquetipo: arquetipo.value,
      privacidad: 'publico',
      ficha: nuevaFicha,
      resumenCambio: `${clave} Nv ${nivel.value}: actualización de atributos, dotes y conjuros.`
    }
    const actualizado = await actualizarBuild(props.id, cambios)
    toast.ok('Build publicado en tu Códice personal.')
    router.push(`/builds/${actualizado.id}`)
  } catch (e) {
    toast.error(e.message || 'No pudimos guardar los cambios.')
  } finally {
    guardando.value = false
  }
}

async function guardarBorrador() {
  try {
    const b = await getBuild(props.id)
    const clave = clase.value.replace(/\s*\(.*\)$/, '').trim()
    const actualizado = await actualizarBuild(props.id, {
      nombre: nombre.value.trim() || b.nombre,
      display: nombre.value.trim() || b.display,
      nivel: Number(nivel.value),
      clase: clave,
      arquetipo: arquetipo.value,
      privacidad: 'borrador',
      resumenCambio: 'Borrador autoguardado.'
    })
    toast.ok('Borrador autoguardado.')
    router.push(`/builds/${actualizado.id}`)
  } catch (e) {
    toast.error(e.message || 'No pudimos autoguardar el borrador.')
  }
}
</script>

<template>
  <main class="flex-grow w-full max-w-[1200px] mx-auto px-4 py-8">
    <div v-if="cargando" class="py-16 flex flex-col items-center gap-4" role="status" aria-live="polite">
      <div class="animate-pulse space-y-3 w-full max-w-md">
        <div class="h-5 bg-[#C2A980]/40 rounded w-2/3"></div>
        <div class="h-3 bg-[#C2A980]/25 rounded w-full"></div>
      </div>
      <p class="font-tarzana text-xs uppercase tracking-widest text-[#8B7D6B]">Abriendo la mesa de forja...</p>
    </div>

    <div v-else-if="error" class="py-16 text-center" role="alert">
      <p class="font-tarzana uppercase tracking-widest text-xs text-[#8B1A1A] font-bold mb-1">No se pudo editar</p>
      <p class="font-minion text-[#5A4A3A]">{{ error }}</p>
      <RouterLink to="/builds" class="btn-copper-outline inline-block mt-5 px-5 py-2 font-tarzana font-bold uppercase tracking-wider text-sm">← Volver a mis builds</RouterLink>
    </div>

    <template v-else>
      <div class="flex flex-wrap items-center justify-between gap-2 mb-4 px-1">
        <div class="flex items-center space-x-2 font-tarzana text-xs tracking-wider text-[#A0A0A0]">
          <RouterLink to="/builds" class="hover:text-[#D4AF37] transition duration-150 font-bold">INICIO</RouterLink>
          <span class="text-[#555] font-bold">/</span>
          <RouterLink to="/builds" class="hover:text-[#D4AF37] transition duration-150 font-bold">BUILDS</RouterLink>
          <span class="text-[#555] font-bold">/</span>
          <span class="text-[#D4AF37] font-bold">NUEVA FICHA DE PERSONAJE</span>
        </div>
        <RouterLink to="/builds" class="text-[#D4AF37] hover:underline flex items-center space-x-1.5 font-bold font-tarzana text-xs tracking-wider">
          <span>←</span>
          <span>VOLVER A MIS BUILDS</span>
        </RouterLink>
      </div>

      <form class="relative rounded-sm p-6 sm:p-10 border-2 border-[#C2A980] bg-[#FDF8EE] shadow-xl space-y-10" @submit.prevent="publicarFicha">
        <div class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-[#8B5A2B]"></div>
        <div class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-[#8B5A2B]"></div>
        <div class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-[#8B5A2B]"></div>
        <div class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-[#8B5A2B]"></div>

        <header class="border-b-2 border-[#8B1A1A] pb-4">
          <div class="flex flex-wrap items-baseline justify-between gap-2">
            <h1 class="font-mason text-2xl sm:text-3xl font-black text-[#8B5A2B] tracking-wide uppercase">Crear Personaje</h1>
            <span class="font-tarzana text-xs uppercase tracking-widest text-[#8B7D6B] font-semibold">Formulario Oficial PF1e SRD</span>
          </div>
          <p class="font-minion italic text-[#4A3B32] text-base sm:text-lg mt-1">
            Forja tu héroe para Pathfinder Primera Edición según las reglas canónicas de Paizo OGL.
          </p>
        </header>

        <section data-purpose="character-identity">
          <div class="flex items-center space-x-2 border-b border-[#8B1A1A] pb-1.5 mb-5">
            <h2 class="font-cinzel text-sm sm:text-base font-bold text-[#8B5A2B] uppercase tracking-wider">✦ 1. Identidad y Avance</h2>
            <div class="flex-1 border-t border-dotted border-[#C2A980]"></div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-12 gap-6 bg-[#FAF5EB] p-5 border border-[#C2A980]/50 rounded-sm">
            <div class="md:col-span-5 flex flex-col justify-between">
              <label for="char-name" class="block font-tarzana text-xs font-bold text-[#8B5A2B] tracking-wider uppercase mb-1">
                Nombre del Personaje <span class="text-[#8B1A1A]">*</span>
              </label>
              <input id="char-name" v-model="nombre" type="text" class="w-full bg-[#FAF5EB] border border-[#8B7D6B] px-3 py-2 text-[#1A1A1A] font-minion text-lg focus:ring-1 focus:ring-[#8B5A2B] focus:border-[#8B5A2B] rounded-none placeholder-gray-400" placeholder="ej. Valeros el Temerario" required />
              <p class="text-[11px] font-tarzana text-[#6B5E50] mt-1.5 italic">Título heroico y renombre en las tierras de Golarion.</p>
            </div>

            <div class="md:col-span-3 flex flex-col justify-between border-y md:border-y-0 md:border-x border-[#C2A980]/40 py-2 md:py-0 md:px-4">
              <div class="flex items-center justify-between mb-1">
                <label for="char-level" class="font-tarzana text-xs font-bold text-[#8B5A2B] tracking-wider uppercase">Nivel</label>
                <span class="font-mason text-xl font-black text-[#8B5A2B]">Nivel {{ nivel }}</span>
              </div>
              <div class="py-2">
                <input id="char-level" v-model.number="nivel" class="slider-horizontal" max="20" min="1" type="range" />
                <div class="flex justify-between text-[10px] font-tarzana text-[#8B7D6B] font-bold px-1 mt-1">
                  <span>1</span><span>5</span><span>10</span><span>15</span><span>20</span>
                </div>
              </div>
              <p class="text-[11px] font-tarzana text-[#6B5E50] italic">Progresión BAB &amp; Habilidades.</p>
            </div>

            <div class="md:col-span-4 flex flex-col justify-between">
              <label for="char-class" class="block font-tarzana text-xs font-bold text-[#8B5A2B] tracking-wider uppercase mb-1">
                Clase de Personaje <span class="text-[#8B1A1A]">*</span>
              </label>
              <div class="space-y-2">
                <select id="char-class" v-model="clase" class="w-full bg-[#FAF5EB] border border-[#8B7D6B] px-3 py-1.5 text-[#1A1A1A] font-tarzana text-sm rounded-none">
                  <option>Guerrero (Fighter)</option>
                  <option>Paladín</option>
                  <option>Mago Arcanista</option>
                  <option>Pícaro</option>
                  <option>Clérigo</option>
                  <option>Alquimista</option>
                  <option>Bárbaro</option>
                  <option>Explorador</option>
                </select>
                <input v-model="arquetipo" type="text" class="w-full bg-[#FAF5EB] border border-[#8B7D6B] px-3 py-1 text-[#1A1A1A] font-tarzana text-xs italic rounded-none" placeholder="Arquetipo (opcional)" />
              </div>
            </div>
          </div>
        </section>

        <section data-purpose="ability-scores">
          <div class="flex flex-wrap items-center justify-between border-b border-[#8B1A1A] pb-1.5 mb-5 gap-2">
            <h2 class="font-cinzel text-sm sm:text-base font-bold text-[#8B5A2B] uppercase tracking-wider">✦ 2. Puntuaciones de Característica (Buy-Points OGL)</h2>
            <div class="flex items-center space-x-3 text-xs font-tarzana font-semibold">
              <span class="bg-[#EAD8B7] px-2.5 py-0.5 border border-[#8B5A2B]/40 rounded" :class="sinCupo ? 'text-[#8B1A1A]' : 'text-[#8B5A2B]'">Puntos restantes: {{ puntosRestantes }}</span>
              <span class="text-[#6B5E50] hidden sm:inline">Fantasy Buy: 20 pts</span>
            </div>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
            <div v-for="r in rasgos" :key="r.etiqueta" class="bg-[#FAF5EB] border border-[#C2A980] p-3 flex flex-col items-center justify-between rounded shadow-sm text-center">
              <span class="font-tarzana font-black text-xs text-[#8B5A2B] tracking-widest uppercase">{{ r.etiqueta }}</span>
              <span class="font-mason text-2xl font-bold text-[#1A1A1A] my-1">{{ r.valor }}</span>
              <span class="font-tarzana text-xs font-black bg-[#EFE3CF] border border-[#C2A980] px-2 py-0.5 rounded mb-2" :class="Number(mod(r.valor)) < 0 ? 'text-[#8B1A1A]' : 'text-[#8B5A2B]'">{{ mod(r.valor) }}</span>
              <div class="h-[125px] flex items-center justify-center my-1">
                <input class="slider-vertical" type="range" min="7" max="20" :value="r.valor" @input="r.valor = Number($event.target.value)" />
              </div>
              <div class="flex items-center justify-between w-full mt-2 px-1">
                <button type="button" class="w-6 h-6 border border-[#8B7D6B] bg-white text-xs font-bold hover:bg-[#E8DCC8]" aria-label="Reducir {{ r.etiqueta }}" @click="ajustar(r.fila, -1)">-</button>
                <button type="button" class="w-6 h-6 border border-[#8B7D6B] bg-white text-xs font-bold hover:bg-[#E8DCC8]" aria-label="Aumentar {{ r.etiqueta }}" @click="ajustar(r.fila, 1)">+</button>
              </div>
            </div>
          </div>
        </section>

        <section data-purpose="feats-selection">
          <div class="flex flex-wrap items-center justify-between border-b border-[#8B1A1A] pb-1.5 mb-5 gap-2">
            <div>
              <h2 class="font-cinzel text-sm sm:text-base font-bold text-[#8B5A2B] uppercase tracking-wider">✦ 3. Dotes Seleccionadas ({{ cupoDotes }})</h2>
              <p class="text-xs font-tarzana text-[#776655] italic">Dotes de nivel y de clase de Guerrero.</p>
            </div>
            <span v-if="dotes.length >= 5" class="text-xs font-tarzana bg-[#EAD8B7] px-2 py-0.5 border border-[#8B5A2B]/40 text-[#8B5A2B] font-bold rounded">Cupo Completo</span>
          </div>
          <div class="flex flex-col sm:flex-row gap-2 mb-4">
            <div class="relative flex-1">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#8B5A2B]">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                </svg>
              </span>
              <input v-model="busquedaDotes" type="text" class="w-full bg-[#FAF5EB] border border-[#8B7D6B] pl-9 pr-3 py-2 text-xs font-tarzana placeholder-gray-500 rounded-none" placeholder="Buscar dotes en el Compendio OGL (ej. Ataque Poderoso, Esquiva...)" />
            </div>
            <button type="button" class="px-5 py-2 bg-[#8B5A2B] text-[#FAF5EB] font-tarzana font-bold text-xs uppercase tracking-wider hover:bg-[#6E421F] transition" @click="dotesFiltradas[0] && anadirDote(dotesFiltradas[0])">Añadir</button>
          </div>
          <div class="bg-[#FAF5EB] p-4 border border-[#C2A980]/70 rounded-sm">
            <div class="flex flex-wrap gap-2.5">
              <div v-for="(d, i) in dotes" :key="d.nombre" class="inline-flex items-center space-x-2 bg-[#F6EFE2] border-[1.5px] border-[#8B5A2B] px-3 py-1.5 rounded-sm">
                <span class="font-tarzana font-bold text-xs text-[#1A1A1A]">{{ d.nombre }}</span>
                <span class="bg-[#E0D3C1] text-[#8B5A2B] text-[10px] font-tarzana font-bold px-1.5 py-0.5 rounded">{{ d.fuente }}</span>
                <button type="button" class="text-[#8B1A1A] hover:text-red-800 font-black text-sm leading-none pl-1" title="Eliminar" @click="quitarDote(i)">×</button>
              </div>
              <p v-if="dotes.length === 0" class="text-xs font-tarzana text-[#8B7D6B] italic">Ninguna dote seleccionada todavía.</p>
            </div>
            <div v-if="dotesFiltradas.length" class="mt-4 pt-3 border-t border-dashed border-[#C2A980]/50 flex flex-wrap items-center gap-2">
              <span class="text-xs font-tarzana font-bold text-[#8B5A2B] uppercase">Sugerencias:</span>
              <button v-for="sug in dotesFiltradas.slice(0, 3)" :key="sug.nombre" type="button" class="min-h-[44px] inline-flex items-center px-2 py-0.5 bg-white border border-dashed border-[#8B5A2B] text-xs font-tarzana text-[#6E421F] hover:bg-[#F2E5D0] rounded" @click="anadirDote(sug)">+ {{ sug.nombre }}</button>
            </div>
          </div>
        </section>

        <section data-purpose="spells-and-magic-abilities">
          <div class="flex flex-wrap items-center justify-between border-b border-[#8B1A1A] pb-1.5 mb-5 gap-2">
            <div>
              <h2 class="font-cinzel text-sm sm:text-base font-bold text-[#8B5A2B] uppercase tracking-wider">✦ 4. Conjuros y Objetos Activables</h2>
              <p class="text-xs font-tarzana text-[#776655] italic">Capacidades de conjuración, varitas o dones sagrados.</p>
            </div>
            <span class="text-xs font-tarzana text-[#776655]">{{ magia.length }} {{ magia.length === 1 ? 'elemento asignado' : 'elementos asignados' }}</span>
          </div>
          <div class="mb-4">
            <input v-model="busquedaMagia" type="text" class="w-full bg-[#FAF5EB] border border-[#8B7D6B] px-3 py-2 text-xs font-tarzana placeholder-gray-500 rounded-none" placeholder="Buscar en el Grimorio Arcano/Divino..." />
          </div>
          <div class="bg-[#FAF5EB] p-4 border border-[#C2A980]/70 rounded-sm">
            <div class="flex flex-wrap gap-2.5">
              <div v-for="(m2, i) in magia" :key="m2.nombre" class="inline-flex items-center space-x-2 bg-[#F6EFE2] border-[1.5px] border-[#8B5A2B] px-3 py-1.5 rounded-sm">
                <span class="font-tarzana font-bold text-xs text-[#1A1A1A]">{{ m2.nombre }}</span>
                <span class="bg-[#E0D3C1] text-[#8B5A2B] text-[10px] font-tarzana font-bold px-1.5 py-0.5 rounded">{{ m2.fuente }}</span>
                <button type="button" class="text-[#8B1A1A] hover:text-red-800 font-black text-sm leading-none pl-1" title="Eliminar" @click="quitarMagia(i)">×</button>
              </div>
              <p v-if="magia.length === 0" class="text-xs font-tarzana text-[#8B7D6B] italic">Sin capacidades mágicas registradas.</p>
            </div>
            <div v-if="magiaFiltrada.length" class="mt-4 pt-3 border-t border-dashed border-[#C2A980]/50 flex flex-wrap items-center gap-2">
              <span class="text-xs font-tarzana font-bold text-[#8B5A2B] uppercase">Disponibles:</span>
              <button v-for="op in magiaFiltrada.slice(0, 3)" :key="op.nombre" type="button" class="min-h-[44px] inline-flex items-center px-2 py-0.5 bg-white border border-dashed border-[#8B5A2B] text-xs font-tarzana text-[#6E421F] hover:bg-[#F2E5D0] rounded" @click="anadirMagia(op)">+ {{ op.nombre }}</button>
            </div>
          </div>
        </section>

        <div class="flex flex-col sm:flex-row justify-end gap-3 pt-2 border-t border-[#C2A980]/60">
          <button type="button" class="btn-copper-outline px-6 py-2.5 font-tarzana font-bold uppercase tracking-wider text-sm" :disabled="guardando" @click="router.push(`/builds/${id}`)">Cancelar</button>
          <button type="button" class="btn-bronze px-6 py-2.5 font-tarzana font-bold uppercase tracking-wider text-sm" :disabled="guardando" @click="guardarBorrador">Guardar Borrador</button>
          <button type="submit" class="btn-gold-relief px-7 py-2.5 font-tarzana font-extrabold uppercase tracking-wider text-sm" :disabled="guardando">
            {{ guardando ? 'Guardando…' : 'Publicar Ficha' }}
          </button>
        </div>
      </form>
    </template>
  </main>
</template>