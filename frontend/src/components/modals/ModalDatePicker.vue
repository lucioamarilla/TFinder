<script setup>
import { ref, watch } from 'vue'
import BaseModal from '@/components/modals/BaseModal.vue'
const props = defineProps({
  open: Boolean,
  candidatos: { type: Array, default: () => [] },
  chip: { type: String, default: '' }
})
const emit = defineEmits(['close', 'accepted'])
const selected = ref(null)
watch(() => props.open, () => {
  if (props.open) selected.value = props.candidatos[0]?.value ?? null
})
</script>

<template>
  <BaseModal :open="open" @close="emit('close')">
    <div class="tf-dlg-card">
      <div class="tf-dlg-ico tf-dlg-ico--warn">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <rect x="3" y="4" width="18" height="18" rx="2" />
          <line x1="16" y1="2" x2="16" y2="6" />
          <line x1="8" y1="2" x2="8" y2="6" />
          <line x1="3" y1="10" x2="21" y2="10" />
          <circle cx="12" cy="15" r="2" />
        </svg>
      </div>
      <h2 class="tf-dlg-title">Proponer Fecha de Sesión</h2>
      <span v-if="chip" class="tf-dlg-chip">{{ chip }}</span>
      <div class="tf-pick-fechas" role="listbox" aria-label="Fechas candidatas">
        <button
          v-for="c in candidatos"
          :key="c.value"
          type="button"
          class="tf-pick-op"
          :class="{ 'tf-pick-op--sel': selected === c.value }"
          :aria-pressed="selected === c.value"
          @click="selected = c.value"
        >
          <span>{{ c.label }}</span><i>{{ c.detalle }}</i>
        </button>
      </div>
      <p class="tf-dlg-msg">Se convocará a los aventureros cuando al menos 3 miembros confirmen la fecha.</p>
      <div class="tf-dlg-fila">
        <button type="button" class="btn btn--secondary" @click="emit('close')">Cancelar</button>
        <button type="button" class="btn" @click="emit('accepted', selected)">Proponer Fecha</button>
      </div>
    </div>
  </BaseModal>
</template>

<style scoped>
.tf-dlg-ico { justify-self: start; }
.tf-pick-fechas { display: grid; gap: var(--space-2xs); }
.tf-pick-op { display: flex; justify-content: space-between; align-items: baseline; gap: var(--space-sm); padding: var(--space-2xs) var(--space-sm); border-radius: var(--radius-card); background: transparent; border: var(--rule-hair) solid var(--color-rule); color: var(--color-ink); font-family: var(--font-body); font-size: var(--text-sm); cursor: pointer; text-align: left; white-space: nowrap; transition: border-color var(--dur-micro) var(--ease-out), background-color var(--dur-micro) var(--ease-out); }
.tf-pick-op i { font-style: normal; color: var(--color-muted); font-size: var(--text-xs); flex: none; }
.tf-pick-op--sel { border-color: var(--color-accent); background: color-mix(in oklab, var(--color-accent) 12%, transparent); color: var(--color-ink); }
</style>