<script setup>
import { ref, computed, provide, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getMesa } from '@/services/mesas.js'
import { getMembresias } from '@/services/membresias.js'
import { getSesiones } from '@/services/sesiones.js'
import { getMiembros, contarJugadores } from '@/services/jugadores.js'
import { isFeatureEnabled } from '@/config/features'
import { useToast } from '@/composables/useToast.js'

const props = defineProps({ mesaId: { type: String, required: true } })

const route = useRoute()
const toast = useToast()

const mesa = ref(null)
const cargando = ref(true)
const noEncontrada = ref(false)
const sesionesCount = ref(0)
const ocupacion = ref({ miembros: 0, capacidad: 5 })
const esGM = ref(false)

const TABS = [
  { segmento: 'gestion', feature: 'gestionMesa', etiqueta: 'Resumen', corta: 'Resumen', flora: true },
  { segmento: 'calendario', feature: 'calendario', etiqueta: 'Calendario & Votación', corta: 'Calendario', glyph: '', flora: false },
  { segmento: 'sesiones', feature: 'sesiones', etiqueta: 'Sesiones', corta: 'Sesiones', glyph: '', flora: false },
  { segmento: 'jugadores', feature: 'jugadores', etiqueta: 'Jugadores', corta: 'Jugadores', glyph: '', flora: false },
]

// Solo se ofrecen las pestanas cuya funcion esta habilitada: asi una tab
// nunca lleva a una pantalla que responda "Proximamente".
const tabsVisibles = computed(() => TABS.filter((tab) => isFeatureEnabled(tab.feature)))

const rutaBase = computed(() => `/mesas/${props.mesaId}`)

function tabActiva(tab) {
  const base = tab.segmento === 'gestion' ? `${rutaBase.value}/gestion` : `${rutaBase.value}/${tab.segmento}`
  return tab.segmento === 'gestion'
    ? route.path === base
    : route.path.startsWith(base)
}

function contador(tab) {
  if (tab.segmento === 'sesiones') return sesionesCount.value
  if (tab.segmento === 'jugadores') return `${ocupacion.value.miembros}/${ocupacion.value.capacidad}`
  return null
}

const estadoBadge = computed(() => {
  const estado = (mesa.value?.estado || '').toLowerCase()
  if (estado.includes('abiert')) {
    return { texto: 'Abierta', cls: 'tag--acid', pulso: true }
  }
  return { texto: 'Cerrada', cls: 'tag--ember', pulso: false }
})

async function cargar() {
  cargando.value = true
  noEncontrada.value = false
  // D-02: la mesa existe si getMesa responde; cada dato secundario degrada
  // su sección sin anular el panel completo.
  try {
    const detalle = await getMesa(props.mesaId)
    mesa.value = detalle
  } catch (e) {
    noEncontrada.value = true
    cargando.value = false
    return
  }
  let falloSecundario = false
  try {
    const sesiones = await getSesiones(props.mesaId)
    sesionesCount.value = sesiones.length
  } catch {
    falloSecundario = true
  }
  try {
    const jugadores = await getMiembros(props.mesaId, mesa.value)
    // El master no ocupa plaza: el badge cuenta solo jugadores (rol 'Jugador')
    // para que coincida con mesa.jugadores del buscador (0/5, no 1/5).
    const lista = jugadores?.miembros
    ocupacion.value = {
      miembros: lista ? contarJugadores(lista) : (mesa.value.jugadores ?? 0),
      capacidad: jugadores?.capacidad ?? mesa.value.plazas ?? null
    }
  } catch {
    falloSecundario = true
    ocupacion.value = { miembros: mesa.value.jugadores ?? 0, capacidad: mesa.value.plazas ?? null }
  }
  try {
    const membresias = await getMembresias()
    esGM.value = membresias.some((m) => String(m.mesaId ?? m.id) === String(props.mesaId) && m.rol === 'master')
  } catch {
    falloSecundario = true
  }
  if (falloSecundario) toast.info('Algunas secciones de la mesa no se pudieron cargar.')
  cargando.value = false
}

onMounted(cargar)
watch(() => props.mesaId, cargar)

provide('mesaGestion', { mesa, cargando, sesionesCount, ocupacion, esGM })
</script>

<template>
  <div v-if="noEncontrada" class="gestion-noencontrada">
    No encontramos la mesa que buscas. Quizá fue archivada por el Director de Juego.
    <RouterLink to="/mis-mesas" class="text-link">← Volver a Mis Mesas</RouterLink>
  </div>

  <div v-else-if="cargando" class="gestion-cargando" role="status">
    <p class="label">Abriendo el grimorio de campaña…</p>
  </div>

  <div v-else-if="mesa" class="gestion-shell">
    <!-- Miga de pan -->
    <div class="miga">
      <div class="miga-ruta">
        <RouterLink to="/mis-mesas" class="text-link">Mis Mesas</RouterLink>
        <span>/</span>
        <span class="label">Gestión de Campaña</span>
        <span>/</span>
        <span class="num">{{ mesa.nombre }}</span>
      </div>
      <span class="tag tag--ink">Modo Director de Juego (GM)</span>
    </div>

    <!-- Cabecera de la mesa -->
    <section class="card cabecera">
      <div class="cabecera-principal">
        <div class="cabecera-identidad">
          <div class="identidad-fila">
            <h1 class="titulo">{{ mesa.nombre }}</h1>
            <span class="tag tag--ink">{{ mesa.sistema || 'PF1E' }}</span>
            <span class="tag" :class="estadoBadge.cls">
              <span v-if="estadoBadge.pulso" class="punto"></span>
              {{ estadoBadge.texto }}
            </span>
          </div>
          <p class="label lore">{{ mesa.lore }}</p>
        </div>

        <div v-if="esGM" class="cabecera-acciones">
          <RouterLink
            :to="`${rutaBase}/editar`"
            class="btn btn--secondary btn--sm"
          >
            Editar mesa
          </RouterLink>
          <!-- Invitar jugador: retirado (el botón no tenía funcionalidad real). -->
        </div>
      </div>
    </section>

    <!-- Tabs horizontales -->
    <nav class="tabs" aria-label="Gestión de la mesa">
      <RouterLink
        v-for="tab in tabsVisibles"
        :key="tab.segmento"
        :to="tab.segmento === 'gestion' ? `${rutaBase}/gestion` : `${rutaBase}/gestion/${tab.segmento}`"
        :class="tabActiva(tab) ? 'tab tab--activa' : 'tab'"
      >
        <span class="tab-nombre tab-nombre--larga">{{ tab.etiqueta }}</span>
        <span class="tab-nombre tab-nombre--corta">{{ tab.corta || tab.etiqueta }}</span>
        <span v-if="contador(tab) !== null" class="tab-contador num">{{ contador(tab) }}</span>
      </RouterLink>
    </nav>

    <!-- Contenido de la pestaña -->
    <div class="card panel">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.gestion-shell { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-lg); display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-md); align-items: start; }
.miga { display: flex; align-items: center; justify-content: space-between; gap: var(--space-md); flex-wrap: wrap; }
.miga-ruta { display: flex; align-items: center; gap: var(--space-2xs); font-size: var(--text-sm); color: var(--color-muted); flex-wrap: wrap; }
.cabecera { padding: var(--space-md); }
.cabecera-principal { display: flex; flex-direction: column; gap: var(--space-sm); }
.cabecera-identidad { display: grid; gap: var(--space-2xs); min-width: 0; }
.identidad-fila { display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-2xs); }
.titulo { margin: 0; font-size: var(--text-title); color: var(--color-ink); }
.lore { color: var(--color-ink-2); max-width: 60ch; }
.cabecera-acciones { display: flex; gap: var(--space-2xs); align-items: center; flex-wrap: wrap; }
/* tabs y .tab son globales (app.css); aquí queda solo lo propio del shell */
.punto { width: 8px; height: 8px; border-radius: 999px; background: currentColor; display: inline-block; }
/* etiquetas dobles de pestaña: la corta solo entra en pantallas chicas para
   no partir palabras ni arrastrar scroll innecesario */
.tab-nombre--corta { display: none; }
@media (max-width: 40rem) { .tab-nombre--larga { display: none; } .tab-nombre--corta { display: inline; } }
.panel { padding: var(--space-md); min-height: 40vh; }
.gestion-noencontrada { max-width: var(--container); margin: 0 auto; padding: 112px var(--gutter) var(--space-lg); text-align: center; display: grid; gap: var(--space-sm); }
.gestion-cargando { max-width: var(--container); margin: 0 auto; padding: 112px var(--gutter) var(--space-lg); }
@media (max-width: 60rem) { .cabecera-principal { align-items: flex-start; } }
</style>
