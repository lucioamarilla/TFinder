<script setup>
import { ref, onMounted } from 'vue'
import { getPrometheus, consultarMetrica } from '@/services/admin.js'
import { useToast } from '@/composables/useToast'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'

const toast = useToast()

const consulta = ref('')
const paneles = ref([])
const cargando = ref(true)
const fallo = ref(null)
const consultando = ref(false)

const barraTono = {
  cobre: 'bg-[#8B5A2B]',
  oro: 'bg-[#D4AF37]',
  verde: 'bg-[#6B8E23]'
}

async function cargar() {
  cargando.value = true
  fallo.value = null
  try {
    const data = await getPrometheus()
    consulta.value = data.consulta
    paneles.value = data.paneles
  } catch (e) {
    fallo.value = e.message || 'El visualizador de métricas no respondió.'
  } finally {
    cargando.value = false
  }
}

async function consultar() {
  consultando.value = true
  try {
    const { resultado } = await consultarMetrica(consulta.value)
    toast.ok(resultado)
  } catch (e) {
    toast.error(e.message)
  } finally {
    consultando.value = false
  }
}

function agregar() {
  toast.ok('Panel añadido al dashboard de Observabilidad.')
}

function silenciar() {
  toast.info('Alerta silenciada por 1 hora.')
}

onMounted(cargar)
</script>

<template>
  <main class="tfinder-shell">
    <nav class="flex items-center justify-between gap-2 text-[11px] font-tarzana font-semibold tracking-wider uppercase mb-4" aria-label="Migas de pan">
      <div class="flex items-center gap-2 text-[#8B7D6B]">
        <RouterLink to="/admin/plataforma" class="hover:text-[#8B5A2B]">Administración</RouterLink>
        <span>/</span>
        <span class="text-[#D4AF37]">Prometheus &amp; Grafana</span>
      </div>
      <span class="hidden sm:block text-[10px] text-[#8B7D6B]">Métricas de producción OGL v1.0a</span>
    </nav>

    <header class="mb-6">
      <h1 class="font-mason text-3xl font-bold text-[#8B5A2B] tracking-wide">✦ Prometheus &amp; Grafana</h1>
      <p class="font-minion italic text-[#5C4633] mt-1">
        Métricas en vivo de los servicios del cónclave (datos simulados).
      </p>
    </header>

    <LoadingState v-if="cargando" message="Conectando con el servidor de métricas…" />

    <ErrorState v-else-if="fallo" title="El visualizador está desconectado" :message="fallo" @retry="cargar" />

    <template v-else>
      <section class="card-parchment corner rounded-sm p-6 mb-5">
        <div class="flex flex-wrap gap-2 items-center">
          <label for="promql" class="sr-only">Consulta PromQL</label>
          <input
            id="promql"
            v-model="consulta"
            type="text"
            class="flex-1 min-w-[220px] py-2 px-3 rounded-sm bg-[#12100E] text-[#F4E8D1] border border-[#3A2E1F] font-tarzana text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/60"
          />
          <button
            type="button"
            class="min-h-[44px] px-5 py-2 bg-[#D4AF37] text-[#1A1A1A] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:brightness-110 transition disabled:opacity-60"
            :disabled="consultando"
            @click="consultar"
          >
            {{ consultando ? 'Consultando…' : 'Consultar' }}
          </button>
        </div>
      </section>

      <div class="grid md:grid-cols-3 gap-4 mb-5">
        <article v-for="panel in paneles" :key="panel.id" class="card-parchment rounded-sm p-5">
          <h2 class="font-tarzana text-xs uppercase tracking-widest text-[#8B7D6B] mb-2">{{ panel.titulo }}</h2>
          <div class="flex items-end gap-1 h-20" aria-hidden="true">
            <div
              v-for="(bar, i) in panel.bars"
              :key="i"
              class="w-3 rounded-t-sm"
              :class="barraTono[bar.tono]"
              :style="{ height: bar.altura + 'px' }"
            ></div>
          </div>
          <p class="font-tarzana text-xs text-[#8B7D6B] mt-2">{{ panel.footer }}</p>
        </article>
      </div>

      <div class="flex flex-wrap gap-2">
        <button type="button" class="min-h-[44px] px-5 py-2.5 bg-[#8B5A2B] text-[#FDF8EE] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:brightness-110 transition" @click="agregar">
          Agregar al dashboard
        </button>
        <button type="button" class="min-h-[44px] px-5 py-2.5 border border-[#8B1A1A] text-[#8B1A1A] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:bg-[#8B1A1A]/10 transition" @click="silenciar">
          Silenciar alerta
        </button>
      </div>
    </template>
  </main>
</template>
