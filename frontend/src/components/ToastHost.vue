<script setup>
import { useToast } from '@/composables/useToast'
const { toasts, dismiss } = useToast()
</script>

<template>
  <div class="tf-toasts" aria-live="polite">
    <div
      v-for="t in toasts"
      :key="t.id"
      class="tf-toast"
      :class="{ 'tf-toast--success': t.type === 'ok', 'tf-toast--error': t.type === 'err' }"
      role="status"
      @click="dismiss(t.id)"
    >
      {{ t.message }}
    </div>
  </div>
</template>