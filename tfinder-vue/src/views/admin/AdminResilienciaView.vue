<script setup>
import { ref, computed, onMounted } from 'vue'
import { getResiliencia } from '@/services/admin.js'
import { useToast } from '@/composables/useToast'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'

const toast = useToast()

const ajustes = ref([])
const estado = ref({ breakerEstado: 'ABIERTO', alcanzable: false, ready: 'sin_datos', dependencias: [], dlqEnCola: 0, detalle: null })
const cargando = ref(true)
const fallo = ref(null)
const verificando = ref(false)

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

const caidas = computed(() => estado.value.dependencias.filter((d) => !d.ok))

function sincronizar(data) {
  estado.value = data
  ajustes.value = data.ajustes
}

async function cargar() {
  cargando.value = true
  fallo.value = null
  try {
    sincronizar(await getResiliencia())
  } catch (e) {
    fallo.value = e.mensaje || e.message || 'El configurador de resiliencia no respondió.'
  } finally {
    cargando.value = false
  }
}

async function verificar() {
  verificando.value = true
  try {
    sincronizar(await getResiliencia())
    if (!estado.value.alcanzable) toast.error('Sin datos del operador: mesas-api no respondió.')
    else if (caidas.value.length) toast.error(`${caidas.value.map((d) => d.nombre).join(', ')} caído(s): breaker abierto.`)
    else toast.ok('mesas-api operativo: breaker cerrado y dependencias en pie.')
  } catch (e) {
    toast.error(e.mensaje || e.message)
  } finally {
    verificando.value = false
  }
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
        Estado real de las dependencias y sellos de referencia del códice. Los parámetros se leen, no se guardan.
      </p>
    </header>

    <LoadingState v-if="cargando" message="Leyendo los sellos de resiliencia…" />

    <ErrorState v-else-if="fallo" title="El configurador no respondió" :message="fallo" @retry="cargar" />

    <template v-else>
      <section class="card-parchment corner rounded-sm p-6 mb-5 space-y-5">
        <div class="flex items-center justify-between gap-2 border-b border-[#C2A980] pb-3">
          <div>
            <p class="font-tarzana font-bold text-[#1A1A1A]">Estado del circuit breaker · {{ estado.servicio ?? 'mesas-api' }}</p>
            <p class="font-tarzana text-xs text-[#8B7D6B]">
              Derivado de <code class="font-mono">/ready</code>: CERRADO si todo está listo, ABIERTO si hay una dependencia caída.
            </p>
          </div>
          <span class="font-mason text-xl font-bold" :class="tonoBreaker[estado.breakerEstado]">{{ estado.breakerEstado }}</span>
        </div>

        <dl class="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div class="bg-[#F4EAD6] rounded-sm px-3 py-2">
            <dt class="font-tarzana text-[10px] uppercase tracking-widest text-[#8B7D6B]">Operador</dt>
            <dd class="font-tarzana text-sm text-[#1A1A1A]">{{ estado.alcanzable ? 'responde' : 'sin datos' }}</dd>
          </div>
          <div class="bg-[#F4EAD6] rounded-sm px-3 py-2">
            <dt class="font-tarzana text-[10px] uppercase tracking-widest text-[#8B7D6B]">ready</dt>
            <dd class="font-tarzana text-sm text-[#1A1A1A]">{{ estado.ready }}</dd>
          </div>
          <div class="bg-[#F4EAD6] rounded-sm px-3 py-2">
            <dt class="font-tarzana text-[10px] uppercase tracking-widest text-[#8B7D6B]">Mensajes en DLQ</dt>
            <dd class="font-tarzana text-sm text-[#1A1A1A]">{{ estado.dlqEnCola }}</dd>
          </div>
          <div class="bg-[#F4EAD6] rounded-sm px-3 py-2">
            <dt class="font-tarzana text-[10px] uppercase tracking-widest text-[#8B7D6B]">Dependencias caídas</dt>
            <dd class="font-tarzana text-sm text-[#1A1A1A]">{{ caidas.length ? caidas.map((d) => d.nombre).join(', ') : 'ninguna' }}</dd>
          </div>
        </dl>

        <p v-if="estado.detalle" class="font-mono text-xs text-[#8B1A1A] break-all">{{ estado.detalle }}</p>

        <div v-for="ajuste in ajustes" :key="ajuste.id" class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="min-w-0">
            <label :for="ajuste.id" class="font-tarzana font-bold text-[#1A1A1A] block">{{ ajuste.label }}</label>
            <p class="font-tarzana text-xs text-[#8B7D6B]">{{ ajuste.helper }}</p>
          </div>
          <div class="flex items-center gap-3 shrink-0">
            <div class="flex items-center gap-2">
              <input
                :id="ajuste.id"
                :value="ajuste.valor"
                type="number"
                :min="ajuste.min"
                :max="ajuste.max"
                readonly
                aria-readonly="true"
                class="w-24 py-2 px-3 rounded-sm bg-[#F4EAD6] border border-[#C2A980] font-tarzana text-sm text-[#5C5346] text-right cursor-not-allowed"
              />
              <span class="font-tarzana text-xs text-[#8B7D6B] w-20">{{ ajuste.unidad }}</span>
            </div>
            <span class="font-tarzana text-xs px-3 py-1 rounded-sm font-bold" :class="tonoBadge[ajuste.badge.tono]">
              {{ ajuste.badge.texto }}
            </span>
          </div>
        </div>
      </section>

      <p class="card-parchment rounded-sm p-4 mb-5 font-minion italic text-sm text-[#5C4633]">
        Los valores anteriores son parámetros de referencia del códice (OGL v1.0a) y se muestran en solo lectura:
        el backend todavía no expone un endpoint que permita guardarlos.
      </p>

      <div class="flex flex-wrap gap-2">
        <button
          type="button"
          class="min-h-[44px] px-5 py-2.5 bg-[#D4AF37] text-[#1A1A1A] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:brightness-110 transition disabled:opacity-60"
          :disabled="verificando"
          @click="verificar"
        >
          {{ verificando ? 'Verificando…' : 'Verificar broker' }}
        </button>
        <RouterLink
          to="/admin/dlq"
          class="min-h-[44px] inline-flex items-center px-5 py-2.5 border border-[#8B5A2B] text-[#8B5A2B] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:bg-[#8B5A2B]/10 transition"
        >
          Abrir DLQ
        </RouterLink>
      </div>
    </template>
  </main>
</template>
