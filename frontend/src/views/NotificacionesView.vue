<template>
  <div class="app-grid">
    <main style="display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-md);">
      <div style="display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: var(--space-sm);">
        <div>
          <h2>Notificaciones</h2>
          <p class="label">{{ noLeidas }} sin leer</p>
        </div>
        <button class="btn btn--secondary" @click="marcarTodas">Marcar todas como leídas</button>
      </div>
      <div class="card" style="padding: var(--space-md);">
        <div v-if="cargando" class="label">Cargando…</div>
        <div v-else-if="lista.length === 0" class="label">Silencio: no hay notificaciones.</div>
        <div v-for="n in lista" :key="n.id" class="notif" :class="n.leida ? 'leida' : 'nueva'">
          <span class="punto" aria-hidden="true"></span>
          <p style="flex: 1; min-width: 200px; margin: 0; font-size: var(--text-sm);">{{ n.texto }}</p>
          <span class="label">{{ n.tiempo }}</span>
          <RouterLink class="btn btn--secondary btn--sm" :to="n.link || '/feed'">Ver</RouterLink>
          <button v-if="!n.leida" class="thread-toggle" @click="marcarLeida(n)">Marcar leída</button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getNotificaciones, marcarLeida as marcarLeidaApi, marcarTodasLeidas } from '@/services/notificaciones'
// sin demo

const lista = ref([])
const cargando = ref(true)

const noLeidas = computed(() => lista.value.filter((n) => !n.leida).length)

async function cargar() {
  cargando.value = true
  try {
    lista.value = await getNotificaciones()
  } finally {
    cargando.value = false
  }
}

async function marcarLeida(n) {
  await marcarLeidaApi(n.id)
  n.leida = true
}

async function marcarTodas() {
  await marcarTodasLeidas()
  await cargar()
  // ok
}

onMounted(cargar)
</script>

<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-md); align-items: start; }
.notif { display: flex; align-items: center; gap: var(--space-md); padding: var(--space-sm); border-bottom: var(--rule-hair) solid var(--color-rule); flex-wrap: wrap; }
.notif:last-child { border-bottom: none; }
.notif.nueva { background: color-mix(in oklab, var(--color-accent-2) 8%, transparent); }
.notif .punto { width: 10px; height: 10px; flex: none; background: var(--color-accent-2); }
.notif.leida .punto { background: var(--color-paper-3); border: var(--rule-hair) solid var(--color-rule); }
@media (max-width: 60rem) { .app-grid { padding-top: 120px; } }
</style>