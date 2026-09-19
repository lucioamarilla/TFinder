<script setup>
import { ref, onMounted } from 'vue'
import { getDlq, reintentarMensaje, descartarMensaje, drenarCola } from '@/services/admin.js'
import { useToast } from '@/composables/useToast'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'

const toast = useToast()

const mensajes = ref([])
const cargando = ref(true)
const fallo = ref(null)
const enAccion = ref(null)
const abierto = ref(null)

async function cargar() {
  cargando.value = true
  fallo.value = null
  try {
    const data = await getDlq()
    mensajes.value = data.mensajes
  } catch (e) {
    fallo.value = e.message || 'La cola de mensajes fallidos no respondió.'
  } finally {
    cargando.value = false
  }
}

function inspeccionar(mensaje) {
  abierto.value = abierto.value === mensaje.id ? null : mensaje.id
  toast.info('Payload inspeccionado (simulado).')
}

async function reintentar(mensaje) {
  enAccion.value = mensaje.id
  try {
    await reintentarMensaje(mensaje.id)
    mensajes.value = mensajes.value.filter((m) => m.id !== mensaje.id)
    toast.ok('Mensaje reintentado con éxito.')
  } catch (e) {
    toast.error(e.message)
  } finally {
    enAccion.value = null
  }
}

async function descartar(mensaje) {
  enAccion.value = mensaje.id
  try {
    await descartarMensaje(mensaje.id)
    mensajes.value = mensajes.value.filter((m) => m.id !== mensaje.id)
    toast.info('Mensaje descartado de la cola.')
  } catch (e) {
    toast.error(e.message)
  } finally {
    enAccion.value = null
  }
}

async function drenar() {
  if (mensajes.value.length === 0) {
    toast.info('La cola ya está vacía.')
    return
  }
  try {
    await drenarCola()
    mensajes.value = []
    toast.ok('Cola drenada correctamente.')
  } catch (e) {
    toast.error(e.message)
  }
}

function exportar() {
  toast.info('Métricas de la cola exportadas.')
}

onMounted(cargar)
</script>

<template>
  <main class="tfinder-shell">
    <nav class="flex items-center justify-between gap-2 text-[11px] font-tarzana font-semibold tracking-wider uppercase mb-4" aria-label="Migas de pan">
      <div class="flex items-center gap-2 text-[#8B7D6B]">
        <RouterLink to="/admin/plataforma" class="hover:text-[#8B5A2B]">Administración</RouterLink>
        <span>/</span>
        <span class="text-[#D4AF37]">Gestor de DLQ</span>
      </div>
      <span class="hidden sm:block text-[10px] text-[#8B7D6B]">Cola de mensajes fallidos OGL v1.0a</span>
    </nav>

    <header class="mb-6">
      <h1 class="font-mason text-3xl font-bold text-[#8B5A2B] tracking-wide">✦ Cola de Mensajes Fallidos (DLQ)</h1>
      <p class="font-minion italic text-[#5C4633] mt-1">
        Mensajes que no pudieron procesarse. Reintentar, descartar o inspeccionar el payload.
      </p>
    </header>

    <LoadingState v-if="cargando" message="Abriendo la cola de mensajes fallidos…" />

    <ErrorState v-else-if="fallo" title="La cola no pudo abrirse" :message="fallo" @retry="cargar" />

    <template v-else>
      <div class="card-parchment rounded-sm overflow-hidden mb-5">
        <div class="overflow-x-auto">
          <table class="w-full font-tarzana text-sm">
            <thead class="bg-[#1A1A1A] text-[#D4AF37] uppercase tracking-widest text-xs">
              <tr class="text-left">
                <th scope="col" class="px-4 py-3">Mensaje</th>
                <th scope="col" class="px-4 py-3">Cola</th>
                <th scope="col" class="px-4 py-3">Reintentos</th>
                <th scope="col" class="px-4 py-3 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody class="text-[#3A2E1F]">
              <template v-for="mensaje in mensajes" :key="mensaje.id">
                <tr class="border-b border-[#E5D6BC] last:border-0">
                  <td class="px-4 py-3 font-bold text-[#1A1A1A]">{{ mensaje.nombre }}</td>
                  <td class="px-4 py-3 text-[#5C5346]">{{ mensaje.cola }}</td>
                  <td class="px-4 py-3">{{ mensaje.reintentos }}</td>
                  <td class="px-4 py-3">
                    <div class="flex flex-wrap items-center justify-end gap-2">
                      <button
                        type="button"
                        class="min-h-[44px] px-3 py-1 font-tarzana text-xs font-bold rounded-sm bg-[#D4AF37] text-[#1A1A1A] hover:brightness-110 transition disabled:opacity-60"
                        :disabled="enAccion === mensaje.id"
                        @click="reintentar(mensaje)"
                      >
                        Reintentar
                      </button>
                      <button
                        type="button"
                        class="min-h-[44px] px-3 py-1 font-tarzana text-xs rounded-sm border border-[#8B7D6B] text-[#8B7D6B] hover:bg-[#8B7D6B]/10 transition"
                        @click="inspeccionar(mensaje)"
                      >
                        Inspeccionar
                      </button>
                      <button
                        type="button"
                        class="min-h-[44px] px-3 py-1 font-tarzana text-xs rounded-sm border border-[#8B1A1A] text-[#8B1A1A] hover:bg-[#8B1A1A]/10 transition disabled:opacity-60"
                        :disabled="enAccion === mensaje.id"
                        @click="descartar(mensaje)"
                      >
                        Descartar
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="abierto === mensaje.id" class="border-b border-[#E5D6BC] bg-[#F8F2E4]">
                  <td colspan="4" class="px-4 py-3">
                    <p class="font-tarzana text-[10px] uppercase tracking-widest text-[#8B7D6B] mb-1">Payload</p>
                    <pre class="font-mono text-xs text-[#1A1A1A] whitespace-pre-wrap break-all">{{ mensaje.payload }}</pre>
                  </td>
                </tr>
              </template>
              <tr v-if="mensajes.length === 0">
                <td colspan="4" class="px-4 py-10 text-center">
                  <p class="font-mason text-lg text-[#8B5A2B] font-bold">La cola está vacía</p>
                  <p class="font-minion italic text-sm text-[#8B7D6B] mt-1">No quedan mensajes fallidos por procesar.</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="flex flex-wrap gap-2">
        <button type="button" class="min-h-[44px] px-4 py-2 bg-[#D4AF37] text-[#1A1A1A] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:brightness-110 transition" @click="drenar">
          Drenar cola
        </button>
        <button type="button" class="min-h-[44px] px-4 py-2 border border-[#8B5A2B] text-[#8B5A2B] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:bg-[#8B5A2B]/10 transition" @click="exportar">
          Exportar métricas
        </button>
      </div>
    </template>
  </main>
</template>
