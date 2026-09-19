<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getComparador } from '@/services/admin.js'
import { useToast } from '@/composables/useToast'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'

const router = useRouter()
const toast = useToast()

const capacidades = ref([])
const ordenMigracion = ref('')
const cargando = ref(true)
const fallo = ref(null)

async function cargar() {
  cargando.value = true
  fallo.value = null
  try {
    const data = await getComparador()
    capacidades.value = data.capacidades
    ordenMigracion.value = data.ordenMigracion
  } catch (e) {
    fallo.value = e.message || 'El comparador no respondió.'
  } finally {
    cargando.value = false
  }
}

function verPlan() {
  toast.info('Ver plan de migración completo (simulado).')
  setTimeout(() => router.push('/admin/prometheus'), 500)
}

function exportar() {
  toast.info('Comparador exportado como informe del cónclave.')
}

onMounted(cargar)
</script>

<template>
  <main class="tfinder-shell">
    <nav class="flex items-center justify-between gap-2 text-[11px] font-tarzana font-semibold tracking-wider uppercase mb-4" aria-label="Migas de pan">
      <div class="flex items-center gap-2 text-[#8B7D6B]">
        <RouterLink to="/admin/plataforma" class="hover:text-[#8B5A2B]">Administración</RouterLink>
        <span>/</span>
        <span class="text-[#D4AF37]">Comparador As-Is / To-Be</span>
      </div>
      <span class="hidden sm:block text-[10px] text-[#8B7D6B]">Gobierno técnico OGL v1.0a</span>
    </nav>

    <header class="mb-6">
      <h1 class="font-mason text-3xl font-bold text-[#8B5A2B] tracking-wide">✦ Comparador As-Is / To-Be</h1>
      <p class="font-minion italic text-[#5C4633] mt-1">
        El monolito del cónclave contra su destino en microservicios: decisión de gobierno técnico.
      </p>
    </header>

    <LoadingState v-if="cargando" message="Comparando el monolito con su destino…" />

    <ErrorState v-else-if="fallo" title="El comparador no pudo abrirse" :message="fallo" @retry="cargar" />

    <template v-else>
      <section class="card-parchment rounded-sm overflow-hidden mb-6">
        <div class="overflow-x-auto">
          <table class="w-full font-tarzana text-sm">
            <thead class="bg-[#1A1A1A] text-[#D4AF37] uppercase tracking-widest text-xs">
              <tr class="text-left">
                <th scope="col" class="px-4 py-3">Capacidad</th>
                <th scope="col" class="px-4 py-3">Estado actual · Monolito</th>
                <th scope="col" class="px-4 py-3">Destino · Microservicios</th>
              </tr>
            </thead>
            <tbody class="text-[#3A2E1F]">
              <tr v-for="fila in capacidades" :key="fila.capacidad" class="border-b border-[#E5D6BC] last:border-0">
                <td class="px-4 py-3 font-bold text-[#1A1A1A]">{{ fila.capacidad }}</td>
                <td class="px-4 py-3">{{ fila.asIs }}</td>
                <td class="px-4 py-3 text-[#6B8E23] font-bold">{{ fila.toBe }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="card-parchment corner rounded-sm p-6 mb-5">
        <h2 class="font-mason text-lg text-[#1A1A1A] font-bold mb-2">Orden de migración recomendada</h2>
        <p class="font-minion text-sm text-[#5C4633]">{{ ordenMigracion }}</p>
      </section>

      <div class="flex flex-wrap gap-2">
        <button type="button" class="min-h-[44px] px-5 py-2.5 bg-[#D4AF37] text-[#1A1A1A] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:brightness-110 transition" @click="verPlan">
          Ver plan de migración
        </button>
        <button type="button" class="min-h-[44px] px-5 py-2.5 border border-[#8B5A2B] text-[#8B5A2B] font-tarzana text-xs font-bold uppercase tracking-wider rounded-sm hover:bg-[#8B5A2B]/10 transition" @click="exportar">
          Exportar informe
        </button>
      </div>
    </template>
  </main>
</template>
