<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getResiliencia, guardarResiliencia, simularCaida } from '@/services/admin.js'
import { useToast } from '@/composables/useToast'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'

const toast = useToast()

const ajustes = ref([])
const breakerEstado = ref('CERRADO')
const valores = reactive({})
const cargando = ref(true)
const fallo = ref(null)
const guardando = ref(false)
const simulando = ref(false)

const tonoBadge = {
  verde: 'bg-[#6B8E23]/15 text-[#6B8E23]',
  cobre: 'bg-[#8B5A2B]/15 text-[#8B5A2B]',
  bronce: 'bg-[#8B7D6B]/15 text-[#8B7D6B]',
  rojo: 'bg-[#8B1A1A]/15 text-[#8B1A1A]'
}

const tonoBreaker = {
  CERRADO: 'text-[#6B8E23]',
  ABIERTO: 'text-[#8B1A1A]'
}

function sincronizar(data) {
  ajustes.value = data.ajustes
  breakerEstado.value = data.breakerEstado
  data.ajustes.forEach((a) => {
    valores[a.id] = a.valor
  })
}

async function cargar() {
  cargando.value = true
  fallo.value = null
  try {
    sincronizar(await getResiliencia())
  } catch (e) {
    fallo.value = e.message || 'El configurador de resiliencia no respondió.'
  } finally {
    cargando.value = false
  }
}

async function guardar() {
  guardando.value = true
  try {
    sincronizar(await guardarResiliencia({ ...valores }))
    toast.ok('Configuración de resiliencia aplicada y versionada.')
  } catch (e) {
    toast.error(e.message)
  } finally {
    guardando.value = false
  }
}

async function simular() {
  simulando.value = true
  try {
    sincronizar(await simularCaida())
    toast.error('Simulacro de caída disparado · el breaker pasará a ABIERTO.')
  } catch (e) {
    toast.error(e.message)
  } finally {
    simulando.value = false
  }
}

function restaurar() {
  cargar()
  toast.info('Valores del códice restaurados sin guardar.')
}

onMounted(cargar)
</script>

<template>
  <main class="tfinder-shell">
    <nav class="flex items-center justify-between gap-2 text-[11px] font-tarzana font-semibold tracking-wider uppercase mb-4" aria-label="Migas de pan">
      <div class="flex items-center gap-2 text-[#8B7D6B]">
        <RouterLink to="/admin/plataforma" class="hover:text-[#8B5A2B]">Administración</RouterLink>
        <span>/</span>
        <span class="text-[#D4AF37]">Configurador de Resiliencia</span>
      </div>
      <span class="hidden sm:block text-[10px] text-[#8B7D6B]">Circuit breakers y retries OGL v1.0a</span>
    </nav>

    <header class="mb-6">
      <h1 class="font-mason text-3xl font-bold text-[#8B5A2B] tracking-wide">✦ Configurador de Resiliencia</h1>
      <p class="font-minion italic text-[#5C4633] mt-1">
        Circuit breakers, reintentos y ventanas de tiempo para proteger al cónclave.
      </p>
    </header>

    <LoadingState v-if="cargando" message="Leyendo los sellos de resiliencia…" />

    <ErrorState v-else-if="fallo" title="El configurador no respondió" :message="fallo" @retry="cargar" />

    <template v-else>
      <section class="card-parchment corner rounded-sm p-6 mb-5 space-y-5">
        <div class="flex items-center justify-between gap-2 border-b border-[#C2A980] pb-3">
          <div>
            <p class="font-tarzana font-bold text-[#1A1A1A]">Estado del circuit breaker · mesas-api</p>
            <p class="font-tarzana text-xs text-[#8B7D6B]">El circuito se abre al superar el umbral de fallos consecutivos.</p>
          </div>
          <span class="font-mason text-xl font-bold" :class="tonoBreaker[breakerEstado]">{{ breakerEstado }}</span>
        </div>

        <div v-for="ajuste in ajustes" :key="ajuste.id" class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="min-w-0">
            <label :for="ajuste.id" class="font-tarzana font-bold text-[#1A1A1A] block">{{ ajuste.label }}</label>
            <p class="font-tarzana text-xs text-[#8B7D6B]">{{ ajuste.helper }}</p>
          </div>
          <div class="flex items-center gap-3 shrink-0">
            <div class="flex items-center gap-2">
              <input
                :id="ajuste.id"
                v-model.number="valores[ajuste.id]"
                type="number"
                :min="ajuste.min"
                :max="ajuste.max"
                class="w-24 py-2 px-3 rounded-sm bg-[#F4EAD6] border border-[#C2A980] font-tarzana text-sm text-[#1A1A1A] text-right focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/60"
              />
              <span class="font-tarzana text-xs text-[#8B7D6B] w-20">{{ ajuste.unidad }}</span>
            </div>
            <span class="font-tarzana text-xs px-3 py-1 rounded-sm font-bold" :class="tonoBadge[ajuste.badge.tono]">
              {{ ajuste.badge.texto }}
            </span>
          </div>
        </div>
      </section>

      <div class="flex flex-wrap gap-2">
        <button
          type="button"
          class="min-h-[44px] px-5 py-2.5 bg-[#D4AF37] text-[#1A1A1A] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:brightness-110 transition disabled:opacity-60"
          :disabled="guardando"
          @click="guardar"
        >
          {{ guardando ? 'Guardando…' : 'Guardar configuración' }}
        </button>
        <button
          type="button"
          class="min-h-[44px] px-5 py-2.5 border border-[#8B5A2B] text-[#8B5A2B] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:bg-[#8B5A2B]/10 transition disabled:opacity-60"
          :disabled="simulando"
          @click="simular"
        >
          Simular caída
        </button>
        <button
          type="button"
          class="min-h-[44px] px-5 py-2.5 border border-[#8B7D6B] text-[#8B7D6B] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:bg-[#8B7D6B]/10 transition"
          @click="restaurar"
        >
          Restaurar valores
        </button>
      </div>
    </template>
  </main>
</template>
