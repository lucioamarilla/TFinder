<template>
  <div class="auth-grid">
    <aside class="auth-side">
      <p class="label">La plataforma social de Pathfinder 1e</p>
      <div class="auth-figure well crt" style="height: 320px; display: grid; place-items: center;">
        <span class="figure-lg acid">20</span>
      </div>
      <p class="label">OGL 1.0a, Paizo Inc. 100% Pathfinder 1ª Edición</p>
    </aside>

    <main class="auth-form">
      <form class="auth-card" novalidate @submit.prevent="submit">
        <div>
          <h2>Iniciar sesión</h2>
          <p class="lead">Bienvenido de vuelta a la mesa.</p>
        </div>
        <div class="field">
          <label class="label" for="email">Email</label>
          <input class="input" :class="{ 'is-error': !okMail && touched }" id="email" v-model="email" type="email" placeholder="tu@email.com" autocomplete="email" />
          <p class="hint-error" :hidden="okMail || !touched">El correo electrónico no tiene un formato válido</p>
        </div>
        <div class="field">
          <label class="label" for="pass">Contraseña</label>
          <input class="input" :class="{ 'is-error': !okPass && touched }" id="pass" v-model="pass" type="password" placeholder="Ingresá tu contraseña" autocomplete="current-password" />
          <p class="hint-error" :hidden="okPass || !touched">La contraseña debe tener al menos 8 caracteres.</p>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: var(--text-sm);">
          <label style="display: flex; gap: var(--space-2xs); align-items: center;"><input type="checkbox" v-model="recordar" /> Recordarme</label>
          <RouterLink class="text-link" to="/recuperar">Olvidé mi contraseña</RouterLink>
        </div>
        <button class="btn" type="submit" :disabled="ocupado">Ingresar</button>
        <p class="hint-error" v-if="error" role="alert" data-test="error-sesion">{{ error }}</p>
        <p style="font-size: var(--text-sm); color: var(--color-muted);">¿No tenés cuenta? <RouterLink class="text-link" to="/registro">Registrate</RouterLink></p>
      </form>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { validarEmail, validarPassword } from '@/rules/auth'

const { login, isAuthenticated } = useAuth()
const router = useRouter()
const route = useRoute()

const email = ref('')
const pass = ref('')
const recordar = ref(true)
const touched = ref(false)
const error = ref(null)
const ocupado = ref(false)

const okMail = computed(() => validarEmail(email.value) === null)
const okPass = computed(() => validarPassword(pass.value) === null)

onMounted(() => {
  if (route.query.sesion === 'expirada') {
    error.value = 'Tu sesión terminó. Ingresá de nuevo.'
    // Limpia el parámetro para que no se repita al recargar.
    const { sesion, ...resto } = route.query
    router.replace({ path: route.path, query: resto })
  }
})

// El guard ya reenvía a /mesas a quien vuelve con sesión abierta.

async function submit() {
  touched.value = true
  error.value = null
  if (!okMail.value || !okPass.value) return
  ocupado.value = true
  try {
    await login({ email: email.value, password: pass.value })
    const destino = typeof route.query.redirect === 'string' && route.query.redirect ? route.query.redirect : '/mesas'
    router.push(destino)
  } catch (e) {
    error.value = e.mensaje || 'No se pudo iniciar la sesión.'
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
.auth-figure { position: relative; max-width: 480px; }
@media (max-width: 60rem) { .auth-grid { grid-template-columns: minmax(0, 1fr); } .auth-side { display: none; } }
</style>