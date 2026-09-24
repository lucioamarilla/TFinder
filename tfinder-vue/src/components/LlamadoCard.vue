<script setup>
import { computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useLlamado } from '@/composables/useLlamado'
import { useSolicitud } from '@/composables/useSolicitud'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  mesa: { type: Object, required: true }
})

const { user } = useAuth()
const toast = useToast()
const abstraccion = useSolicitud(props.mesa.id)
const llamado = useLlamado(props.mesa.id)

const esGM = computed(() => user.value?.rol === 'gm')
const anotarseEstado = computed(() => abstraccion.estado.value)

function botonAnotar() {
  const email = user.value?.email ?? 'aventurero@tfinder.dev'
  abstraccion
    .unirse(email)
    .then((estadoFinal) => {
      if (estadoFinal === 'solicitada') {
        toast.ok('¡Vacante reservada! Solicitud enviada al director de juego.')
      } else if (estadoFinal === 'agotada') {
        toast.error('Cupo agotado — alguien se anotó primero.')
      } else {
        toast.error(abstraccion.mensaje.value)
      }
    })
    .catch((e) => toast.error(e?.mensaje ?? 'No pudimos anotarte al llamado.'))
}

async function abrir() {
  try {
    await llamado.abrir()
    toast.ok('Llamado abierto durante 120 segundos.')
  } catch (e) {
    toast.error(e?.mensaje ?? 'No se pudo abrir el llamado.')
  }
}

function pildora() {
  if (llamado.estado.value === 'abierto') return 'Llamado abierto'
  if (llamado.estado.value === 'error') return 'Estado desconocido'
  return 'Cerrado (expiró)'
}

function chipClase() {
  if (llamado.estado.value === 'abierto') return 'bg-[#6B8E23] text-[#FDF8EE]'
  if (llamado.estado.value === 'error') return 'bg-[#8B1A1A] text-[#FDF8EE]'
  return 'bg-[#8B7D6B]/30 text-[#5C4633]'
}
</script>

<template>
  <article class="card-parchment corner rounded-sm p-5 flex flex-col">
    <div class="flex items-center justify-between gap-3 mb-3">
      <div>
        <h3 class="font-mason font-bold text-[#1A1A1A]">{{ mesa.nombre }}</h3>
        <span class="font-tarzana text-xs text-[#8B7D6B]">{{ mesa.sistema }} · Nivel {{ mesa.nivel }}</span>
      </div>
      <span
        class="px-3 py-1 rounded-full font-tarzana text-xs font-bold tracking-wide"
        :class="chipClase()"
      >
        {{ pildora() }}
      </span>
    </div>

    <div class="font-minion text-sm text-[#5C4633] mb-4 flex-grow">
      <p>{{ mesa.descripcion || 'Crónica activa de la comunidad.' }}</p>
      <p class="mt-2 text-[#8B5A2B]">
        {{ mesa.jugadores }}/{{ mesa.plazas }} ocupadas
        <template v-if="mesa.vacante"> · ¡ÚLTIMA VACANTE!</template>
      </p>
      <p
        v-if="llamado.estado === 'abierto'"
        class="mt-2 font-tarzana uppercase tracking-wider text-xs text-[#6B8E23]"
        role="timer"
        :aria-live="'polite'"
      >
        estado: abierto · {{ llamado.ttl }} s
      </p>
    </div>

    <div class="flex gap-2">
      <button
        v-if="esGM"
        type="button"
        class="flex-1 min-h-[44px] py-2 bg-[#D4AF37] text-[#1A1A1A] font-tarzana text-xs font-bold rounded-sm hover:brightness-110 transition disabled:opacity-60"
        :disabled="llamado.estado === 'abierto'"
        @click="abrir"
      >
        {{ llamado.estado === 'abierto' ? 'Llamado activo' : 'Abrir llamado' }}
      </button>
      <button
        type="button"
        class="flex-1 min-h-[44px] py-2 bg-[#8B5A2B] text-[#FDF8EE] font-tarzana text-xs font-bold rounded-sm hover:brightness-110 transition disabled:opacity-60"
        :disabled="
          abstraccion.estado === 'enviando' ||
          abstraccion.estado === 'solicitada' ||
          !mesa.vacante ||
          llamado.estado !== 'abierto'
        "
        @click="botonAnotar"
      >
        <template v-if="abstraccion.estado === 'enviando'">Anotando…</template>
        <template v-else-if="abstraccion.estado === 'solicitada'">✔ Solicitud enviada</template>
        <template v-else>Anotarse al llamado</template>
      </button>
    </div>
  </article>
</template>