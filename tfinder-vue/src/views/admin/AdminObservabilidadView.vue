<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { getCanalesReales, getEventosRecorridos } from '@/services/admin.js'
import { useToast } from '@/composables/useToast'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'

const SEGUIMIENTO_MS = 60000

const router = useRouter()
const toast = useToast()

const canales = ref([])
const eventos = ref([])
const cargando = ref(true)
const fallo = ref(null)
const siguiendo = ref(false)
const cidActivo = ref(null)
let timer = null

const degradados = computed(() => canales.value.filter((c) => c.tono === 'ocre'))
const caidos = computed(() => canales.value.filter((c) => !c.live))

const tonoServicio = {
  verde: 'text-[#6B8E23] border-[#6B8E23]/40',
  ocre: 'text-[#8B5A2B] border-[#8B5A2B]/40',
  gris: 'text-[#8B7D6B] border-[#8B7D6B]/40'
}

const rotuloServicio = {
  verde: 'Operativo',
  ocre: 'Degradado',
  gris: 'Sin datos del operador'
}

const tonoChip = (ok) => (ok ? 'text-[#6B8E23] border-[#6B8E23]/40' : 'text-[#8B1A1A] border-[#8B1A1A]/40')

async function cargarEventos() {
  eventos.value = await getEventosRecorridos(cidActivo.value ? { correlationId: cidActivo.value } : {})
}

async function cargar() {
  cargando.value = true
  fallo.value = null
  try {
    canales.value = await getCanalesReales()
    await cargarEventos()
  } catch (e) {
    fallo.value = e.mensaje || e.message || 'El tablero de observabilidad no respondió.'
  } finally {
    cargando.value = false
  }
}

async function refrescarSilencioso() {
  try {
    canales.value = await getCanalesReales()
    await cargarEventos()
  } catch {
    /* un refresh fallido no debe tapar lo que ya está en pantalla */
  }
}

function alternarSeguimiento() {
  siguiendo.value = !siguiendo.value
  if (siguiendo.value) {
    timer = setInterval(refrescarSilencioso, SEGUIMIENTO_MS)
    toast.ok(`Auto-refresco cada ${SEGUIMIENTO_MS / 1000}s.`)
  } else {
    clearInterval(timer)
    timer = null
    toast.info('Auto-refresco detenido.')
  }
}

async function filtrarPorCid(cid) {
  cidActivo.value = cidActivo.value === cid ? null : cid
  if (cidActivo.value) {
    try {
      eventos.value = await getEventosRecorridos({ correlationId: cidActivo.value })
    } catch (e) {
      toast.error(e.mensaje || e.message)
    }
  } else {
    await cargarEventos()
  }
}

function abrirDashboards() {
  router.push('/admin/prometheus')
}

onMounted(cargar)
onBeforeUnmount(() => clearInterval(timer))
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
        Salud real de los microservicios del cónclave, leída de <code class="font-mono not-italic">/live</code> y <code class="font-mono not-italic">/ready</code> de cada servicio.
      </p>
    </header>

    <LoadingState v-if="cargando" message="Consultando la salud de los servicios…" />

    <ErrorState v-else-if="fallo" title="El tablero está a oscuras" :message="fallo" @retry="cargar" />

    <template v-else>
      <div class="grid md:grid-cols-4 gap-4 mb-5">
        <article v-for="canal in canales" :key="canal.id" class="card-parchment corner rounded-sm p-5">
          <div class="flex items-center justify-between gap-2">
            <h2 class="font-tarzana font-bold text-[#1A1A1A]">{{ canal.nombre }}</h2>
            <span class="font-tarzana text-[11px] font-bold px-2 py-0.5 rounded border" :class="tonoServicio[canal.tono]">
              ● {{ rotuloServicio[canal.tono] }}
            </span>
          </div>
          <p class="font-tarzana text-[10px] uppercase tracking-widest text-[#8B7D6B] mt-2">
            live: {{ canal.live ? 'vivo' : 'sin respuesta' }} · ready: {{ canal.ready }}
          </p>
          <ul v-if="canal.dependencias.length" class="flex flex-wrap gap-1.5 mt-2">
            <li
              v-for="dep in canal.dependencias"
              :key="dep.clave"
              class="font-tarzana text-[10px] px-1.5 py-0.5 rounded border"
              :class="tonoChip(dep.ok)"
            >
              {{ dep.nombre }} {{ dep.ok ? '✓' : '✗' }}
            </li>
          </ul>
          <p v-if="canal.detalle" class="font-mono text-[10px] text-[#8B1A1A] mt-2 break-all">{{ canal.detalle }}</p>
        </article>
      </div>

      <section class="card-parchment rounded-sm p-5 mb-5">
        <h2 class="font-tarzana text-xs uppercase tracking-widest text-[#8B5A2B] mb-2">Estado del conclave</h2>
        <ul class="space-y-1.5 font-minion text-sm text-[#3A2E1F]">
          <li>
            <span class="text-[#8B5A2B] mr-1" aria-hidden="true">✧</span>
            <template v-if="caidos.length">
              Sin datos del operador en {{ caidos.map((c) => c.nombre).join(', ') }}: el servicio no respondió.
            </template>
            <template v-else>Los 4 servicios respondieron <code class="font-mono">/live</code>.</template>
          </li>
          <li v-if="degradados.length">
            <span class="text-[#8B5A2B] mr-1" aria-hidden="true">✧</span>
            Degradados: {{ degradados.map((c) => `${c.nombre} (${c.dependencias.filter((d) => !d.ok).map((d) => d.nombre).join(', ') || 'sin detalle'})`).join('; ') }}.
          </li>
          <li v-if="!degradados.length && !caidos.length">
            <span class="text-[#8B5A2B] mr-1" aria-hidden="true">✧</span>
            Ninguna dependencia caída: postgres, redis y rabbitmq responden en los 4 servicios.
          </li>
        </ul>
      </section>

      <section class="card-parchment rounded-sm overflow-hidden mb-5">
        <div class="px-5 pt-5 pb-3 flex flex-wrap items-center justify-between gap-2">
          <h2 class="font-mason text-lg font-bold text-[#8B5A2B]">event-log con correlation ID</h2>
          <div class="flex items-center gap-2">
            <span v-if="siguiendo" class="font-tarzana text-[10px] uppercase tracking-widest text-[#6B8E23] font-bold">● Auto-refresco 60s</span>
            <button
              v-if="cidActivo"
              type="button"
              class="font-tarzana text-[10px] uppercase tracking-widest px-2 py-1 rounded border border-[#8B5A2B] text-[#8B5A2B] hover:bg-[#8B5A2B]/10"
              @click="filtrarPorCid(cidActivo)"
            >
              Quitar filtro ✕
            </button>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full font-minion text-sm">
            <thead class="bg-[#F4EAD6]">
              <tr class="text-left font-tarzana uppercase tracking-wider text-xs text-[#1A1A1A] border-b border-[#C2A980]">
                <th scope="col" class="px-4 py-3">Ocurrió</th>
                <th scope="col" class="px-4 py-3">Entidad</th>
                <th scope="col" class="px-4 py-3">Acción</th>
                <th scope="col" class="px-4 py-3">Correlation ID</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="evento in eventos" :key="evento.id" class="border-b border-[#C2A980]/60 last:border-0 align-top">
                <td class="px-4 py-3 font-tarzana text-xs text-[#5C5346] whitespace-nowrap">{{ evento.ocurridoEn }}</td>
                <td class="px-4 py-3 font-tarzana text-xs text-[#3A2E1F]">{{ evento.entidad }}</td>
                <td class="px-4 py-3 text-[#3A2E1F]">
                  {{ evento.accion }}
                  <pre v-if="evento.metadata" class="font-mono text-[10px] text-[#8B7D6B] whitespace-pre-wrap break-all mt-1">{{ evento.metadata }}</pre>
                </td>
                <td class="px-4 py-3 font-tarzana text-xs">
                  <button
                    v-if="evento.correlationId"
                    type="button"
                    class="text-[#8B5A2B] hover:underline min-h-[44px] text-left"
                    :class="{ 'font-bold': cidActivo === evento.correlationId }"
                    @click="filtrarPorCid(evento.correlationId)"
                  >
                    {{ evento.correlationId }}
                  </button>
                  <span v-else class="text-[#8B7D6B]">—</span>
                </td>
              </tr>
              <tr v-if="eventos.length === 0">
                <td colspan="4" class="px-4 py-10 text-center">
                  <p class="font-mason text-lg text-[#8B5A2B] font-bold">Sin eventos registrados</p>
                  <p class="font-minion italic text-sm text-[#8B7D6B] mt-1">
                    {{ cidActivo ? 'Ningún recorrido con ese correlation ID.' : 'El event-log está vacío.' }}
                  </p>
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
          @click="alternarSeguimiento"
        >
          {{ siguiendo ? 'Detener seguimiento' : 'Activar seguimiento' }}
        </button>
        <button type="button" class="min-h-[44px] px-5 py-2.5 border border-[#8B5A2B] text-[#8B5A2B] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:bg-[#8B5A2B]/10 transition" @click="abrirDashboards">
          Abrir dashboards
        </button>
      </div>
    </template>
  </main>
</template>
