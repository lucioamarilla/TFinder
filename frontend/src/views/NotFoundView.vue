<template>
  <main class="nf">
    <div style="display: grid; gap: var(--space-md); justify-items: center;">
      <p class="figure-lg acid" style="font-size: 96px;">404</p>
      <h1 style="font-size: var(--text-section);">Esta cripta está vacía</h1>
      <p class="lead">La página que buscás no existe o fue movida.</p>
      <div style="display: flex; gap: var(--space-md); flex-wrap: wrap; justify-content: center;">
        <RouterLink class="btn" to="/">Volver al inicio</RouterLink>
        <RouterLink class="btn btn--secondary" to="/mesas">Explorar mesas</RouterLink>
      </div>
    </div>
  </main>
</template>

<script setup></script>

<style scoped>
.nf { min-height: 100dvh; display: grid; place-items: center; text-align: center; padding: var(--space-xl); }
</style>