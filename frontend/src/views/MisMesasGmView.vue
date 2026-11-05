<template>
  <div class="app-grid">
    <main style="display: grid; gap: var(--space-md);">
      <div style="display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: var(--space-sm);">
        <div>
          <h2>Mis mesas</h2>
          <p class="label">Donde dirigís hoy</p>
        </div>
        <div style="display: flex; gap: var(--space-sm); flex-wrap: wrap;">
          <RouterLink class="btn btn--secondary" to="/mis-mesas">Como jugador</RouterLink>
          <RouterLink class="btn" to="/mesas/nueva">Nueva mesa</RouterLink>
        </div>
      </div>
      <div v-if="cargando" class="label">Cargando…</div>
      <div v-else-if="mias.length === 0" class="card" style="padding: var(--space-xl); text-align: center;">
        <p>Todavía no dirigís ninguna mesa.</p>
        <RouterLink class="btn btn--secondary" to="/mesas/nueva" style="margin-top: var(--space-md);">Publicá tu campaña</RouterLink>
      </div>
      <div v-else class="card">
        <div v-for="m in mias" :key="m.id" class="mesa-row">
          <div class="mesa-thumb">{{ m.nombre.split(' ').map(x=>x[0]).slice(0,2).join('') }}</div>
          <div style="min-width: 0;">
            <p style="font-weight: 700; font-size: var(--text-sm); margin: 0;">{{ m.nombre }}</p>
            <p style="font-size: var(--text-xs); color: var(--color-muted); margin: 0;">{{ m.horario }}, nivel {{ m.nivel }} · {{ m.jugadores }}/{{ m.plazas }} jugadores</p>
          </div>
          <div style="display: flex; gap: var(--space-2xs);">
            <RouterLink class="btn btn--secondary btn--sm" :to="'/mesas/' + m.id + '/gm'">Gestionar</RouterLink>
            <RouterLink class="btn btn--sm" :to="'/mesas/' + m.id + '/sesion'">Sesión</RouterLink>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMisMesas } from '@/services/mesas'

const mias = ref([])
const cargando = ref(true)

onMounted(async () => {
  try {
    const todas = await getMisMesas()
    mias.value = todas.filter((m) => m.miRol === 'master')
  } catch (e) {
    mias.value = []
  } finally {
    cargando.value = false
  }
})
</script>

<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-lg); align-items: start; }
@media (max-width: 60rem) { .app-grid { padding-top: 120px; } }
</style>