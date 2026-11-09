<script setup>
import { useToast } from '@/composables/useToast'
const { toasts, dismiss } = useToast()

// Mensajes de error y advertencia se anuncian con assertividad (alert);
// el resto con cortesía (status).
function rolDe(type) {
  return type === 'err' || type === 'warn' ? 'alert' : 'status'
}
</script>

<template>
  <TransitionGroup tag="div" name="tf-toast" class="tf-toasts">
    <div
      v-for="t in toasts"
      :key="t.id"
      class="tf-toast"
      :class="`tf-toast--${t.type}`"
      :role="rolDe(t.type)"
      data-test="toast"
    >
      <span class="aviso-ico" aria-hidden="true">
        <svg v-if="t.type === 'err'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" /></svg>
        <svg v-else-if="t.type === 'warn'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" /></svg>
        <svg v-else-if="t.type === 'ok'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" /></svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" /><line x1="12" y1="16" x2="12" y2="12" /><line x1="12" y1="8" x2="12.01" y2="8" /></svg>
      </span>
      <span class="aviso-cuerpo">{{ t.message }}</span>
      <button
        class="tf-toast-x"
        type="button"
        aria-label="Cerrar aviso"
        @click="dismiss(t.id)"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
      </button>
    </div>
  </TransitionGroup>
</template>
