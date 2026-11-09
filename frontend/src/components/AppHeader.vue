<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useShell } from '@/composables/useShell'
import { getMisMesas } from '@/services/mesas'
import ModalConfirmar from '@/components/modals/ModalConfirmar.vue'

const router = useRouter()
const { user, isAuthenticated, logout } = useAuth()
const { toggleMenu } = useShell()

const menuAbierto = ref(false)

// F1: header único — las fuentes de datos ya no son el simulador directo,
// pasan por la capa de servicios (dual-mode demo/api).
const misCampanas = ref([])

async function refrescarHeader() {
  if (!isAuthenticated.value) return
  try {
    misCampanas.value = (await getMisMesas()).map((m) => ({ mesaId: m.id, rol: m.miRol, mesa: m }))
  } catch {
    misCampanas.value = []
  }
}

onMounted(refrescarHeader)
// El header puede montarse sin router (vistas aisladas en specs).
router?.afterEach?.(() => refrescarHeader())

const modalSalir = ref(false)

async function confirmarSalida() {
  modalSalir.value = false
  menuAbierto.value = false
  await logout()
  router?.push('/')
}
</script>

<template>
  <nav class="nav-pill show" aria-label="Principal">
    <RouterLink class="wordmark" to="/">
      <img src="/assets/logo-tfinder.png" alt="Logo de TFinder" width="38" height="38" />
      TFinder
    </RouterLink>

    <!-- D-03: trigger del panel móvil; en desktop queda oculto por CSS -->
    <button type="button" class="menu-movil" data-test="menu-movil" aria-label="Abrir menú" @click="toggleMenu">☰</button>

    <!-- buscador global retirado (sin backend) -->
    <nav>
      <RouterLink to="/mesas">Explorar mesas</RouterLink>
      <RouterLink v-if="isAuthenticated" to="/mis-mesas">Mis mesas</RouterLink>
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

      <RouterLink class="nav-perfil" to="/perfil" aria-label="Tu perfil" :title="user.titulo" data-test="perfil-acceso">
        <span class="nav-avatar"><span class="num">{{ user.iniciales }}</span></span>
      </RouterLink>
      <button type="button" class="btn btn--secondary nav-login" data-test="cerrar-sesion" @click="modalSalir = true">Cerrar sesión</button>
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
</template>

<style scoped>
/* aria-current del nav vive en app.css; aquí solo el disparador móvil */
.menu-movil { background: transparent; border: var(--rule-hair) solid var(--color-rule); border-radius: var(--radius-card); cursor: pointer; padding: var(--space-2xs) var(--space-sm); font-weight: 700; min-height: 32px; min-width: 32px; }
/* móvil: el burger es el control primario de navegación; lleva mínimum de 44px de toque */
@media (max-width: 40rem) { .menu-movil { min-width: 44px; min-height: 44px; } }
@media (min-width: 60.0625rem) { .menu-movil { display: none; } }
</style>