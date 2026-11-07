<template>
  <div class="auth-grid">
    <aside class="auth-side">
      <p class="label">La plataforma social de Pathfinder 1e</p>
      <div class="auth-figure well crt" style="height: 320px; display: grid; place-items: center;">
        <span class="figure-lg ember">1d20</span>
      </div>
      <p class="label">OGL 1.0a, Paizo Inc. 100% Pathfinder 1ª Edición</p>
    </aside>

    <main class="auth-form">
      <form class="auth-card" novalidate @submit.prevent="submit">
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
            <label><input type="radio" name="rol" value="jugador" v-model="rol" /><span>Jugador</span><span class="label">Postulás ficha y tirás dados</span></label>
            <label><input type="radio" name="rol" value="director" v-model="rol" /><span>Director de juego</span><span class="label">Publicás y dirigís mesas</span></label>
          </div>
        </div>
        <label style="display: flex; gap: var(--space-2xs); align-items: center; font-size: var(--text-sm);">
          <input type="checkbox" id="terminos" v-model="terminos" /> Acepto los términos y el uso de OGL de Paizo Inc.
        </label>
        <p class="hint-error" :hidden="terminos || !touched">Falta aceptar los términos.</p>
        <button class="btn" type="submit" :disabled="ocupado">Crear cuenta</button>
        <p class="hint-error" v-if="error" role="alert" data-test="error-registro">{{ error }}</p>
        <p style="font-size: var(--text-sm); color: var(--color-muted);">¿Ya tenés cuenta? <RouterLink class="text-link" to="/login">Ingresá</RouterLink></p>
      </form>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { validarEmail, validarPassword, validarNombre } from '@/rules/auth'

const { register } = useAuth()
const router = useRouter()

const usuario = ref('')
const email = ref('')
const pass = ref('')
const rol = ref('jugador')
const terminos = ref(false)
const touched = ref(false)
const error = ref(null)
const ocupado = ref(false)

const okU = computed(() => validarNombre(usuario.value) === null)
const okM = computed(() => validarEmail(email.value) === null)
const okP = computed(() => validarPassword(pass.value) === null)

async function submit() {
  touched.value = true
  error.value = null
  if (!terminos.value) return
  if (!(okU.value && okM.value && okP.value)) return
  ocupado.value = true
  try {
    await register({ nombre: usuario.value.trim(), email: email.value, password: pass.value, rol: rol.value })
    router.push('/mesas')
  } catch (e) {
    error.value = e.mensaje || 'No se pudo crear la cuenta.'
  } finally {
    ocupado.value = false
  }
}
</script>

<style scoped>
.auth-grid { min-height: 100dvh; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); }
.auth-side { background: var(--color-paper); border-right: var(--rule-bar) solid var(--color-rule); display: flex; flex-direction: column; justify-content: space-between; padding: var(--space-xl); overflow: hidden; position: relative; }
.auth-form { display: grid; place-items: center; padding: var(--space-xl); }
.auth-card { width: 100%; max-width: 460px; display: grid; gap: var(--space-md); }
.role-pick { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--space-sm); }
.role-pick label { display: grid; gap: var(--space-3xs); border: var(--rule-bar) solid var(--color-rule); border-radius: var(--radius-card); padding: var(--space-sm); cursor: pointer; font-weight: 700; font-size: var(--text-sm); }
.role-pick input { position: absolute; opacity: 0; }
.role-pick label:has(input:checked) { border-color: var(--color-accent); background: var(--color-paper-2); box-shadow: var(--shadow-card); }
.role-pick .label { font-weight: 400; }
@media (max-width: 60rem) { .auth-grid { grid-template-columns: minmax(0, 1fr); } .auth-side { display: none; } }
</style>