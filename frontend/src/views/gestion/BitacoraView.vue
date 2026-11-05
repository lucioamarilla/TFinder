<template>
  <div class="bitacora" data-test="bitacora-sesion">
    <form class="composer" style="display: grid; gap: var(--space-sm);" @submit.prevent="enviar">
      <div style="display: flex; align-items: baseline; justify-content: space-between; gap: var(--space-md); flex-wrap: wrap;">
        <div>
          <h2 style="margin: 0;">Bitácora de la sesión</h2>
          <p class="label" style="margin-top: var(--space-3xs);">
            Documentación histórica de lo sucedido
          </p>
        </div>
        <RouterLink class="text-link" :to="`/mesas/${mesaId}/gestion/sesiones`">← Volver a sesiones</RouterLink>
      </div>

      <label class="label" for="bi-texto">Registrar acontecimiento</label>
      <textarea
        id="bi-texto"
        v-model="texto"
        class="input"
        rows="3"
        data-test="bitacora-texto"
        placeholder="Qué pasó, quién hizo qué, qué quedó pendiente…"
      ></textarea>
      <p class="hint-error" v-if="error" role="alert" data-test="bitacora-error">{{ error }}</p>
      <div style="display: flex; justify-content: flex-end;">
        <button class="btn" type="submit" :disabled="enviando" data-test="bitacora-enviar">
          {{ enviando ? 'Guardando…' : 'Registrar anotación' }}
        </button>
      </div>
    </form>

    <div v-if="cargando" class="card" style="padding: var(--space-lg); text-align: center; margin-top: var(--space-md);" role="status">
      Cargando la bitácora…
    </div>
    <div v-else-if="errorCarga" class="card" style="padding: var(--space-lg); text-align: center; margin-top: var(--space-md);" role="alert">
      <p>No pudimos abrir la bitácora de esta sesión.</p>
      <button class="btn btn--secondary" style="margin-top: var(--space-sm);" @click="cargar">Reintentar</button>
    </div>
    <div v-else-if="anotaciones.length === 0" class="card" style="padding: var(--space-lg); text-align: center; margin-top: var(--space-md);" data-test="bitacora-vacia">
      <p class="label">La bitácora está en blanco</p>
      <p style="font-size: var(--text-sm); color: var(--color-ink-2); margin-top: var(--space-2xs);">
        Todos los integrantes pueden anotar el primer acontecimiento.
      </p>
    </div>

    <ol v-else class="card" data-test="bitacora-lista" style="margin-top: var(--space-md); display: grid; gap: var(--space-sm); list-style: none; padding: 0;">
      <li v-for="(a, i) in anotaciones" :key="a.id" style="padding: var(--space-md); display: grid; grid-template-columns: auto minmax(0,1fr); gap: var(--space-md);">
        <span class="num" style="color: var(--color-accent-2);">{{ i + 1 }}</span>
        <div>
          <p class="label" style="margin: 0;">
            <strong style="color: var(--color-ink);">{{ a.autor }}</strong>
            <span style="margin-left: var(--space-2xs);">{{ fechaLegible(a.creadoEn) }}</span>
          </p>
          <p style="font-size: var(--text-sm); color: var(--color-ink-2); margin: var(--space-2xs) 0 0; white-space: pre-wrap;">{{ a.texto }}</p>
        </div>
      </li>
    </ol>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { getAnotaciones, registrarAnotacion } from '@/services/sesiones'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const props = defineProps({
  mesaId: { type: [String, Number], default: null },
  sesionId: { type: [String, Number], default: null },
})
const { user } = useAuth()
const { toast } = useToast()

const mesaId = String(props.mesaId ?? route.params.mesaId ?? route.params.id)
const sesionId = String(props.sesionId ?? route.params.sesionId)

const anotaciones = ref([])
const texto = ref('')
const cargando = ref(true)
const errorCarga = ref(null)
const enviando = ref(false)
const error = ref(null)

function fechaLegible(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return String(iso)
  return d.toLocaleString('es-AR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

async function cargar() {
  cargando.value = true
  errorCarga.value = null
  try {
    anotaciones.value = await getAnotaciones(mesaId, sesionId)
  } catch {
    errorCarga.value = true
  } finally {
    cargando.value = false
  }
}

async function enviar() {
  error.value = null
  if (!texto.value.trim()) {
    error.value = 'El texto de la anotación no puede estar vacío.'
    return
  }
  enviando.value = true
  try {
    await registrarAnotacion(mesaId, sesionId, texto.value, {
      nombre: user.value?.nombre,
      email: user.value?.email,
      id: user.value?.id,
    })
    texto.value = ''
    await cargar()
    toast('Anotación registrada en la bitácora.', 'success')
  } catch (e) {
    error.value = e.mensaje || e.message || 'No se pudo registrar la anotación.'
  } finally {
    enviando.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.bitacora { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); }
@media (max-width: 60rem) { .bitacora { padding-top: 120px; } }
</style>
