<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast.js'
import { getHistorial, restaurarVersion } from '@/services/builds.js'
import { pdfApi } from '@/api/endpoints'
import { usePdfDescarga } from '@/composables/usePdfDescarga.js'

const props = defineProps({ id: { type: String, required: true } })

const pdf = usePdfDescarga(() => pdfApi.solicitarBuild(Number(props.id)))

const router = useRouter()
const toast = useToast()

const versiones = ref([])
const cargando = ref(true)
const error = ref(null)
const difVista = ref(false)

async function cargar() {
  cargando.value = true
  error.value = null
  try {
    versiones.value = await getHistorial(props.id)
  } catch (e) {
    error.value = e.message || 'No pudimos cargar el historial.'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)

const activa = computed(() => versiones.value.find((v) => v.activa)?.version || '')
const anterior = computed(() => versiones.value.find((v) => !v.activa)?.version || '')

const aComparar = ref(null)
const bComparar = ref(null)

const opcionesCompara = computed(() => versiones.value.slice(0).reverse())

function badgeClase(v) {
  if (v.activa) return 'bg-[#6B8E23]/15 text-[#6B8E23]'
  return 'bg-[#8B7D6B]/15 text-[#8B7D6B]'
}

const diff = computed(() => {
  if (!aComparar.value || !bComparar.value) return null
  const a = versiones.value.find((v) => v.version === aComparar.value)
  const b = versiones.value.find((v) => v.version === bComparar.value)
  if (!a?.snapshot || !b?.snapshot) return []
  const campos = [
    { clave: 'nivel', nombre: 'Nivel' },
    { clave: 'armaPrincipal', nombre: 'Arma principal' },
    { clave: 'pg', nombre: 'Puntos de golpe' },
    { clave: 'dotes', nombre: 'Dotes' },
    { clave: 'piezasEquipo', nombre: 'Piezas de equipo' },
    { clave: 'valorTotal', nombre: 'Valor total' }
  ]
  return campos
    .filter((c) => a.snapshot[c.clave] !== b.snapshot[c.clave])
    .map((c) => ({ nombre: c.nombre, desde: a.snapshot[c.clave], hacia: b.snapshot[c.clave] }))
})

function abrirDiff(version) {
  aComparar.value = activa.value || versiones.value[0]?.version
  bComparar.value = version
  difVista.value = true
}

async function restaurar(version) {
  await restaurarVersion(props.id, version)
  toast.ok(`Versión restaurada · la hoja vuelve a v${version}.`)
  await cargar()
}

function exportar() {
  if (pdf.fase.value === 'enviando' || pdf.fase.value === 'en_cola') return
  if (pdf.fase.value === 'listo') {
    pdf.abrirDescarga()
    return
  }
  pdf.exportar()
}
</script>

<template>
  <main class="tfinder-shell">
    <div class="flex flex-wrap items-start justify-between gap-3 mb-2">
      <div>
        <h1 class="font-mason text-3xl text-[#8B5A2B] font-bold">✦ Historial de Versiones</h1>
        <p class="font-minion italic text-[#5C4633] mt-1">Cada cambio del héroe queda grabado en el códice. Podés comparar, restaurar o exportar versiones.</p>
      </div>
      <RouterLink :to="`/builds/${id}`" class="font-tarzana text-xs font-bold text-[#8B5A2B] hover:underline uppercase tracking-wider">← Volver a la ficha</RouterLink>
    </div>

    <div class="flex flex-wrap gap-2 mb-6">
      <button
        type="button"
        class="px-5 py-2.5 font-tarzana text-xs font-bold rounded-sm transition disabled:opacity-60"
        :class="pdf.fase === 'listo' ? 'bg-[#6B8E23] text-[#FDF8EE]' : 'bg-[#D4AF37] text-[#1A1A1A] hover:brightness-110'"
        :disabled="['enviando', 'en_cola'].includes(pdf.fase)"
        @click="exportar"
      >
        {{ { inactivo: 'Exportar historial', enviando: 'Esperando 202…', en_cola: 'Generando…', listo: 'Descargar PDF', error: 'Reintentar' }[pdf.fase] }}
      </button>
      <span v-if="pdf.fase === 'en_cola'" class="inline-flex items-center gap-1 text-[#8B5A2B] font-tarzana text-xs font-bold uppercase tracking-wider self-center">
        <span class="w-2 h-2 rounded-full bg-[#D4AF37] animate-pulse"></span> en cola (async)
      </span>
      <p v-if="pdf.fase === 'error'" class="text-[#8B1A1A] font-minion text-sm" role="alert">
        Falló la generación: {{ pdf.mensaje }}
      </p>
      <button
        v-if="activa && anterior"
        type="button"
        class="px-5 py-2.5 border border-[#8B5A2B] text-[#8B5A2B] font-tarzana text-xs font-bold rounded-sm"
        @click="abrirDiff(anterior)"
      >
        Comparar {{ activa }} · {{ anterior }}
      </button>
      <select v-model="bComparar" class="px-3 py-2.5 rounded-sm bg-[#F4EAD6] border border-[#C2A980] font-tarzana text-xs font-bold text-[#5C4633]">
        <option value="" disabled>Seleccionar versión a comparar…</option>
        <option v-for="v in opcionesCompara" :key="v.version" :value="v.version">v{{ v.version }}</option>
      </select>
    </div>

    <div v-if="cargando" class="py-10 text-center font-tarzana text-xs uppercase tracking-widest text-[#8B7D6B]">Desempolvando el códice…</div>
    <div v-else-if="error" class="py-10 text-center font-minion text-[#8B1A1A]">{{ error }}</div>

    <template v-else>
      <div v-if="difVista && diff" class="parchment-sheet relative border border-[#C2A980] rounded-sm p-6 mb-4 shadow-md">
        <div class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-[#8B5A2B]"></div>
        <div class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-[#8B5A2B]"></div>
        <div class="flex items-center justify-between flex-wrap gap-2 mb-4">
          <h2 class="font-mason text-lg text-[#1A1A1A] font-bold">Cámara de difusión · v{{ aComparar }} ↔ v{{ bComparar }}</h2>
          <button type="button" class="font-tarzana text-xs font-bold text-[#8B5A2B] hover:underline uppercase" @click="difVista = false">Cerrar ✕</button>
        </div>
        <p v-if="diff.length === 0" class="font-tarzana text-sm text-[#8B7D6B]">Las versiones seleccionadas comparten el mismo snapshot; no hay diferencias registradas.</p>
        <ul v-else class="space-y-2">
          <li v-for="d in diff" :key="d.nombre" class="flex flex-wrap items-center gap-2 font-tarzana text-sm border-b border-dotted border-[#C2A980]/60 pb-1.5">
            <span class="font-bold text-[#8B5A2B] uppercase w-40">{{ d.nombre }}</span>
            <span class="text-[#8B1A1A] font-bold line-through decoration-2">{{ d.desde }}</span>
            <span class="text-[#6B8E23] font-bold">→ {{ d.hacia }}</span>
          </li>
        </ul>
        <p class="text-[11px] font-tarzana text-[#6B5E50] italic mt-3">Diff simulado sobre el snapshot OGL registrado en el códice.</p>
      </div>

      <section v-for="v in versiones" :key="v.version" class="parchment-sheet relative border border-[#C2A980] rounded-sm p-6 mb-4 shadow-md">
        <div class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-[#8B5A2B]"></div>
        <div class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-[#8B5A2B]"></div>
        <div class="flex items-center justify-between flex-wrap gap-2 mb-1">
          <h2 class="font-mason text-lg text-[#1A1A1A] font-bold">v{{ v.version }} · {{ v.resumen }}</h2>
          <span class="font-tarzana text-xs px-3 py-1 rounded-sm font-bold" :class="badgeClase(v)">{{ v.activa ? 'ACTIVA' : 'ANTERIOR' }}</span>
        </div>
        <p class="font-tarzana text-sm text-[#8B7D6B] mb-3">{{ v.fecha }} · {{ v.autor }} · {{ v.resumen }}</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-if="!v.activa"
            type="button"
            class="px-4 py-2 bg-[#8B5A2B] text-[#FDF8EE] font-tarzana text-xs font-bold rounded-sm hover:brightness-110"
            @click="restaurar(v.version)"
          >
            {{ versiones[0] === v ? 'Restaurar versión' : 'Restaurar' }}
          </button>
          <button type="button" class="px-4 py-2 border border-[#8B7D6B] text-[#8B7D6B] font-tarzana text-xs font-bold rounded-sm" @click="abrirDiff(v.version)">Ver diff</button>
        </div>
      </section>

      <p v-if="versiones.length === 0" class="parchment-sheet relative border border-[#C2A980] rounded-sm p-6 shadow-md font-minion italic text-[#5C4633]">
        Este build todavía no registra versiones en el códice.
      </p>
    </template>
  </main>
</template>