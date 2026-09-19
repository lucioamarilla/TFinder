<script setup>
import { ref, computed, onMounted } from 'vue'
import { getTrazabilidad } from '@/services/admin.js'
import { useToast } from '@/composables/useToast'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'

const toast = useToast()

const cadenas = ref([])
const traza = ref([])
const cargando = ref(true)
const fallo = ref(null)

const tonoEstado = {
  OK: 'text-[#6B8E23] border-[#6B8E23]/40 bg-[#6B8E23]/10',
  DLQ: 'text-[#8B1A1A] border-[#8B1A1A]/40 bg-[#8B1A1A]/10',
  DEGRADADO: 'text-[#8B5A2B] border-[#8B5A2B]/40 bg-[#8B5A2B]/10'
}

function clasesEstado(estado) {
  return tonoEstado[estado] || 'text-[#8B7D6B] border-[#C2A980] bg-[#C2A980]/10'
}

const matriz = computed(() =>
  cadenas.value.flatMap((cadena) =>
    cadena.requisitos.map((req) => {
      const historias = cadena.historias.filter((h) => (h.requisitos || []).includes(req.id))
      const idsHistorias = historias.map((h) => h.id)
      const casos = cadena.casosUso.filter((cu) => (cu.historias || []).some((h) => idsHistorias.includes(h)))
      return {
        requisito: req,
        historias,
        casos
      }
    })
  )
)

async function cargar() {
  cargando.value = true
  fallo.value = null
  try {
    const data = await getTrazabilidad()
    cadenas.value = data.cadenas
    traza.value = data.traza
  } catch (e) {
    fallo.value = e.message || 'El registro de trazabilidad no respondió.'
  } finally {
    cargando.value = false
  }
}

function verPayload(fila) {
  toast.info(`Payload de ${fila.id} expandido (simulado).`)
}

function reintentar(fila) {
  toast.ok(`Reintentado ${fila.id} en 3 min · cola de mensajes fallidos.`)
}

function exportar() {
  toast.ok('Exportación de trazas (CSV) iniciada.')
}

function auditar() {
  toast.info('Auditoría profunda programada para las 03:00.')
}

onMounted(cargar)
</script>

<template>
  <main class="tfinder-shell">
    <nav class="flex items-center justify-between gap-2 text-[11px] font-tarzana font-semibold tracking-wider uppercase mb-4" aria-label="Migas de pan">
      <div class="flex items-center gap-2 text-[#8B7D6B]">
        <RouterLink to="/admin/plataforma" class="hover:text-[#8B5A2B]">Administración</RouterLink>
        <span>/</span>
        <span class="text-[#D4AF37]">Trazabilidad de Solicitudes</span>
      </div>
      <span class="hidden sm:block text-[10px] text-[#8B7D6B]">Registro inmutable OGL v1.0a</span>
    </nav>

    <header class="mb-6">
      <h1 class="font-mason text-3xl font-bold text-[#8B5A2B] tracking-wide">✦ Trazabilidad de Solicitudes</h1>
      <p class="font-minion italic text-[#5C4633] mt-1">
        Registro inmutable de cada operación del cónclave: quién, cuándo y contra qué servicio.
      </p>
    </header>

    <LoadingState v-if="cargando" message="Reconstruyendo la cadena de trazabilidad…" />

    <ErrorState v-else-if="fallo" title="La traza está incompleta" :message="fallo" @retry="cargar" />

    <template v-else>
      <section
        v-for="cadena in cadenas"
        :key="cadena.id"
        class="card-parchment corner rounded-sm p-5 sm:p-6 mb-5"
      >
        <div class="flex items-center justify-between gap-3 border-b border-[#C2A980] pb-2 mb-4">
          <h2 class="font-mason text-lg font-bold text-[#8B5A2B]">Cadena {{ cadena.id }}</h2>
          <span class="font-tarzana text-[11px] uppercase tracking-wider text-[#8B7D6B]">Problema → Necesidad → Requisito → HU → CU</span>
        </div>

        <div class="grid lg:grid-cols-5 gap-4">
          <div>
            <p class="font-tarzana text-[10px] uppercase tracking-widest text-[#8B7D6B] mb-1">Problema</p>
            <div class="border border-[#8B1A1A]/40 bg-[#8B1A1A]/5 rounded-sm p-3 h-full">
              <p class="font-tarzana text-[11px] font-bold text-[#8B1A1A]">{{ cadena.problema.id }}</p>
              <p class="font-minion text-sm text-[#1A1A1A] font-semibold mt-0.5">{{ cadena.problema.titulo }}</p>
              <p class="font-minion text-xs text-[#5C5346] mt-1">{{ cadena.problema.detalle }}</p>
            </div>
          </div>

          <div>
            <p class="font-tarzana text-[10px] uppercase tracking-widest text-[#8B7D6B] mb-1">Necesidad</p>
            <div class="border border-[#8B5A2B]/40 bg-[#8B5A2B]/5 rounded-sm p-3 h-full">
              <p class="font-tarzana text-[11px] font-bold text-[#8B5A2B]">{{ cadena.necesidad.id }}</p>
              <p class="font-minion text-sm text-[#1A1A1A] font-semibold mt-0.5">{{ cadena.necesidad.titulo }}</p>
              <p class="font-minion text-xs text-[#5C5346] mt-1">{{ cadena.necesidad.detalle }}</p>
            </div>
          </div>

          <div>
            <p class="font-tarzana text-[10px] uppercase tracking-widest text-[#8B7D6B] mb-1">Requisitos</p>
            <ul class="space-y-1.5">
              <li v-for="req in cadena.requisitos" :key="req.id" class="border border-[#C2A980] bg-[#F8F2E4] rounded-sm p-2.5">
                <div class="flex items-center justify-between gap-2">
                  <span class="font-tarzana text-[11px] font-bold text-[#1A1A1A]">{{ req.id }}</span>
                  <span class="font-tarzana text-[10px] font-bold px-1.5 py-0.5 rounded border" :class="clasesEstado(req.estado)">{{ req.estado }}</span>
                </div>
                <p class="font-minion text-xs text-[#3A2E1F] mt-0.5">{{ req.titulo }}</p>
              </li>
            </ul>
          </div>

          <div>
            <p class="font-tarzana text-[10px] uppercase tracking-widest text-[#8B7D6B] mb-1">Historias de Usuario</p>
            <ul class="space-y-1.5">
              <li v-for="hu in cadena.historias" :key="hu.id" class="border border-[#C2A980] bg-[#F8F2E4] rounded-sm p-2.5">
                <div class="flex items-center justify-between gap-2">
                  <span class="font-tarzana text-[11px] font-bold text-[#1A1A1A]">{{ hu.id }}</span>
                  <span class="font-tarzana text-[10px] font-bold px-1.5 py-0.5 rounded border" :class="clasesEstado(hu.estado)">{{ hu.estado }}</span>
                </div>
                <p class="font-minion text-xs text-[#3A2E1F] mt-0.5">{{ hu.titulo }}</p>
              </li>
            </ul>
          </div>

          <div>
            <p class="font-tarzana text-[10px] uppercase tracking-widest text-[#8B7D6B] mb-1">Casos de Uso</p>
            <ul class="space-y-1.5">
              <li v-for="cu in cadena.casosUso" :key="cu.id" class="border border-[#6B8E23]/40 bg-[#6B8E23]/5 rounded-sm p-2.5">
                <div class="flex items-center justify-between gap-2">
                  <span class="font-tarzana text-[11px] font-bold text-[#1A1A1A]">{{ cu.id }}</span>
                  <span class="font-tarzana text-[10px] font-bold px-1.5 py-0.5 rounded border" :class="clasesEstado(cu.estado)">{{ cu.estado }}</span>
                </div>
                <p class="font-minion text-xs text-[#3A2E1F] mt-0.5">{{ cu.titulo }}</p>
              </li>
            </ul>
          </div>
        </div>
      </section>

      <section class="card-parchment rounded-sm p-5 sm:p-6 mb-5">
        <h2 class="font-mason text-lg font-bold text-[#8B5A2B] border-b border-[#C2A980] pb-2 mb-4">Matriz de cobertura</h2>
        <div class="overflow-x-auto">
          <table class="w-full font-minion text-sm">
            <thead class="bg-[#F4EAD6]">
              <tr class="text-left font-tarzana uppercase tracking-wider text-xs text-[#1A1A1A]">
                <th scope="col" class="px-4 py-2.5">Requisito</th>
                <th scope="col" class="px-4 py-2.5">Historias de Usuario</th>
                <th scope="col" class="px-4 py-2.5">Casos de Uso</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="fila in matriz" :key="fila.requisito.id" class="border-b border-[#C2A980]/60 last:border-0 align-top">
                <td class="px-4 py-2.5">
                  <span class="font-tarzana text-xs font-bold text-[#1A1A1A]">{{ fila.requisito.id }}</span>
                  <span class="font-minion text-xs text-[#5C5346] block">{{ fila.requisito.titulo }}</span>
                </td>
                <td class="px-4 py-2.5 font-tarzana text-xs text-[#3A2E1F]">
                  <span v-if="fila.historias.length">{{ fila.historias.map((h) => h.id).join(', ') }}</span>
                  <span v-else class="text-[#8B1A1A]">Sin cobertura</span>
                </td>
                <td class="px-4 py-2.5 font-tarzana text-xs text-[#3A2E1F]">
                  <span v-if="fila.casos.length">{{ fila.casos.map((c) => c.id).join(', ') }}</span>
                  <span v-else class="text-[#8B1A1A]">Sin cobertura</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="card-parchment rounded-sm overflow-hidden mb-5">
        <div class="px-5 pt-5 pb-3">
          <h2 class="font-mason text-lg font-bold text-[#8B5A2B]">Registro de trazas</h2>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full font-minion text-sm">
            <thead class="bg-[#1A1A1A] text-[#D4AF37] font-tarzana uppercase tracking-widest text-xs">
              <tr class="text-left">
                <th scope="col" class="px-4 py-3">Traza</th>
                <th scope="col" class="px-4 py-3">Servicio</th>
                <th scope="col" class="px-4 py-3">Fecha</th>
                <th scope="col" class="px-4 py-3">Estado</th>
                <th scope="col" class="px-4 py-3 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="fila in traza" :key="fila.id" class="border-b border-[#E5D6BC] last:border-0 align-top">
                <td class="px-4 py-3">
                  <p class="font-tarzana font-bold text-[#1A1A1A]">{{ fila.id }}</p>
                  <p class="font-tarzana text-[10px] text-[#8B7D6B]">{{ fila.correlationId }}</p>
                </td>
                <td class="px-4 py-3">
                  <p class="font-tarzana text-xs text-[#3A2E1F]">{{ fila.metodo }} {{ fila.ruta }}</p>
                  <p class="font-tarzana text-[10px] text-[#8B7D6B]">{{ fila.servicio }} · {{ fila.duracionMs }}ms</p>
                </td>
                <td class="px-4 py-3 font-tarzana text-xs text-[#5C5346] whitespace-nowrap">{{ fila.fecha }}</td>
                <td class="px-4 py-3">
                  <span class="font-tarzana text-[11px] font-bold px-2 py-0.5 rounded border" :class="clasesEstado(fila.estado)">{{ fila.estado }}</span>
                </td>
                <td class="px-4 py-3 text-right">
                  <button
                    v-if="fila.estado === 'DLQ'"
                    type="button"
                    class="min-h-[44px] px-3 py-1 font-tarzana text-xs font-bold rounded-sm bg-[#D4AF37] text-[#1A1A1A] hover:brightness-110 transition"
                    @click="reintentar(fila)"
                  >
                    Reintentar
                  </button>
                  <button
                    v-else
                    type="button"
                    class="min-h-[44px] px-3 py-1 font-tarzana text-xs font-bold rounded-sm border border-[#8B7D6B] text-[#8B7D6B] hover:bg-[#8B7D6B]/10 transition"
                    @click="verPayload(fila)"
                  >
                    Ver payload
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <div class="flex flex-wrap gap-2">
        <button type="button" class="min-h-[44px] px-5 py-2.5 bg-[#D4AF37] text-[#1A1A1A] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:brightness-110 transition" @click="exportar">
          Exportar traza
        </button>
        <button type="button" class="min-h-[44px] px-5 py-2.5 border border-[#8B5A2B] text-[#8B5A2B] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:bg-[#8B5A2B]/10 transition" @click="auditar">
          Auditar todo
        </button>
      </div>
    </template>
  </main>
</template>
