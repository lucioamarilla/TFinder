<script setup>
defineProps({
  title: {
    type: String,
    default: 'Todavía no hay mesas publicadas'
  },
  message: {
    type: String,
    default:
      'Cuando alguien abra una mesa, va a aparecer acá. Podés volver más tarde o crear la tuya.'
  }
})
</script>

<template>
  <section class="card vacio" role="status">
    <div class="icono" aria-hidden="true">
  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6"/><path d="m15.5 7.5 3 3L22 7l-3-3"/></svg>
</div>
    <p class="label linea">Sin resultados</p>
    <h2 class="titulo">{{ title }}</h2>
    <p class="mensaje">{{ message }}</p>
    <div class="acciones">
      <slot />
    </div>
  </section>
</template>

<style scoped>
.vacio { max-width: 36rem; margin-inline: auto; padding: var(--space-lg); text-align: center; display: grid; gap: var(--space-2xs); justify-items: center; }
.icono { font-size: 2rem; user-select: none; }
.linea { text-transform: uppercase; letter-spacing: .1em; color: var(--color-accent-2); }
.titulo { margin: 0; font-size: var(--text-title); color: var(--color-ink); }
.mensaje { margin: 0; color: var(--color-ink-2); font-size: var(--text-md); }
.acciones { display: flex; align-items: center; gap: var(--space-sm); justify-content: center; margin-top: var(--space-sm); flex-wrap: wrap; }
</style>
