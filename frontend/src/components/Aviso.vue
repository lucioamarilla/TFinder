<script setup>
// Aviso del sistema: error, advertencia, éxito e info, en tamaño inline o banner.
// Conserva la a11y previa de las vistas: alert para error/warn, status para ok/info.
defineProps({
  tipo: { type: String, default: 'error' },
  banner: { type: Boolean, default: false }
})
</script>

<template>
  <div
    class="aviso"
    :class="[`aviso--${tipo}`, { 'aviso--banner': banner }]"
    :role="tipo === 'error' || tipo === 'warn' ? 'alert' : 'status'"
  >
    <span class="aviso-ico" aria-hidden="true">
      <svg v-if="tipo === 'error'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" /></svg>
      <svg v-else-if="tipo === 'warn'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" /></svg>
      <svg v-else-if="tipo === 'ok'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" /></svg>
      <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" /><line x1="12" y1="16" x2="12" y2="12" /><line x1="12" y1="8" x2="12.01" y2="8" /></svg>
    </span>
    <div class="aviso-cuerpo">
      <slot />
    </div>
  </div>
</template>
