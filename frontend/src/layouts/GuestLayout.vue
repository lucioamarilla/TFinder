<script setup>
// F1 · Auth independiente: SIN navegación de usuarios autenticados. Solo la
// marca (vuelve a la landing) y el contenido del formulario.
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="guest" data-test="guest-layout">
    <header class="guest-head">
      <RouterLink to="/" class="guest-brand" aria-label="Volver al inicio">
        <img src="/assets/logo-tfinder.png" alt="Logo de TFinder" width="38" height="38" />
        <span>TFinder</span>
      </RouterLink>
    </header>
    <main class="guest-main">
      <slot />
    </main>
    <footer class="guest-foot">
      <p>Sesión y credenciales verificadas por mesas-api.</p>
    </footer>
  </div>
</template>

<style scoped>
.guest { min-height: 100dvh; display: grid; grid-template-rows: auto minmax(0, 1fr) auto; }
.guest-head { display: flex; justify-content: center; padding: var(--space-lg) var(--gutter) var(--space-md); }
.guest-brand { display: inline-flex; align-items: center; gap: var(--space-2xs); text-decoration: none; color: var(--color-accent-2); font-weight: 900; font-size: var(--text-md); }
.guest-brand img { width: 38px; height: 38px; object-fit: contain; }
.guest-main { display: grid; place-items: center; padding: var(--space-lg) var(--gutter); }
.guest-foot { text-align: center; padding: var(--space-md); }
.guest-foot p { font-size: var(--text-xs); color: var(--color-muted); margin: 0; }
</style>
