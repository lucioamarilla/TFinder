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
    botin: 'A determinar por el GM'
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
  <main class="encuentros">
    <h1 class="titulo">✦ Generador de Encuentros</h1>
    <p class="label intro">Forjá combates equilibrados contra el grupo según la guía CR de PF1e.</p>

    <section class="card panel">
      <div class="selectores">
        <label class="field" for="enc-nivel">
          <span class="label">Nivel del grupo</span>
          <select id="enc-nivel" v-model="nivelGrupo" class="input">
            <option>Nivel 4 (5 héroes)</option>
            <option>Nivel 3</option>
            <option>Nivel 5</option>
            <option>Nivel 6</option>
          </select>
        </label>
        <label class="field" for="enc-dif">
          <span class="label">Dificultad</span>
          <select id="enc-dif" v-model="dificultad" class="input">
            <option>Trivial</option>
            <option>Media</option>
            <option>Desafiante</option>
            <option>Épica</option>
          </select>
        </label>
        <label class="field" for="enc-entorno">
          <span class="label">Entorno</span>
          <select id="enc-entorno" v-model="entorno" class="input">
            <option v-for="e in Object.keys(BESTIARIO)" :key="e">{{ e }}</option>
          </select>
        </label>
      </div>
      <div class="envio">
        <button type="button" class="btn" :disabled="lanzando" @click="lanzar">
          {{ lanzando ? 'Tirando el d20…' : 'Lanzar encuentro' }}
        </button>
      </div>
    </section>

    <section v-if="resultado" class="card panel">
      <div class="resultado-cabecera">
        <h2 class="titulo-resultado">{{ resultado.nombre }}</h2>
        <span class="tag tag--acid">CR {{ resultado.crSugerido }} · d20 {{ resultado.d20 }}</span>
      </div>
      <ul class="lista">
        <li v-for="c in resultado.grupo" :key="c.nombre">
          <strong>{{ c.nombre }}</strong> ×{{ c.cantidad }} · CR {{ c.cr }} · {{ c.xp }} XP c/u
        </li>
      </ul>
      <p class="label pie">
        XP estimada: <strong>{{ resultado.xpTotal }}</strong> · Botín: <strong>{{ resultado.botin }}</strong> · esconderijo tras la guarida (percepción DC 15)
      </p>
    </section>

    <div class="acciones">
      <button type="button" class="btn" :disabled="!resultado" @click="anadirSesion">Añadir a la sesión</button>
      <button type="button" class="btn btn--secondary" :disabled="!resultado" @click="guardarBestiario">Guardar en bestiario</button>
    </div>
  </main>
</template>

<style scoped>
.encuentros { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-lg); display: grid; gap: var(--space-md); align-items: start; }
.titulo { margin: 0 0 var(--space-2xs); font-size: var(--text-title); color: var(--color-ink); }
.intro { color: var(--color-ink-2); margin: 0 0 var(--space-xs); }
.panel { display: grid; gap: var(--space-sm); }
.selectores { display: grid; gap: var(--space-sm); grid-template-columns: minmax(0, 1fr); }
@media (min-width: 40rem) { .selectores { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
.field { display: grid; gap: var(--space-3xs); }
.selectores .input { width: 100%; }
.envio { display: flex; justify-content: flex-start; }
.resultado-cabecera { display: flex; align-items: center; justify-content: space-between; gap: var(--space-2xs); flex-wrap: wrap; }
.titulo-resultado { margin: 0; font-size: var(--text-md); color: var(--color-ink); }
.lista { margin: 0; padding-left: var(--space-lg); display: grid; gap: var(--space-3xs); color: var(--color-ink); font-size: var(--text-sm); }
.pie { margin: 0; color: var(--color-ink-2); display: block; }
.pie strong { color: var(--color-ink); }
.acciones { display: flex; gap: var(--space-2xs); flex-wrap: wrap; }
@media (max-width: 60rem) { .encuentros { padding-top: 120px; } }
</style>
