<script setup>
const props = defineProps({
  comentario: { type: Object, required: true },
  nivel: { type: Number, default: 0 }
})

const TONOS = {
  oro: 'bg-[#D4AF37] text-[#1A1A1A] border-[#8B5A2B]',
  bronce: 'bg-[#9C6734] text-[#FDF8EE] border-[#573312]',
  verde: 'bg-[#6B8E23] text-[#FDF8EE] border-[#4F6A19]',
  garnet: 'bg-[#8B1A1A] text-[#FDF8EE] border-[#5E0F0F]',
  copper: 'bg-[#8B5A2B] text-[#FDF8EE] border-[#573312]',
  olive: 'bg-[#6B8E23] text-[#FDF8EE] border-[#4F6A19]'
}
</script>

<template>
  <article
    class="border border-[#E5D7C0] rounded-sm p-3"
    :class="nivel === 0 ? 'bg-[#FDF8EE]' : 'bg-[#F4EAD6]'"
  >
    <div class="flex gap-2.5">
      <span
        class="w-8 h-8 rounded-full border flex items-center justify-center font-mason text-[11px] font-bold flex-shrink-0"
        :class="TONOS[comentario.tono] || TONOS.bronce"
      >
        {{ comentario.iniciales }}
      </span>
      <div class="flex-grow min-w-0">
        <div class="flex items-center flex-wrap gap-2 text-[11px] font-tarzana">
          <b class="text-[#8B5A2B]">{{ comentario.autor }}</b>
          <span class="text-[#8B7D6B]">· {{ comentario.tiempo }}</span>
          <span class="ml-auto flex items-center gap-1 text-[#556B2F] font-bold" :aria-label="`${comentario.votos} votos`">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path clip-rule="evenodd" fill-rule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" />
            </svg>
            {{ comentario.votos }}
          </span>
        </div>
        <p class="font-minion text-sm text-[#332517] leading-relaxed mt-1.5">{{ comentario.texto }}</p>
        <div class="flex items-center gap-4 mt-2 text-[11px] font-tarzana">
          <button type="button" class="font-bold text-[#8B5A2B] hover:text-[#523315] transition-colors">
            Responder
          </button>
          <button
            v-if="comentario.bendicion"
            type="button"
            class="text-[#6B8E23] hover:text-[#4F6A19] transition-colors"
          >
            ✦ Otorgar Bendición
          </button>
        </div>

        <div v-if="comentario.respuestas && comentario.respuestas.length" class="mt-3 ml-2 pl-4 border-l-2 border-[#C2A980] space-y-3">
          <FeedComment
            v-for="respuesta in comentario.respuestas"
            :key="respuesta.id"
            :comentario="respuesta"
            :nivel="nivel + 1"
          />
        </div>
      </div>
    </div>
  </article>
</template>
