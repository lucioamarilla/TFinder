<template>
  <div class="app-grid">
    <main style="display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-md);">
      <div style="display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: var(--space-sm);">
        <div>
          <h2>Bandeja de solicitudes</h2>
          <p class="label">{{ pendientes.length }} pendientes en tus mesas</p>
        </div>
      </div>
      <p class="hint-error" v-if="error" role="alert" data-test="error-bandeja">{{ error }}</p>
      <div class="card" style="padding: var(--space-md);">
        <div v-if="cargando" class="label">Cargando…</div>
        <div v-else-if="pendientes.length === 0" style="font-size: var(--text-sm); color: var(--color-ink-2);">Todavía no hay solicitudes para tus mesas.</div>
        <div v-for="s in pendientes" :key="s.id" class="solicitud">
          <div class="quien">
            <span class="av">{{ iniciales(s.nombre) }}</span>
            <div>
              <p style="font-weight: 700; font-size: var(--text-sm); margin: 0;">{{ s.nombre }} · {{ s.mesaNombre }}</p>
              <p style="font-size: var(--text-xs); color: var(--color-muted); margin: 0;">{{ s.nota || 'Sin nota' }}</p>
            </div>
          </div>
          <div style="display: flex; gap: var(--space-2xs);">
            <button class="btn btn--sm" @click="aceptar(s)">Aceptar</button>
            <button class="btn btn--danger btn--sm" @click="rechazar(s)">Rechazar</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getMisMesas } from '@/services/mesas'
import { getSolicitudes, aceptarSolicitud, rechazarSolicitud } from '@/services/jugadores'
// sin demo

const pendientes = ref([])
const cargando = ref(true)
const error = ref(null)

function iniciales(n) { return (n || '').trim().split(/\s+/).map((p) => p[0]).slice(0, 2).join('').toUpperCase() || 'AV' }

async function cargar() {
  cargando.value = true
  error.value = null
  try {
    const mias = await getMisMesas()
    const gmMesas = mias.filter((m) => m.miRol === 'master')
    const todas = []
    for (const m of gmMesas) {
      const sols = await getSolicitudes(m.id)
      for (const s of sols) {
        if (s.estado === 'pendiente') todas.push({ ...s, mesaNombre: m.nombre, mesaId: m.id })
      }
    }
    pendientes.value = todas
  } catch (e) {
    error.value = e?.message || 'No se pudieron cargar las solicitudes.'
  } finally {
    cargando.value = false
  }
}

async function aceptar(s) {
  try {
    await aceptarSolicitud(s.mesaId, s.id)
    await cargar()
    // ok
  } catch (e) {
    error.value = e?.message || 'No se pudo aceptar.'
  }
}

async function rechazar(s) {
  try {
    await rechazarSolicitud(s.mesaId, s.id)
    await cargar()
    // ok
  } catch (e) {
    error.value = e?.message || 'No se pudo rechazar.'
  }
}

onMounted(cargar)
</script>

<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-md); align-items: start; }
.solicitud { display: flex; align-items: center; gap: var(--space-md); padding: var(--space-sm); border-bottom: var(--rule-hair) solid var(--color-rule); flex-wrap: wrap; }
.solicitud:last-child { border-bottom: none; }
.quien { display: flex; align-items: center; gap: var(--space-sm); flex: 1; min-width: 200px; }
.av { width: 34px; height: 34px; display: grid; place-items: center; background: var(--color-paper-3); border: var(--rule-hair) solid var(--color-rule); font-weight: 700; font-size: var(--text-xs); }
@media (max-width: 60rem) { .app-grid { padding-top: 120px; } }
</style>