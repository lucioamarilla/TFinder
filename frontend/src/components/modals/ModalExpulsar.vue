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
    <div class="tf-dlg-card">
      <div class="tf-dlg-ico tf-dlg-ico--danger">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M16 17l5-5-5-5M21 12H9" />
          <path d="M14 21H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10" />
        </svg>
      </div>
      <h2 class="tf-dlg-title">Expulsar a {{ jugador.nombre }}</h2>
      <span class="tf-dlg-chip">{{ jugador.chip || jugador.rol }}</span>
      <p class="tf-dlg-msg">Se desvinculará su build y perderá el acceso a la mesa.</p>
      <div class="tf-dlg-fila">
        <button type="button" class="btn btn--secondary" @click="emit('close')">Cancelar</button>
        <button type="button" class="btn btn--danger" @click="emit('accepted')">Expulsar</button>
      </div>
    </div>
  </BaseModal>
</template>

<style scoped>
.tf-dlg-card { background: var(--color-paper-2); border: var(--rule-bar) solid var(--color-rule); border-radius: var(--radius-card); box-shadow: var(--shadow-card); padding: var(--space-lg); max-width: 440px; width: 100%; display: grid; gap: var(--space-sm); }
.tf-dlg-ico { width: 44px; height: 44px; display: grid; place-items: center; border: var(--rule-bar) solid var(--color-rule); border-radius: var(--radius-card); }
.tf-dlg-ico--danger { color: var(--color-error); border-color: var(--color-error); }
.tf-dlg-title { margin: 0; font-size: var(--text-title); color: var(--color-ink); }
.tf-dlg-chip { font-size: var(--text-xs); color: var(--color-muted); }
.tf-dlg-msg { margin: 0; font-size: var(--text-sm); color: var(--color-ink-2); }
.tf-dlg-fila { display: flex; justify-content: flex-end; gap: var(--space-sm); margin-top: var(--space-sm); flex-wrap: wrap; }
</style>