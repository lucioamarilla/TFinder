<script setup>
// F09/D-15: panel de la consola admin (resumen de las tres colas reales).
import { ref, onMounted } from 'vue'
import { getEventos, getDlq, getEmails } from '@/services/admin'

const eventos = ref([])
const dlq = ref([])
const emails = ref([])
const cargando = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    const [ev, dl, em] = await Promise.all([getEventos({ limite: 50 }), getDlq(50), getEmails(50)])
    eventos.value = ev
    dlq.value = dl
    emails.value = em
  } catch (e) {
    error.value = e?.message || 'No se pudo leer la consola.'
  } finally {
    cargando.value = false
  }
})
</script>

<template>
  <main class="admin-main">
    <h1>Consola admin</h1>
    <p class="label">Observabilidad operativa del sistema: eventos de dominio, cola de muertos (DLQ) y correos salientes.</p>
    <p v-if="error" class="hint-error" role="alert" data-test="error-admin">{{ error }}</p>

    <div v-if="cargando" class="label">Cargando consola…</div>
    <div v-else class="grid-3-cards">
      <article class="card" data-test="admin-card-eventos">
        <h2>Eventos de dominio</h2>
        <p class="figure-lg acid">{{ eventos.length }}</p>
        <p style="font-size: var(--text-sm); color: var(--color-ink-2);">Últimos registrados en el event log.</p>
        <RouterLink class="btn btn--secondary" to="/admin/eventos">Ver eventos</RouterLink>
      </article>
      <article class="card" data-test="admin-card-dlq">
        <h2>DLQ (mensajes muertos)</h2>
        <p class="figure-lg ember">{{ dlq.length }}</p>
        <p style="font-size: var(--text-sm); color: var(--color-ink-2);">Reintentar republica el mensaje al exchange; descartar lo elimina.</p>
        <RouterLink class="btn btn--secondary" to="/admin/dlq">Administrar DLQ</RouterLink>
      </article>
      <article class="card" data-test="admin-card-emails">
        <h2>Emails salientes</h2>
        <p class="figure-lg">{{ emails.length }}</p>
        <p style="font-size: var(--text-sm); color: var(--color-ink-2);">Envíos de notificación; los fallidos se pueden reintentar.</p>
        <RouterLink class="btn btn--secondary" to="/admin/emails">Ver emails</RouterLink>
      </article>
    </div>
  </main>
</template>

<style scoped>
.admin-main { max-width: var(--container); margin-inline: auto; padding: var(--space-lg) var(--gutter); display: grid; gap: var(--space-md); }
.grid-3-cards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-md); }
@media (max-width: 60rem) { .grid-3-cards { grid-template-columns: minmax(0, 1fr); } }
.figure-lg.ember { color: var(--color-accent); }
.figure-lg.acid { color: var(--color-accent-2); }
figure-lg { font-size: var(--text-display-s); }
.figure-lg { font-family: var(--font-outlier); font-weight: 700; font-size: var(--text-display-s); line-height: 1; }
</style>
