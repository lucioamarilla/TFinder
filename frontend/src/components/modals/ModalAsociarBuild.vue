<script setup>
import { ref, watch } from 'vue'
import BaseModal from '@/components/modals/BaseModal.vue'

const props = defineProps({
  open: Boolean,
  build: { type: Object, default: () => ({ nombre: '', detalle: '' }) },
  mesas: { type: Array, default: () => [] }
})

const emit = defineEmits(['close', 'accepted'])

const selectedMesa = ref(null)

watch(
  () => props.open,
  () => {
    if (props.open) selectedMesa.value = props.mesas[0]?.id ?? null
  }
)
</script>

<template>
  <BaseModal :open="open" @close="emit('close')">
    <div class="sim-dlg-card" style="text-align: left">
      <div class="sim-dlg-ico sim-cobre" style="margin-left: auto; margin-right: auto">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
          <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
        </svg>
      </div>
      <h2 style="text-align: center">Asociar Build a Mesa</h2>
      <span class="sim-dlg-chip" style="display: block">Build Activo: {{ build.nombre }}</span>
      <div class="sim-assoc-mesas" role="radiogroup" aria-label="Mesas disponibles">
        <label v-for="m in mesas" :key="m.id" class="sim-assoc-op" :class="{ 'sim-votado': selectedMesa === m.id }">
          <input v-model="selectedMesa" type="radio" name="mesa_asociar" :value="m.id" />
          <span>{{ m.nombre }}</span><i>· {{ m.estado }}</i>
        </label>
      </div>
      <div class="sim-dlg-fila">
        <button class="sdcb" @click="emit('close')">Cancelar</button>
        <button class="sdok" @click="emit('accepted', selectedMesa)">Asociar</button>
      </div>
    </div>
  </BaseModal>
</template>

<style scoped>
.sim-assoc-mesas {
  display: grid;
  gap: 6px;
  margin-bottom: 14px;
}
.sim-assoc-op {
  display: flex;
  gap: 8px;
  align-items: center;
  font-family: var(--tf-labels);
  font-size: 13px;
  color: #1A1A1A;
  padding: 8px 10px;
  border: 1px solid rgba(139, 90, 43, .35);
  border-radius: 3px;
  cursor: pointer;
}
.sim-assoc-op.sim-votado {
  border-color: var(--tf-olive-bright);
  background: rgba(107, 142, 35, .1);
}
.sim-assoc-op i {
  font-style: normal;
  color: var(--tf-copper);
}
</style>