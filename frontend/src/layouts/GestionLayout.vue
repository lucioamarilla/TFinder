<script setup>
// Gestión de campaña por tabs: contexto compartido para las vistas de gestion/*.
// F2 (2.4): GUARD de membresía — solo integrantes (master o jugador) en de la
// mesa; el backend ya devuelve 403 en cada dato, acá corregimos la UX.
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MesaGestionShell from '@/components/mesa/MesaGestionShell.vue'
import { useRolEnMesa } from '@/composables/useRolEnMesa'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const router = useRouter()
const { rolEn } = useRolEnMesa()
const { isAuthenticated } = useAuth()
const { toast } = useToast()

onMounted(async () => {
  if (!isAuthenticated.value) return // el guard global ya manda a /login
  const rol = await rolEn(route.params.id)
  if (!rol) {
    toast('No sos integrante de esa mesa: solo sus integrantes la administran.', 'error')
    router.replace('/mesas')
  }
})
</script>

<template>
  <MesaGestionShell :mesa-id="route.params.id">
    <RouterView />
  </MesaGestionShell>
</template>
