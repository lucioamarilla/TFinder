<template>
  <div class="bitacora" data-test="modo-sesion-jugador">
    <article class="card" style="padding: var(--space-lg);">
      <div style="display: flex; align-items: baseline; justify-content: space-between; gap: var(--space-md); flex-wrap: wrap;">
        <div>
          <h2 style="margin: 0;">Bitácora de la sesión (jugador)</h2>
          <p class="label" style="margin-top: var(--space-3xs);">
            Mirá lo acontecido y anotá tu parte: la bitácora es de todos los integrantes.
          </p>
        </div>
        <RouterLink class="text-link" to="/mis-mesas">← Mis mesas</RouterLink>
      </div>

      <div v-if="sesiones.length === 0" style="text-align: center; padding: var(--space-lg); margin-top: var(--space-md);" data-test="sin-sesiones">
        <p class="label">Tu mesa todavía no tiene sesiones</p>
        <p style="font-size: var(--text-sm); color: var(--color-ink-2); margin-top: var(--space-2xs);">
          Cuando tu master cree una sesión, vas a verla y anotar acá.
        </p>
      </div>

      <template v-else>
        <label class="label" style="display: block; margin-top: var(--space-md);" for="sel-sesion-j">Sesión</label>
        <select id="sel-sesion-j" class="input input--medio" v-model="sesionActiva" data-test="select-sesion-j">
          <option v-for="s in sesiones" :key="s.id" :value="String(s.id)">
            Sesión del {{ (s.fecha || '').slice(0, 10) }} · {{ s.estado }}
          </option>
        </select>
        <div style="margin-top: var(--space-md);">
          <button class="btn" :disabled="!sesionActiva || asistiendo" @click="marcarAsistencia">Marcar asistencia</button>
          <p v-if="mensajeAsistencia" class="label" style="margin-top: var(--space-2xs);">{{ mensajeAsistencia }}</p>
        </div>
        <BitacoraFor :mesa-id="mesaId" :sesion-id="sesionActiva" />
      </template>
    </article>
  </div>
</template>

<script setup>
import { onMounted, ref, defineAsyncComponent } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { getSesiones } from '@/services/sesiones'
import { sesionesApi } from '@/api/endpoints'

// F3: el jugador anota en la bitácora (sin mecánicas: la sesión es registro).
const BitacoraFor = defineAsyncComponent(() => import('@/views/gestion/BitacoraView.vue'))

const route = useRoute()
const mesaId = String(route.params.id)
const sesiones = ref([])
const sesionActiva = ref(null)
const asistiendo = ref(false)
const mensajeAsistencia = ref('')

onMounted(async () => {
  try {
    sesiones.value = await getSesiones(mesaId)
    if (sesiones.value.length > 0) sesionActiva.value = String(sesiones.value[0].id)
  } catch {
    sesiones.value = []
  }
})

async function marcarAsistencia() {
  if (!sesionActiva.value) return
  asistiendo.value = true
  mensajeAsistencia.value = ''
  try {
    await sesionesApi.marcarAsistencia(Number(sesionActiva.value))
    mensajeAsistencia.value = 'Asistencia registrada.'
  } catch (e) {
    mensajeAsistencia.value = e?.message || 'No se pudo registrar la asistencia.'
  } finally {
    asistiendo.value = false
  }
}
</script>

<style scoped>
.bitacora { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); }
@media (max-width: 60rem) { .bitacora { padding-top: 120px; } }
</style>
