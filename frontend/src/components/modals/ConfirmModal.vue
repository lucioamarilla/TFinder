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
    <div class="tf-dlg-card">
      <div class="tf-dlg-ico" :class="{ 'tf-dlg-ico--warn': variante === 'confirm', 'tf-dlg-ico--danger': variante === 'danger' }">
        <svg v-if="variante === 'danger'" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
        <svg v-else width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 16v-4" />
          <path d="M12 8h.01" />
        </svg>
      </div>
      <h2 class="tf-dlg-title">{{ titulo }}</h2>
      <span v-if="chip" class="tf-dlg-chip">{{ chip }}</span>
      <p class="tf-dlg-msg">{{ mensaje }}</p>
      <div class="tf-dlg-fila">
        <button type="button" class="btn btn--secondary" @click="emit('close')">Cancelar</button>
        <button type="button" class="btn" :class="variante === 'danger' ? 'btn--danger' : ''" @click="emit('accept')">{{ etiquetaOk }}</button>
      </div>
    </div>
  </BaseModal>
</template>

<style scoped>
/* variación centrada posesión de este modal: el icono y el texto van al centro */
.tf-dlg-ico { justify-self: center; }
.tf-dlg-title, .tf-dlg-chip, .tf-dlg-msg { text-align: center; }
.tf-dlg-fila { justify-content: stretch; }
.tf-dlg-fila .btn { flex: 1; }
</style>