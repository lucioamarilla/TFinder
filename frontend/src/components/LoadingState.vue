<script setup>
defineProps({
  message: {
    type: String,
    default: 'Reuniendo las mesas disponibles…'
  }
})
</script>

<template>
  <section class="flex flex-col items-center gap-4 py-10" role="status" aria-live="polite">
    <p class="font-stat uppercase text-xs tracking-widest text-[#8B5A2B] font-bold">Cargando</p>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 w-full max-w-3xl justify-items-center" aria-hidden="true">
      <div v-for="n in 4" :key="n" class="card-parchment w-full max-w-[340px] min-h-[200px] p-4 rounded-[2px] animate-pulse">
        <div class="w-2/3 h-4 bg-[#C2A980]/40 rounded mb-3"></div>
        <div class="w-full h-2 bg-[#C2A980]/25 rounded mb-2"></div>
        <div class="w-full h-2 bg-[#C2A980]/25 rounded mb-2"></div>
        <div class="w-1/2 h-2 bg-[#C2A980]/25 rounded"></div>
      </div>
    </div>
    <p class="font-narrative italic text-[#5A4A3A]">{{ message }}</p>
  </section>
</template>