<template>
  <AuthShell figura="1d20" figura-tono="ember">
    <!-- PASO 1: datos del registro -->
    <form v-if="paso === 1" class="auth-card" novalidate @submit.prevent="submit">
      <div>
        <h2>Crear cuenta</h2>
        <p class="lead">Menos de un minuto y estás tirando iniciativa.</p>
      </div>
      <div class="field">
        <label class="label" for="usuario">Nombre de usuario</label>
        <input class="input" :class="{ 'is-error': !okU && touched }" id="usuario" v-model="usuario" placeholder="valeros_de_sandpoint" autocomplete="username" />
        <p class="hint-error" :hidden="okU || !touched">El nombre de usuario es obligatorio</p>
      </div>
      <div class="field">
        <label class="label" for="email">Email</label>
        <input class="input" :class="{ 'is-error': !okM && touched }" id="email" v-model="email" type="email" placeholder="tu@email.com" autocomplete="email" />
        <p class="hint-error" :hidden="okM || !touched">El correo electrónico no tiene un formato válido</p>
      </div>
      <div class="field">
        <label class="label" for="pass">Contraseña</label>
        <input class="input" :class="{ 'is-error': !okP && touched }" id="pass" v-model="pass" type="password" placeholder="Mínimo 8 caracteres" autocomplete="new-password" />
        <p class="hint-error" :hidden="okP || !touched">La contraseña debe tener al menos 8 caracteres.</p>
      </div>
      <div class="field">
        <p class="label">Cómo jugás</p>
        <div class="role-pick">
          <label><input type="radio" name="rol" value="jugador" v-model="rol" /><span>Jugador</span><span class="role-deta">Postulás ficha y tirás dados</span></label>
          <label><input type="radio" name="rol" value="director" v-model="rol" /><span>Director de juego</span><span class="role-deta">Publicás y dirigís mesas</span></label>
        </div>
      </div>
      <label class="choice"><input type="checkbox" id="terminos" v-model="terminos" /> Acepto los términos y el uso de OGL de Paizo Inc.</label>
      <p class="hint-error" :hidden="terminos || !touched">Falta aceptar los términos.</p>
      <button class="btn" type="submit" :disabled="ocupado">Crear cuenta</button>
      <Aviso v-if="error" tipo="error" data-test="error-registro">{{ error }}</Aviso>
      <p class="label">¿Ya tenés cuenta? <RouterLink class="text-link" to="/login">Ingresá</RouterLink></p>
    </form>

    <!-- PASO 2: verificar el código enviado al mail -->
    <form v-else class="auth-card" novalidate @submit.prevent="verificar">
      <div>
        <h2>Verificá tu correo</h2>
        <p class="lead">
          Te enviamos un código de 6 dígitos a
          <strong>{{ email }}</strong>. Ingresalo para completar el registro.
        </p>
      </div>
      <div class="field">
        <label class="label" for="codigo">Código de verificación</label>
        <input class="input" :class="{ 'is-error': !okC && touchedCod }" id="codigo" v-model="codigo" inputmode="numeric" pattern="[0-9]*" maxlength="6" placeholder="••••••" autocomplete="one-time-code" @input="soloDigitos" />
        <p class="hint-error" :hidden="okC || !touchedCod">El código tiene 6 dígitos</p>
      </div>
      <button class="btn" type="submit" :disabled="!okC || ocupado">Verificar y crear cuenta</button>
      <button class="btn btn--secondary" type="button" :disabled="cooldown > 0 || ocupado" @click="reenviar" data-test="reenviar-codigo">
        {{ cooldown > 0 ? `Reenviar código (${cooldown}s)` : 'Reenviar código' }}
      </button>
      <Aviso v-if="error" tipo="error" data-test="error-codigo">{{ error }}</Aviso>
      <p class="label"><RouterLink class="text-link" to="/login">Volver al login</RouterLink></p>
    </form>
  </AuthShell>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { validarEmail, validarPassword, validarNombre } from '@/rules/auth'
import Aviso from '@/components/Aviso.vue'
import AuthShell from '@/components/AuthShell.vue'

const { register, verificarRegistro, reenviarRegistro } = useAuth()
const router = useRouter()

const paso = ref(1)
const usuario = ref('')
const email = ref('')
const pass = ref('')
const rol = ref('jugador')
const terminos = ref(false)
const touched = ref(false)
const error = ref(null)
const ocupado = ref(false)

// Paso 2
const codigo = ref('')
const touchedCod = ref(false)
const cooldown = ref(0)
let temporizador = null

const okU = computed(() => validarNombre(usuario.value) === null)
const okM = computed(() => validarEmail(email.value) === null)
const okP = computed(() => validarPassword(pass.value) === null)
const okC = computed(() => /^\d{6}$/.test(codigo.value))

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
  if (!terminos.value) return
  if (!(okU.value && okM.value && okP.value)) return
  ocupado.value = true
  try {
    const resultado = await register({ nombre: usuario.value.trim(), email: email.value, password: pass.value, rol: rol.value })
    if (resultado?.pendiente) {
      // Modo API: la cuenta nace al verificar el código del mail (paso 2).
      email.value = String(email.value).trim().toLowerCase()
      paso.value = 2
      arrancarCooldown()
      return
    }
    // Modo demo: register ya instaló la sesión.
    router.push('/mesas')
  } catch (e) {
    error.value = e.mensaje || 'No se pudo crear la cuenta.'
  } finally {
    ocupado.value = false
  }
}

async function reenviar() {
  error.value = null
  ocupado.value = true
  try {
    await reenviarRegistro(email.value)
    arrancarCooldown()
  } catch (e) {
    error.value = e.mensaje || 'No se pudo reenviar el código.'
  } finally {
    ocupado.value = false
  }
}

async function verificar() {
  touchedCod.value = true
  error.value = null
  if (!okC.value) return
  ocupado.value = true
  try {
    await verificarRegistro(email.value, codigo.value)
    router.push('/mesas')
  } catch (e) {
    error.value = e.mensaje || 'No se pudo verificar el código.'
  } finally {
    ocupado.value = false
  }
}
</script>

<style scoped>
.role-pick { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--space-sm); }
.role-pick label { display: grid; gap: var(--space-3xs); border: var(--rule-bar) solid var(--color-rule); border-radius: var(--radius-card); padding: var(--space-sm); cursor: pointer; font-weight: 700; font-size: var(--text-sm); }
.role-pick input { position: absolute; opacity: 0; }
.role-pick label:has(input:checked) { border-color: var(--color-accent); background: var(--color-paper-2); box-shadow: var(--shadow-card); }
.role-pick .role-deta { font-weight: 400; font-size: var(--text-xs); color: var(--color-muted); min-width: 10em; }
</style>
