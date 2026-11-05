<script setup>
import { useToast } from '@/composables/useToast'

const { toasts, dismiss } = useToast()
</script>

<template>
  <div id="sim-toasts" aria-live="polite">
    <div
      v-for="t in toasts"
      :key="t.id"
      class="sim-toast"
      :class="{ 'sim-ok': t.type === 'ok', 'sim-err': t.type === 'err' }"
      role="status"
      @click="dismiss(t.id)"
    >
      {{ t.message }}
    </div>
  </div>
</template>