<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getObservabilidad } from '@/services/admin.js'
import { adminApi } from '@/api/endpoints'
import { useToast } from '@/composables/useToast'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'

const router = useRouter()
const toast = useToast()

const servicios = ref([])
const alertas = ref([])
const logs = ref([])
const cargando = ref(true)
const fallo = ref(null)
const siguiendo = ref(false)
const cidFiltro = ref('')

function formatearHora(iso) {
  try {
    return new Date(iso).toLocaleTimeString('es-CO', { hour12: false })
  } catch {
    return '-'
  }
}

function convertirLog(e) {
  return {
    id: e.id,
    timestamp: formatearHora(e.ocurridoEn),
    nivel: 'INFO',
    servicio: 'notif',
    mensaje: `evento ${e.accion} · ${e.entidadTipo ?? ''}`,
    correlationId: e.correlationId || '-'
  }
}

async function traerLogs() {
  try {
    const { datos } = await adminApi.eventLog(cidFiltro.value || undefined)
    logs.value = datos.slice(0, 20).map(convertirLog)
    if (cidFiltro.value) toast.info(`Traza del recorrido ${cidFiltro.value}`)
  } catch {
    logs.value = []
    if (cidFiltro.value) toast.error('notif-api no responde: sin trazas del operador.')
  }
}

async function cargar() {
  cargando.value = true
  fallo.value = null
  try {
    const data = await getObservabilidad()
    servicios.value = data.servicios
    alertas.value = data.alertas
    if (data.logs.length > 0) logs.value = data.logs.slice(0, 20)
  } catch (e) {
    fallo.value = e.message || 'El tablero de observabilidad no respondió.'
  } finally {
    cargando.value = false
  }
}

function seguir(cid) {
  cidFiltro.value = cid === cidFiltro.value ? '' : cid
  traerLogs()
}

function activarSeguimiento() {
  siguiendo.value = true
  toast.ok('Auto-refresco activado (60s).')
}

function abrirDashboards() {
  toast.info('Redirigiendo a Prometheus & Grafana…')
  setTimeout(() => router.push('/admin/prometheus'), 500)
}

onMounted(cargar)
</script>

<template>
  <main class="tfinder-shell">
    <nav class="flex items-center justify-between gap-2 text-[11px] font-tarzana font-semibold tracking-wider uppercase mb-4" aria-label="Migas de pan">
      <div class="flex items-center gap-2 text-[#8B7D6B]">
        <RouterLink to="/admin/plataforma" class="hover:text-[#8B5A2B]">Administración</RouterLink>
        <span>/</span>
        <span class="text-[#D4AF37]">Observabilidad</span>
      </div>
      <span class="hidden sm:block text-[10px] text-[#8B7D6B]">Telemetría OGL v1.0a</span>
    </nav>

    <header class="mb-6">
      <h1 class="font-mason text-3xl font-bold text-[#8B5A2B] tracking-wide">✦ Observabilidad</h1>
      <p class="font-minion italic text-[#5C4633] mt-1">
        Salud real de los microservicios del cónclave: /live y /ready de cada servicio.
      </p>
    </header>

    <LoadingState v-if="cargando" message="Consultando la salud de los servicios…" />

    <ErrorState v-else-if="fallo" title="El tablero está a oscuras" :message="fallo" @retry="cargar" />

    <template v-else>
      <div class="grid md:grid-cols-3 gap-4 mb-5">
        <article v-for="svc in servicios" :key="svc.id" class="card-parchment corner rounded-sm p-5">
          <div class="flex items-center justify-between gap-2">
            <h2 class="font-tarzana font-bold text-[#1A1A1A]">{{ svc.nombre }}</h2>
            <span class="font-tarzana text-[11px] font-bold px-2 py-0.5 rounded border" :class="tonoServicio[svc.tono]">
              ● {{ svc.estado }}
            </span>
          </div>
          <div class="h-2 bg-[#E5D6BC] rounded-full mt-3 overflow-hidden">
            <div class="h-full rounded-full" :class="barraTono[svc.tono]" :style="{ width: svc.salud + '%' }"></div>
          </div>
          <div class="flex flex-wrap justify-between gap-2 font-tarzana text-xs text-[#8B7D6B] mt-2">
            <span>{{ svc.detalle }}</span>
            <span v-if="svc.dependencias" class="text-[#6B8E23]">
              pg:{{ svc.dependencias.postgres ? '✓' : '✗' }} · redis:{{ svc.dependencias.redis ? '✓' : '✗' }} · rq:{{ svc.dependencias.rabbitmq ? '✓' : '✗' }}
            </span>
          </div>
        </article>
      </div>

      <section class="card-parchment rounded-sm p-5 mb-5">
        <h2 class="font-tarzana text-xs uppercase tracking-widest text-[#8B5A2B] mb-2">Últimas alertas</h2>
        <ul class="space-y-1.5">
          <li v-for="(alerta, i) in alertas" :key="i" class="font-minion text-sm text-[#3A2E1F]">
            <span class="text-[#8B5A2B] mr-1" aria-hidden="true">✧</span>{{ alerta }}
          </li>
        </ul>
      </section>

      <section class="card-parchment rounded-sm overflow-hidden mb-5">
        <div class="px-5 pt-5 pb-3 flex items-center justify-between gap-2">
          <h2 class="font-mason text-lg font-bold text-[#8B5A2B]">Logs con correlation ID</h2>
          <span v-if="siguiendo" class="font-tarzana text-[10px] uppercase tracking-widest text-[#6B8E23] font-bold">● Auto-refresco 60s</span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full font-minion text-sm">
            <thead class="bg-[#F4EAD6]">
              <tr class="text-left font-tarzana uppercase tracking-wider text-xs text-[#1A1A1A] border-b border-[#C2A980]">
                <th scope="col" class="px-4 py-3">Hora</th>
                <th scope="col" class="px-4 py-3">Nivel</th>
                <th scope="col" class="px-4 py-3">Servicio</th>
                <th scope="col" class="px-4 py-3">Mensaje</th>
                <th scope="col" class="px-4 py-3">Correlation ID</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in logs" :key="log.id" class="border-b border-[#C2A980]/60 last:border-0 align-top">
                <td class="px-4 py-3 font-tarzana text-xs text-[#5C5346] whitespace-nowrap">{{ log.timestamp }}</td>
                <td class="px-4 py-3 font-tarzana text-xs text-[#6B8E23] font-bold">{{ log.nivel }}</td>
                <td class="px-4 py-3 font-tarzana text-xs text-[#3A2E1F]">{{ log.servicio }}</td>
                <td class="px-4 py-3 text-[#3A2E1F]">{{ log.mensaje }}</td>
                <td class="px-4 py-3 font-tarzana text-xs">
                  <button
                    type="button"
                    class="text-[#8B5A2B] hover:underline min-h-[44px]"
                    :class="{ 'font-bold': cidFiltro === log.correlationId }"
                    @click="seguir(log.correlationId)"
                  >
                    {{ log.correlationId }} {{ cidFiltro === log.correlationId ? '· filtrando' : '' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <div class="flex flex-wrap gap-2">
        <button
          type="button"
          class="min-h-[44px] px-5 py-2.5 bg-[#D4AF37] text-[#1A1A1A] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:brightness-110 transition disabled:opacity-60"
          :disabled="siguiendo"
          @click="activarSeguimiento"
        >
          {{ siguiendo ? 'Seguimiento activo' : 'Activar seguimiento' }}
        </button>
        <button type="button" class="min-h-[44px] px-5 py-2.5 border border-[#8B5A2B] text-[#8B5A2B] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:bg-[#8B5A2B]/10 transition" @click="abrirDashboards">
          Abrir dashboards
        </button>
      </div>
    </template>
  </main>
</template>
