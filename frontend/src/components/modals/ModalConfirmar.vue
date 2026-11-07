<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  titulo: { type: String, default: '¿Confirmás esta acción?' },
  mensaje: { type: String, default: '' },
  etiquetaOk: { type: String, default: 'Confirmar' },
  etiquetaCancel: { type: String, default: 'Cancelar' }
})

const emit = defineEmits(['close', 'accept'])

const dialog = ref(null)

watch(
  () => props.open,
  (v) => {
    const el = dialog.value
    if (!el) return
    if (v && !el.open) {
      if (typeof el.showModal === 'function') el.showModal()
      else el.open = true
    }
    if (!v && el.open) {
      if (typeof el.close === 'function') el.close()
      else el.open = false
    }
  },
  { immediate: true }
)

function onBackdrop(e) {
  if (dialog.value && e.target === dialog.value) emit('close')
}
</script>

<template>
  <dialog ref="dialog" class="tf-dialog" data-test="modal-cerrar-sesion" @close="emit('close')" @click="onBackdrop">
    <div class="tf-modal">
      <h3>{{ titulo }}</h3>
      <p v-if="mensaje">{{ mensaje }}</p>
      <div class="tf-modal-actions">
        <button type="button" class="btn btn--secondary" data-test="cancelar-salir" @click="emit('close')">
          {{ etiquetaCancel }}
        </button>
        <button type="button" class="btn btn--danger" data-test="confirmar-salir" @click="emit('accept')">
          {{ etiquetaOk }}
        </button>
      </div>
    </div>
  </dialog>
</template>