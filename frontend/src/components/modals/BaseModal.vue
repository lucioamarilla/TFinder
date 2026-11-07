<script setup>
import { ref, watch } from 'vue'
const props = defineProps({ open: Boolean })
const emit = defineEmits(['close'])
const dialog = ref(null)
watch(() => props.open, (v) => {
  const el = dialog.value
  if (!el) return
  if (v && !el.open) el.showModal()
  if (!v && el.open) el.close()
}, { immediate: true })
function onBackdrop(e) {
  if (dialog.value && e.target === dialog.value) dialog.value.close()
}
</script>

<template>
  <dialog ref="dialog" class="tf-dialog" @close="emit('close')" @click="onBackdrop">
    <slot />
  </dialog>
</template>

<style scoped>
.tf-dialog {
  border: none;
  background: transparent;
  padding: 0;
  margin: auto;
  max-width: none;
  max-height: none;
  overflow: visible;
  color: var(--color-ink);
}
.tf-dialog::backdrop {
  background: color-mix(in oklab, var(--color-shade) 70%, transparent);
  backdrop-filter: blur(2px);
}
.tf-dialog > :deep(*) { /* slot content styled by children */ }
</style>