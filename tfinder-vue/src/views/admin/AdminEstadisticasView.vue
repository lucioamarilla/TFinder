<script setup>
import { ref, onMounted } from 'vue'
import { getEstadisticas } from '@/services/admin.js'
import { useToast } from '@/composables/useToast'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'

const toast = useToast()

const datos = ref(null)
const cargando = ref(true)
const fallo = ref(null)
const desde = ref('4712-10-08')
const hasta = ref('4712-10-14')

const tonoResumen = {
  cobre: 'text-[#8B5A2B]',
  oro: 'text-[#D4AF37]',
  verde: 'text-[#6B8E23]'
}

const tonoBadge = {
  verde: 'text-[#6B8E23] bg-[#6B8E23]/10 border-[#6B8E23]/40',
  rojo: 'text-[#8B1A1A] bg-[#8B1A1A]/10 border-[#8B1A1A]/40',
  oro: 'text-[#8F6F16] bg-[#D4AF37]/20 border-[#8F6F16]/40'
}

async function cargar() {
  cargando.value = true
  fallo.value = null
  try {
    datos.value = await getEstadisticas()
  } catch (e) {
    fallo.value = e.message || 'El motor de telemetría no respondió.'
  } finally {
    cargando.value = false
  }
}

function filtrar() {
  toast.ok('Logs filtrados por rango de fechas.')
}

function exportar() {
  toast.info('Exportación CSV preparada (simulada).')
}

onMounted(cargar)
</script>

<template>
  <main class="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    <nav class="flex items-center justify-between gap-2 text-[11px] font-tarzana font-semibold tracking-wider uppercase" aria-label="Migas de pan">
      <div class="flex items-center gap-2 text-[#8B7D6B]">
        <RouterLink to="/dashboard" class="hover:text-[#8B5A2B]">Inicio</RouterLink>
        <span>/</span>
        <span>Administración</span>
        <span>/</span>
        <span class="text-[#D4AF37]">Estadísticas y Logs de Actividad</span>
      </div>
      <div class="hidden sm:flex items-center gap-3 text-[10px]">
        <span class="inline-flex items-center gap-1.5 text-[#6B8E23] font-bold">
          <span class="w-1.5 h-1.5 rounded-full bg-[#6B8E23] animate-pulse" aria-hidden="true"></span>
          Motor de telemetría: activo
        </span>
        <span class="text-[#8B7D6B]">Códice de auditoría Paizo OGL v1.0a</span>
      </div>
    </nav>

    <LoadingState v-if="cargando" message="Reuniendo métricas del cónclave…" />

    <ErrorState v-else-if="fallo" title="El motor de telemetría está en silencio" :message="fallo" @retry="cargar" />

    <template v-else>
      <header class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
        <div>
          <h1 class="font-mason text-3xl sm:text-4xl font-black text-[#8B5A2B] tracking-wide">✦ Estadísticas y Logs ✦</h1>
          <p class="font-minion italic text-[#5C5346] mt-1">
            Compendio analítico del Cónclave: flujo de aventureros, creación de mesas y registro inmutable de decretos.
          </p>
        </div>
        <div class="grid grid-cols-3 gap-3 shrink-0">
          <div v-for="item in datos.resumen" :key="item.label" class="bg-[#FDF8EE] border border-[#C2A980] rounded-sm px-3 py-2 text-center">
            <p class="font-tarzana text-[0.62rem] uppercase tracking-widest text-[#8B7D6B] leading-tight">{{ item.label }}</p>
            <p class="font-mason text-xl font-bold mt-0.5" :class="tonoResumen[item.tono]">{{ item.valor }}</p>
          </div>
        </div>
      </header>

      <div class="grid lg:grid-cols-2 gap-6">
        <section class="bg-[#FDF8EE] border border-[#C2A980] rounded-sm p-6">
          <h2 class="font-mason text-lg font-bold text-[#8B5A2B] border-b border-[#C2A980] pb-2">{{ datos.usuariosSemana.titulo }}</h2>
          <p class="font-minion italic text-xs text-[#8B7D6B] mt-1">{{ datos.usuariosSemana.subtitulo }}</p>
          <div class="flex items-center gap-2 mt-3 font-tarzana text-[11px] text-[#5C5346]">
            <span class="w-3 h-3 bg-[#8B5A2B] inline-block" aria-hidden="true"></span> Cuentas Registradas
          </div>
          <div class="relative h-64 bg-[#F8F2E4] border border-[#D9C4A1] rounded-sm mt-3 px-4 pb-6 pt-3 flex items-end gap-2 sm:gap-3">
            <div class="absolute inset-x-4 top-3 bottom-6 flex flex-col justify-between pointer-events-none" aria-hidden="true">
              <span class="border-t border-dashed border-[#C2A980]/50 w-full"></span>
              <span class="border-t border-dashed border-[#C2A980]/50 w-full"></span>
              <span class="border-t border-dashed border-[#C2A980]/50 w-full"></span>
              <span class="border-t border-dashed border-[#C2A980]/50 w-full"></span>
            </div>
            <div v-for="bar in datos.usuariosSemana.series" :key="bar.label" class="group relative flex-1 flex flex-col items-center justify-end h-full">
              <span
                class="absolute -top-6 font-tarzana text-[10px] font-bold whitespace-nowrap"
                :class="bar.actual ? 'text-[#8B5A2B]' : 'text-[#5C5346] opacity-0 group-hover:opacity-100'"
              >{{ bar.valor }}<span v-if="bar.actual"> ✦</span></span>
              <div
                class="w-full rounded-t-sm transition-all"
                :class="bar.actual ? 'bg-[#D4AF37] ring-2 ring-[#8B5A2B]/40' : 'bg-[#8B5A2B] group-hover:brightness-110'"
                :style="{ height: bar.altura + '%' }"
                :title="`${bar.label}: ${bar.valor}`"
              ></div>
            </div>
          </div>
          <div class="flex flex-wrap justify-between gap-2 mt-3 font-tarzana text-[11px]">
            <span class="text-[#8B7D6B]">{{ datos.usuariosSemana.media }}</span>
            <span class="text-[#6B8E23] font-bold">{{ datos.usuariosSemana.delta }}</span>
          </div>
        </section>

        <section class="bg-[#FDF8EE] border border-[#C2A980] rounded-sm p-6">
          <h2 class="font-mason text-lg font-bold text-[#8B5A2B] border-b border-[#C2A980] pb-2">{{ datos.mesasDia.titulo }}</h2>
          <p class="font-minion italic text-xs text-[#8B7D6B] mt-1">{{ datos.mesasDia.subtitulo }}</p>
          <div class="flex items-center gap-2 mt-3 font-tarzana text-[11px] text-[#5C5346]">
            <span class="w-3 h-3 bg-[#D4AF37] inline-block" aria-hidden="true"></span> Mesas de Campaña
          </div>
          <div class="relative h-64 bg-[#F8F2E4] border border-[#D9C4A1] rounded-sm mt-3 px-4 pb-6 pt-3 flex items-end gap-2 sm:gap-3">
            <div class="absolute inset-x-4 top-3 bottom-6 flex flex-col justify-between pointer-events-none" aria-hidden="true">
              <span class="border-t border-dashed border-[#C2A980]/50 w-full"></span>
              <span class="border-t border-dashed border-[#C2A980]/50 w-full"></span>
              <span class="border-t border-dashed border-[#C2A980]/50 w-full"></span>
              <span class="border-t border-dashed border-[#C2A980]/50 w-full"></span>
            </div>
            <div v-for="bar in datos.mesasDia.series" :key="bar.label" class="group relative flex-1 flex flex-col items-center justify-end h-full">
              <span
                class="absolute -top-6 font-tarzana text-[10px] font-bold whitespace-nowrap"
                :class="bar.pico ? 'text-[#8B5A2B]' : 'text-[#5C5346] opacity-0 group-hover:opacity-100'"
              >{{ bar.valor }}<span v-if="bar.pico"> ✦</span></span>
              <div
                class="w-full rounded-t-sm transition-all"
                :class="bar.pico ? 'bg-[#8B5A2B] ring-2 ring-[#D4AF37]/50' : 'bg-[#D4AF37] group-hover:brightness-110'"
                :style="{ height: bar.altura + '%' }"
                :title="`${bar.label}: ${bar.valor}`"
              ></div>
            </div>
          </div>
          <div class="flex flex-wrap justify-between gap-2 mt-3 font-tarzana text-[11px]">
            <span class="text-[#8B7D6B]">{{ datos.mesasDia.total }}</span>
            <span class="text-[#8B5A2B] font-bold">{{ datos.mesasDia.pico }}</span>
          </div>
        </section>
      </div>

      <section class="bg-[#FDF8EE] border border-[#C2A980] rounded-sm p-6 space-y-5">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
          <div>
            <h2 class="font-mason text-lg font-bold text-[#8B5A2B]">📜 Registro de Logs y Auditoría</h2>
            <p class="font-minion italic text-xs text-[#8B7D6B] mt-0.5">
              Trazabilidad canónica de interacciones, autenticaciones y decretos en el servidor OGL.
            </p>
          </div>
          <div class="flex flex-wrap items-end gap-2">
            <div>
              <label for="log-desde" class="block font-tarzana text-[10px] uppercase tracking-wider text-[#8B7D6B]">Desde:</label>
              <input id="log-desde" v-model="desde" type="text" class="py-1.5 px-2 rounded-sm bg-[#F4EAD6] border border-[#C2A980] font-tarzana text-xs text-[#1A1A1A]" />
            </div>
            <div>
              <label for="log-hasta" class="block font-tarzana text-[10px] uppercase tracking-wider text-[#8B7D6B]">Hasta:</label>
              <input id="log-hasta" v-model="hasta" type="text" class="py-1.5 px-2 rounded-sm bg-[#F4EAD6] border border-[#C2A980] font-tarzana text-xs text-[#1A1A1A]" />
            </div>
            <button type="button" class="min-h-[44px] px-4 py-2 bg-[#D4AF37] text-[#1A1A1A] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:brightness-110 transition" @click="filtrar">
              Filtrar logs →
            </button>
            <button type="button" class="min-h-[44px] px-4 py-2 border border-[#8B5A2B] text-[#8B5A2B] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:bg-[#8B5A2B]/10 transition" @click="exportar">
              Exportar CSV
            </button>
          </div>
        </div>

        <div class="border border-[#C2A980] rounded-sm overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full font-minion text-sm">
              <thead class="bg-[#F4EAD6]">
                <tr class="text-left font-tarzana uppercase tracking-wider text-xs text-[#1A1A1A] border-b border-[#C2A980]">
                  <th scope="col" class="px-4 py-3">Timestamp</th>
                  <th scope="col" class="px-4 py-3">Usuario</th>
                  <th scope="col" class="px-4 py-3">Acción</th>
                  <th scope="col" class="px-4 py-3">Dirección IP</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in datos.logs" :key="log.id" class="border-b border-[#C2A980]/60 last:border-0 align-top">
                  <td class="px-4 py-3 font-tarzana text-xs text-[#5C5346] whitespace-nowrap">{{ log.timestamp }}</td>
                  <td class="px-4 py-3">
                    <div class="flex items-center gap-2">
                      <span
                        class="w-8 h-8 rounded-full border flex items-center justify-center font-tarzana text-[11px] font-bold shrink-0"
                        :class="log.rolSuspendido ? 'bg-[#FDF8EE] border-[#8B1A1A] text-[#8B1A1A]' : 'bg-[#2a241b] border-[#D4AF37] text-[#D4AF37]'"
                      >{{ log.iniciales }}</span>
                      <div class="min-w-0">
                        <p class="font-tarzana font-bold text-[#1A1A1A]">{{ log.usuario }}</p>
                        <p class="font-tarzana text-[10px] uppercase" :class="log.rolSuspendido ? 'text-[#8B1A1A]' : 'text-[#8B5A2B]'">{{ log.rol }}</p>
                      </div>
                    </div>
                  </td>
                  <td class="px-4 py-3 max-w-lg">
                    <p class="text-[#3A2E1F]">{{ log.accion }}</p>
                    <span v-if="log.badge" class="inline-block mt-1 font-tarzana text-[10px] font-bold uppercase px-2 py-0.5 rounded border" :class="tonoBadge[log.badge.tono]">
                      {{ log.badge.texto }}
                    </span>
                  </td>
                  <td class="px-4 py-3 font-tarzana text-xs whitespace-nowrap">
                    <span :class="log.ipAlerta ? 'text-[#8B1A1A] font-bold' : 'text-[#5C5346]'">{{ log.ip }}</span>
                    <span class="block text-[10px] text-[#8B7D6B]">({{ log.origen }})</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="bg-[#F4EAD6] border-t border-[#C2A980] px-4 py-3 flex flex-col sm:flex-row items-center justify-between gap-3">
            <div class="flex items-center gap-3 font-tarzana text-xs text-[#8B7D6B]">
              <span>Mostrando 1 - {{ datos.logs.length }} de 4,892 eventos registrados</span>
              <span class="text-[#8B5A2B] font-semibold">Buffer de auditoría activo</span>
            </div>
            <div class="flex items-center gap-1 font-tarzana text-xs">
              <button type="button" class="min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2 py-1 rounded-sm border border-[#C2A980] text-[#8B7D6B] opacity-50 cursor-not-allowed" disabled>« Anterior</button>
              <button type="button" class="min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2.5 py-1 rounded-sm bg-[#8B5A2B] text-[#FDF8EE] font-bold" @click="toast.info('Ya estás en la primera página del registro de logs.')">1</button>
              <button type="button" class="min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2.5 py-1 rounded-sm border border-[#C2A980] hover:border-[#8B5A2B] text-[#8B5A2B]" @click="toast.info('Página 2 de logs (simulada).')">2</button>
              <button type="button" class="min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2.5 py-1 rounded-sm border border-[#C2A980] hover:border-[#8B5A2B] text-[#8B5A2B]" @click="toast.info('Página 3 de logs (simulada).')">3</button>
              <span class="px-1 text-[#8B7D6B]">…</span>
              <button type="button" class="min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2.5 py-1 rounded-sm border border-[#C2A980] hover:border-[#8B5A2B] text-[#8B5A2B]" @click="toast.info('Última página de logs (simulada).')">816</button>
              <button type="button" class="min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2 py-1 rounded-sm border border-[#C2A980] hover:border-[#8B5A2B] text-[#8B5A2B]" @click="toast.info('Página siguiente de logs (simulada).')">Siguiente »</button>
            </div>
          </div>
        </div>
      </section>

      <div class="bg-[#F8F2E4] border border-[#C2A980] rounded-sm p-4">
        <p class="font-minion text-sm text-[#5C5346]">
          <span class="text-[#8B5A2B] text-lg mr-1" aria-hidden="true">⚖</span>
          <b class="font-mason text-[#8B5A2B]">Protocolo de Registro del Alguacil:</b>
          Todos los eventos de autenticación, moderación de perfiles y creación de mesas son criptográficamente sellados
          conforme a las directrices de juego justo y las cláusulas abiertas de la licencia <b>OGL v1.0a de Paizo Inc</b>.
          Los registros se conservan por 90 ciclos solares.
        </p>
      </div>
    </template>
  </main>
</template>
