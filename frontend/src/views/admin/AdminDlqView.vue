<script setup>
// F09/D-15: DLQ operativa — listar, reintentar (republica al exchange) y
// descartar. Los vacios se muestran; los fallos se informan con toast.
import { ref, onMounted } from 'vue'
import { getDlq, reintentarDlq, descartarDlq } from '@/services/admin'
import { useToast } from '@/composables/useToast'

const mensajes = ref([])
const cargando = ref(true)
const error = ref(null)
const ocupado = ref(false)
const toast = useToast()

async function cargar() {
  cargando.value = true
  error.value = null
  try {
    mensajes.value = await getDlq(50)
  } catch (e) {
    error.value = e?.message || 'No se pudo leer la DLQ.'
  } finally {
    cargando.value = false
  }
}

function textoPayload(p) {
  try {
    const plano = typeof p === 'string' ? JSON.parse(p) : p
    return JSON.stringify(plano)
  } catch {
    return String(p ?? '')
  }
}

async function reintentar(id) {
  ocupado.value = true
  try {
    await reintentarDlq(id)
    mensajes.value = mensajes.value.filter((m) => m.id !== id)
    toast.ok(`Mensaje #${id} repuesto a su cola original.`)
  } catch (e) {
    toast.error(e?.message || `No se pudo reintentar el mensaje #${id}.`)
  } finally {
    ocupado.value = false
  }
}

async function descartar(id) {
  ocupado.value = true
  try {
    await descartarDlq(id)
    mensajes.value = mensajes.value.filter((m) => m.id !== id)
    toast.ok(`Mensaje #${id} descartado.`)
  } catch (e) {
    toast.error(e?.message || `No se pudo descartar el mensaje #${id}.`)
  } finally {
    ocupado.value = false
  }
}

onMounted(cargar)
</script>

<template>
  <main class="admin-main">
    <h1>DLQ · mensajes muertos</h1>
    <p class="label">dlq.general: mensajería que la infraestructura no pudo procesar. Reintentar la republica; descartar la borra de la tabla.</p>
    <p v-if="error" class="hint-error" role="alert" data-test="error-dlq">{{ error }}</p>
    <div v-if="cargando" class="label">Cargando…</div>
    <div v-else>
      <div v-if="mensajes.length === 0" class="card vacio" data-test="sin-dlq">
        La cola de muertos está vacía: sin residuos operativos.
      </div>
      <article v-for="m in mensajes" :key="m.id" class="card fila-dlq" data-test="fila-dlq">
        <div>
          <span class="num">{{ m.id }}</span>
          <span class="tag tag--ink">{{ m.cola }}</span>
        </div>
        <div>
          <p style="font-size: var(--text-sm); margin: 0;" data-test="dlq-error"><strong>Error:</strong> {{ m.error }}</p>
          <p class="payload mono">{{ textoPayload(m.payload) }}</p>
          <p class="label">{{ m.fecha || '' }}</p>
        </div>
        <div class="acciones">
          <button type="button" class="btn btn--secondary" data-test="dlq-reintentar" :disabled="ocupado" @click="reintentar(m.id)">Reintentar</button>
          <button type="button" class="btn btn--danger" data-test="dlq-descartar" :disabled="ocupado" @click="descartar(m.id)">Descartar</button>
        </div>
      </article>
    </div>
  </main>
</template>

<style scoped>
.admin-main { max-width: var(--container); margin-inline: auto; padding: var(--space-lg) var(--gutter); display: grid; gap: var(--space-md); }
.fila-dlq { display: grid; grid-template-columns: minmax(120px, auto) minmax(0, 1fr) auto; gap: var(--space-md); align-items: start; }
.payload { font-size: var(--text-xs); color: var(--color-ink-2); overflow-wrap: anywhere; max-height: 6rem; overflow: auto; }
.acciones { display: flex; gap: var(--space-2xs); }
.btn--danger { background: var(--color-error); color: var(--color-paper); border-color: var(--color-error); }
@media (max-width: 60rem) { .fila-dlq { grid-template-columns: minmax(0, 1fr); } }
.vacio { padding: var(--space-lg); text-align: center; color: var(--color-ink-2); }
</style>
