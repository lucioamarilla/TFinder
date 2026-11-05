<template>
  <div class="app-grid">
    <main style="display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-md);">
      <div style="display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: var(--space-sm);">
        <div>
          <h2>Wiki de campaña</h2>
          <p class="label">{{ paginasAccesibles.length === 1 ? 'Una página accesible para vos' : paginasAccesibles.length + ' páginas accesibles para vos' }}</p>
        </div>
      </div>
      <input class="input" v-model="q" type="search" placeholder="Buscar en la wiki…" style="max-width: 420px;" />
      <div v-if="cargando" class="label">Cargando…</div>
      <div class="card" style="padding: var(--space-md);">
        <div v-if="paginasAccesibles.length === 0" style="font-size: var(--text-sm); color: var(--color-ink-2);">Ninguna página coincide (solo ves lo que tu sesión permite).</div>
        <div v-for="p in paginasAccesibles" :key="p.id" class="page-row">
          <div>
            <p style="font-weight: 700; font-size: var(--text-sm); margin: 0;">
              <RouterLink class="text-link" :to="'/wiki/' + p.id">{{ p.titulo }}</RouterLink>
            </p>
            <p style="font-size: var(--text-xs); color: var(--color-muted); margin: 0;">{{ p.tipo }} · {{ etiquetaVisibilidad(p.visibilidad) }} · {{ p.mesaNombre }}</p>
          </div>
          <span class="tag tag--ink">{{ etiquetaVisibilidad(p.visibilidad) }}</span>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { getMisMesas } from '@/services/mesas'
import { getWiki } from '@/services/wiki'

const { user, isAuthenticated } = useAuth()

const q = ref('')
const paginas = ref([])
const cargando = ref(true)

onMounted(async () => {
  try {
    const mesas = await getMisMesas()
    const todas = []
    for (const m of mesas) {
      try {
        const w = await getWiki(m.id)
        for (const p of w.paginas || []) {
          todas.push({ ...p, mesaNombre: m.nombre, mesaId: m.id })
        }
      } catch (e) {
        // ignore
      }
    }
    paginas.value = todas
  } catch (e) {
    paginas.value = []
  } finally {
    cargando.value = false
  }
})

const paginasAccesibles = computed(() => {
  const texto = q.value.trim().toLowerCase()
  return paginas.value.filter((p) => !texto || (p.titulo + ' ' + p.tipo).toLowerCase().includes(texto))
})

function etiquetaVisibilidad(v) {
  return v === 'publica' ? 'Pública' : v === 'privada' ? 'Privada · solo GM' : 'Jugadores de la mesa'
}
</script>

<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-lg); align-items: start; }
.page-row { display: flex; align-items: center; justify-content: space-between; gap: var(--space-md); padding-block: var(--space-sm); border-bottom: var(--rule-hair) solid var(--color-rule); flex-wrap: wrap; }
.page-row:last-child { border-bottom: none; }
@media (max-width: 60rem) { .app-grid { padding-top: 120px; } }
</style>