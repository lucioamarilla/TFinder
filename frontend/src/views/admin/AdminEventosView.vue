<script setup>
// F09/D-15: event log de dominio (notif-api, rol admin).
import { ref, onMounted } from 'vue'
import { getEventos } from '@/services/admin'

const eventos = ref([])
const cargando = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    eventos.value = await getEventos({ limite: 100 })
  } catch (e) {
    error.value = e?.message || 'No se pudo leer el event log.'
  } finally {
    cargando.value = false
  }
})
</script>

<template>
  <main class="admin-main">
    <h1>Eventos de dominio</h1>
    <p class="label">Chronología del sistema: entidad, acción, usuario y correlación.</p>
    <p v-if="error" class="hint-error" role="alert" data-test="error-eventos">{{ error }}</p>
    <div v-if="cargando" class="label">Cargando…</div>
    <div v-else>
      <div v-if="eventos.length === 0" class="card vacio" data-test="sin-eventos">
        El event log no tiene registros visibles todavía.
      </div>
      <table v-else class="tabla" data-test="tabla-eventos">
        <thead>
          <tr><th>#</th><th>Entidad</th><th>Acción</th><th>Usuario</th><th>Correlación</th><th>Ocurrido</th></tr>
        </thead>
        <tbody>
          <tr v-for="e in eventos" :key="e.id" data-test="fila-evento">
            <td>{{ e.id }}</td>
            <td>{{ e.entidadTipo }}<span v-if="e.entidadId"> · {{ e.entidadId }}</span></td>
            <td>{{ e.accion }}</td>
            <td>{{ e.usuarioId || '—' }}</td>
            <td class="mono">{{ e.correlationId || '—' }}</td>
            <td>{{ e.ocurridoEn || '—' }}</td>
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
.mono { font-variant-numeric: tabular-nums; }
.vacio { padding: var(--space-lg); text-align: center; color: var(--color-ink-2); }
</style>
