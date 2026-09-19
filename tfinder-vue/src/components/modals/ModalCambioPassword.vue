<script setup>
import { reactive, ref, watch } from 'vue'
import { useToast } from '@/composables/useToast'
import BaseModal from '@/components/modals/BaseModal.vue'

const props = defineProps({ open: Boolean })

const emit = defineEmits(['close', 'guardada'])

const toast = useToast()
const form = reactive({ actual: '', nueva: '', confirmacion: '' })
const error = ref('')

watch(
  () => props.open,
  () => {
    if (props.open) {
      form.actual = ''
      form.nueva = ''
      form.confirmacion = ''
      error.value = ''
    }
  }
)

function validar() {
  if (!form.actual) return 'Ingresá tu contraseña actual.'
  if (form.nueva.length < 8) return 'La nueva contraseña debe tener al menos 8 caracteres.'
  if (!/[A-Z]/.test(form.nueva) || !/[0-9]/.test(form.nueva)) {
    return 'La nueva contraseña debe incluir una mayúscula y un número.'
  }
  if (form.nueva !== form.confirmacion) return 'La confirmación no coincide.'
  return null
}

function guardar() {
  const err = validar()
  if (err) {
    error.value = err
    return
  }
  emit('guardada', form.nueva)
  emit('close')
  toast.ok('Contraseña actualizada · vínculo rúnico renovado.')
}
</script>

<template>
  <BaseModal :open="open" @close="emit('close')">
    <div class="sim-dlg-card">
      <div class="sim-dlg-ico sim-cobre">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <rect x="3" y="11" width="18" height="11" rx="2" />
          <path d="M7 11V7a5 5 0 0 1 10 0v4" />
        </svg>
      </div>
      <h2>Cambiar Contraseña</h2>
      <form class="sim-pass-form" @submit.prevent="guardar">
        <input v-model="form.actual" type="password" placeholder="Contraseña actual" aria-label="Contraseña actual" />
        <input v-model="form.nueva" type="password" placeholder="Nueva contraseña" aria-label="Nueva contraseña" />
        <input v-model="form.confirmacion" type="password" placeholder="Confirmar nueva contraseña" aria-label="Confirmar nueva contraseña" />
        <span v-if="error" class="sim-pass-err" role="alert">{{ error }}</span>
        <span class="sim-pass-hint">✓ Mínimo 8 caracteres · mayúscula y número.</span>
        <div class="sim-dlg-fila">
          <button type="button" class="sdcb" @click="emit('close')">Cancelar</button>
          <button type="submit" class="sdok">Guardar</button>
        </div>
      </form>
    </div>
  </BaseModal>
</template>

<style scoped>
.sim-pass-form {
  display: grid;
  gap: 8px;
  text-align: left;
  margin-bottom: 12px;
}
.sim-pass-form input {
  border: 1px solid #C2A980;
  background: #F4EAD6;
  border-radius: 3px;
  padding: 8px 10px;
  font-family: var(--tf-serif);
  color: #1A1A1A;
}
.sim-pass-form input:focus {
  outline: 2px solid var(--tf-gold);
  outline-offset: 1px;
}
.sim-pass-hint {
  font-family: var(--tf-labels);
  font-size: 11px;
  color: var(--tf-olive-bright);
}
.sim-pass-err {
  font-family: var(--tf-labels);
  font-size: 12px;
  color: var(--tf-garnet);
}
</style>