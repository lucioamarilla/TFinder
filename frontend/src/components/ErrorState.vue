<script setup>
defineProps({
  title: {
    type: String,
    default: 'No pudimos cargar las mesas'
  },
  message: {
    type: String,
    default:
      'El servicio de mesas no respondió. Revisá la conexión e intentá de nuevo.'
  },
  isNotFound: {
    type: Boolean,
    default: false
  }
})

defineEmits(['retry'])
</script>

<template>
  <section class="card vacio" role="alert">
    <p class="label error-linea">Error</p>
    <h2 class="titulo">{{ title }}</h2>
    <p class="mensaje">{{ message }}</p>
    <div class="acciones">
      <button
        v-if="!isNotFound"
        type="button"
        class="btn"
        @click="$emit('retry')"
      >
        Reintentar
      </button>
      <RouterLink v-else class="btn btn--secondary" to="/mesas">
        Volver al listado
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.vacio { max-width: 36rem; margin-inline: auto; padding: var(--space-lg); text-align: center; display: grid; gap: var(--space-2xs); justify-items: center; }
.error-linea { text-transform: uppercase; letter-spacing: .1em; color: var(--color-error); }
.titulo { margin: 0; font-size: var(--text-title); color: var(--color-ink); }
.mensaje { margin: 0; color: var(--color-ink-2); font-size: var(--text-md); }
.acciones { display: flex; align-items: center; gap: var(--space-sm); justify-content: center; margin-top: var(--space-sm); flex-wrap: wrap; }
</style>
