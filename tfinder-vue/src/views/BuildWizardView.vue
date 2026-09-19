<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast.js'
import { crearBuild } from '@/services/builds.js'

const router = useRouter()
const toast = useToast()

const generando = ref(false)

const nombre = ref('')
const clase = ref('Clérigo')
const nivel = ref(1)

const atributos = ref([
  { etiqueta: 'FUE', valor: 14, fila: 0 },
  { etiqueta: 'DES', valor: 10, fila: 1 },
  { etiqueta: 'CON', valor: 12, fila: 2 },
  { etiqueta: 'INT', valor: 10, fila: 3 },
  { etiqueta: 'SAB', valor: 16, fila: 4 },
  { etiqueta: 'CAR', valor: 13, fila: 5 }
])

const lineamiento = computed(() => {
  const base = nombre.value.trim() || (clase.value.toLowerCase().startsWith('clér') || clase.value.toLowerCase().startsWith('cler') ? 'Héroe devoto' : 'Héroe del Nexus')
  return `${base} (${clase.value} Nv ${nivel.value})`
})

function mod(valor) {
  const m = Math.floor((valor - 10) / 2)
  return m >= 0 ? `+${m}` : `${m}`
}

async function generar() {
  generando.value = true
  try {
    const ficha = {
      rasgos: atributos.value.map((r) => ({
        etiqueta: r.etiqueta,
        valor: Number(r.valor),
        mod: mod(Number(r.valor)),
        ancho: Math.min(100, Math.round(((Number(r.valor) - 7) / 13) * 100))
      })),
      dotes: [],
      magia: { intro: '', items: [] },
      equipo: [],
      habilidades: [],
      defensa: {},
      ataque: {}
    }
    const nuevo = await crearBuild({
      nombre: nombre.value.trim() || 'Personaje sin nombre',
      clase: clase.value,
      nivel: Number(nivel.value),
      raza: 'Humano',
      arquetipo: '',
      rol: 'Personalizable',
      alineamiento: 'N',
      privacidad: 'borrador',
      detalle: 'Progresión diseñada desde cero con el asistente.',
      ficha
    })
    toast.ok('¡Build generada! Derivando a la forja del editor…')
    router.push(`/builds/${nuevo.id}/editar`)
  } catch (e) {
    toast.error(e.message || 'No pudimos generar la build.')
    generando.value = false
  }
}

function ajustarPreferencias() {
  toast.info('Preferencias del asistente ajustadas.')
}
</script>

<template>
  <main class="tfinder-shell">
    <h1 class="font-mason text-3xl text-[#8B5A2B] font-bold mb-2">✦ Asistente de Creación de Build</h1>
    <p class="font-minion italic text-[#5C4633] mb-6">Guía paso a paso para forjar un héroe coherente con la reglamentación PF1e.</p>

    <section class="parchment-sheet relative border border-[#C2A980] rounded-sm p-6 mb-4 shadow-md">
      <div class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-[#8B5A2B]"></div>
      <div class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-[#8B5A2B]"></div>
      <h2 class="font-tarzana text-xs uppercase tracking-widest text-[#D4AF37] mb-3">Paso 1 · Identidad</h2>
      <div class="grid sm:grid-cols-2 gap-4">
        <div>
          <label for="wiz-nombre" class="font-tarzana text-xs uppercase text-[#8B5A2B] block mb-1">Nombre del héroe</label>
          <input id="wiz-nombre" v-model="nombre" type="text" placeholder="ej. Kyra Sol Devoto" class="w-full py-2 px-3 rounded-sm bg-[#F4EAD6] border border-[#C2A980] font-minion text-sm" />
        </div>
        <div>
          <label for="wiz-categoria" class="font-tarzana text-xs uppercase text-[#8B5A2B] block mb-1">Categoría</label>
          <div class="flex gap-2">
            <select id="wiz-categoria" v-model="clase" class="flex-1 py-2 px-3 rounded-sm bg-[#F4EAD6] border border-[#C2A980] font-minion text-sm">
              <option>Clérigo</option>
              <option>Guerrero</option>
              <option>Pícaro</option>
              <option>Mago</option>
              <option>Paladín</option>
              <option>Explorador</option>
              <option>Bárbaro</option>
              <option>Alquimista</option>
            </select>
            <select v-model.number="nivel" class="py-2 px-3 rounded-sm bg-[#F4EAD6] border border-[#C2A980] font-minion text-sm">
              <option v-for="n in 20" :key="n" :value="n">Nvl {{ n }}</option>
            </select>
          </div>
        </div>
      </div>
    </section>

    <section class="parchment-sheet relative border border-[#C2A980] rounded-sm p-6 mb-4 shadow-md">
      <div class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-[#8B5A2B]"></div>
      <div class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-[#8B5A2B]"></div>
      <h2 class="font-tarzana text-xs uppercase tracking-widest text-[#D4AF37] mb-3">Paso 2 · Atributos base</h2>
      <div class="flex flex-wrap gap-3">
        <div v-for="r in atributos" :key="r.etiqueta" class="px-4 py-2 rounded-sm bg-[#F4EAD6] border border-[#C2A980] font-tarzana text-sm flex items-center gap-2">
          <b>{{ r.etiqueta }}</b>
          <input v-model.number="r.valor" type="number" min="7" max="20" class="w-11 bg-[#FDF8EE] border border-[#C2A980]/60 px-1 text-center font-tarzana" />
          <small :class="Number(mod(r.valor)) >= 2 ? 'text-[#6B8E23]' : 'text-[#8B7D6B]'">{{ mod(r.valor) }}</small>
        </div>
      </div>
      <div class="mt-3 font-minion text-sm text-[#8B7D6B] italic">Arquetipo sugerido para {{ clase.toLowerCase() }}: <b>Espadachín</b> · <b>Devoto Sanador</b> · <b>Sombra</b></div>
    </section>

    <section class="parchment-sheet relative border border-[#C2A980] rounded-sm p-6 shadow-md">
      <div class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-[#8B5A2B]"></div>
      <div class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-[#8B5A2B]"></div>
      <h2 class="font-tarzana text-xs uppercase tracking-widest text-[#D4AF37] mb-3">Paso 3 · Sugerencias del escriba</h2>
      <p class="font-minion text-sm text-[#5C4633] mb-4">
        Se recomiendan: <b>Canalización de energía</b>, <b>Dominio de Sanación</b> y la dote <b>Iniciativa Mejorada</b>. Build resultante: <b>{{ lineamiento }}</b>
      </p>
      <div class="flex flex-wrap gap-2">
        <button type="button" class="px-5 py-2.5 bg-[#D4AF37] text-[#1A1A1A] font-tarzana text-xs font-bold rounded-sm hover:brightness-110 transition" :disabled="generando" @click="generar">
          {{ generando ? 'Generando…' : 'Generar build' }}
        </button>
        <button type="button" class="px-5 py-2.5 border border-[#8B5A2B] text-[#8B5A2B] font-tarzana text-xs font-bold rounded-sm" :disabled="generando" @click="ajustarPreferencias">Ajustar preferencias</button>
      </div>
    </section>
  </main>
</template>