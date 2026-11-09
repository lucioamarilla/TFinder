<template>
  <AuthShell figura="1d4">
    <form v-if="paso === 1" class="auth-card" novalidate @submit.prevent="submit">
      <div>
        <h2>Recuperar contraseña</h2>
        <p class="lead">Ingresá tu email y te enviamos un código para restablecerla.</p>
      </div>
      <div class="field">
        <label class="label" for="email">Email</label>
        <input class="input" :class="{ 'is-error': !okM && touched }" id="email" v-model="email" type="email" placeholder="tu@email.com" autocomplete="email" />
        <p class="hint-error" :hidden="okM || !touched">El correo electrónico no tiene un formato válido</p>
      </div>
      <button class="btn" type="submit" :disabled="ocupado">Enviar código</button>
      <p class="label"><RouterLink class="text-link" to="/login">Volver al login</RouterLink></p>
    </form>
    <form v-else-if="paso === 2" class="auth-card" novalidate @submit.prevent="confirmar">
        <div>
          <h2>Código de recuperación</h2>
          <p class="lead">Si el correo existe, te enviamos un código. También revisá el spam.</p>
        </div>
        <div class="field">
          <label class="label" for="codigo">Código de verificación</label>
          <input class="input" :class="{ 'is-error': !okC && touchedCod }" id="codigo" v-model="codigo" inputmode="numeric" maxlength="6" placeholder="••••••" autocomplete="one-time-code" @input="soloDigitos" />
          <p class="hint-error" :hidden="okC || !touchedCod">El código tiene 6 dígitos</p>
        </div>
        <div class="field">
          <label class="label" for="nueva">Nueva contraseña</label>
          <input class="input" :class="{ 'is-error': !okP && touchedCod }" id="nueva" v-model="nueva" type="password" placeholder="Mínimo 8 caracteres" autocomplete="new-password" />
          <p class="hint-error" :hidden="okP || !touchedCod">La contraseña debe tener al menos 8 caracteres.</p>
        </div>
        <div class="field">
          <label class="label" for="confirmar">Confirmar contraseña</label>
          <input class="input" :class="{ 'is-error': !okConfirm && touchedCod }" id="confirmar" v-model="confirmarPass" type="password" placeholder="Repetí la contraseña" autocomplete="new-password" />
          <p class="hint-error" :hidden="okConfirm || !touchedCod">Las contraseñas no coinciden.</p>
        </div>
        <button class="btn" type="submit" :disabled="ocupado || !(okC && okP && okConfirm)">Cambiar contraseña</button>
        <button class="btn btn--secondary" type="button" :disabled="cooldown > 0 || ocupado" @click="reenviar" data-test="reenviar-codigo">
          {{ cooldown > 0 ? `Reenviar código (${cooldown}s)` : 'Reenviar código' }}
        </button>
        <Aviso v-if="error" tipo="error" data-test="error-recupero">{{ error }}</Aviso>
      </form>

      <div v-else class="auth-card">
        <div>
          <h2>Listo</h2>
          <p class="lead">La contraseña quedó actualizada. Entrá con la nueva.</p>
        </div>
        <RouterLink class="btn" to="/login">Ingresar</RouterLink>
      </div>
  </AuthShell>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { validarEmail, validarPassword } from '@/rules/auth'
import Aviso from '@/components/Aviso.vue'
import AuthShell from '@/components/AuthShell.vue'

const { recuperar, confirmarRecupero } = useAuth()

const paso = ref(1)
const email = ref('')
const touched = ref(false)
const error = ref(null)
const ocupado = ref(false)

// Paso 2
const codigo = ref('')
const nueva = ref('')
const confirmarPass = ref('')
const touchedCod = ref(false)
const cooldown = ref(0)
let temporizador = null

const okM = computed(() => validarEmail(email.value) === null)
const okC = computed(() => /^\d{6}$/.test(codigo.value))
const okP = computed(() => validarPassword(nueva.value) === null)
const okConfirm = computed(() => confirmarPass.value.length > 0 && confirmarPass.value === nueva.value)

function soloDigitos(e) {
  codigo.value = e.target.value.replace(/\D/g, '').slice(0, 6)
}

function arrancarCooldown(segundos = 60) {
  cooldown.value = segundos
  clearInterval(temporizador)
  temporizador = setInterval(() => {
    cooldown.value -= 1
    if (cooldown.value <= 0) clearInterval(temporizador)
  }, 1000)
}

onUnmounted(() => clearInterval(temporizador))

async function submit() {
  touched.value = true
  error.value = null
  if (!okM.value) return
  ocupado.value = true
  try {
    // Respuesta genérica del backend: no revela si el correo existe.
    await recuperar(email.value)
    email.value = String(email.value).trim().toLowerCase()
    paso.value = 2
    arrancarCooldown()
  } catch (e) {
    error.value = e.mensaje || 'No se pudo enviar el código.'
  } finally {
    ocupado.value = false
  }
}

async function reenviar() {
  error.value = null
  ocupado.value = true
  try {
    await recuperar(email.value) // reenvía con cooldown del backend
    arrancarCooldown()
  } catch (e) {
    error.value = e.mensaje || 'No se pudo reenviar el código.'
  } finally {
    ocupado.value = false
  }
}

async function confirmar() {
  touchedCod.value = true
  error.value = null
  if (!(okC.value && okP.value && okConfirm.value)) return
  ocupado.value = true
  try {
    await confirmarRecupero(email.value, codigo.value, nueva.value)
    paso.value = 3
  } catch (e) {
    error.value = e.mensaje || 'No se pudo restablecer la contraseña.'
  } finally {
    ocupado.value = false
  }
}
</script>

<style scoped>
/* la armadura vive en AuthShell.vue; aquí solo queda el formulario */
</style>
