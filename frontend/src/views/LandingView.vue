<template>
  <ascii-d20
    ref="dadoEl"
    dock="right"
    style="--d20-fg: var(--color-accent-2); --d20-bg: var(--color-paper); --d20-accent: var(--color-ink);"
    result="20"
    scroll-height="350vh"
  >
    <div class="hero-overlay hero show">
      <div class="wrap">
        <h1 style="font-size: var(--text-display); max-width: 12ch; margin: 0 0 var(--space-md);">Encontrá tu mesa y tirá iniciativa</h1>
        <p class="lead" style="margin: 0 0 var(--space-lg);">Mesas de Pathfinder 1ª edición en español: postulaciones gestionadas por el GM, fechas elegidas por votación del grupo, asistencia registrada y bitácora de campaña.</p>
        <div style="display: flex; gap: var(--space-md); flex-wrap: wrap;">
          <RouterLink class="btn" to="/mesas">Encontrar mesa</RouterLink>
          <RouterLink class="btn btn--secondary" to="/mesas/nueva">Publicá tu campaña</RouterLink>
        </div>
      </div>
    </div>
  </ascii-d20>

  <nav class="nav-pill show" aria-label="Principal">
    <RouterLink class="wordmark" to="/"><img src="/assets/logo-tfinder.png" alt="Logo de TFinder" width="38" height="38">TFinder</RouterLink>
    <nav>
      <a href="#funciones">Qué podés hacer</a>
      <a href="#flujo">Cómo funciona</a>
      <RouterLink to="/mesas">Explorar mesas</RouterLink>
    </nav>
    <!-- D-03: la landing respeta la sesión; la nav fija de invitado solo cuando corresponde -->
    <template v-if="!isAuthenticated">
      <RouterLink class="btn btn--secondary nav-login" to="/login">Iniciar sesión</RouterLink>
      <RouterLink class="btn" to="/registro">Crear cuenta</RouterLink>
    </template>
    <template v-else>
      <RouterLink class="nav-perfil" data-test="perfil-acceso" to="/perfil" :title="user?.titulo || 'Tu perfil'">
        <span class="nav-avatar"><span class="num">{{ user?.iniciales }}</span></span>
      </RouterLink>
      <button type="button" class="btn btn--secondary nav-login" data-test="cerrar-sesion-landing" @click="modalSalir = true">Cerrar sesión</button>
    </template>
  </nav>

  <ModalConfirmar
    :open="modalSalir"
    titulo="¿Cerrar sesión?"
    mensaje="Vas a salir de tu cuenta en TFinder."
    etiqueta-ok="Cerrar sesión"
    etiqueta-cancel="Cancelar"
    @close="modalSalir = false"
    @accept="confirmarSalida"
  />

  <section class="section wrap" id="funciones" data-test="funciones-landing">
    <h2>Qué podés hacer en TFinder</h2>
    <p class="lead" style="margin-bottom: var(--space-lg);">Todo lo que mostramos acá ya está en funcionamiento en la app.</p>
    <div class="landing-grid">
      <article class="card feature">
        <span class="figure-lg">01</span>
        <h3>Cuentas verificadas</h3>
        <p>Registro con código de seis dígitos por email, recuperación de contraseña por código y perfil editable.</p>
        <RouterLink class="text-link" :to="cuenta.enlace">{{ cuenta.texto }}</RouterLink>
      </article>
      <article class="card feature">
        <span class="figure-lg">02</span>
        <h3>Explorar mesas</h3>
        <p>Mirá las mesas de la comunidad con su ocupación y cupo, y pedí entrar con una postulación.</p>
        <RouterLink class="text-link" to="/mesas">Explorar mesas</RouterLink>
      </article>
      <article class="card feature">
        <span class="figure-lg">03</span>
        <h3>Creá tu campaña</h3>
        <p>Definí tono, horario, nivel inicial y cupo máximo. Tu mesa queda listada como abierta o cerrada.</p>
        <RouterLink class="text-link" to="/mesas/nueva">Publicá tu mesa</RouterLink>
      </article>
      <article class="card feature">
        <span class="figure-lg">04</span>
        <h3>Postulaciones y Llamado</h3>
        <p>El GM acepta o rechaza quiénes entran (y puede expulsar). Para reclutar más rápido, abrí un Llamado: una ventana con tiempo límite.</p>
      </article>
      <article class="card feature">
        <span class="figure-lg">05</span>
        <h3>Calendario con votación</h3>
        <p>El GM propone fechas, el grupo vota (con voto editable) y al confirmar la ganadora se genera la sesión.</p>
      </article>
      <article class="card feature">
        <span class="figure-lg">06</span>
        <h3>Sesiones y asistencia</h3>
        <p>Al confirmar la fecha se genera la sesión: cada jugador marca su asistencia y la mesa anota lo acontecido en la bitácora compartida.</p>
      </article>
    </div>
  </section>

  <section class="section wrap" id="flujo">
    <h2>Cómo funciona</h2>
    <p class="lead" style="margin-bottom: var(--space-lg);">De la cuenta vacía a la primera tirada.</p>
    <div class="card">
      <div class="mesa-row step-row">
        <span class="figure-lg" style="font-size: var(--text-2xl);">01</span>
        <div><h3 style="margin: 0;">Creá tu cuenta</h3><p style="font-size: var(--text-sm); color: var(--color-ink-2); margin: 0;">Email verificado con un código de seis dígitos.</p></div>
        <span class="tag tag--ink step-tag">Código por email</span>
      </div>
      <div class="mesa-row step-row">
        <span class="figure-lg" style="font-size: var(--text-2xl);">02</span>
        <div><h3 style="margin: 0;">Creá tu mesa o postulate</h3><p style="font-size: var(--text-sm); color: var(--color-ink-2); margin: 0;">Tono, horario, nivel y cupo; o buscá una mesa abierta y mandá tu postulación.</p></div>
        <span class="tag tag--ink step-tag">Nivel y cupo</span>
      </div>
      <div class="mesa-row step-row cursor-row">
        <span class="figure-lg" style="font-size: var(--text-2xl); color: var(--color-accent-ink);">03</span>
        <div><h3 style="margin: 0; color: var(--color-accent-ink);">Se arma el grupo</h3><p style="font-size: var(--text-sm); margin: 0;">El GM acepta postulaciones o abre un Llamado con ventana de tiempo. El cupo se cierra solo.</p></div>
        <span class="num step-tag" style="font-size: var(--text-sm);">GM decide</span>
      </div>
      <div class="mesa-row step-row">
        <span class="figure-lg" style="font-size: var(--text-2xl);">04</span>
        <div><h3 style="margin: 0;">Votan la fecha y jugá</h3><p style="font-size: var(--text-sm); color: var(--color-ink-2); margin: 0;">La fecha confirmada crea la sesión: asistencia y bitácora compartida.</p></div>
        <span class="tag tag--acid step-tag">Sesión + bitácora</span>
      </div>
    </div>
  </section>

  <section class="section wrap" id="mesas">
    <div style="display: flex; align-items: baseline; justify-content: space-between; gap: var(--space-md); flex-wrap: wrap; margin-bottom: var(--space-lg);">
      <h2 style="margin: 0;">Mesas abiertas ahora</h2>
      <RouterLink class="text-link" to="/mesas">Ver todas las mesas</RouterLink>
    </div>
    <div class="card" style="padding: var(--space-md);">
      <div v-if="mesasAbiertas.length === 0" data-test="vacio-mesas" style="text-align: center; padding: var(--space-lg);">
        <p>Todavía no hay mesas abiertas. La primera campaña de la comunidad aparecerá acá.</p>
        <RouterLink class="btn btn--secondary" to="/mesas/nueva" style="margin-top: var(--space-md);">Publicá tu campaña</RouterLink>
      </div>
      <div v-else data-test="landing-mesas-reales">
        <RouterLink v-for="m in mesasAbiertas" :key="m.id" class="mesa-row" :to="`/mesas/${m.id}`">
          <div class="mesa-thumb crt">PF1e</div>
          <div>
            <p style="font-weight: 700; font-size: var(--text-sm); margin: 0;">{{ m.nombre }}</p>
            <p style="font-size: var(--text-xs); color: var(--color-muted); margin: 0;">{{ m.gm || 'Master pendiente' }}, {{ m.horario || 'A coordinar' }}</p>
          </div>
          <span class="num" style="font-size: var(--text-sm);">{{ m.jugadores }}/{{ m.plazas ?? '∞' }}</span>
        </RouterLink>
      </div>
    </div>
  </section>

  <section class="ember-band">
    <div class="wrap" style="display: grid; gap: var(--space-md);">
      <h2 class="display" style="font-size: var(--text-section); margin: 0; text-shadow: none;">Tus próximas sesiones empiezan acá</h2>
      <p v-if="!isAuthenticated" style="margin: 0; font-size: var(--text-lead);">Creá tu cuenta verificada y sumate a las mesas de Pathfinder 1ª edición en español.</p>
      <p v-else style="margin: 0; font-size: var(--text-lead);">Seguí gestionando tu campaña o explorá qué mesas de la comunidad están abiertas.</p>
      <div style="display: flex; gap: var(--space-md); flex-wrap: wrap;">
        <RouterLink class="btn" :to="ctaPrincipal.to" style="box-shadow: 6px 6px 0 var(--color-accent-ink); border-color: var(--color-accent-ink);">{{ ctaPrincipal.texto }}</RouterLink>
        <RouterLink class="btn btn--secondary" to="/mesas" style="color: var(--color-accent-ink); border-color: var(--color-accent-ink);">Explorar mesas</RouterLink>
      </div>
    </div>
  </section>

  <footer class="colophon">
    <div class="wrap cols">
      <div>
        <p style="display: flex; align-items: center; gap: var(--space-2xs); margin: 0 0 var(--space-2xs);"><img src="/assets/logo-tfinder.png" alt="Logo de TFinder" width="46" height="46"><span class="display" style="font-size: var(--text-md); color: var(--color-accent-2);">TFinder</span></p>
        <p class="label">Encontrá tu mesa y tirá iniciativa</p>
      </div>
      <div>
        <p class="label" style="margin-bottom: var(--space-2xs);">Explorá</p>
        <p style="font-size: var(--text-sm);"><a class="text-link" href="#funciones">Qué podés hacer</a>, <a class="text-link" href="#flujo">cómo funciona</a>, <RouterLink class="text-link" to="/mesas">mesas abiertas</RouterLink>, <RouterLink class="text-link" to="/mesas/nueva">publicá tu mesa</RouterLink></p>
      </div>
      <div>
        <p class="label" style="margin-bottom: var(--space-2xs);">Sistema</p>
        <p style="font-size: var(--text-sm); color: var(--color-muted);">Tema Arcade · Pathfinder 1ª Ed. (OGL 1.0a, Paizo Inc.)</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import '@/components/ascii-d20.js'
import { getMesas } from '@/services/mesas'
import { useAuth } from '@/composables/useAuth'
import ModalConfirmar from '@/components/modals/ModalConfirmar.vue'

const router = useRouter()
const { user, isAuthenticated, logout } = useAuth()

const dadoEl = ref(null)
function onDado(e) {
  document.documentElement.dataset.intro = e.detail.progress >= 0.98 ? 'done' : 'playing'
}

const modalSalir = ref(false)

// D-03: cerrar sesión visible también en la landing (con confirmación).
async function confirmarSalida() {
  modalSalir.value = false
  await logout()
  router?.push('/')
}

// Enlaces de cuenta y CTA según sesión (el guard redirige a guest-only → /mesas).
const cuenta = computed(() => isAuthenticated.value
  ? { enlace: '/perfil', texto: 'Ampliar tu perfil' }
  : { enlace: '/registro', texto: 'Crear cuenta' })

const ctaPrincipal = computed(() => isAuthenticated.value
  ? { to: '/mis-mesas', texto: 'Ir a mis mesas' }
  : { to: '/registro', texto: 'Crear cuenta' })

// F1: 2.5 — nada de cifras inventadas; datos reales con estados vacíos.
const mesasAbiertas = ref([])

onMounted(async () => {
  document.documentElement.dataset.intro = 'playing'
  dadoEl.value?.addEventListener('d20-progress', onDado)

  try {
    const todas = await getMesas()
    mesasAbiertas.value = todas.filter((m) => String(m.estado ?? '').toLowerCase() === 'abierta').slice(0, 6)
  } catch { mesasAbiertas.value = [] }

})

onUnmounted(() => {
  dadoEl.value?.removeEventListener('d20-progress', onDado)
  delete document.documentElement.dataset.intro
})
</script>

<style scoped>
/* landing-specific CSS: solo lo que no existe ya en base/app (sin duplicados) */
.section { padding-block: var(--section-gap-s); }
.section + .section { border-top: var(--rule-hair) solid var(--color-rule); padding-top: 0; }
/* firma del hero: aberración cromática CRT sobre el título display */
h1 { text-shadow: -1.5px 0 0 var(--color-crt-r), 1.5px 0 0 var(--color-crt-c); text-wrap: balance; }
.lead { color: var(--color-ink-2); }
.landing-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-md); align-items: stretch; }
.feature { padding: var(--space-md); display: grid; gap: var(--space-2xs); align-content: start; }
.feature p { margin: 0; font-size: var(--text-sm); color: var(--color-ink-2); }
.feature .text-link { font-size: var(--text-sm); justify-self: start; }
.step-row { display: grid; grid-template-columns: 80px minmax(0, 1fr) auto; }
@media (max-width: 60rem) { .step-row { grid-template-columns: 64px minmax(0, 1fr); } .step-row .step-tag { grid-column: 2; justify-self: start; } }
.d20-runway { position: relative; display: grid; height: 220vh; }
.hero-overlay { grid-area: 1 / 1; position: sticky; top: -57px; height: 100dvh; display: flex; align-items: flex-end; pointer-events: none; }
.hero-overlay .wrap { width: 100%; pointer-events: none; padding-bottom: var(--space-3xl); }
.js .hero-overlay { opacity: 0; visibility: hidden; transition: opacity var(--dur-long) var(--ease-out), visibility 0s linear var(--dur-long); }
.js .hero-overlay.show { opacity: 1; visibility: visible; transition: opacity var(--dur-long) var(--ease-out); }
.js .hero-overlay.show .btn, .js .hero-overlay.show a { pointer-events: auto; }
.js .nav-pill { opacity: 0; visibility: hidden; transition: opacity var(--dur-long) var(--ease-out), visibility 0s linear var(--dur-long); }
.js .nav-pill.show { opacity: 1; visibility: visible; transition: opacity var(--dur-long) var(--ease-out); }
@media (max-width: 60rem) { .hero-overlay { align-items: flex-start; padding-top: 120px; } .hero-overlay .wrap { padding-bottom: 0; } }
.ember-band { background: var(--color-accent); color: var(--color-accent-ink); padding-block: var(--space-xl); }
/* estilos de nav-perfil definidos globalmente en app.css */
.ember-band :focus-visible { outline-color: var(--color-accent-ink); }
@media (max-width: 72rem) { .landing-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 60rem) { .wrap { padding-inline: var(--space-md); } .landing-grid { grid-template-columns: minmax(0, 1fr); } }
</style>

<style>
.nav-pill { transition: opacity .5s ease, visibility .5s ease; }
html[data-intro='playing'] .nav-pill { opacity: 0 !important; visibility: hidden !important; pointer-events: none !important; }
html[data-intro='done'] .nav-pill { opacity: 1 !important; visibility: visible !important; pointer-events: auto !important; }
</style>
