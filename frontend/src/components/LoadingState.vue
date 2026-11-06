<script setup>
defineProps({
  message: {
    type: String,
    default: 'Reuniendo las mesas disponibles…'
  }
})
</script>

<template>
  <section class="cargando" role="status" aria-live="polite">
    <p class="label remarcada">Cargando</p>
    <div class="sckels" aria-hidden="true">
      <div v-for="n in 4" :key="n" class="card sckel">
        <div class="linea linea--grande"></div>
        <div class="linea"></div>
        <div class="linea"></div>
        <div class="linea linea--mitad"></div>
      </div>
    </div>
    <p class="subtitulo">{{ message }}</p>
  </section>
</template>

<style scoped>
.cargando { display: flex; flex-direction: column; align-items: center; gap: var(--space-md); padding-block: var(--space-lg); }
.remarcada { text-transform: uppercase; letter-spacing: .1em; color: var(--color-accent-2); }
.sckels { display: grid; grid-template-columns: repeat(1, minmax(0, 1fr)); gap: var(--space-md); width: 100%; max-width: 48rem; justify-items: center; }
@media (min-width: 40rem) { .sckels { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.sckel { width: 100%; max-width: 21rem; min-height: 12rem; padding: var(--space-md); display: grid; gap: var(--space-2xs); align-content: start; animation: pulso 1.4s ease-in-out infinite; }
.linea { height: 8px; border-radius: 999px; background: var(--color-paper-3); width: 100%; }
.linea--grande { height: 16px; width: 66%; margin-bottom: var(--space-2xs); }
.linea--mitad { width: 50%; }
@keyframes pulso { 0%, 100% { opacity: .75; } 50% { opacity: 1; } }
.subtitulo { color: var(--color-ink-2); font-style: italic; margin: 0; }
</style>
