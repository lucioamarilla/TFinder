<template>
  <div class="bitacora" data-test="modo-sesion-gm">
    <article class="card" style="padding: var(--space-lg);">
      <div style="display: flex; align-items: baseline; justify-content: space-between; gap: var(--space-md); flex-wrap: wrap;">
        <div>
          <h2 style="margin: 0;">Bitácora del modo sesión</h2>
          <p class="label" style="margin-top: var(--space-3xs);">
            Documentación histórica: elegí la sesión y anotá lo acontecido.
          </p>
        </div>
        <RouterLink class="text-link" :to="`/mesas/${mesaId}/gestion/sesiones`">← Ver sesiones</RouterLink>
      </div>

      <div v-if="sesiones.length === 0" style="text-align: center; padding: var(--space-lg); margin-top: var(--space-md);" data-test="sin-sesiones">
        <p class="label">No hay sesiones para anotar todavía</p>
        <p style="font-size: var(--text-sm); color: var(--color-ink-2); margin-top: var(--space-2xs);">
          Creá una sesión desde la pestaña Sesiones y volvé a la bitácora.
        </p>
        <RouterLink class="btn btn--secondary" :to="`/mesas/${mesaId}/gestion/sesiones`" style="margin-top: var(--space-sm);">
          Ir a sesiones
        </RouterLink>
      </div>

      <template v-else>
        <label class="label" style="display: block; margin-top: var(--space-md);" for="sel-sesion">Sesión</label>
        <select id="sel-sesion" class="input input--medio" v-model="sesionActiva" data-test="select-sesion">
          <option v-for="s in sesiones" :key="s.id" :value="String(s.id)">
            Sesión del {{ (s.fecha || '').slice(0, 10) }} · {{ s.estado }}
          </option>
        </select>
        <BitacoraView :mesa-id="mesaId" :sesion-id="sesionActiva" data-test="bitacora-embebida" />
      </template>
    </article>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import BitacoraView from '@/views/gestion/BitacoraView.vue'
import { getSesiones } from '@/services/sesiones'

// F3: el modo sesión es una BITÁCORA (pliego 2.3) — sin turnos ni mecánicas.
const route = useRoute()
const mesaId = String(route.params.id)
const sesiones = ref([])
const sesionActiva = ref(null)

onMounted(async () => {
  try {
    sesiones.value = await getSesiones(mesaId)
    if (sesiones.value.length > 0) sesionActiva.value = String(sesiones.value[0].id)
  } catch {
    sesiones.value = []
  }
})
</script>

<style scoped>
.bitacora { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); }
@media (max-width: 60rem) { .bitacora { padding-top: 120px; } }
</style>
