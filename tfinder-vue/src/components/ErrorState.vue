<script setup>
defineProps({
  title: {
    type: String,
    default: 'No pudimos cargar las mesas'
  },
  message: {
    type: String,
    default:
      'El servicio de mesas no respondió. Revisá la conexión e intentá de nuevo.'
  },
  isNotFound: {
    type: Boolean,
    default: false
  }
})

defineEmits(['retry'])
</script>

<template>
  <section class="card-parchment p-8 text-center max-w-xl mx-auto rounded-[2px]" role="alert">
    <p class="font-stat uppercase tracking-widest text-xs text-[#8B1A1A] font-bold mb-1">Error</p>
    <h2 class="font-mason font-bold text-xl text-[#8B5A2B]">{{ title }}</h2>
    <p class="font-narrative text-[#5A4A3A] mt-2">{{ message }}</p>
    <div class="mt-5 flex items-center justify-center gap-3">
      <button
        v-if="!isNotFound"
        type="button"
        class="btn-gold px-6 py-2.5 font-stat font-bold uppercase tracking-wider text-sm rounded-[2px]"
        @click="$emit('retry')"
      >
        Reintentar
      </button>
      <RouterLink v-else class="btn-copper-outline px-6 py-2.5 font-stat font-bold uppercase tracking-wider text-sm rounded-[2px]" to="/mesas">
        Volver al listado
      </RouterLink>
    </div>
  </section>
</template>