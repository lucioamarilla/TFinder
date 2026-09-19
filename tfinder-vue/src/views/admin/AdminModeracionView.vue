<script setup>
import { ref, computed, onMounted } from 'vue'
import { getModeracion, ocultarCaso, restaurarCaso, eliminarCaso } from '@/services/admin.js'
import { useToast } from '@/composables/useToast'
import ConfirmModal from '@/components/modals/ConfirmModal.vue'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'

const toast = useToast()

const stats = ref([])
const pestanas = ref([])
const casos = ref([])
const tab = ref('pendiente')
const cargando = ref(true)
const fallo = ref(null)
const enAccion = ref(null)
const modalEliminar = ref(false)
const casoAeliminar = ref(null)

const visibles = computed(() => {
  if (tab.value === 'todos') return casos.value
  return casos.value.filter((c) => c.estado === tab.value)
})

const tonoStat = {
  rojo: 'text-[#8B1A1A]',
  cobre: 'text-[#8B5A2B]',
  tinta: 'text-[#1A1A1A]'
}

const tonoMotivo = {
  rojo: 'text-[#8B1A1A]',
  cobre: 'text-[#8B5A2B]'
}

const badgeTipo = {
  POST: 'border-[#8B5A2B]/40 bg-[#8B5A2B]/10 text-[#8B5A2B]',
  COMENTARIO: 'border-[#8B7D6B] bg-[#C2A980]/20 text-[#5C5346]',
  WIKI: 'border-[#6B8E23]/40 bg-[#6B8E23]/10 text-[#6B8E23]',
  BUILD: 'border-[#8F6F16]/40 bg-[#D4AF37]/20 text-[#8F6F16]'
}

async function cargar() {
  cargando.value = true
  fallo.value = null
  try {
    const data = await getModeracion()
    stats.value = data.stats
    pestanas.value = data.pestanas
    casos.value = data.casos
  } catch (e) {
    fallo.value = e.message || 'El Tribunal de Vigilancia no respondió.'
  } finally {
    cargando.value = false
  }
}

function cambiarTab(id, label) {
  tab.value = id
  toast.info(`Vista del tribunal: ${label}.`)
}

function reemplazar(actualizado) {
  const i = casos.value.findIndex((c) => c.id === actualizado.id)
  if (i >= 0) casos.value.splice(i, 1, actualizado)
}

async function ocultar(caso) {
  enAccion.value = caso.id
  try {
    reemplazar(await ocultarCaso(caso.id))
    toast.ok('Contenido ocultado de la comunidad.')
  } catch (e) {
    toast.error(e.message)
  } finally {
    enAccion.value = null
  }
}

async function restaurar(caso) {
  enAccion.value = caso.id
  try {
    reemplazar(await restaurarCaso(caso.id))
    toast.ok('Contenido restaurado y republicado.')
  } catch (e) {
    toast.error(e.message)
  } finally {
    enAccion.value = null
  }
}

function pedirEliminar(caso) {
  casoAeliminar.value = caso
  modalEliminar.value = true
}

async function confirmarEliminar() {
  const caso = casoAeliminar.value
  modalEliminar.value = false
  if (!caso) return
  try {
    await eliminarCaso(caso.id)
    casos.value = casos.value.filter((c) => c.id !== caso.id)
    toast.ok('Contenido eliminado del cónclave.')
  } catch (e) {
    toast.error(e.message)
  } finally {
    casoAeliminar.value = null
  }
}

onMounted(cargar)
</script>

<template>
  <main class="flex-grow max-w-7xl w-full mx-auto px-6 py-10">
    <nav class="flex items-center justify-between gap-2 text-[11px] font-tarzana font-semibold tracking-wider uppercase mb-4" aria-label="Migas de pan">
      <div class="flex items-center gap-2 text-[#8B7D6B]">
        <RouterLink to="/dashboard" class="hover:text-[#8B5A2B]">Inicio</RouterLink>
        <span>/</span>
        <span>Administración</span>
        <span>/</span>
        <span class="text-[#D4AF37]">Tribunal de Vigilancia</span>
      </div>
      <div class="hidden sm:flex items-center gap-3 text-[10px]">
        <span class="inline-flex items-center gap-1.5 text-[#8B1A1A] font-bold">
          <span class="w-1.5 h-1.5 rounded-full bg-[#8B1A1A] animate-pulse" aria-hidden="true"></span>
          3 reportes activos sin resolver
        </span>
        <span class="text-[#8B7D6B]">Códice de disciplina Paizo OGL v1.0a</span>
      </div>
    </nav>

    <header class="mb-6">
      <h1 class="font-mason text-3xl font-bold text-[#8B5A2B] tracking-wide">✦ Moderación ✦</h1>
      <p class="font-minion italic text-[#8B7D6B] mt-1">
        Supervisión de pergaminos, debates del concilio y decretos reportados por aventureros de la comunidad.
      </p>
    </header>

    <LoadingState v-if="cargando" message="Abriendo el Tribunal de Vigilancia…" />

    <ErrorState
      v-else-if="fallo"
      title="El Tribunal está en receso"
      :message="fallo"
      @retry="cargar"
    />

    <template v-else>
      <div class="grid sm:grid-cols-3 gap-4 mb-6">
        <div v-for="stat in stats" :key="stat.label" class="bg-[#FDF8EE]/90 border border-[#C2A980] rounded-sm px-4 py-3 text-center">
          <p class="font-tarzana text-[0.68rem] uppercase tracking-widest text-[#8B7D6B]">{{ stat.label }}</p>
          <p class="font-mason text-2xl font-bold mt-1" :class="tonoStat[stat.tono]">{{ stat.valor }}</p>
        </div>
      </div>

      <div class="flex flex-wrap gap-2 border-b border-[#C2A980] mb-0" role="tablist">
        <button
          v-for="p in pestanas"
          :key="p.id"
          type="button"
          role="tab"
          :aria-selected="tab === p.id"
          class="min-h-[44px] px-4 font-mason text-sm font-bold flex items-center gap-2 border-b-2 -mb-px transition-colors"
          :class="tab === p.id ? 'border-[#D4AF37] text-[#8B5A2B]' : 'border-transparent text-[#8B7D6B] hover:text-[#8B5A2B]'"
          @click="cambiarTab(p.id, p.label)"
        >
          {{ p.label }}
          <span
            class="min-w-[22px] px-1.5 py-0.5 rounded-full text-[11px] font-tarzana"
            :class="tab === p.id ? 'bg-[#8B1A1A] text-[#FDF8EE]' : 'bg-[#C2A980]/50 text-[#1A1A1A]'"
          >{{ p.conteo }}</span>
        </button>
      </div>

      <div class="bg-[#FDF8EE]/95 border-2 border-[#C2A980] shadow-xl rounded-sm overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full font-minion text-sm">
            <thead class="bg-[#F4EAD6]">
              <tr class="text-left font-tarzana uppercase tracking-wider text-xs text-[#1A1A1A] border-b border-[#C2A980]">
                <th scope="col" class="px-4 py-3">Tipo</th>
                <th scope="col" class="px-4 py-3">Contenido (Muestra)</th>
                <th scope="col" class="px-4 py-3">Autor</th>
                <th scope="col" class="px-4 py-3">Fecha</th>
                <th scope="col" class="px-4 py-3 text-center">Reportes</th>
                <th scope="col" class="px-4 py-3 text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="caso in visibles" :key="caso.id" class="border-b border-[#C2A980]/60 last:border-0 align-top">
                <td class="px-4 py-3">
                  <span class="font-tarzana text-[11px] font-bold uppercase px-2 py-0.5 rounded border" :class="badgeTipo[caso.tipo]">
                    {{ caso.tipo }}
                  </span>
                </td>
                <td class="px-4 py-3 max-w-md">
                  <p class="text-[#1A1A1A]">{{ caso.contenido }}</p>
                  <p class="font-tarzana text-[11px] uppercase mt-1 text-[#8B7D6B]">
                    Motivo: <span class="font-bold" :class="tonoMotivo[caso.tonoMotivo]">{{ caso.motivo }}</span>
                  </p>
                </td>
                <td class="px-4 py-3">
                  <p class="font-tarzana font-bold text-[#1A1A1A]">{{ caso.autor }}</p>
                  <p class="font-tarzana text-[11px] text-[#8B7D6B]">{{ caso.autorMeta }}</p>
                </td>
                <td class="px-4 py-3 font-tarzana text-xs text-[#5C5346] whitespace-nowrap">{{ caso.fecha }}</td>
                <td class="px-4 py-3 text-center">
                  <span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-[#8B1A1A]/10 border border-[#8B1A1A]/30 text-[#8B1A1A] font-tarzana font-bold">
                    {{ caso.reportes }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <div class="flex flex-wrap items-center justify-center gap-2">
                    <button
                      type="button"
                      class="min-h-[44px] px-3 py-1.5 rounded-sm bg-[#D4AF37] text-[#1A1A1A] font-tarzana text-[11px] font-bold uppercase hover:brightness-110 transition disabled:opacity-60"
                      :disabled="enAccion === caso.id || caso.estado === 'oculto'"
                      title="Ocultar del tablón"
                      @click="ocultar(caso)"
                    >
                      Ocultar
                    </button>
                    <button
                      type="button"
                      class="min-h-[44px] px-3 py-1.5 rounded-sm bg-[#8B1A1A] text-[#FDF8EE] font-tarzana text-[11px] font-bold uppercase hover:bg-[#6D1313] transition disabled:opacity-60"
                      :disabled="enAccion === caso.id"
                      title="Purgar definitivamente"
                      @click="pedirEliminar(caso)"
                    >
                      Eliminar
                    </button>
                    <button
                      type="button"
                      class="min-h-[44px] px-3 py-1.5 rounded-sm bg-[#6B8E23] text-[#FDF8EE] font-tarzana text-[11px] font-bold uppercase hover:brightness-110 transition disabled:opacity-60"
                      :disabled="enAccion === caso.id || caso.estado === 'pendiente'"
                      title="Desestimar y mantener"
                      @click="restaurar(caso)"
                    >
                      Restaurar
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="visibles.length === 0">
                <td colspan="6" class="px-4 py-10 text-center">
                  <p class="font-mason text-lg text-[#8B5A2B] font-bold">Sin casos en esta vista</p>
                  <p class="font-minion text-sm text-[#8B7D6B] italic mt-1">El Tribunal no registra contenido pendiente con este filtro.</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="bg-[#F4EAD6] border-t border-[#C2A980] px-4 py-3 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div class="flex items-center gap-3 font-tarzana text-xs text-[#8B7D6B]">
            <span>Mostrando 1 a {{ visibles.length }} de 27 casos reportados</span>
            <span class="text-[#8B5A2B] font-semibold">Registro de auditoría activo</span>
          </div>
          <div class="flex items-center gap-1 font-tarzana text-xs">
            <button type="button" class="min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2 py-1 rounded-sm border border-[#C2A980] text-[#8B7D6B] opacity-50 cursor-not-allowed" disabled>« Previo</button>
            <button type="button" class="min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2.5 py-1 rounded-sm bg-[#D4AF37] text-[#1A1A1A] font-bold" @click="toast.info('Ya estás en la primera página del registro.')">1</button>
            <button type="button" class="min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2.5 py-1 rounded-sm border border-[#C2A980] hover:border-[#8B5A2B] text-[#8B5A2B]" @click="toast.info('Página 2 del registro (simulada).')">2</button>
            <button type="button" class="min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2.5 py-1 rounded-sm border border-[#C2A980] hover:border-[#8B5A2B] text-[#8B5A2B]" @click="toast.info('Página 3 del registro (simulada).')">3</button>
            <button type="button" class="min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2 py-1 rounded-sm border border-[#C2A980] hover:border-[#8B5A2B] text-[#8B5A2B]" @click="toast.info('Página siguiente del registro (simulada).')">Siguiente »</button>
          </div>
        </div>
      </div>

      <div class="mt-6 bg-[#FDF8EE]/80 border border-[#C2A980] rounded-sm p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <p class="font-minion text-sm text-[#5C5346]">
          <span class="text-[#8B5A2B] text-lg mr-1" aria-hidden="true">⚖</span>
          <b class="font-mason text-[#8B5A2B]">Protocolo del Tribunal:</b>
          Todo contenido eliminado o suspendido genera un edicto archivado según las cláusulas de juego limpio OGL v1.0a.
          Los aventureros afectados reciben una notificación formal en su Centro de Notificaciones.
        </p>
        <button
          type="button"
          class="shrink-0 font-tarzana text-xs font-bold uppercase tracking-wider text-[#8B5A2B] hover:underline"
          @click="toast.info('Códice de conducta del Cónclave (simulado).')"
        >
          Ver Código de Conducta →
        </button>
      </div>
    </template>

    <ConfirmModal
      :open="modalEliminar"
      titulo="¿Eliminar contenido?"
      :chip="casoAeliminar?.contenido"
      mensaje="Esta acción no se puede deshacer. El reporte se archivará en el Tribunal de Vigilancia."
      variante="danger"
      etiqueta-ok="Eliminar"
      @close="modalEliminar = false"
      @accept="confirmarEliminar"
    />
  </main>
</template>
