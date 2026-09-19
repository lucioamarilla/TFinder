<script setup>
import BaseModal from '@/components/modals/BaseModal.vue'

defineProps({
  open: Boolean,
  titulo: { type: String, default: '¿Confirmás esta acción?' },
  mensaje: { type: String, default: '' },
  variante: { type: String, default: 'confirm' },
  etiquetaOk: { type: String, default: 'Confirmar' },
  chip: { type: String, default: '' }
})

const emit = defineEmits(['close', 'accept'])
</script>

<template>
  <BaseModal :open="open" @close="emit('close')">
    <div class="sim-dlg-card">
      <div class="sim-dlg-ico" :class="{ 'sim-cobre': variante === 'confirm' }">
        <svg
          v-if="variante === 'danger'"
          width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"
        >
          <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
        <svg
          v-else
          width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"
        >
          <circle cx="12" cy="12" r="10" />
          <path d="M12 16v-4" />
          <path d="M12 8h.01" />
        </svg>
      </div>
      <h2>{{ titulo }}</h2>
      <span v-if="chip" class="sim-dlg-chip">{{ chip }}</span>
      <p>{{ mensaje }}</p>
      <div class="sim-dlg-fila">
        <button class="sdcb" @click="emit('close')">Cancelar</button>
        <button :class="variante === 'danger' ? 'sd-danger' : 'sdok'" @click="emit('accept')">{{ etiquetaOk }}</button>
      </div>
    </div>
  </BaseModal>
</template>