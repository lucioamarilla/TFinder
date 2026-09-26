<script setup>
import { useAuth } from '@/composables/useAuth'
import { FOOTER_NAV } from '@/config/nav'
import { comingSoonPath, isFeatureEnabled } from '@/config/features'

const { role } = useAuth()

function navTarget(item) {
  return item.feature && !isFeatureEnabled(item.feature) ? comingSoonPath(item.feature) : item.to
}
</script>

<template>
  <footer class="sim-footer" :data-rol="role">
    <div class="sim-footer-inner">
      <div class="sim-footer-brand"><b>TFINDER</b><i>Pathfinder 1e Nexus</i></div>
      <nav class="sim-footer-nav" aria-label="Navegación de pie">
        <RouterLink v-for="l in FOOTER_NAV[role]" :key="l.to" :to="navTarget(l)">
          {{ l.label }}
          <span v-if="l.feature && !isFeatureEnabled(l.feature)" class="block text-[0.6rem] uppercase opacity-80">Próximamente</span>
        </RouterLink>
      </nav>
      <div class="sim-footer-legal">
        Bajo pauta de compatibilidad Pathfinder 1e · OGL v1.0a · Sin afiliación con Paizo Inc. · Prototipo de producto: datos e interacciones simuladas.
      </div>
    </div>
  </footer>
</template>