<script setup>
import { ref, onMounted } from 'vue'
import { getMesas, ultimaMedicion } from '@/services/mesas'
import { useAuth } from '@/composables/useAuth'
import LlamadoCard from '@/components/LlamadoCard.vue'
import { useToast } from '@/composables/useToast'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'
import EmptyState from '@/components/EmptyState.vue'

const toast = useToast()
const { user } = useAuth()

const esGM = () => user.value?.rol === 'gm'

const mesas = ref([])
const cargando = ref(true)
const fallo = ref(null)
const refrescando = ref(false)
const cacheMs = ref(0)

async function cargar() {
  cargando.value = true
  fallo.value = null
  try {
    mesas.value = (await getMesas()).filter((m) => m.vacante)
    cacheMs.value = ultimaMedicion()
  } catch (e) {
    fallo.value = e?.mensaje ?? 'El catálogo real de mesas no respondió.'
  } finally {
    cargando.value = false
  }
}

async function refrescar() {
  refrescando.value = true
  try {
    await cargar()
    toast.ok(`Catálogo refrescado (caché ~${cacheMs.value} ms).`)
  } finally {
    refrescando.value = false
  }
}

onMounted(cargar)
</script>

<template>
  <main class="tfinder-shell">
    <section class="card-parchment corner p-6 sm:p-8 rounded-sm mb-6">
      <div class="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 class="font-mason text-3xl text-[#8B5A2B] font-bold mb-1">✦ Matchmaking de Mesa</h1>
          <p class="font-minion italic text-[#5C4633]">
            El GM abre un llamado con TTL real de Redis; los jugadores se anotan a la carrera por la última vacante.
          </p>
        </div>
        <span
          class="px-3 py-1 rounded-full border border-[#D4AF37] text-[#8B5A2B] font-tarzana text-xs font-bold"
        >
          caché ~{{ cacheMs }} ms
        </span>
      </div>

      <div class="mt-5 flex flex-wrap items-center gap-3">
        <button
          v-if="esGM()"
          type="button"
          class="min-h-[44px] px-4 py-2 bg-[#D4AF37] text-[#1A1A1A] font-tarzana text-xs font-bold rounded-sm hover:brightness-110 transition"
          @click="refrescar"
        >
          {{ refrescando ? 'Sincronizando…' : 'Refrescar catálogo' }}
        </button>
      </div>
    </section>

    <h2 class="font-mason text-xl text-[#8B5A2B] font-bold mb-4">Mesas con vacante abierta al llamado</h2>

    <LoadingState v-if="cargando" message="Consultando mesas reales…" />

    <ErrorState
      v-else-if="fallo"
      title="El catálogo está en silencio"
      :message="fallo"
      @retry="cargar"
    />

    <EmptyState
      v-else-if="mesas.length === 0"
      title="No hay mesas con vacantes"
      message="El cónclave no registró mesas disponibles todavía."
    />

    <div v-else class="grid md:grid-cols-2 gap-4">
      <LlamadoCard v-for="mesa in mesas" :key="mesa.id" :mesa="mesa" />
    </div>
  </main>
</template>