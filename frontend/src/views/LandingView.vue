<template>
  <div class="d20-runway" style="--d20-fg: var(--color-accent-2); --d20-bg: var(--color-paper); --d20-accent: var(--color-ink);">
    <ascii-d20 id="dado" result="random" scroll-height="100%" cy="0.6"></ascii-d20>
    <div class="hero-overlay hero">
      <div class="wrap">
        <h1 style="font-size: var(--text-display); max-width: 12ch; margin: 0 0 var(--space-md);">Encontrá tu mesa y tirá iniciativa</h1>
        <p class="lead" style="margin: 0 0 var(--space-lg);">Campañas de PF1e en español, fichas sincronizadas, un GM esperándote.</p>
        <div style="display: flex; gap: var(--space-md); flex-wrap: wrap;">
          <RouterLink class="btn" to="/mesas">Encontrar mesa</RouterLink>
          <RouterLink class="btn btn--secondary" to="/mesas/nueva">Publicá tu campaña</RouterLink>
        </div>
      </div>
    </div>
  </div>

  <nav class="nav-pill" aria-label="Principal">
    <RouterLink class="wordmark" to="/"><img src="/assets/logo-tfinder.png" alt="Logo de TFinder" width="38" height="38" style="width:38px;height:38px;object-fit:contain;">TFinder</RouterLink>
    <nav>
      <a href="#mesas">Explorar mesas</a>
      <a href="#comunidad">Comunidades</a>
      <RouterLink to="/mesas">Mesas abiertas</RouterLink>
    </nav>
    <!-- D-03: la landing respeta la sesión; la nav fija de invitado solo cuando corresponde -->
    <template v-if="!isAuthenticated">
      <RouterLink class="btn btn--secondary nav-login" to="/login">Iniciar sesión</RouterLink>
      <RouterLink class="btn" to="/registro">Crear cuenta</RouterLink>
    </template>
    <template v-else>
      <RouterLink class="nav-perfil" data-test="perfil-acceso" to="/perfil" :title="user?.titulo || 'Tu perfil'">
        <span class="nav-avatar"><span class="num">{{ user?.iniciales }}</span></span>
        <span class="nav-nombre">{{ user?.nombre }}</span>
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

  <section class="section wrap" id="mesa-viva">
    <h2>La partida, en vivo</h2>
    <!-- F1: sin cifras inventadas. Datos reales del backend con estados vacíos. -->
    <div class="grid-2">
      <article v-if="postDestacado" class="card post-card">
        <div class="votecell vote">
          <span class="count" style="font-size: var(--text-lg);" aria-label="Votos">{{ postDestacado.votos }}</span>
        </div>
        <div class="body">
          <p class="post-title" style="margin: 0;">{{ postDestacado.titulo }}</p>
          <p class="label" style="margin-bottom: var(--space-2xs);">Publicado por {{ postDestacado.autorNombre || postDestacado.autor }}<span v-if="postDestacado.comunidad"> en {{ postDestacado.comunidad }}</span></p>
          <p style="font-size: var(--text-sm); color: var(--color-ink-2);">{{ postDestacado.cuerpo }}</p>
          
        </div>
      </article>
      <div v-else class="card" style="padding: var(--space-lg);" data-test="vacio-post">
        <p class="label">El feed todavía está silencioso</p>
        <p style="font-size: var(--text-sm); color: var(--color-ink-2); margin-top: var(--space-2xs);">Cuando la comunidad publique, acá vas a ver la charla más votada.</p>
        
      </div>

      <div v-if="mesasAbiertas.length > 0" class="card" style="padding: var(--space-md);" data-test="landing-mesas-reales">
        <p class="label" style="margin-bottom: var(--space-2xs);">Mesas abiertas ahora</p>
        <RouterLink v-for="m in mesasAbiertas" :key="m.id" class="mesa-row" :to="`/mesas/${m.id}`">
          <div class="mesa-thumb crt">PF1e</div>
          <div>
            <p style="font-weight: 700; font-size: var(--text-sm); margin: 0;">{{ m.nombre }}</p>
            <p style="font-size: var(--text-xs); color: var(--color-muted); margin: 0;">{{ m.gm || 'Master pendiente' }}, {{ m.horario || 'A coordinar' }}</p>
          </div>
          <span class="num" style="font-size: var(--text-sm);">{{ m.jugadores }}/{{ m.plazas ?? '∞' }}</span>
        </RouterLink>
      </div>
      <div v-else class="card" style="padding: var(--space-lg);" data-test="vacio-mesas">
        <p class="label">No hay mesas abiertas</p>
        <p style="font-size: var(--text-sm); color: var(--color-ink-2); margin-top: var(--space-2xs);">Sé el primero: creá tu campaña y empezá a reclutar.</p>
        <RouterLink class="btn btn--secondary" to="/mesas/nueva" style="margin-top: var(--space-sm);">Publicá tu campaña</RouterLink>
      </div>
    </div>
  </section>

  <section class="section wrap" id="flujo">
    <h2>Cómo funciona</h2>
    <p class="lead" style="margin-bottom: var(--space-lg);">Cuatro movimientos hasta la primera tirada.</p>
    <div class="card">
      <div class="mesa-row step-row">
        <span class="figure-lg" style="font-size: var(--text-2xl);">01</span>
        <div><h3 style="margin: 0;">Creás tu mesa</h3><p style="font-size: var(--text-sm); color: var(--color-ink-2); margin: 0;">AP, nivel, Golarion y alineamientos.</p></div>
        <span class="tag tag--ink step-tag">4 min</span>
      </div>
      <div class="mesa-row step-row">
        <span class="figure-lg" style="font-size: var(--text-2xl);">02</span>
        <div><h3 style="margin: 0;">Postulan ficha</h3><p style="font-size: var(--text-sm); color: var(--color-ink-2); margin: 0;">Fichas auditadas contra el compendio.</p></div>
        <span class="tag tag--ink step-tag">Instantáneo</span>
      </div>
      <div class="mesa-row step-row cursor-row">
        <span class="figure-lg" style="font-size: var(--text-2xl); color: var(--color-accent-ink);">03</span>
        <div><h3 style="margin: 0; color: var(--color-accent-ink);">Cerrás con SeatMeter</h3><p style="font-size: var(--text-sm); margin: 0;">Cupo lleno, hilo privado automático.</p></div>
        <span class="num step-tag" style="font-size: var(--text-sm);">4/4</span>
      </div>
      <div class="mesa-row step-row">
        <span class="figure-lg" style="font-size: var(--text-2xl);">04</span>
        <div><h3 style="margin: 0;">Tirá iniciativa</h3><p style="font-size: var(--text-sm); color: var(--color-ink-2); margin: 0;">Foundry VTT, Roll20 o mesa presencial.</p></div>
        <span class="tag tag--acid step-tag">En vivo</span>
      </div>
    </div>
  </section>

  <section class="section wrap" id="mesas">
    <div style="display: flex; align-items: baseline; justify-content: space-between; gap: var(--space-md); flex-wrap: wrap; margin-bottom: var(--space-lg);">
      <h2 style="margin: 0;">Todas las mesas de la comunidad</h2>
      <RouterLink class="text-link" to="/mesas">Explorar mesas →</RouterLink>
    </div>
    <div class="card" style="padding: var(--space-md);">
      <div v-if="mesasAbiertas.length === 0" data-test="vacio-mesas-2" style="text-align: center; padding: var(--space-lg);">
        <p>Nadie abrió una mesa todavía. La primeras acciones de la comunidad son del master: creala y aparecés acá.</p>
        <RouterLink class="btn btn--secondary" to="/mesas/nueva" style="margin-top: var(--space-md);">Publicá tu campaña</RouterLink>
      </div>
      <RouterLink v-for="m in mesasAbiertas" :key="m.id" class="mesa-row" :to="`/mesas/${m.id}`">
        <div class="mesa-thumb crt">PF1e</div>
        <div>
          <p style="font-weight: 700; font-size: var(--text-sm); margin: 0;">{{ m.nombre }}</p>
          <p style="font-size: var(--text-xs); color: var(--color-muted); margin: 0;">{{ m.gm || 'Master pendiente' }}, {{ m.horario || 'A coordinar' }}</p>
        </div>
        <span class="num" style="font-size: var(--text-sm);">{{ m.jugadores }}/{{ m.plazas ?? '∞' }}</span>
      </RouterLink>
    </div>
  </section>

  <section class="section wrap" id="comunidad">
    <h2>La comunidad</h2>
    <p class="lead" style="margin-bottom: var(--space-lg);">Acá vive la memoria de la mesa: el feed, la wiki de campaña y el historial de sesiones.</p>
    <div class="grid-2">
      <div class="card" style="padding: var(--space-md);" data-test="comunidades-landing">
        <p class="label" style="margin-bottom: var(--space-2xs);">Comunidades activas</p>
        <p v-if="comunidades.length === 0" style="font-size: var(--text-sm); color: var(--color-ink-2);">
          Aún no hay comunidades. Publicá una nota en el feed y creá la primera.
        </p>
        <p v-for="c in comunidades" :key="c.id" style="font-size: var(--text-sm); margin: var(--space-3xs) 0;">
          
          <span class="label" style="margin-left: var(--space-2xs);">{{ c.cantidad }} {{ c.cantidad === 1 ? 'publicación' : 'publicaciones' }}</span>
        </p>
      </div>
      <div class="card" style="padding: var(--space-md);">
        <p class="label" style="margin-bottom: var(--space-2xs);">Tu primera mesa en 4 movimientos</p>
        <div class="thread">
          <div class="reply"><span class="num">01</span><p style="font-size: var(--text-sm); margin: 0;">Creás la mesa (él queda como Master).</p></div>
          <div class="reply level-2"><span class="num">02</span><p style="font-size: var(--text-sm); margin: 0;">Los jugadores postulan y vos aceptás.</p></div>
          <div class="reply level-2"><span class="num">03</span><p style="font-size: var(--text-sm); margin: 0;">Documentan sesiones en la bitácora y la wiki.</p></div>
          <div class="reply level-2"><span class="num">04</span><p style="font-size: var(--text-sm); margin: 0;">Todo queda archivado como historio de la campaña.</p></div>
        </div>
      </div>
    </div>
  </section>

  <section class="ember-band">
    <div class="wrap" style="display: grid; gap: var(--space-md);">
      <h2 class="display" style="font-size: var(--text-section); margin: 0; text-shadow: none;">Tus próximas sesiones empiezan acá</h2>
      <p style="margin: 0; font-size: var(--text-lead);">Sumate a la comunidad hispanohablante de Pathfinder 1e.</p>
      <div style="display: flex; gap: var(--space-md); flex-wrap: wrap;">
        <RouterLink class="btn" to="/mesas" style="box-shadow: 6px 6px 0 var(--color-accent-ink); border-color: var(--color-accent-ink);">Explorar mesas</RouterLink>
        <RouterLink class="btn btn--secondary" to="/mesas/nueva" style="color: var(--color-accent-ink); border-color: var(--color-accent-ink);">Publicá tu campaña</RouterLink>
      </div>
    </div>
  </section>

  <footer class="colophon">
    <div class="wrap cols">
      <div>
        <p style="display: flex; align-items: center; gap: var(--space-2xs); margin: 0 0 var(--space-2xs);"><img src="/assets/logo-tfinder.png" alt="Logo de TFinder" width="46" height="46" style="width:46px;height:46px;object-fit:contain;"><span class="display" style="font-size: var(--text-md); color: var(--color-accent-2);">TFinder</span></p>
        <p class="label">Encontrá tu mesa y tirá iniciativa</p>
      </div>
      <div>
        <p class="label" style="margin-bottom: var(--space-2xs);">Explorá</p>
        <p style="font-size: var(--text-sm);"><a class="text-link" href="#mesas">Mesas</a>, <a class="text-link" href="#comunidad">comunidades</a>, <a class="text-link" href="#flujo">cómo funciona</a></p>
      </div>
      <div>
        <p class="label" style="margin-bottom: var(--space-2xs);">Sistema</p>
        <p style="font-size: var(--text-sm); color: var(--color-muted);">Tema Arcade · OGL 1.0a, Paizo Inc.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { registerAsciiD20, initLandingWiring } from '@/utils/asciiD20'
import { getMesas } from '@/services/mesas'
import { useAuth } from '@/composables/useAuth'
import ModalConfirmar from '@/components/modals/ModalConfirmar.vue'

const router = useRouter()
const { user, isAuthenticated, logout } = useAuth()

const modalSalir = ref(false)

// D-03: cerrar sesión visible también en la landing (con confirmación).
async function confirmarSalida() {
  modalSalir.value = false
  await logout()
  router?.push('/')
}


// F1: 2.5 — nada de cifras inventadas; datos reales con estados vacíos.
const mesasAbiertas = ref([])
const postDestacado = ref(null)
const comunidades = ref([])

onMounted(async () => {
  document.documentElement.classList.add('js')
  registerAsciiD20()
  setTimeout(initLandingWiring, 0)

  try {
    const todas = await getMesas()
    mesasAbiertas.value = todas.filter((m) => String(m.estado ?? '').toLowerCase() === 'abierta').slice(0, 5)
  } catch { mesasAbiertas.value = [] }

})
</script>

<style scoped>
/* landing-specific CSS (subset) */
.wrap { max-width: var(--container); margin-inline: auto; padding-inline: var(--gutter); }
.section { padding-block: var(--section-gap-s); }
.section + .section { border-top: var(--rule-hair) solid var(--color-rule); padding-top: 0; }
h1, .display { font-family: var(--font-display); font-weight: var(--display-weight, 400); line-height: 1.02; text-transform: uppercase; letter-spacing: var(--tracking-display); text-shadow: -1.5px 0 0 var(--color-crt-r), 1.5px 0 0 var(--color-crt-c); }
h2 { font-family: var(--font-body); font-weight: 900; letter-spacing: -0.02em; line-height: 1; font-size: var(--text-section); margin: 0 0 var(--space-md); }
h3 { font-family: var(--font-body); font-weight: 900; letter-spacing: -0.02em; line-height: 1.1; font-size: var(--text-title); margin: 0 0 var(--space-2xs); }
.lead { font-size: var(--text-lead); color: var(--color-ink-2); max-width: 52ch; }
.label { font-weight: 700; font-size: var(--text-sm); color: var(--color-muted); }
.num { font-weight: 700; font-variant-numeric: tabular-nums; }
.post-title { font-family: var(--font-body); font-weight: 900; letter-spacing: -0.02em; line-height: 1.1; font-size: var(--text-lg); }
.figure-lg { font-family: var(--font-outlier); font-weight: 700; font-size: var(--text-display-s); line-height: 1; font-variant-numeric: tabular-nums; color: var(--color-ink); }
.figure-lg.acid { color: var(--color-accent-2); }
.figure-lg.ember { color: var(--color-accent); }
.vote { display: flex; flex-direction: column; align-items: center; gap: var(--space-3xs); }
.vote button { background: none; border: none; color: var(--color-muted); cursor: pointer; padding: var(--space-3xs); }
.vote .count { font-weight: 700; font-variant-numeric: tabular-nums; color: var(--color-ink); }
.post-card { display: grid; grid-template-columns: 56px minmax(0, 1fr); }
.post-card .votecell { padding: var(--space-sm); border-right: var(--rule-hair) solid var(--color-rule); }
.post-card .body { padding: var(--space-sm) var(--space-md); }
.seats { display: flex; gap: var(--space-2xs); align-items: center; }
.seats i { width: 10px; height: 10px; background: var(--color-accent-2); border: var(--rule-hair) solid var(--color-paper); }
.seats i.off { background: var(--color-paper-3); border-color: var(--color-rule); }
.thread { display: grid; gap: var(--space-sm); margin-top: var(--space-sm); }
.thread .reply { display: grid; grid-template-columns: 40px minmax(0, 1fr); gap: var(--space-sm); }
.thread .reply.level-2 { padding-left: var(--space-lg); border-left: var(--rule-hair) solid var(--color-rule); margin-left: var(--space-lg); }
.thread .reply.level-3 { padding: var(--space-3xs) var(--space-sm); margin-left: calc(var(--space-lg) * 2); }
.mesa-row { display: grid; grid-template-columns: 48px minmax(0, 1fr) auto; gap: var(--space-sm); align-items: center; padding: var(--space-sm); text-decoration: none; color: inherit; }
.mesa-row:hover { background: var(--color-paper-3); }
.mesa-row + .mesa-row { border-top: var(--rule-hair) solid var(--color-rule); }
.mesa-thumb { width: 48px; height: 48px; background: var(--color-paper-3); border: var(--rule-hair) solid var(--color-rule); display: grid; place-items: center; font-weight: 900; font-size: 12px; color: var(--color-muted); }
.step-row { display: grid; grid-template-columns: 80px minmax(0, 1fr) auto; }
@media (max-width: 60rem) { .step-row { grid-template-columns: 64px minmax(0, 1fr); } .step-row .step-tag { grid-column: 2; justify-self: start; } }
.crt { position: relative; isolation: isolate; }
.crt::after { content: ""; position: absolute; inset: 0; pointer-events: none; z-index: var(--z-base); background-image: repeating-linear-gradient(to right, color-mix(in oklab, var(--color-crt-r) 5%, transparent) 0 1px, color-mix(in oklab, var(--color-crt-g) 5%, transparent) 1px 2px, color-mix(in oklab, var(--color-crt-b) 5%, transparent) 2px 3px), repeating-linear-gradient(to bottom, transparent 0 2px, color-mix(in oklab, var(--color-shade) 16%, transparent) 2px 3px); }
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
/* estilos de nav-perfil/nav-nombre definidos globalmente en app.css */
.ember-band :focus-visible { outline-color: var(--color-accent-ink); }
.grid-2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--space-lg); align-items: start; }
.grid-hero { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); gap: var(--gap-columns); align-items: center; }
@media (max-width: 60rem) { .wrap { padding-inline: var(--space-md); } .grid-2, .grid-hero { grid-template-columns: minmax(0, 1fr); } .score-line { grid-template-columns: minmax(0, 1fr); } .score-line > div { border-inline-start: none; border-top: var(--rule-hair) solid var(--color-rule); } .score-line > div:first-child { border-top: none; } .thread .reply.level-2 { margin-left: var(--space-sm); padding-left: var(--space-sm); } .thread .reply.level-3 { margin-left: var(--space-md); } }
footer.colophon { border-top: var(--rule-bar) solid var(--color-rule); padding-block: var(--space-xl); }
footer.colophon .cols { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-lg); }
footer.colophon a { color: var(--color-ink-2); text-decoration: none; border-bottom: 2px solid var(--color-accent-2); }
@media (max-width: 60rem) { footer.colophon .cols { grid-template-columns: minmax(0, 1fr); } }
</style>