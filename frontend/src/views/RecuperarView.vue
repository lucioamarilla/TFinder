<template>
  <div class="auth-grid">
    <aside class="auth-side">
      <p class="label">Recuperación de acceso</p>
      <div class="auth-figure well crt" style="height: 320px; display: grid; place-items: center;">
        <span class="figure-lg">1d4</span>
      </div>
      <p class="label">OGL 1.0a, Paizo Inc. 100% Pathfinder 1ª Edición</p>
    </aside>

    <main class="auth-form">
      <form class="auth-card" novalidate @submit.prevent="submit">
        <div>
          <h2>Recuperar contraseña</h2>
          <p class="lead">Te enviamos un enlace para restablecerla.</p>
        </div>
        <div class="field">
          <label class="label" for="email">Email</label>
          <input class="input" :class="{ 'is-error': !okM && touched }" id="email" v-model="email" type="email" placeholder="tu@email.com" autocomplete="email" />
          <p class="hint-error" :hidden="okM || !touched">El correo electrónico no tiene un formato válido</p>
        </div>
        <button class="btn" type="submit">Enviar enlace</button>
        <p style="font-size: var(--text-sm); color: var(--color-muted);"><RouterLink class="text-link" to="/login">Volver al login</RouterLink></p>
      </form>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { validarEmail } from '@/rules/auth'

const { recuperar } = useAuth()
const email = ref('')
const touched = ref(false)
const error = ref(null)
const ocupado = ref(false)
const okM = computed(() => validarEmail(email.value) === null)

async function submit() {
  touched.value = true
  error.value = null
  if (!okM.value) return
  ocupado.value = true
  try {
    await recuperar(email.value)
  } catch (e) {
    error.value = e.mensaje || 'No se pudo enviar el enlace.'
  } finally {
    ocupado.value = false
  }
}
</script>

<style scoped>
.auth-grid { min-height: 100dvh; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); }
.auth-side { background: var(--color-paper); border-right: var(--rule-bar) solid var(--color-rule); display: flex; flex-direction: column; justify-content: space-between; padding: var(--space-xl); overflow: hidden; position: relative; }
.auth-form { display: grid; place-items: center; padding: var(--space-xl); }
.auth-card { width: 100%; max-width: 420px; display: grid; gap: var(--space-md); }
@media (max-width: 60rem) { .auth-grid { grid-template-columns: minmax(0, 1fr); } .auth-side { display: none; } }
</style>