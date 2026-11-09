<script setup>
// Armadura compartida de las pantallas de sesión (login, registro, recuperar):
// la figura del dado a la izquierda y la tarjeta del formulario en el slot.
// Antes,LoginView/RegistroView/RecuperarView copiaban este CSS tres veces.
defineProps({
  figura: { type: String, default: '1d20' },
  figuraTono: { type: String, default: '' }
})
</script>

<template>
  <div class="auth-grid">
    <aside class="auth-side">
      <p class="label">La plataforma social de Pathfinder 1e</p>
      <div class="auth-figure well crt">
        <span class="figure-lg" :class="figuraTono">{{ figura }}</span>
      </div>
      <p class="label">OGL 1.0a, Paizo Inc. 100% Pathfinder 1ª Edición</p>
    </aside>

    <main class="auth-form">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.auth-grid { min-height: 100dvh; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); }
.auth-side { background: var(--color-paper); border-right: var(--rule-bar) solid var(--color-rule); display: flex; flex-direction: column; justify-content: space-between; padding: var(--space-xl); overflow: hidden; position: relative; }
.auth-figure { height: 320px; max-width: 480px; display: grid; place-items: center; }
@media (max-width: 60rem) { .auth-grid { grid-template-columns: minmax(0, 1fr); } .auth-side { display: none; } }
</style>
