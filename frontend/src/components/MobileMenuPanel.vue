<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useShell } from '@/composables/useShell'
import { NAV } from '@/config/nav'
import { comingSoonPath, isFeatureEnabled } from '@/config/features'

const router = useRouter()
const { role, logout } = useAuth()
const { mobileOpen, closeMenu } = useShell()

const nav = computed(() => NAV[role.value])

function navTarget(item) {
  return item.feature && !isFeatureEnabled(item.feature) ? comingSoonPath(item.feature) : item.to
}

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
  <div v-if="mobileOpen" class="panel" data-test="panel-movil" @click.self="closeMenu">
    <nav class="panel-nav" aria-label="Menú móvil">
      <RouterLink
        v-for="l in nav"
        :key="l.to"
        :to="navTarget(l)"
        @click="go"
      >
        {{ l.label }}
        <span v-if="l.feature && !isFeatureEnabled(l.feature)" class="proximamente">Próximamente</span>
      </RouterLink>
      <template v-if="role !== 'guest'">
        <RouterLink class="perfil" to="/perfil" @click="go">Mi perfil</RouterLink>
        <button type="button" class="salir" @click="onLogout">Cerrar sesión</button>
      </template>
      <span v-else class="label lema-adicional">PF1e · OGL v1.0a</span>
    </nav>
  </div>
</template>

<style scoped>
.panel {
  position: fixed; inset: 0; z-index: 900;
  display: flex; flex-direction: column;
  background: var(--color-ink);
  border-top: var(--rule-bar) solid var(--color-accent);
  padding: var(--space-lg) var(--gutter);
}
.panel-nav { display: flex; flex-direction: column; gap: var(--space-3xs); }
.panel-nav a, .panel-nav button {
  color: var(--color-paper); text-decoration: none;
  padding: var(--space-2xs) var(--space-sm); border-radius: var(--radius-card);
  font-weight: 700; font-size: var(--text-md); text-align: left;
  background: transparent; border: 0; cursor: pointer;
}
.panel-nav a:hover, .panel-nav button:hover { background: var(--color-paper-3); color: var(--color-accent); }
.panel-nav .salir { color: var(--color-error); border: var(--rule-hair) solid var(--color-error); font-weight: 900; }
.panel-nav .salir:hover { background: var(--color-error); color: var(--color-paper); }
.proximamente { display: block; font-size: var(--text-xs); text-transform: uppercase; color: var(--color-muted); }
.perfil { color: var(--color-muted); }
.lema-adicional { padding-top: var(--space-sm); color: var(--color-muted); text-transform: uppercase; letter-spacing: .14em; font-size: var(--text-xs); }
</style>
