<template>
  <AuthShell figura="20" figura-tono="acid">
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
      <div class="fila-secundaria">
        <label class="choice"><input type="checkbox" v-model="recordar" /> Recordarme</label>
        <RouterLink class="text-link" to="/recuperar">Olvidé mi contraseña</RouterLink>
      </div>
      <button class="btn" type="submit" :disabled="ocupado">Ingresar</button>
      <Aviso v-if="error" tipo="error" data-test="error-sesion">{{ error }}</Aviso>
      <p class="label">¿No tenés cuenta? <RouterLink class="text-link" to="/registro">Registrate</RouterLink></p>
    </form>
  </AuthShell>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { validarEmail, validarPassword } from '@/rules/auth'
import Aviso from '@/components/Aviso.vue'
import AuthShell from '@/components/AuthShell.vue'

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
.fila-secundaria { display: flex; justify-content: space-between; align-items: center; gap: var(--space-sm); flex-wrap: wrap; }
</style>