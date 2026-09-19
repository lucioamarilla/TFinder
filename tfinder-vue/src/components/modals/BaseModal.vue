<script setup>
import { ref, watch } from 'vue'

const props = defineProps({ open: Boolean })
const emit = defineEmits(['close'])

const dialog = ref(null)

watch(
  () => props.open,
  (v) => {
    const el = dialog.value
    if (!el) return
    if (v && !el.open) el.showModal()
    if (!v && el.open) el.close()
  },
  { immediate: true }
)

function onBackdrop(e) {
  if (dialog.value && e.target === dialog.value) dialog.value.close()
}
</script>

<template>
  <dialog ref="dialog" class="sim-dlg" @close="emit('close')" @click="onBackdrop">
    <slot />
  </dialog>
</template>