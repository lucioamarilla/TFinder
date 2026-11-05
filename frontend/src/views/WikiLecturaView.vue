<template>
  <div class="app-grid">
    <main style="display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-md);">
      <div v-if="cargando" class="label">Cargando…</div>
      <article v-else-if="!pagina" class="card" style="padding: var(--space-xl); text-align: center;">
        <h2>Página no encontrada</h2>
        <p style="font-size: var(--text-sm); color: var(--color-ink-2); margin-top: var(--space-sm);">La página no existe o fue eliminada.</p>
        <RouterLink class="btn btn--secondary" to="/wiki" style="margin-top: var(--space-md);">Volver al índice</RouterLink>
      </article>

      <template v-else>
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: var(--space-sm);">
          <div>
            <p class="label">Página de wiki, {{ pagina.tipo }}</p>
            <h2 style="max-width: none;">{{ pagina.titulo }}</h2>
          </div>
          <div style="display: flex; gap: var(--space-sm); flex-wrap: wrap;">
            <RouterLink v-if="puedeEditar" class="btn btn--secondary" :to="'/wiki/' + pagina.id + '/editar'">Editar</RouterLink>
            <RouterLink class="btn btn--secondary" to="/wiki">Índice</RouterLink>
          </div>
        </div>
        <article class="card lectura">
          <div class="cuerpo">
            <p v-for="(t, i) in parrafos" :key="i">{{ t }}</p>
          </div>
          <hr class="divisor-oro">
          <p class="label">Actualizada: {{ pagina.actualizada || 'hoy' }}</p>
        </article>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { wikiApi } from '@/api/endpoints'
import { paginaApi } from '@/services/wiki'

const route = useRoute()
const { user, isAuthenticated } = useAuth()

const pagina = ref(null)
const cargando = ref(true)

onMounted(async () => {
  try {
    const { datos } = await wikiApi.detallar(route.params.id)
    pagina.value = paginaApi(datos)
  } catch (e) {
    pagina.value = null
  } finally {
    cargando.value = false
  }
})

const puedeEditar = computed(() => isAuthenticated.value) // simplificado

const parrafos = computed(() => {
  const contenido = pagina.value?.contenido || []
  const textos = contenido.map((b) => (typeof b === 'string' ? b : b?.texto)).filter(Boolean)
  if (textos.length) return textos
  return pagina.value?.cuerpo ? [pagina.value.cuerpo] : []
})
</script>

<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-md); align-items: start; }
.lectura { padding: var(--space-lg); }
.lectura .cuerpo { font-size: var(--text-lg); line-height: 1.6; color: var(--color-ink-2); display: grid; gap: var(--space-md); max-width: 62ch; }
.divisor-oro { height: 2px; background: linear-gradient(to right, transparent, var(--color-accent-2), transparent); border: none; margin-block: var(--space-lg); }
@media (max-width: 60rem) { .app-grid { padding-top: 120px; } }
</style>