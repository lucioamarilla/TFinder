<script setup>
import { ref, computed, inject, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import ConfirmModal from '@/components/modals/ConfirmModal.vue'
import { getSesiones } from '@/services/sesiones.js'
import { eliminarMesa } from '@/services/mesas.js'
import { useToast } from '@/composables/useToast.js'

const props = defineProps({ mesaId: { type: String, required: true } })

const router = useRouter()
const toast = useToast()

const gestion = inject('mesaGestion')
const mesa = computed(() => gestion?.mesa.value)
const esGM = computed(() => gestion?.esGM.value ?? false)

const sesiones = ref([])
const confirmarEliminar = ref(false)
const eliminando = ref(false)

const proximasSesiones = computed(() =>
  sesiones.value
    // D-12: el contrato define abierta|cerrada; proponemos las primeras 3
    // abiertas por fecha, de la mas cercana a la mas lejana.
    .filter((s) => s.estado === 'abierta')
    .sort((a, b) => String(a.fecha).localeCompare(String(b.fecha)))
    .slice(0, 3)
)

const ESTADOS = {
  abierta: { texto: 'ABIERTA', cls: 'tag--acid' },
  cerrada: { texto: 'REALIZADA', cls: 'tag--ember' }
}

function ordinalSesion(s) {
  const ordenadas = [...sesiones.value].sort((a, b) => String(a.fecha).localeCompare(String(b.fecha)))
  return `#${ordenadas.findIndex((x) => x.id === s.id) + 1}`
}

function fmt(f) {
  if (!f) return 'Fecha por definir'
  const m = String(f).match(/^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2}))?/)
  if (!m) return String(f)
  const [, y, mes, d, hh, mm] = m
  return `${d}/${mes}/${y}${hh ? ` · ${hh}:${mm}` : ''}`
}

async function cargarSesiones() {
  try {
    sesiones.value = await getSesiones(props.mesaId)
  } catch {
    sesiones.value = []
  }
}

onMounted(cargarSesiones)
watch(() => props.mesaId, cargarSesiones)

async function confirmarBaja() {
  eliminando.value = true
  try {
    await eliminarMesa(props.mesaId)
    toast.ok('Campaña disuelta · la crónica quedó archivada en el Cónclave.')
    router.push('/mis-mesas')
  } catch (e) {
    toast.error(e.message || 'No pudimos archivar la campaña.')
  } finally {
    eliminando.value = false
    confirmarEliminar.value = false
  }
}

const parametros = computed(() => {
  if (!mesa.value) return { izquierda: [], derecha: [] }
  // D-12: datos reales de MesaOut; nada hardcodeado ni campos inexistentes.
  const ocupacionTexto = `${mesa.value.jugadores ?? 0}/${mesa.value.plazas ?? '∞'}`
  return {
    izquierda: [
      { k: 'Sistema y Reglas:', v: 'Pathfinder 1ª Edición (OGL v1.0a)' },
      { k: 'Ambientación:', v: mesa.value.tono || '—' },
      { k: 'Nivel de Personajes:', v: mesa.value.rangoNivel || '—' },
      { k: 'Modalidad:', v: 'Mesa de la comunidad' },
      { k: 'Frecuencia / Horario:', v: mesa.value.horario || 'A coordinar con los participantes' }
    ],
    derecha: [
      { k: 'Director de Juego (GM):', v: mesa.value.gm || 'Por asignar', tu: true },
      { k: 'Ocupación de Mesa:', v: ocupacionTexto },
      { k: 'Sistema de Plataforma:', v: 'Mesa presencial o VTT acordada' },
      { k: 'Tono de la Crónica:', v: mesa.value.descripcion || '—' },
      { k: 'Visibilidad Pública:', v: 'Listada en el Buscador de Mesas TFinder', verde: true }
    ]
  }
})
</script>

<template>
      <div class="resumen">
      <!-- Parámetros de campaña -->
      <div>
        <h2 class="seccion-titulo">Parámetros de Campaña y Crónica</h2>
        <div class="card param-grid">
          <div class="param-col">
            <div v-for="item in parametros.izquierda" :key="item.k" class="param-fila">
              <span class="claves">{{ item.k }}</span>
              <span class="valores">{{ item.v }}</span>
            </div>
          </div>
          <div class="param-col">
            <div v-for="item in parametros.derecha" :key="item.k" class="param-fila">
              <span class="claves">{{ item.k }}</span>
              <span class="valores" :class="item.verde ? 'ok' : ''">{{ item.v }}<span v-if="item.tu" class="tag tag--ink tu">Tú</span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Sinopsis -->
      <div class="card">
        <div class="sinopsis-cabecera">
          <span class="claves">Sinopsis de la Mesa:</span>
          <span class="label">Visible para aspirantes a jugadores</span>
        </div>
        <p class="sinopsis">«{{ mesa?.descripcion }}»</p>
      </div>

      <!-- Próximas sesiones -->
      <div>
        <div class="seccion-cabecera">
          <h2 class="seccion-titulo">Próximas Sesiones Programadas</h2>
          <RouterLink
            :to="`/mesas/${mesaId}/calendario`"
            class="text-link"
          >
            + Convocar nueva fecha
          </RouterLink>
        </div>

        <div class="lista-sesiones">
          <div v-if="proximasSesiones.length === 0" class="label">Nada convocado todavía: proponé una fecha en el calendario.</div>
          <div
            v-for="(sesion, idx) in proximasSesiones"
            :key="sesion.id"
            class="card sesion-fila"
            :class="idx === 0 ? 'sesion-fila--primera' : ''"
          >
            <div class="sesion-ident">
              <div class="crt sesion-bloque">
                <span class="label">Sesión</span>
                <span class="num ordinal">{{ ordinalSesion(sesion) }}</span>
              </div>
              <div>
                <div class="sesion-titulos">
                  <span class="sesion-nombre">Sesión {{ ordinalSesion(sesion) }}</span>
                  <span class="tag" :class="ESTADOS[sesion.estado]?.cls">{{ ESTADOS[sesion.estado]?.texto || sesion.estado }}</span>
                </div>
                <p class="label fecha">Convocada para {{ fmt(sesion.fecha) }}</p>
              </div>
            </div>
            <RouterLink
              :to="`/mesas/${mesaId}/gestion/sesiones`"
              class="btn btn--secondary btn--sm"
            >
              Gestionar Hoja de Ruta
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- Zona peligrosa -->
      <div class="peligrosa">
        <div class="card peligrosa-card">
          <div class="peligrosa-texto">
            <div class="peligrosa-titulo-numerado">
              <span class="num">⚠</span>
              <span class="peligrosa-titulo">Zona Peligrosa de Campaña</span>
            </div>
            <p class="label">La disolución de la mesa archivará permanentemente las notas de la crónica, foros tácticos y desvinculará las fichas de los jugadores.</p>
          </div>

          <button
            type="button"
            class="btn btn--danger"
            @click="confirmarEliminar = true"
          >
            Eliminar Mesa
          </button>
        </div>
      </div>
    </div>

    <ConfirmModal
      :open="confirmarEliminar"
      :titulo="`¿Disolver «${mesa?.nombre}»?`"
      chip="Acción irreversible de archivo"
      mensaje="La campaña desaparecerá del buscador y sus notas de crónica quedarán selladas. ¿Continuar?"
      variante="danger"
      etiqueta-ok="Eliminar Mesa"
      @close="confirmarEliminar = false"
      @accept="confirmarBaja"
    />
</template>

<style scoped>
.resumen { display: grid; gap: var(--space-lg); }
.seccion-titulo { margin: 0 0 var(--space-sm); font-size: var(--text-title); color: var(--color-ink); }
.seccion-cabecera { display: flex; align-items: baseline; justify-content: space-between; gap: var(--space-md); flex-wrap: wrap; margin-bottom: var(--space-sm); }
.param-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--space-md) var(--space-lg); }
.param-col { display: grid; gap: var(--space-xs); min-width: 0; }
.param-fila { display: flex; justify-content: space-between; gap: var(--space-sm); padding-block: var(--space-2xs); border-bottom: var(--rule-hair) solid var(--color-rule); flex-wrap: wrap; }
.claves { font-weight: 700; font-size: var(--text-sm); color: var(--color-accent-2); text-transform: uppercase; letter-spacing: .04em; }
.valores { font-size: var(--text-md); color: var(--color-ink); display: inline-flex; align-items: center; gap: var(--space-2xs); }
.valores.ok { color: var(--color-accent-2); font-weight: 700; }
.tu { font-size: var(--text-xs); }
.sinopsis-cabecera { display: flex; justify-content: space-between; gap: var(--space-md); margin-bottom: var(--space-2xs); flex-wrap: wrap; }
.sinopsis { margin: 0; font-style: italic; color: var(--color-ink); }
.lista-sesiones { display: grid; gap: var(--space-sm); }
.sesion-fila { display: flex; align-items: center; justify-content: space-between; gap: var(--space-md); padding: var(--space-sm) var(--space-md); flex-wrap: wrap; }
.sesion-fila--primera { border-color: var(--color-accent); }
.sesion-ident { display: flex; align-items: center; gap: var(--space-sm); min-width: 0; }
.sesion-bloque { width: 56px; height: 56px; display: grid; place-content: center; text-align: center; gap: 2px; background: var(--color-paper-3); border: var(--rule-hair) solid var(--color-rule); }
.ordinal { font-size: var(--text-md); color: var(--color-ink); }
.sesion-titulos { display: flex; align-items: center; gap: var(--space-2xs); flex-wrap: wrap; }
.sesion-nombre { font-weight: 700; color: var(--color-ink); }
.fecha { color: var(--color-ink-2); }
.peligrosa { border-top: var(--rule-bar) solid var(--color-rule); padding-top: var(--space-md); }
.peligrosa-card { display: flex; align-items: center; justify-content: space-between; gap: var(--space-md); border-color: var(--color-error); flex-wrap: wrap; }
.peligrosa-titulo-numerado { display: flex; gap: var(--space-2xs); align-items: center; color: var(--color-error); font-weight: 700; text-transform: uppercase; letter-spacing: .06em; font-size: var(--text-sm); }
.peligrosa-texto { display: grid; gap: var(--space-2xs); max-width: 60ch; }
@media (max-width: 60rem) { .param-grid { grid-template-columns: minmax(0, 1fr); } }
</style>
