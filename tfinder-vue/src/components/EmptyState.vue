<script setup>
defineProps({
  title: {
    type: String,
    default: 'Todavía no hay mesas publicadas'
  },
  message: {
    type: String,
    default:
      'Cuando alguien abra una mesa, va a aparecer acá. Podés volver más tarde o crear la tuya.'
  }
})
</script>

<template>
  <section class="card-parchment p-10 text-center max-w-xl mx-auto rounded-[2px]" role="status">
    <div class="text-4xl mb-3 select-none" aria-hidden="true">🗝️</div>
    <p class="font-stat uppercase tracking-widest text-xs text-[#8B5A2B] font-bold mb-1">Sin resultados</p>
    <h2 class="font-mason font-bold text-xl text-[#8B5A2B]">{{ title }}</h2>
    <p class="font-narrative text-[#5A4A3A] mt-2">{{ message }}</p>
    <div class="mt-5 flex items-center justify-center gap-3">
      <slot />
    </div>
  </section>
</template>