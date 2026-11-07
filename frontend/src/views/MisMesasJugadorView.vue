<template>
  <div class="app-grid">
    <main style="display: grid; gap: var(--space-md);">
      <div style="display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: var(--space-sm);">
        <div>
          <h2>Mis mesas</h2>
          <p class="label">Donde jugás hoy</p>
        </div>
        <div style="display: flex; gap: var(--space-sm); flex-wrap: wrap;">
          <RouterLink class="btn" to="/mesas/nueva">Nueva mesa</RouterLink>
          <RouterLink class="btn btn--secondary" to="/mesas">Explorar más</RouterLink>
        </div>
      </div>
      <div v-if="cargando" class="label">Cargando…</div>
      <div v-else-if="mias.length === 0" class="card" style="padding: var(--space-xl); text-align: center;">
        <p>Todavía no te uniste a ninguna mesa.</p>
        <RouterLink class="btn btn--secondary" to="/mesas" style="margin-top: var(--space-md);">Explorar mesas</RouterLink>
      </div>
      <div v-else class="card">
        <div v-for="m in mias" :key="m.id" class="mesa-row">
          <div class="mesa-thumb">{{ m.nombre.split(' ').map(x=>x[0]).slice(0,2).join('') }}</div>
          <div style="min-width: 0;">
            <p style="font-weight: 700; font-size: var(--text-sm); margin: 0;">{{ m.nombre }}</p>
            <p style="font-size: var(--text-xs); color: var(--color-muted); margin: 0;">{{ m.gm }}, {{ m.horario }}, nivel {{ m.nivel }}</p>
          </div>
          <div class="mesa-row-actions" style="display: flex; align-items: center; gap: var(--space-sm); flex-wrap: wrap;">
            <span class="tag tag--ink">{{ m.miRol === 'master' ? 'Director' : 'Jugador' }}</span>
            <span class="num" style="font-size: var(--text-sm);">{{ m.jugadores }}/{{ m.plazas }}</span>
            <RouterLink v-if="m.miRol === 'master'" class="btn btn--secondary btn--sm" :to="'/mesas/' + m.id + '/gestion'">Gestionar</RouterLink>
            <RouterLink v-else class="btn btn--secondary btn--sm" :to="'/mesas/' + m.id">Ver mesa</RouterLink>
            <RouterLink v-if="m.miRol !== 'master'" class="btn btn--secondary btn--sm" :to="'/mesas/' + m.id + '/sesion/jugador'">Bitácora</RouterLink>
            <button v-if="m.miRol !== 'master'" class="btn btn--danger btn--sm" @click="salir(m)">Salir</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMisMesas } from '@/services/mesas'
import { mesasApi } from '@/api/endpoints'
import { useAuth } from '@/composables/useAuth'

const { user } = useAuth()
const mias = ref([])
const cargando = ref(true)

onMounted(async () => {
  try {
    const todas = await getMisMesas()
    mias.value = todas
  } catch (e) {
    mias.value = []
  } finally {
    cargando.value = false
  }
})

async function salir(mesa) {
  try {
    await mesasApi.salir(mesa.id)
    mias.value = mias.value.filter((m) => m.id !== mesa.id)
  } catch (e) {
  }
}
</script>

<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-lg); align-items: start; }
@media (max-width: 60rem) { .app-grid { padding-top: 120px; } }
</style>
