<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useNotifications } from '@/composables/useNotifications'
import { useShell } from '@/composables/useShell'
import { NAV } from '@/config/nav'
import { onMounted } from 'vue'

const router = useRouter()
const { role, user, logout } = useAuth()
const { unreadCount, loadCount } = useNotifications()
const { mobileOpen: menuOpen, toggleMenu, closeMenu } = useShell()

const nav = computed(() => NAV[role.value])
const home = computed(() => (role.value === 'guest' ? '/' : role.value === 'admin' ? '/admin/moderacion' : '/dashboard'))

function onLogout() {
  logout()
  closeMenu()
  router.push('/')
}

onMounted(() => {
  if (role.value !== 'guest') loadCount()
})
</script>

<template>
  <header class="sim-header" :data-rol="role">
    <RouterLink class="sim-logo" :to="home"> <b>TFINDER</b><i>Pathfinder 1e Nexus</i> </RouterLink>

    <nav class="sim-nav" aria-label="Navegación principal">
      <RouterLink
        v-for="l in nav"
        :key="l.to"
        :to="l.to"
        :class="l.cta ? 'sim-cta' : ''"
        active-class="activo"
      >
        {{ l.label }}
      </RouterLink>
    </nav>

    <div class="sim-right">
      <span v-if="role === 'guest'" class="sim-badge">PF1e · OGL v1.0a</span>
      <template v-else>
        <span class="sim-badge">+ PF1e Compatible OGL</span>
        <RouterLink class="sim-bell" to="/notificaciones" title="Notificaciones">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
          <span v-if="unreadCount > 0" class="sim-count">{{ unreadCount }}</span>
        </RouterLink>
        <RouterLink class="sim-perfil" to="/perfil" active-class="activo">
          <span class="sim-avatar" :class="{ activo: $route.path === '/perfil' }">{{ user?.iniciales }}</span>
          <span class="sim-nombre"><b>{{ user?.nombre }}</b><i>{{ user?.titulo }}</i></span>
        </RouterLink>
        <button type="button" class="sim-logout" title="Cerrar sesión" @click="onLogout">Cerrar sesión</button>
      </template>
    </div>

    <button
      type="button"
      class="sim-menu-toggle"
      aria-label="Abrir menú de navegación"
      :aria-expanded="menuOpen"
      @click="toggleMenu"
    >
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
        <line x1="3" y1="6" x2="21" y2="6" />
        <line x1="3" y1="12" x2="21" y2="12" />
        <line x1="3" y1="18" x2="21" y2="18" />
      </svg>
    </button>
  </header>
</template>