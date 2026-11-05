<script setup>
import BaseModal from '@/components/modals/BaseModal.vue'

defineProps({
  open: Boolean,
  jugador: { type: Object, default: () => ({ nombre: '', rol: '', chip: '' }) },
  mesaNombre: { type: String, default: 'esta mesa' }
})

const emit = defineEmits(['close', 'accepted'])
</script>

<template>
  <BaseModal :open="open" @close="emit('close')">
    <div class="sim-dlg-card">
      <div class="sim-dlg-ico">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M16 17l5-5-5-5M21 12H9" />
          <path d="M14 21H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10" />
        </svg>
      </div>
      <h2>Expulsar a {{ jugador.nombre }}</h2>
      <span class="sim-dlg-chip">{{ jugador.chip || jugador.rol }}</span>
      <p>Se desvinculará su build y perderá el acceso a la mesa. Jurisdicción canónica del Director de Juego.</p>
      <div class="sim-dlg-fila">
        <button class="sdcb" @click="emit('close')">Cancelar</button>
        <button class="sd-danger" @click="emit('accepted')">Expulsar</button>
      </div>
    </div>
  </BaseModal>
</template>