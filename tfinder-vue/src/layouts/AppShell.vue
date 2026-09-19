<script setup>
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import MobileMenuPanel from '@/components/MobileMenuPanel.vue'
import ToastHost from '@/components/ToastHost.vue'
</script>

<template>
  <AppHeader />
  <MobileMenuPanel />
  <ToastHost />
  <main class="tf-main">
    <slot />
  </main>
  <AppFooter />
</template>