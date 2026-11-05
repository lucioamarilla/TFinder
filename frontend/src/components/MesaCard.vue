<script setup>
defineProps({ mesa: { type: Object, required: true } })
</script>

<template>
  <article class="card-parchment p-4 rounded-[2px] book-spine-accent pl-5 flex flex-col justify-between">
    <div>
      <div class="flex items-start justify-between gap-2 mb-1.5">
        <h3 class="font-mason text-[1.1rem] text-[#8B5A2B] font-bold leading-tight">{{ mesa.nombre }}</h3>
        <div class="flex items-center gap-1 shrink-0">
          <span class="font-tarzana text-[0.7rem] bg-[#1A1A1A] text-[#FDF8EE] font-bold px-1.5 py-0.5 rounded-[2px]">{{ mesa.sistema }}</span>
          <span class="font-tarzana text-[0.7rem] font-bold px-1.5 py-0.5 rounded-[2px]" :class="mesa.estado === 'Abierta' ? 'bg-[#6B8E23] text-[#FDF8EE]' : 'bg-[#8B1A1A] text-[#FDF8EE]'">{{ mesa.estado }}</span>
        </div>
      </div>

      <p class="font-minion italic text-[0.8rem] text-[#1A1A1A] mb-2">
        Dirigida por <span class="font-semibold text-[#8B5A2B]">{{ mesa.gm }}</span>
      </p>

      <div class="h-[1px] bg-[#8B1A1A]/40 w-full mb-2"></div>

      <p class="font-minion text-xs text-[#1A1A1A]/85 leading-relaxed line-clamp-3 mb-3">{{ mesa.lore }}</p>
    </div>

    <div class="pt-2 border-t border-[#C2A980]/50 flex items-center justify-between mt-2">
      <span class="font-tarzana text-[0.8rem] text-[#8B7D6B] font-semibold flex items-center gap-1">
        <span class="text-xs" aria-hidden="true">⚔</span> {{ mesa.jugadores }}/{{ mesa.plazas }} Jugadores
      </span>
      <RouterLink class="font-tarzana text-[0.8rem] font-bold btn-link-details uppercase tracking-wider" :to="`/mesas/${mesa.id}`">
        Ver detalles →
      </RouterLink>
    </div>
  </article>
</template>