<script setup>
import { useAuth } from '@/composables/useAuth'
import { FOOTER_NAV } from '@/config/nav'

const { role } = useAuth()
</script>

<template>
  <footer class="sim-footer" :data-rol="role">
    <div class="sim-footer-inner">
      <div class="sim-footer-brand"><b>TFINDER</b><i>Pathfinder 1e Nexus</i></div>
      <nav class="sim-footer-nav" aria-label="Navegación de pie">
        <RouterLink v-for="l in FOOTER_NAV[role]" :key="l.to" :to="l.to">{{ l.label }}</RouterLink>
      </nav>
      <div class="sim-footer-legal">
        Bajo pauta de compatibilidad Pathfinder 1e · OGL v1.0a · Sin afiliación con Paizo Inc. · Prototipo de producto: datos e interacciones simuladas.
      </div>
    </div>
  </footer>
</template>