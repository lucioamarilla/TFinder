<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { featureLabel } from '@/config/features'

const route = useRoute()
const titulo = computed(() => featureLabel(route.params.feature))
</script>

<template>
  <main class="flex-grow flex items-center justify-center px-6 py-16">
    <section class="card-parchment w-full max-w-2xl text-center p-10 sm:p-14" role="status">
      <p class="font-tarzana uppercase tracking-[0.25em] text-xs font-bold text-[#8B7D6B]">.Functionalidad en preparación</p>
      <h1 class="font-mason text-3xl sm:text-4xl font-bold text-[#8B5A2B] mt-3">{{ titulo }}</h1>
      <p class="font-narrative text-lg text-[#5A4A3A] mt-4">Próximamente</p>
      <p class="font-minion text-[#5A4A3A] mt-2">Esta función estará disponible próximamente.</p>
      <RouterLink to="/mesas" class="btn-gold inline-flex px-6 py-3 mt-8 font-tarzana font-bold uppercase tracking-wider text-sm">
        Volver a explorar mesas
      </RouterLink>
    </section>
  </main>
</template>
