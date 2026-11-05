<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { getMisMesas } from '@/services/mesas'
import { getNoLeidas, getNotificaciones } from '@/services/notificaciones'

const router = useRouter()
const { user, isAuthenticated, isAdmin, logout } = useAuth()

const menuAbierto = ref(false)
const consulta = ref('')

// F1: header único — las fuentes de datos ya no son el simulador directo,
// pasan por la capa de servicios (dual-mode demo/api).
const noLeidas = ref(0)
const frescas = ref([])
const misCampanas = ref([])

async function refrescarHeader() {
  if (!isAuthenticated.value) return
  try {
    noLeidas.value = await getNoLeidas()
    frescas.value = (await getNotificaciones()).slice(-5).reverse()
  } catch { /* sin datos aún: badge en 0 */ }
  try {
    misCampanas.value = (await getMisMesas()).map((m) => ({ mesaId: m.id, rol: m.miRol, mesa: m }))
  } catch {
    misCampanas.value = []
  }
}

onMounted(refrescarHeader)
// El header puede montarse sin router (vistas aisladas en specs).
router?.afterEach?.(() => refrescarHeader())

function buscar() {
  if (!consulta.value.trim()) return
  router.push({ path: '/busqueda', query: { q: consulta.value.trim() } })
}

async function salir() {
  menuAbierto.value = false
  await logout()
  router?.push('/')
}
</script>

<template>
  <nav class="nav-pill show" aria-label="Principal">
    <RouterLink class="wordmark" to="/">
      <img src="/assets/logo-tfinder.png" alt="Logo de TFinder" width="38" height="38" />
      Tfinder
    </RouterLink>

    <!-- buscador global retirado (sin backend) -->
    <nav>
      <RouterLink to="/mesas">Explorar mesas</RouterLink>
      <RouterLink to="/feed">Feed</RouterLink>
      <RouterLink v-if="isAuthenticated" to="/mis-mesas">Mis mesas</RouterLink>
      <RouterLink to="/builds">Builds</RouterLink>
      <!-- retirados: bestiario, compendio -->
    </nav>

    <template v-if="!isAuthenticated">
      <RouterLink class="btn btn--secondary nav-login" data-test="acceso-login" to="/login">Iniciar sesión</RouterLink>
      <RouterLink class="btn" to="/registro">Crear cuenta</RouterLink>
    </template>

    <template v-else>
      <details v-if="misCampanas.length > 0" class="nav-menu" data-test="selector-campanas">
        <summary>Mis campañas</summary>
        <div>
          <RouterLink v-for="c in misCampanas" :key="c.mesaId" :to="`/mesas/${c.mesaId}`">
            {{ c.mesa.nombre }} · {{ c.rol === 'master' ? 'Master' : 'Jugador' }}
          </RouterLink>
        </div>
      </details>

      <details class="nav-menu nav-campana">
        <summary data-test="campana" aria-label="Notificaciones">🔔
          <span v-if="noLeidas > 0" class="bell-badge" data-test="badge-no-leidas">{{ noLeidas }}</span>
        </summary>
        <div data-test="panel-campana">
          <p v-if="frescas.length === 0" class="nav-campana-empty">Silencio: nada sin leer.</p>
          <RouterLink v-for="n in frescas" :key="n.id" :to="n.link || '/notificaciones'" :class="{ sinLeer: n.nueva }">
            {{ n.texto }}
          </RouterLink>
          <RouterLink to="/notificaciones" class="nav-campana-todas">Ver todas las notificaciones</RouterLink>
        </div>
      </details>

      <RouterLink class="nav-avatar" to="/perfil" aria-label="Tu perfil" :title="user.titulo">
        <span class="num">{{ user.iniciales }}</span>
      </RouterLink>
      <details class="nav-menu" :open="menuAbierto" @toggle="menuAbierto = $event.target.open">
        <summary aria-label="Menú de sesión">Menú</summary>
        <div>
          <RouterLink to="/mis-mesas" @click="menuAbierto = false">Mis mesas</RouterLink>
          <RouterLink to="/builds" @click="menuAbierto = false">Builds</RouterLink>
          <RouterLink to="/notificaciones" @click="menuAbierto = false">Notificaciones</RouterLink>
          <RouterLink to="/perfil" @click="menuAbierto = false">Mi perfil</RouterLink>
          <!-- D10: la consola admin es 100% simulada; solo en modo demo -->
          <!-- retirado: consola admin -->
          <button type="button" data-test="cerrar-sesion" @click="salir">Cerrar sesión</button>
        </div>
      </details>
    </template>
  </nav>
</template>

<style scoped>
nav a[aria-current="page"] { color: var(--color-accent-2); border-bottom-color: var(--color-accent); }
.nav-menu button { width: 100%; text-align: left; padding: var(--space-2xs) var(--space-sm); font-weight: 700; font-size: var(--text-sm); color: var(--color-error); background: transparent; border: 0; cursor: pointer; }
.nav-menu button:hover { color: var(--color-error); text-decoration: underline; }
.nav-busqueda { flex: none; }
.nav-busqueda .input { height: 34px; width: clamp(100px, 22vw, 260px); font-size: var(--text-xs); padding-block: 0; }
.nav-campana summary { position: relative; }
.bell-badge { position: absolute; top: -6px; right: -8px; min-width: 16px; height: 16px; border-radius: 999px; background: var(--color-error); color: var(--color-paper); font: 700 10px/16px var(--font-body); text-align: center; padding-inline: 3px; }
.nav-campana-empty { padding: var(--space-2xs) var(--space-sm); font-size: var(--text-xs); color: var(--color-muted); }
.nav-campana div a { display: block; }
.nav-campana div a.sinLeer { color: var(--color-accent-2); }
@media (max-width: 60rem) { .nav-busqueda { display: none; } }
</style>
