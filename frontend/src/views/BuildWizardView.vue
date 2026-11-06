<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast.js'
import { crearBuild } from '@/services/builds.js'
import { validarBuild } from '@/rules/builds.js'

const router = useRouter()
const toast = useToast()

const generando = ref(false)

const tipo = ref('personaje')
const nombre = ref('Héroe del Nexus')
const clase = ref('Clérigo')
const nivel = ref(1)
const detalle = ref('')

const atributos = ref([
  { etiqueta: 'FUE', valor: 14, fila: 0 },
  { etiqueta: 'DES', valor: 10, fila: 1 },
  { etiqueta: 'CON', valor: 12, fila: 2 },
  { etiqueta: 'INT', valor: 10, fila: 3 },
  { etiqueta: 'SAB', valor: 16, fila: 4 },
  { etiqueta: 'CAR', valor: 13, fila: 5 }
])

const lineamiento = computed(() => {
  const claseSegura = clase.value ?? ''
  const base = nombre.value.trim() || (claseSegura.toLowerCase().startsWith('clér') || claseSegura.toLowerCase().startsWith('cler') ? 'Héroe devoto' : 'Héroe del Nexus')
  return `${base} (${claseSegura || '—'} Nv ${nivel.value})`
})

function mod(valor) {
  const m = Math.floor((valor - 10) / 2)
  return m >= 0 ? `+${m}` : `${m}`
}

async function generar() {
  generando.value = true
  try {
    // VAL-44/45: clase obligatoria y atributos 3–18 antes de forjar la ficha
    const atributosObj = Object.fromEntries(atributos.value.map((r) => [r.etiqueta, Number(r.valor)]))
    const errores = validarBuild({ tipo: tipo.value, clase: clase.value, nivel: nivel.value, atributos: atributosObj, nombre: nombre.value, detalle: detalle.value })
    if (errores.length) {
      errores.forEach((mensaje) => toast.error(mensaje))
      generando.value = false
      return
    }
    const esPersonaje = tipo.value === 'personaje'
    const ficha = esPersonaje
      ? {
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
      : { cuerpo: detalle.value }
    const nuevo = await crearBuild({
      tipo: tipo.value,
      nombre: nombre.value.trim() || (esPersonaje ? 'Personaje sin nombre' : 'Creación sin nombre'),
      clase: esPersonaje ? clase.value : null,
      nivel: esPersonaje ? Number(nivel.value) : null,
      raza: esPersonaje ? 'Humano' : null,
      arquetipo: esPersonaje ? '' : null,
      rol: esPersonaje ? 'Personalizable' : null,
      alineamiento: esPersonaje ? 'N' : null,
      privacidad: 'borrador',
      detalle: detalle.value || (esPersonaje ? 'Progresión diseñada desde cero con el asistente.' : 'Creado con el asistente.'),
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
  <div class="app-grid">
    <main class="stack">
      <header>
        <h1>✦ Asistente de Creación de Build</h1>
        <p class="label">Guía paso a paso para forjar cualquier creación: personaje, objeto, lugar, criatura o nota.</p>
      </header>

      <section class="card">
        <h2 class="label" style="color: var(--color-accent); margin-bottom: var(--space-sm);">Paso 1 · Identidad</h2>
        <div class="grid sm:grid-cols-2 gap-4">
          <div class="field">
            <label for="wiz-tipo" class="label">Tipo de creación</label>
            <select id="wiz-tipo" v-model="tipo" class="input">
              <option value="personaje">Personaje</option>
              <option value="objeto">Objeto</option>
              <option value="lugar">Lugar</option>
              <option value="criatura">Criatura</option>
              <option value="nota">Nota</option>
            </select>
          </div>
          <div class="field">
            <label for="wiz-nombre" class="label">Nombre</label>
            <input id="wiz-nombre" v-model="nombre" type="text" placeholder="ej. Kyra Sol Devoto" class="input" />
          </div>
          <div v-if="tipo === 'personaje'" class="field">
            <label for="wiz-categoria" class="label">Clase</label>
            <div class="flex gap-2">
              <select id="wiz-categoria" v-model="clase" class="input">
                <option>Clérigo</option>
                <option>Guerrero</option>
                <option>Pícaro</option>
                <option>Mago</option>
                <option>Paladín</option>
                <option>Explorador</option>
                <option>Bárbaro</option>
                <option>Alquimista</option>
              </select>
              <select v-model.number="nivel" class="input">
                <option v-for="n in 20" :key="n" :value="n">Nvl {{ n }}</option>
              </select>
            </div>
          </div>
          <div v-if="tipo !== 'personaje'" class="field sm:col-span-2">
            <label for="wiz-detalle" class="label">Descripción / cuerpo</label>
            <textarea id="wiz-detalle" v-model="detalle" rows="4" class="input" placeholder="Describe la creación…"></textarea>
          </div>
        </div>
      </section>

      <section v-if="tipo === 'personaje'" class="card">
        <h2 class="label" style="color: var(--color-accent); margin-bottom: var(--space-sm);">Paso 2 · Atributos base</h2>
        <div class="flex flex-wrap gap-3">
          <div v-for="r in atributos" :key="r.etiqueta" class="well" style="padding: var(--space-xs); display: flex; align-items: center; gap: var(--space-2xs);">
            <b>{{ r.etiqueta }}</b>
            <input :data-attr="r.etiqueta" v-model.number="r.valor" type="number" min="7" max="20" class="input" style="width: 64px; text-align: center;" />
            <small :style="{ color: Number(mod(r.valor)) >= 2 ? 'var(--color-success, #6B8E23)' : 'var(--color-muted)' }">{{ mod(r.valor) }}</small>
          </div>
        </div>
        <p class="label" style="margin-top: var(--space-sm); font-style: italic;">Arquetipo sugerido para {{ (clase || '—').toLowerCase() }}: Espadachín · Devoto Sanador · Sombra</p>
      </section>

      <section class="card">
        <h2 class="label" style="color: var(--color-accent); margin-bottom: var(--space-sm);">Paso 3 · Sugerencias del escriba</h2>
        <p class="label" style="margin-bottom: var(--space-md);">
          Se recomiendan: Canalización de energía, Dominio de Sanación y la dote Iniciativa Mejorada. Build resultante: <b>{{ lineamiento }}</b>
        </p>
        <div class="flex flex-wrap gap-2">
          <button type="button" class="btn" :disabled="generando" @click="generar">
            {{ generando ? 'Generando…' : 'Generar build' }}
          </button>
          <button type="button" class="btn btn--secondary" :disabled="generando" @click="ajustarPreferencias">Ajustar preferencias</button>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-lg); align-items: start; }
.stack { display: grid; gap: var(--space-lg); }
@media (max-width: 60rem) { .app-grid { padding-top: 120px; } }
</style>