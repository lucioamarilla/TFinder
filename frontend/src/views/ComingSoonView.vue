<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { featureLabel } from '@/config/features'

const route = useRoute()
const titulo = computed(() => featureLabel(route.params.feature))
</script>

<template>
  <main class="espere">
    <section class="card panel" role="status">
      <p class="label linea">Funcionalidad en preparación</p>
      <h1 class="titulo">{{ titulo }}</h1>
      <p class="subtitulo">Próximamente</p>
      <p class="label">Esta función estará disponible próximamente.</p>
      <RouterLink to="/mesas" class="btn volver">
        Volver a explorar mesas
      </RouterLink>
    </section>
  </main>
</template>

<style scoped>
.espere { display: flex; align-items: center; justify-content: center; padding: var(--space-xl) var(--gutter); }
.panel { max-width: 42rem; width: 100%; text-align: center; padding: var(--space-xl) var(--space-lg); display: grid; gap: var(--space-2xs); justify-items: center; }
.linea { text-transform: uppercase; letter-spacing: .25em; color: var(--color-ink-2); }
.titulo { margin: var(--space-xs) 0 0; font-size: var(--text-display-s); color: var(--color-ink); }
.subtitulo { margin: 0; font-size: var(--text-lead); color: var(--color-ink-2); }
.volver { margin-top: var(--space-md); }
</style>
