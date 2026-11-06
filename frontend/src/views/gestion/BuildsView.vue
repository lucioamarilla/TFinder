<script setup>
import { ref, computed, inject, onMounted, watch } from 'vue'
import { useToast } from '@/composables/useToast.js'
import ModalAsociarBuild from '@/components/modals/ModalAsociarBuild.vue'
import { getBuilds, miBuildActivo, vincularBuild } from '@/services/builds.js'
import { getMiembros } from '@/services/jugadores.js'
import { getMesas } from '@/services/mesas.js'

const props = defineProps({ mesaId: { type: String, required: true } })

const toast = useToast()
const gestion = inject('mesaGestion')

const builds = ref([])
const equipo = ref({ miembros: [], capacidad: 5 })
const miBuild = ref(null)
const mesas = ref([])
const modalAbierto = ref(false)

const libres = computed(() => Math.max(0, equipo.value.capacidad - equipo.value.miembros.length))
const conBuild = computed(() => builds.value.filter((b) => b.protagonista).length)

const ICONOS_CLASE = {
  Guerrero: 'M6.92 3.75L12 8.83l5.08-5.08 1.42 1.42L13.42 10.25 18.5 15.33l-1.42 1.42L12 11.67l-5.08 5.08-1.42-1.42 5.08-5.08L5.5 5.17z',
  Paladín: 'M12 2l8 4v6c0 5-3.4 8.5-8 10-4.6-1.5-8-5-8-10V6l8-4zm-1 12l5-5-1.4-1.4L11 11.2 9.4 9.6 8 11l3 3z',
  Mago: 'M12 2l1.8 5.2L19 9l-5.2 1.8L12 16l-1.8-5.2L5 9l5.2-1.8L12 2z',
  Explorador: 'M12 2l9 5v10l-9 5-9-5V7l9-5zm0 4.5L6 9.7v5.6l6 3.2 6-3.2V9.7l-6-3.2z'
}

async function cargar() {
  const mesa = gestion?.mesa.value ?? null
  const [lista, jugadores, todas] = await Promise.all([getBuilds(props.mesaId), getMiembros(props.mesaId, mesa), getMesas()])
  builds.value = lista
  equipo.value = jugadores
  mesas.value = todas.map((m) => ({ id: m.id, nombre: m.nombre, estado: m.estado }))
  miBuild.value = await miBuildActivo()
}

onMounted(cargar)
watch(() => props.mesaId, cargar)

function abrirModal() {
  modalAbierto.value = true
}

async function asociar(mesaDestinoId) {
  modalAbierto.value = false
  if (!mesaDestinoId) return
  const destino = mesas.value.find((m) => m.id === mesaDestinoId)
  await vincularBuild(miBuild.value.id, mesaDestinoId)
  toast.ok(`Build vinculado a «${destino?.nombre || 'la mesa'}».`)
}
</script>

<template>
      <div class="builds">
      <div class="builds-cabecera">
        <div>
          <h2 class="titulo-seccion">✦ Builds Asociados a la Campaña</h2>
          <p class="label">
            {{ conBuild }} de {{ equipo.miembros.length }} jugadores activos tienen un build enlazado.
          </p>
        </div>
        <button type="button" class="btn btn--sm" @click="abrirModal">
          Asociar mi Build
        </button>
      </div>

      <div class="tarjetas">
        <article v-for="build in builds" :key="build.id" class="card ficha">
          <div class="ficha-cabeza">
            <div class="crt icono-clase">
              <svg class="glifo" viewBox="0 0 24 24" fill="currentColor">
                <path :d="ICONOS_CLASE[build.clase] || ICONOS_CLASE.Guerrero"></path>
              </svg>
            </div>
            <div class="min-w">
              <h3 class="ficha-nombre">{{ build.nombre }}</h3>
              <p class="label ficha-clase">{{ build.clase }} · Nivel {{ build.nivel }}</p>
            </div>
          </div>

          <p class="ficha-detalle">{{ build.detalle }}</p>

          <div class="ficha-pie">
            <span class="label dueño">Jugador: {{ build.persona }} ({{ build.handle }})</span>
            <RouterLink :to="`/builds/${build.id}`" class="text-link">
              Ver Ficha →
            </RouterLink>
          </div>
        </article>

        <!-- Ranura vacante -->
        <article v-for="n in libres" :key="`vacante-${n}`" class="vacante">
          <span class="mas">＋</span>
          <p class="label vacante-texto">
            La campaña tiene espacio para un aventurero adicional. Una vez aceptada una solicitud, su build aparecerá aquí.
          </p>
          <RouterLink :to="`/mesas/${mesaId}/gestion/jugadores`" class="text-link">
            + Invitar a Jugador
          </RouterLink>
        </article>
      </div>

      <p class="label nota-final">
        Los builds asociados se recalculan automáticamente al subir de nivel en la campaña. Los jugadores pueden importar fichas en formato JSON desde Pathbuilder 1e o exportar su bloque de estadísticas OGL para imprimir en mesa.
      </p>
    </div>

    <ModalAsociarBuild
      :open="modalAbierto"
      :build="{ nombre: miBuild?.nombre || '', detalle: miBuild?.detalle || '' }"
      :mesas="mesas"
      @close="modalAbierto = false"
      @accepted="asociar"
    />
</template>

<style scoped>
.builds { display: grid; gap: var(--space-md); }
.builds-cabecera { display: flex; align-items: center; justify-content: space-between; gap: var(--space-md); flex-wrap: wrap; border-bottom: var(--rule-bar) solid var(--color-rule); padding-bottom: var(--space-sm); }
.titulo-seccion { margin: 0; font-size: var(--text-title); color: var(--color-ink); }
.tarjetas { display: grid; gap: var(--space-sm); grid-template-columns: repeat(1, minmax(0, 1fr)); }
@media (min-width: 60rem) { .tarjetas { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
.ficha { display: flex; flex-direction: column; justify-content: space-between; gap: var(--space-sm); border-left: var(--rule-bar) solid var(--color-accent-2); }
.ficha-cabeza { display: flex; align-items: flex-start; gap: var(--space-sm); }
.icono-clase { width: 44px; height: 44px; display: grid; place-content: center; background: var(--color-ink); border: var(--rule-hair) solid var(--color-accent); flex-shrink: 0; }
.glifo { width: 24px; height: 24px; color: var(--color-accent); }
.min-w { min-width: 0; }
.ficha-nombre { margin: 0; font-size: var(--text-md); font-weight: 700; color: var(--color-ink); line-height: 1.15; }
.ficha-clase { margin: 0; text-transform: uppercase; letter-spacing: .06em; }
.ficha-detalle { margin: 0; font-size: var(--text-sm); color: var(--color-ink-2); font-style: italic; }
.ficha-pie { display: flex; align-items: center; justify-content: space-between; gap: var(--space-2xs); padding-top: var(--space-2xs); border-top: var(--rule-hair) solid var(--color-rule); flex-wrap: wrap; }
.dueño { color: var(--color-ink-2); }
.vacante { border: var(--rule-hair) dashed var(--color-rule); padding: var(--space-md); display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; gap: var(--space-2xs); min-height: 10.5rem; }
.mas { color: var(--color-ink-2); font-size: var(--text-xl); }
.vacante-texto { max-width: 15rem; color: var(--color-ink-2); font-style: italic; }
.nota-final { border-top: var(--rule-hair) solid var(--color-rule); padding-top: var(--space-sm); color: var(--color-ink-2); margin: 0; }
@media (max-width: 60rem) { .builds { padding-top: 0; } }
</style>
