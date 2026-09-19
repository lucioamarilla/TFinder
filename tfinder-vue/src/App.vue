<script setup>
import { computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import GuestLayout from '@/layouts/GuestLayout.vue'
import AppLayout from '@/layouts/AppLayout.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'

const { role } = useAuth()
const layouts = { guest: GuestLayout, auth: AppLayout, admin: AdminLayout }
const Layout = computed(() => layouts[role.value])
</script>

<template>
  <component :is="Layout">
    <RouterView />
  </component>
</template>