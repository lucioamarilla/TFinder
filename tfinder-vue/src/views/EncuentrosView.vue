<script setup>
import { ref } from 'vue'
import { useToast } from '@/composables/useToast.js'
import { useRouter } from 'vue-router'

const toast = useToast()
const router = useRouter()

const nivelGrupo = ref('Nivel 4 (5 héroes)')
const dificultad = ref('Desafiante')
const entorno = ref('Ruinas subterráneas')

const resultado = ref(null)
const lanzando = ref(false)

const BESTIARIO = {
  'Ruinas subterráneas': [
    { nombre: 'Goblin lobo', cr: '1/2', xp: 850, porDefecto: true },
    { nombre: 'Worg', cr: '2', xp: 600, porDefecto: true },
    { nombre: 'Chamán goblin', cr: '1', xp: 400, porDefecto: true },
    { nombre: 'Gólem de arcilla', cr: '5', xp: 1600 },
    { nombre: 'Murciélago vampírico', cr: '3', xp: 800 }
  ],
  'Ciudad': [
    { nombre: 'Matón de la calle', cr: '1/2', xp: 400 },
    { nombre: 'Asesino encapuchado', cr: '3', xp: 800 },
    { nombre: 'Noble corrupto', cr: '2', xp: 600 },
    { nombre: 'Sobrino de la guardia', cr: '1', xp: 400 }
  ],
  'Bosque': [
    { nombre: 'Lobo gris', cr: '1', xp: 400 },
    { nombre: 'Oso pardo', cr: '4', xp: 1200 },
    { nombre: 'Hada tramposa', cr: '3', xp: 800 },
    { nombre: 'Sombra del bosque', cr: '5', xp: 1600 }
  ],
  'Pantano': [
    { nombre: 'Cocodrilo', cr: '2', xp: 600 },
    { nombre: 'Shambling Mound', cr: '6', xp: 2400 },
    { nombre: 'Boggard', cr: '1', xp: 400 },
    { nombre: 'Vampiro terrestre', cr: '4', xp: 1200 }
  ]
}

const NOMBRES_ENCUENTRO = ['El Nido del Worg', 'La Guarida del Chamán', 'Emboscada de Medianoche', 'El Puente Podrido', 'La Madriguera Abandonada']

const TONOS_BOTIN = ['1.220 gp', '890 gp', '1.540 gp', '675 gp', '2.050 gp']

const MODIFICADOR_DIFICULTAD = {
  'Trivial': -1,
  'Media': 0,
  'Desafiante': 1,
  'Épica': 2
}

function lanzar() {
  lanzando.value = true
  const d20 = 1 + Math.floor(Math.random() * 20)
  const criaturas = BESTIARIO[entorno.value] || BESTIARIO['Ruinas subterráneas']
  const seleccion = []
  const disponibles = criaturas.slice()
  if (dificultad.value === 'Desafiante') {
    const jefe = disponibles.splice(Math.min(disponibles.length - 1, 2), 1)[0] || disponibles[0]
    seleccion.push({ ...jefe, cantidad: 1 })
  }
  const metaXP = 800 * (1 + (MODIFICADOR_DIFICULTAD[dificultad.value.split(' ')[0]] || 0)) * 3
  while (seleccion.reduce((sum, c) => sum + c.cantidad * c.xp, 0) < metaXP && disponibles.length) {
    const criatura = disponibles[Math.floor(Math.random() * disponibles.length)]
    const cantidad = criatura.porDefecto ? 2 : 1
    const ya = seleccion.find((s) => s.nombre === criatura.nombre)
    if (ya) ya.cantidad += cantidad
    else seleccion.push({ ...criatura, cantidad })
  }
  resultado.value = {
    nombre: NOMBRES_ENCUENTRO[Math.floor(Math.random() * NOMBRES_ENCUENTRO.length)],
    d20,
    crSugerido: 4 + (MODIFICADOR_DIFICULTAD[dificultad.value.split(' ')[0]] || 0),
    grupo: seleccion,
    xpTotal: seleccion.reduce((sum, c) => sum + c.cantidad * c.xp, 0),
    botin: TONOS_BOTIN[Math.floor(Math.random() * TONOS_BOTIN.length)]
  }
  setTimeout(() => {
    lanzando.value = false
    toast.ok(`d20 = ${resultado.value.d20} · CR ${resultado.value.crSugerido} · ${resultado.value.grupo.map((g) => `${g.cantidad} ${g.nombre}`).join(', ')}.`)
  }, 450)
}

function anadirSesion() {
  toast.ok('Encuentro añadido a la próxima sesión.')
  router.push('/mis-mesas')
}

function guardarBestiario() {
  toast.ok(`«${resultado.value?.nombre || 'Encuentro'}» guardado en el bestiario de la mesa.`)
}
</script>

<template>
  <main class="tfinder-shell">
    <h1 class="font-mason text-3xl text-[#8B5A2B] font-bold mb-2">✦ Generador de Encuentros</h1>
    <p class="font-minion italic text-[#5C4633] mb-6">Forjá combates equilibrados contra el grupo según la guía CR de PF1e.</p>

    <section class="parchment-sheet relative border border-[#C2A980] rounded-sm p-6 mb-5 shadow-md">
      <div class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-[#8B5A2B]"></div>
      <div class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-[#8B5A2B]"></div>
      <div class="grid sm:grid-cols-3 gap-4">
        <div>
          <label for="enc-nivel" class="font-tarzana text-xs uppercase tracking-wider text-[#8B5A2B]">Nivel del grupo</label>
          <select id="enc-nivel" v-model="nivelGrupo" class="w-full py-2 px-3 rounded-sm bg-[#F4EAD6] border border-[#C2A980] font-minion text-sm">
            <option>Nivel 4 (5 héroes)</option>
            <option>Nivel 3</option>
            <option>Nivel 5</option>
            <option>Nivel 6</option>
          </select>
        </div>
        <div>
          <label for="enc-dif" class="font-tarzana text-xs uppercase tracking-wider text-[#8B5A2B]">Dificultad</label>
          <select id="enc-dif" v-model="dificultad" class="w-full py-2 px-3 rounded-sm bg-[#F4EAD6] border border-[#C2A980] font-minion text-sm">
            <option>Trivial</option>
            <option>Media</option>
            <option>Desafiante</option>
            <option>Épica</option>
          </select>
        </div>
        <div>
          <label for="enc-entorno" class="font-tarzana text-xs uppercase tracking-wider text-[#8B5A2B]">Entorno</label>
          <select id="enc-entorno" v-model="entorno" class="w-full py-2 px-3 rounded-sm bg-[#F4EAD6] border border-[#C2A980] font-minion text-sm">
            <option v-for="e in Object.keys(BESTIARIO)" :key="e">{{ e }}</option>
          </select>
        </div>
      </div>
      <div class="mt-4">
        <button type="button" class="px-5 py-2.5 bg-[#D4AF37] text-[#1A1A1A] font-tarzana text-xs font-bold rounded-sm hover:brightness-110 transition" :disabled="lanzando" @click="lanzar">
          {{ lanzando ? 'Tirando el d20…' : 'Lanzar encuentro' }}
        </button>
      </div>
    </section>

    <section v-if="resultado" class="parchment-sheet relative border border-[#C2A980] rounded-sm p-6 mb-5 shadow-md">
      <div class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-[#8B5A2B]"></div>
      <div class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-[#8B5A2B]"></div>
      <div class="flex items-center justify-between flex-wrap gap-2 mb-1">
        <h2 class="font-mason text-lg text-[#8B5A2B] font-bold">{{ resultado.nombre }}</h2>
        <span class="font-tarzana text-xs px-3 py-1 rounded-sm bg-[#6B8E23]/15 text-[#6B8E23] font-bold">CR {{ resultado.crSugerido }} · d20 {{ resultado.d20 }}</span>
      </div>
      <ul class="font-minion text-sm text-[#3A2E1F] space-y-1 mb-4">
        <li v-for="c in resultado.grupo" :key="c.nombre">
          <b>{{ c.nombre }}</b> ×{{ c.cantidad }} · CR {{ c.cr }} · {{ c.xp }} XP c/u
        </li>
      </ul>
      <div class="font-tarzana text-xs text-[#8B7D6B]">
        XP estimada: <b>{{ resultado.xpTotal }}</b> · Botín: <b>{{ resultado.botin }}</b> · escondrijo tras la guarida (percepción DC 15)
      </div>
    </section>

    <div class="flex flex-wrap gap-2">
      <button type="button" class="px-5 py-2.5 bg-[#8B5A2B] text-[#FDF8EE] font-tarzana text-xs font-bold rounded-sm hover:brightness-110" :disabled="!resultado" @click="anadirSesion">Añadir a la sesión</button>
      <button type="button" class="px-5 py-2.5 border border-[#8B5A2B] text-[#8B5A2B] font-tarzana text-xs font-bold rounded-sm" :disabled="!resultado" @click="guardarBestiario">Guardar en bestiario</button>
    </div>
  </main>
</template>