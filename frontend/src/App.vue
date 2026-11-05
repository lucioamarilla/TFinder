<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import GuestLayout from '@/layouts/GuestLayout.vue'

const route = useRoute()
// F1: única fuente de decisión de layout. Landing y auth van desnudos,
// todo lo autenticado comparte la shell con el header único.
const layout = computed(() => {
  if (route.meta.layout === 'guest') return 'guest'
  if (route.name === 'landing') return 'landing'
  return 'shell'
})
</script>

<template>
  <RouterView v-if="layout === 'landing'" />
  <GuestLayout v-else-if="layout === 'guest'">
    <RouterView />
  </GuestLayout>
  <AppShell v-else>
    <RouterView />
  </AppShell>
</template>