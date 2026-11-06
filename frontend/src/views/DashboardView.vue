<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMembresias } from '@/services/membresias'
import { getActividad } from '@/services/actividad'
import { getEventosProximos } from '@/services/eventos'
import { getFeedPosts } from '@/services/feed'
import { useNotifications } from '@/composables/useNotifications'

const router = useRouter()
const { unreadCount, loadCount } = useNotifications()

const roleColor = (post) => (post.etiqueta === 'Guía de Build' ? 'tag--ember' : 'tag--ink')

const membresias = ref([])
const actividad = ref([])
const eventos = ref([])
const posts = ref([])
const isLoading = ref(true)
const error = ref(null)

async function load() {
  isLoading.value = true
  error.value = null
  try {
    const [m, a, e, p] = await Promise.all([
      getMembresias(),
      getActividad(),
      getEventosProximos(),
      getFeedPosts()
    ])
    membresias.value = m
    actividad.value = a
    eventos.value = e
    posts.value = p
    loadCount()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Ocurrió un error inesperado.'
  } finally {
    isLoading.value = false
  }
}

const activas = computed(() => membresias.value.filter((m) => m.estado !== 'Cerrada').length)
const sesionesProximas = computed(() => eventos.value.filter((e) => e.tipo.startsWith('Sesión')).length)

const tagEstado = (estado) => (estado === 'Abierta' ? 'tag--acid' : estado === 'Cerrada' ? 'tag--ember' : 'tag--ink')

const destinoMesa = (m) => (m.rol === 'gm' ? `/mesas/${m.id}/gestion` : `/mesas/${m.id}`)

const iconoActividad = (tipo) => {
  const svgs = {
    diario: `<path d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" stroke-linecap="round" stroke-linejoin="round"></path>`,
    espadas: `<path d="M3.75 13.5l10.5-10.5m0 0L17.25 6m-3-3l3 3M6.75 16.5l-3 3m0 0l3-3m-3 3h3m7.5-10.5l6 6m0 0l-3 3m3-3l-3-3" stroke-linecap="round" stroke-linejoin="round"></path>`,
    foro: `<path d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.502 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" stroke-linecap="round" stroke-linejoin="round"></path>`,
    estrella: `<path d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" stroke-linecap="round" stroke-linejoin="round"></path>`,
    reloj: `<path d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"></path>`
  }
  return svgs[tipo] ?? svgs.reloj
}

onMounted(() => load())
</script>

<template>
  <main class="dash" aria-label="Dashboard personal">
    <div class="dash-card">
      <div v-if="isLoading" class="cargando" role="status" aria-live="polite">
        <div class="sckels">
          <div class="linea linea--grande"></div>
          <div class="linea"></div>
          <div class="linea"></div>
          <div class="linea linea--mitad"></div>
        </div>
        <p class="label">Abriendo el Códex...</p>
      </div>

      <div v-else-if="error" class="cargando" role="alert">
        <p class="label contra">Error al cargar el dashboard</p>
        <p class="label">{{ error }}</p>
        <button type="button" class="btn reintentar" @click="load">Reintentar</button>
      </div>

      <template v-else>
        <!-- COLUMNA IZQUIERDA (70%) -->
        <section class="col-principal">
          <!-- Resumen -->
          <div class="resumen" aria-label="Resumen rápido">
            <div class="chip-numero">
              <p class="label resumen-clave">Campañas activas</p>
              <p class="num resumen-num">{{ activas }}</p>
            </div>
            <div class="chip-numero">
              <p class="label resumen-clave">Sesiones próximas</p>
              <p class="num resumen-num">{{ sesionesProximas }}</p>
            </div>
            <div class="chip-numero">
              <p class="label resumen-clave">Notificaciones</p>
              <p class="num resumen-num">{{ unreadCount }}</p>
            </div>
          </div>

          <!-- Mis Mesas -->
          <article aria-label="Mis mesas">
            <div class="seccion-cabecera">
              <h2 class="subtitulo">◆ Mis Mesas</h2>
              <span class="label conteo">
                {{ membresias.length }} {{ membresias.length === 1 ? 'Campaña activa' : 'Campañas activas' }}
              </span>
            </div>

            <div class="lista-mesas">
              <RouterLink
                v-for="m in membresias"
                :key="m.mesaId"
                :to="destinoMesa(m)"
                class="card fila-mesa"
              >
                <div class="fila-mesa-ident">
                  <div class="fila-mesa-chips">
                    <h3 class="mesa-nombre">{{ m.nombre }}</h3>
                    <span class="tag tag--ink">{{ m.sistema }}</span>
                    <span class="tag" :class="tagEstado(m.estado)">{{ m.estado }}</span>
                  </div>
                  <p class="label">
                    Rol:
                    <strong>{{ m.rol === 'gm' ? 'Director de Juego (GM)' : `Jugador (${m.personaje})` }}</strong>
                  </p>
                </div>
                <span class="text-link">Entrar →</span>
              </RouterLink>
            </div>
          </article>

          <!-- Actividad Reciente -->
          <article aria-label="Actividad reciente">
            <div class="seccion-cabecera">
              <h2 class="subtitulo">◆ Actividad Reciente</h2>
              <span class="label conteo">Actualizaciones de Campaña</span>
            </div>

            <div class="card lista-actividad">
              <div v-for="item in actividad" :key="item.id" class="actividad">
                <div class="crt icono-actividad">
                  <svg class="glifo-actividad" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true" v-html="iconoActividad(item.icono)"></svg>
                </div>
                <div class="actividad-cuerpo">
                  <p class="actividad-texto">
                    <strong v-if="item.fuerte">{{ item.fuerte }}</strong>
                    {{ item.cuerpo }}
                    <em v-if="item.citado">“{{ item.citado }}”</em>
                  </p>
                  <span class="label actividad-tiempo">{{ item.tiempo }}</span>
                </div>
              </div>
            </div>
          </article>

          <!-- Próximos Eventos -->
          <article aria-label="Próximos eventos">
            <div class="seccion-cabecera">
              <h2 class="subtitulo">◆ Próximos Eventos</h2>
              <span class="label conteo">Convocatorias y votaciones</span>
            </div>

            <div class="lista-eventos">
              <div v-for="ev in eventos" :key="ev.id" class="fila-evento">
                <div class="evento-ident">
                  <span class="tag" :class="ev.tipo.startsWith('Sesión') ? 'tag--acid' : 'tag--ember'">{{ ev.tipo }}</span>
                  <div class="min-w">
                    <p class="evento-titulo">{{ ev.titulo }}</p>
                    <p class="label">{{ ev.mesaNombre }} · {{ ev.nota }}</p>
                  </div>
                </div>
                <RouterLink :to="`/mesas/${ev.mesaId}`" class="text-link">
                  Ver mesa →
                </RouterLink>
              </div>
            </div>
          </article>
        </section>

        <!-- COLUMNA DERECHA (30%) -->
        <aside class="col-lateral" aria-label="Feed rápido">
          <div class="lateral-cuerpo">
            <div class="seccion-cabecera">
              <h2 class="subtitulo lateral-titulo">❖ Feed Rápido</h2>
            </div>

            <div class="posts">
              <div v-for="post in posts" :key="post.id" class="post">
                <div class="post-cabeza">
                  <div class="crt avatar">{{ post.iniciales }}</div>
                  <span class="post-autor">{{ post.autor }}</span>
                  <span class="label post-tiempo">{{ post.tiempo }}</span>
                </div>
                <p class="post-cuerpo">“{{ post.cuerpo }}”</p>
                <RouterLink to="/feed" class="text-link">Leer más en Feed →</RouterLink>
              </div>
            </div>

            <div class="lateral-bloque">
              <span class="label">Grimorio de Personajes</span>
              <div class="lateral-caja">
                <p class="label">Exporta y sincroniza tus fichas bajo licencia OGL v1.0a Paizo con un clic.</p>
                <RouterLink to="/builds/nuevo" class="btn btn--sm">
                  Crear Ficha / Build OGL
                </RouterLink>
              </div>
            </div>

          <div class="lateral-pie">
            <p class="label">Sistema D20 • Pathfinder RPG 1e</p>
          </div>
        </aside>
      </template>
    </div>

    <!-- FAB: Crear nueva mesa -->
    <button
      type="button"
      aria-label="Crear nueva mesa"
      class="fab"
      title="Crear nueva mesa"
      @click="router.push('/mesas/nueva')"
    >
      +
    </button>
  </main>
</template>

<style scoped>
.dash { max-width: 72rem; width: 100%; margin-inline: auto; padding: var(--space-md); display: block; }
.dash-card { background: var(--color-paper); border: var(--rule-bar) solid var(--color-rule); display: flex; flex-direction: column; overflow: hidden; min-height: 60vh; }
@media (min-width: 60rem) { .dash-card { flex-direction: row; align-items: stretch; } }
.contra { color: var(--color-error); }
.cargando { padding: var(--space-lg); text-align: center; display: grid; gap: var(--space-sm); justify-items: center; width: 100%; }
.sckels { width: 100%; max-width: 28rem; display: grid; gap: var(--space-2xs); }
.linea { height: 10px; border-radius: 999px; background: var(--color-paper-3); }
.linea--grande { width: 66%; height: 16px; }
.linea--mitad { width: 50%; }
.col-principal { display: flex; flex-direction: column; gap: var(--space-lg); padding: var(--space-md); width: 100%; }
@media (min-width: 60rem) { .col-principal { width: 70%; padding: var(--space-lg); } }
.resumen { display: grid; gap: var(--space-2xs); grid-template-columns: minmax(0, 1fr); }
@media (min-width: 40rem) { .resumen { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
.chip-numero { background: var(--color-ink); border: var(--rule-hair) solid var(--color-accent); padding: var(--space-sm); text-align: center; border-radius: var(--radius-card); }
.resumen-clave { text-transform: uppercase; letter-spacing: .14em; font-size: var(--text-xs); color: var(--color-accent); margin: 0; }
.resumen-num { color: var(--color-accent); font-family: var(--font-display); font-size: var(--text-xl); margin: var(--space-3xs) 0 0; font-weight: 700; }
.seccion-cabecera { display: flex; align-items: center; justify-content: space-between; gap: var(--space-2xs); border-bottom: var(--rule-hair) solid var(--color-rule); padding-bottom: var(--space-2xs); margin-bottom: var(--space-sm); }
.subtitulo { margin: 0; font-size: var(--text-title); color: var(--color-ink); }
.lateral-titulo { font-size: var(--text-md); text-transform: uppercase; }
.conteo { text-transform: uppercase; letter-spacing: .06em; }
.lista-mesas { display: grid; gap: var(--space-2xs); }
.fila-mesa { display: flex; flex-direction: column; gap: var(--space-2xs); border-left: var(--rule-bar) solid var(--color-accent); padding: var(--space-sm) var(--space-md); text-decoration: none; align-items: flex-start; }
@media (min-width: 40rem) { .fila-mesa { flex-direction: row; align-items: center; justify-content: space-between; min-height: 72px; } }
.fila-mesa:hover { background: var(--color-paper-3); }
.fila-mesa-ident { display: grid; gap: var(--space-3xs); min-width: 0; }
.fila-mesa-chips { display: flex; align-items: center; gap: var(--space-2xs); flex-wrap: wrap; }
.mesa-nombre { margin: 0; font-size: var(--text-md); font-weight: 700; color: var(--color-ink); }
.lista-actividad { padding: var(--space-sm) var(--space-md); display: grid; }
.actividad { padding-block: var(--space-sm); border-bottom: var(--rule-hair) solid var(--color-rule); display: flex; gap: var(--space-sm); align-items: flex-start; }
.actividad:last-child { border-bottom: 0; }
.icono-actividad { padding: var(--space-3xs); background: var(--color-paper-3); border: var(--rule-hair) solid var(--color-rule); color: var(--color-accent-2); flex-shrink: 0; }
.glifo-actividad { width: 16px; height: 16px; }
.actividad-cuerpo { display: flex; flex-direction: column; gap: var(--space-3xs); min-width: 0; flex: 1; }
@media (min-width: 40rem) { .actividad-cuerpo { flex-direction: row; justify-content: space-between; align-items: baseline; } }
.actividad-texto { margin: 0; color: var(--color-ink); font-size: var(--text-sm); line-height: 1.4; min-width: 0; }
.actividad-texto strong { color: var(--color-accent-2); }
.actividad-tiempo { white-space: nowrap; color: var(--color-muted); }
.lista-eventos { display: grid; gap: var(--space-2xs); }
.fila-evento { display: flex; flex-direction: column; gap: var(--space-2xs); border: var(--rule-hair) solid var(--color-rule); background: var(--color-paper); padding: var(--space-2xs) var(--space-sm); }
@media (min-width: 40rem) { .fila-evento { flex-direction: row; align-items: center; justify-content: space-between; } }
.evento-ident { display: flex; align-items: center; gap: var(--space-2xs); min-width: 0; }
.min-w { min-width: 0; }
.evento-titulo { margin: 0; font-weight: 700; color: var(--color-ink); }
.col-lateral { border-top: var(--rule-bar) solid var(--color-rule); width: 100%; display: flex; flex-direction: column; justify-content: space-between; gap: var(--space-md); padding: var(--space-md); background: var(--color-paper-2); }
@media (min-width: 60rem) { .col-lateral { width: 30%; border-top: 0; border-left: var(--rule-bar) solid var(--color-rule); } }
.lateral-cuerpo { display: grid; gap: var(--space-md); }
.posts { display: grid; gap: var(--space-md); }
.post { display: grid; gap: var(--space-3xs); }
.post-cabeza { display: grid; grid-template-columns: auto auto 1fr; gap: var(--space-2xs); align-items: center; }
.avatar { width: 22px; height: 22px; display: grid; place-content: center; border-radius: 999px; background: var(--color-accent-2); color: var(--color-paper); font-weight: 700; font-size: 10px; }
.post-autor { font-weight: 700; font-size: var(--text-sm); color: var(--color-ink); }
.post-tiempo { text-align: right; color: var(--color-muted); }
.post-cuerpo { margin: 0; font-size: var(--text-sm); color: var(--color-ink-2); font-style: italic; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.lateral-bloque { display: grid; gap: var(--space-2xs); border-top: var(--rule-hair) solid var(--color-rule); padding-top: var(--space-sm); }
.lateral-caja { padding: var(--space-sm); border: var(--rule-hair) solid var(--color-rule); text-align: center; display: grid; gap: var(--space-2xs); justify-items: center; }
.lateral-pie { border-top: var(--rule-hair) solid var(--color-rule); padding-top: var(--space-sm); text-align: center; }
.lateral-pie .label { margin: 0; text-transform: uppercase; letter-spacing: .14em; }
.reintentar { justify-self: center; }
.fab { position: fixed; bottom: 2rem; right: 2rem; width: 3.5rem; height: 3.5rem; border-radius: 999px; background: var(--color-accent); border: 2px solid var(--color-accent-ink); box-shadow: 0 4px 16px var(--color-shade), inset 0 1px 1px var(--color-paper); color: var(--color-accent-ink); font-size: 1.75rem; font-weight: 900; line-height: 1; display: grid; place-content: center; cursor: pointer; z-index: 50; padding-block-end: 2px; }
.fab:hover { transform: scale(1.05); }
</style>
