<script setup>
import { ref } from 'vue'
import { useToast } from '@/composables/useToast.js'

const toast = useToast()

const tags = ref([
  { nombre: 'DPS', usos: 24, verde: false },
  { nombre: 'Soporte', usos: 17, verde: false },
  { nombre: 'Tanque', usos: 11, verde: false },
  { nombre: 'Evocación', usos: 9, verde: false },
  { nombre: 'Hechicería', usos: 14, verde: false },
  { nombre: 'PF1e', usos: 46, verde: true }
])

const nuevoTag = ref('')

function crearTag() {
  const nombre = nuevoTag.value.trim().replace(/^#/, '')
  if (!nombre) {
    toast.error('Escribí un nombre para el tag.')
    return
  }
  if (tags.value.some((t) => t.nombre.toLowerCase() === nombre.toLowerCase())) {
    toast.info(`El tag «${nombre}» ya existe.`)
    return
  }
  tags.value.push({ nombre, usos: 0, verde: false })
  nuevoTag.value = ''
  toast.ok(`Tag «${nombre}» creado y disponible.`)
}

function aplicar(tag) {
  const aplicados = aplicadosSet.value
  if (aplicados.has(tag.nombre)) {
    aplicados.delete(tag.nombre)
    toast.info(`Tag «${tag.nombre}» retirado del build.`)
  } else {
    aplicados.add(tag.nombre)
    toast.ok(`Build etiquetada como «${tag.nombre}».`)
  }
}

const aplicadosSet = ref(new Set())
</script>

<template>
  <main class="tags-shell">
    <h1 class="titulo">✦ Gestor de Tags</h1>
    <p class="label intro">Etiquetá builds y publicaciones del feed para que el cónclave encuentre lo que busca.</p>

    <section class="card bloque">
      <h2 class="rotulo">Tags existentes</h2>
      <div class="chips">
        <span
          v-for="t in tags"
          :key="t.nombre"
          class="tag"
          :class="t.verde ? 'tag--acid' : 'tag--ink'"
        >{{ t.nombre }} · {{ t.usos }}</span>
      </div>
    </section>

    <section class="card bloque">
      <h2 class="rotulo">Crear tag</h2>
      <form class="alto-cargo" @submit.prevent="crearTag">
        <input v-model="nuevoTag" type="text" placeholder="ej. Cazarrecompensas" class="input" />
        <button type="submit" class="btn">Crear tag</button>
      </form>
    </section>

    <section class="card bloque">
      <h2 class="rotulo">Aplicar a build</h2>
      <div class="chips">
        <button
          v-for="t in tags.slice(0, 5)"
          :key="t.nombre"
          type="button"
          class="btn btn--sm"
          :class="aplicadosSet.has(t.nombre) ? '' : 'btn--secondary'"
          @click="aplicar(t)"
        >
          {{ aplicadosSet.has(t.nombre) ? '✓ ' : '+ ' }}{{ t.nombre }}
        </button>
      </div>
      <p class="label apuntados">{{ aplicadosSet.size }} tags aplicados a este build.</p>
    </section>
  </main>
</template>

<style scoped>
.tags-shell { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-lg); display: grid; gap: var(--space-md); align-items: start; }
.titulo { margin: 0 0 var(--space-2xs); font-size: var(--text-title); color: var(--color-ink); }
.intro { color: var(--color-ink-2); margin: 0 0 var(--space-xs); }
.bloque { display: grid; gap: var(--space-sm); justify-items: start; }
.rotulo { margin: 0; font-size: var(--text-sm); color: var(--color-ink-2); text-transform: uppercase; letter-spacing: .1em; }
.chips { display: flex; flex-wrap: wrap; gap: var(--space-2xs); }
.alto-cargo { display: flex; gap: var(--space-2xs); flex-wrap: wrap; width: 100%; }
.alto-cargo .input { flex: 1; min-width: 12rem; }
.apuntados { color: var(--color-ink-2); }
@media (max-width: 60rem) { .tags-shell { padding-top: 120px; } }
</style>
