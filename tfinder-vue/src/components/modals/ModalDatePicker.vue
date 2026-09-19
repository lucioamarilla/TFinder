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

watch(
  () => props.open,
  () => {
    if (props.open) selected.value = props.candidatos[0]?.value ?? null
  }
)
</script>

<template>
  <BaseModal :open="open" @close="emit('close')">
    <div class="sim-dlg-card">
      <div class="sim-dlg-ico sim-cobre">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <rect x="3" y="4" width="18" height="18" rx="2" />
          <line x1="16" y1="2" x2="16" y2="6" />
          <line x1="8" y1="2" x2="8" y2="6" />
          <line x1="3" y1="10" x2="21" y2="10" />
          <circle cx="12" cy="15" r="2" />
        </svg>
      </div>
      <h2>Proponer Fecha de Sesión</h2>
      <span v-if="chip" class="sim-dlg-chip">{{ chip }}</span>
      <div class="sim-pick-fechas" role="listbox" aria-label="Fechas candidatas">
        <button
          v-for="c in candidatos"
          :key="c.value"
          type="button"
          class="sim-pick-op"
          :class="{ 'sim-votado': selected === c.value }"
          :aria-pressed="selected === c.value"
          @click="selected = c.value"
        >
          <span>{{ c.label }}</span><i>{{ c.detalle }}</i>
        </button>
      </div>
      <p>Se convocará a los aventureros cuando al menos 3 miembros confirmen la fecha.</p>
      <div class="sim-dlg-fila">
        <button class="sdcb" @click="emit('close')">Cancelar</button>
        <button class="sdok" @click="emit('accepted', selected)">Proponer Fecha</button>
      </div>
    </div>
  </BaseModal>
</template>

<style scoped>
.sim-pick-fechas {
  display: grid;
  gap: 8px;
  margin-bottom: 12px;
}
.sim-pick-op {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 4px;
  background: transparent;
  border: 1px solid rgba(139, 90, 43, .4);
  color: #1A1A1A;
  font-family: var(--tf-labels);
  font-size: 14px;
  cursor: pointer;
  transition: all .15s;
  text-align: left;
}
.sim-pick-op i {
  font-style: normal;
  color: var(--tf-copper);
  font-size: 12px;
}
.sim-pick-op.sim-votado {
  border-color: var(--tf-olive-bright);
  background: rgba(107, 142, 35, .12);
  color: var(--tf-olive);
}
</style>