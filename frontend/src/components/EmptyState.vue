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
    <div class="icono" aria-hidden="true">🗝️</div>
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
