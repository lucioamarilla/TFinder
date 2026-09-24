<script setup>
import { ref, onMounted } from 'vue'
import { matchmakingApi } from '@/api/endpoints'
import { useToast } from '@/composables/useToast'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'
import EmptyState from '@/components/EmptyState.vue'

const toast = useToast()

const ROLES = ['Jugador', 'Director de Juego', 'Indistinto']
const MODALIDADES = ['Presencial', 'En línea (VTT)', 'Híbrida']
const DISPONIBILIDADES = ['Fines de semana', 'Entre semana', 'Flexible']

const filtros = ref({
  rol: 'Jugador',
  modalidad: 'Presencial',
  disponibilidad: 'Fines de semana'
})

const candidatos = ref([])
const cargando = ref(true)
const fallo = ref(null)
const aplicando = ref(false)
const enviando = ref(null)
const anotado = ref(false)

async function cargar(filtrosActivos) {
  cargando.value = true
  fallo.value = null
  try {
    candidatos.value = await getCandidatos(filtrosActivos)
  } catch (e) {
    fallo.value = e.message || 'El registro del gremio no respondió.'
  } finally {
    cargando.value = false
  }
}

async function aplicarFiltros() {
  aplicando.value = true
  try {
    await cargar({ ...filtros.value })
    toast.ok('Filtros de matchmaking aplicados.')
  } catch (e) {
    toast.error(e.message)
  } finally {
    aplicando.value = false
  }
}

async function llamadoAbierto() {
  try {
    await anotarseEnLlamadoAbierto()
    anotado.value = true
    toast.info('Te has anotado en la lista de espera de mesas.')
  } catch (e) {
    toast.error(e.message)
  }
}

async function solicitar(candidato) {
  enviando.value = candidato.id
  try {
    await enviarSolicitud(candidato.id)
    toast.ok(candidato.toast)
  } catch (e) {
    toast.error(e.message)
  } finally {
    enviando.value = null
  }
}

onMounted(() => cargar(null))
</script>

<template>
  <main class="tfinder-shell">
    <section class="card-parchment corner p-6 sm:p-8 rounded-sm mb-6">
      <h1 class="font-mason text-3xl text-[#8B5A2B] font-bold mb-1">✦ Matchmaking de Mesa</h1>
      <p class="font-minion italic text-[#5C4633] mb-5">
        Encontrá a tus próximos compañeros de aventura según estilo de juego, disponibilidad y tono de crónica.
      </p>

      <div class="grid sm:grid-cols-3 gap-4">
        <div>
          <label for="mm-rol" class="block font-tarzana text-xs uppercase tracking-wider text-[#8B5A2B] mb-1">Rol buscado</label>
          <select
            id="mm-rol"
            v-model="filtros.rol"
            class="w-full py-2 px-3 rounded-sm bg-[#F4EAD6] border border-[#C2A980] font-minion text-sm text-[#1A1A1A] focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/60"
          >
            <option v-for="opcion in ROLES" :key="opcion" :value="opcion">{{ opcion }}</option>
          </select>
        </div>
        <div>
          <label for="mm-modalidad" class="block font-tarzana text-xs uppercase tracking-wider text-[#8B5A2B] mb-1">Modalidad</label>
          <select
            id="mm-modalidad"
            v-model="filtros.modalidad"
            class="w-full py-2 px-3 rounded-sm bg-[#F4EAD6] border border-[#C2A980] font-minion text-sm text-[#1A1A1A] focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/60"
          >
            <option v-for="opcion in MODALIDADES" :key="opcion" :value="opcion">{{ opcion }}</option>
          </select>
        </div>
        <div>
          <label for="mm-disponibilidad" class="block font-tarzana text-xs uppercase tracking-wider text-[#8B5A2B] mb-1">Disponibilidad</label>
          <select
            id="mm-disponibilidad"
            v-model="filtros.disponibilidad"
            class="w-full py-2 px-3 rounded-sm bg-[#F4EAD6] border border-[#C2A980] font-minion text-sm text-[#1A1A1A] focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/60"
          >
            <option v-for="opcion in DISPONIBILIDADES" :key="opcion" :value="opcion">{{ opcion }}</option>
          </select>
        </div>
      </div>

      <div class="mt-4 flex flex-wrap gap-2">
        <button
          type="button"
          class="min-h-[44px] px-4 py-2 bg-[#D4AF37] text-[#1A1A1A] font-tarzana text-xs font-bold rounded-sm hover:brightness-110 transition focus:outline-none focus:ring-2 focus:ring-[#8B5A2B]/50 disabled:opacity-60"
          :disabled="aplicando"
          @click="aplicarFiltros"
        >
          {{ aplicando ? 'Aplicando…' : 'Aplicar filtros' }}
        </button>
        <button
          type="button"
          class="min-h-[44px] px-4 py-2 border border-[#8B5A2B] text-[#8B5A2B] font-tarzana text-xs font-bold rounded-sm hover:bg-[#8B5A2B]/10 transition focus:outline-none focus:ring-2 focus:ring-[#8B5A2B]/40"
          :disabled="anotado"
          @click="llamadoAbierto"
        >
          {{ anotado ? '✔ Anotado' : 'Llamado abierto' }}
        </button>
      </div>
    </section>

    <h2 class="font-mason text-xl text-[#8B5A2B] font-bold mb-4">Aventureros afines a tu perfil</h2>

    <LoadingState v-if="cargando" message="Consultando el registro de aventureros…" />

    <ErrorState
      v-else-if="fallo"
      title="El registro del gremio está en silencio"
      :message="fallo"
      @retry="cargar(null)"
    />

    <EmptyState
      v-else-if="candidatos.length === 0"
      title="Ningún aventurero coincide con esos filtros"
      message="Probá ampliar la disponibilidad o el rol buscado para convocar a más compañeros."
    >
      <button
        type="button"
        class="btn-copper-outline px-5 py-2 font-tarzana font-bold uppercase tracking-wider text-xs rounded-sm"
        @click="cargar(null)"
      >
        Ver todos los aventureros
      </button>
    </EmptyState>

    <div v-else class="grid md:grid-cols-3 gap-4">
      <article v-for="candidato in candidatos" :key="candidato.id" class="card-parchment corner rounded-sm p-5 flex flex-col">
        <div class="flex items-center gap-3 mb-3">
          <span class="w-11 h-11 rounded-full bg-[#C2A980] border border-[#D4AF37] flex items-center justify-center font-mason font-bold text-[#1A1A1A]">
            {{ candidato.iniciales }}
          </span>
          <div>
            <h3 class="font-mason font-bold text-[#1A1A1A]">{{ candidato.nombre }}</h3>
            <span class="font-tarzana text-xs text-[#8B7D6B]">{{ candidato.meta }}</span>
          </div>
        </div>
        <p class="font-minion text-sm text-[#5C4633] mb-4 flex-grow">{{ candidato.bio }}</p>
        <button
          type="button"
          class="w-full min-h-[44px] py-2 bg-[#8B5A2B] text-[#FDF8EE] font-tarzana text-xs font-bold rounded-sm hover:brightness-110 transition focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 disabled:opacity-60"
          :disabled="enviando === candidato.id"
          @click="solicitar(candidato)"
        >
          {{ enviando === candidato.id ? 'Enviando…' : 'Enviar solicitud' }}
        </button>
      </article>
    </div>
  </main>
</template>
