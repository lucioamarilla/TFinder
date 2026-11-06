<script setup>
// F09/D-15: emails de notificacion; los fallidos se reintentan por SMTP real
// (repos.esse endpoint reenvia y actualцiza estado).
import { ref, onMounted } from 'vue'
import { getEmails, reintentarEmail } from '@/services/admin'
import { useToast } from '@/composables/useToast'

const emails = ref([])
const cargando = ref(true)
const error = ref(null)
const ocupado = ref(false)
const toast = useToast()

async function cargar() {
  cargando.value = true
  error.value = null
  try {
    emails.value = await getEmails(50)
  } catch (e) {
    error.value = e?.message || 'No se pudieron leer los emails.'
  } finally {
    cargando.value = false
  }
}

async function reintentar(id) {
  ocupado.value = true
  try {
    const resultado = await reintentarEmail(id)
    const idx = emails.value.findIndex((e) => e.id === id)
    if (idx >= 0) emails.value[idx] = { ...emails.value[idx], estado: resultado.estado, error: resultado.error ?? null }
    toast.ok(resultado.estado === 'enviado' ? `Email #${id} reenviado.` : `Email #${id} falló de nuevo: ${resultado.error}`)
  } catch (e) {
    toast.error(e?.message || `No se pudo reintentar el email #${id}.`)
  } finally {
    ocupado.value = false
  }
}

onMounted(cargar)
</script>

<template>
  <main class="admin-main">
    <h1>Emails de notificación</h1>
    <p class="label">Últimos envíos; los fallidos pueden reintentarse.</p>
    <p v-if="error" class="hint-error" role="alert" data-test="error-emails">{{ error }}</p>
    <div v-if="cargando" class="label">Cargando…</div>
    <div v-else>
      <div v-if="emails.length === 0" class="card vacio" data-test="sin-emails">Sin envíos registrados.</div>
      <table v-else class="tabla" data-test="tabla-emails">
        <thead>
          <tr><th>#</th><th>Destino</th><th>Asunto</th><th>Estado</th><th></th></tr>
        </thead>
        <tbody>
          <tr v-for="e in emails" :key="e.id" data-test="fila-email">
            <td>{{ e.id }}</td>
            <td>{{ e.destino }}</td>
            <td>{{ e.asunto }}</td>
            <td data-test="estado-email">{{ e.estado }}<span v-if="e.error" class="hint-error"> · {{ e.error }}</span></td>
            <td><button v-if="e.estado !== 'enviado'" type="button" class="btn btn--sm" data-test="email-reintentar" :disabled="ocupado" @click="reintentar(e.id)">Reintentar</button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </main>
</template>

<style scoped>
.admin-main { max-width: var(--container); margin-inline: auto; padding: var(--space-lg) var(--gutter); display: grid; gap: var(--space-md); }
.tabla { width: 100%; border: var(--rule-hair) solid var(--color-rule); border-collapse: collapse; background: var(--color-paper); font-size: var(--text-sm); }
.tabla th, .tabla td { text-align: left; padding: var(--space-2xs) var(--space-sm); border-bottom: var(--rule-hair) solid var(--color-rule); }
.tabla th { font-weight: 700; color: var(--color-muted); }
.vacio { padding: var(--space-lg); text-align: center; color: var(--color-ink-2); }
</style>
