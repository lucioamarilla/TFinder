<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useShell } from '@/composables/useShell'
import { NAV } from '@/config/nav'

const router = useRouter()
const { role, logout } = useAuth()
const { mobileOpen, closeMenu } = useShell()

const nav = computed(() => NAV[role.value])

function go() {
  closeMenu()
}

function onLogout() {
  logout()
  go()
  router.push('/')
}
</script>

<template>
  <div v-if="mobileOpen" class="sim-panel" data-sim-panel @click.self="closeMenu">
    <nav class="sim-panel-nav" aria-label="Menú móvil">
      <RouterLink
        v-for="l in nav"
        :key="l.to"
        :to="l.to"
        :class="l.cta ? 'sim-cta' : ''"
        @click="go"
      >
        {{ l.label }}
      </RouterLink>
      <template v-if="role !== 'guest'">
        <RouterLink class="sim-panel-perfil" to="/perfil" @click="go">Mi perfil</RouterLink>
        <button type="button" class="sim-panel-btn sim-logout" @click="onLogout">Cerrar sesión</button>
      </template>
      <span v-else class="sim-badge">PF1e · OGL v1.0a</span>
    </nav>
  </div>
</template>