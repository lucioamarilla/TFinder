<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { sesionesApi } from '@/api/endpoints'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  mesaId: { type: String, required: true },
  sesionId: { type: String, required: true }
})

const { user } = useAuth()
const toast = useToast()

const esGM = computed(() => user.value?.rol === 'gm')

const qr = ref(null)
const segundosRestantes = ref(0)
const cargando = ref(false)
const error = ref(null)

const qrDataPegado = ref('')
const validando = ref(false)
const resultado = ref(null)
const usado = ref(false)

let countdown = null
const MARGEN_S = 5

function iniciarCuentaRegresiva(expiraEnSeg) {
  if (countdown) clearInterval(countdown)
  segundosRestantes.value = expiraEnSeg
  countdown = setInterval(() => {
    segundosRestantes.value = Math.max(0, segundosRestantes.value - 1)
    if (segundosRestantes.value <= 0) clearInterval(countdown)
  }, 1000)
}

async function generar() {
  cargando.value = true
  error.value = null
  resultado.value = null
  try {
    const { datos } = await sesionesApi.qr(Number(props.sesionId))
    qr.value = { png: datos.png_base64, data: datos.qr_data }
    iniciarCuentaRegresiva(datos.expira_en_seg)
  } catch (e) {
    error.value = e?.mensaje ?? 'No se pudo generar el QR de asistencia.'
  } finally {
    cargando.value = false
  }
}

function decodificar(u) {
  try {
    const raw = u
    const pad = raw + '='.repeat((4 - (raw.length % 4)) % 4)
    return JSON.parse(atob(pad))
  } catch {
    return null
  }
}

async function validar() {
  if (!qrDataPegado.value.trim()) return
  validando.value = true
  resultado.value = null
  try {
    const payload = decodificar(qrDataPegado.value.trim())
    const usuarioId = payload?.cuerpo?.u
    if (!usuarioId) {
      resultado.value = 'El qr_data pegado no contiene el identificador de jugador.'
      return
    }
    const { datos } = await sesionesApi.validarQr(Number(props.sesionId), {
      usuario_id: usuarioId,
      qr_data: qrDataPegado.value.trim()
    })
    resultado.value = `${datos.asistencia} · ${new Date().toLocaleTimeString()}`
    usado.value = true
    toast.ok('Asistencia registrada.')
  } catch (e) {
    usado.value = true
    resultado.value = e?.codigo === 409 ? 'QR vencido o ya utilizado (409 single-use)' : e?.mensaje
    toast.error(resultado.value)
  } finally {
    validando.value = false
  }
}

onMounted(generar)
onUnmounted(() => countdown && clearInterval(countdown))
</script>

<template>
  <div class="max-w-2xl mx-auto px-4 py-10">
    <header class="mb-6 flex items-center justify-between">
      <button
        type="button"
        class="font-tarzana text-xs uppercase tracking-wider text-[#8B5A2B] hover:underline"
        @click="$router.push(`/mesas/${mesaId}/sesiones`)"
      >
        ← Volver a sesiones
      </button>
      <span class="px-3 py-1 rounded-full border border-[#D4AF37] text-[#8B5A2B] font-tarzana text-xs font-bold">
        Sesión · QR de asistencia
      </span>
    </header>

    <section class="card-parchment corner p-6 sm:p-8 rounded-sm">
      <h1 class="font-mason text-2xl text-[#8B5A2B] font-bold mb-2">✦ Pase de Asistencia</h1>
      <p class="font-minion italic text-[#5C4633] mb-6">
        QR single-use validado por el director de juego (TTL de 600 s en Redis).
      </p>

      <p v-if="error" class="p-3 rounded-sm border border-[#8B1A1A]/60 bg-[#8B1A1A]/10 text-[#8B1A1A] font-minion text-sm mb-5" role="alert">
        {{ error }}
      </p>

      <div v-if="cargando" class="text-center py-8 font-minion text-[#5C4633]">Generando el sello del gremio…</div>

      <template v-else-if="qr">
        <div class="flex flex-col items-center">
          <img
            :src="`data:image/png;base64,${qr.png}`"
            alt="QR de asistencia"
            class="w-56 h-56 rounded-sm border-2 border-[#C2A980] bg-white p-2"
          />
          <p class="mt-4 font-tarzana text-sm font-bold" role="timer" :aria-live="'polite'">
            <span :class="segundosRestantes > 60 ? 'text-[#6B8E23]' : 'text-[#8B1A1A]'">
              Vence en {{ segundosRestantes }} s
            </span>
          </p>
          <button
            type="button"
            class="mt-4 min-h-[44px] px-4 py-2 border border-[#8B5A2B] text-[#8B5A2B] font-tarzana text-xs font-bold rounded-sm hover:bg-[#8B5A2B]/10 transition disabled:opacity-60"
            :disabled="segundosRestantes > 0"
            @click="generar"
          >
            Generar otro QR
          </button>

          <details class="mt-6 w-full">
            <summary class="cursor-pointer font-tarzana text-xs uppercase tracking-wider text-[#8B5A2B]">
              Datos del QR (para el GM)
            </summary>
            <code class="block mt-2 p-3 rounded-sm bg-[#1A1A1A] text-[#D4AF37] font-mono text-xs break-all">
              {{ qr.data }}
            </code>
          </details>
        </div>
      </template>
    </section>

    <section v-if="esGM" class="card-parchment corner p-6 sm:p-8 rounded-sm mt-6">
      <h2 class="font-mason text-lg text-[#8B5A2B] font-bold mb-3">Panel del Director de Juego · Validar asistencia</h2>
      <div class="flex flex-col sm:flex-row gap-3">
        <input
          v-model="qrDataPegado"
          type="text"
          placeholder="Pegá el qr_data escaneado del jugador"
          class="flex-1 min-h-[44px] px-3 rounded-sm bg-[#F4EAD6] border border-[#C2A980] font-minion text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/60"
          :disabled="validando"
        />
        <button
          type="button"
          class="min-h-[44px] px-5 py-2 bg-[#8B5A2B] text-[#FDF8EE] font-tarzana text-xs font-bold rounded-sm hover:brightness-110 transition disabled:opacity-60"
          :disabled="validando || !qrDataPegado.trim()"
          @click="validar"
        >
          {{ validando ? 'Validando…' : 'Validar asistencia' }}
        </button>
      </div>
      <p v-if="resultado" class="mt-4 font-tarzana text-sm font-bold" :class="usado && resultado !== 'Asistencia registrada' ? 'text-[#8B1A1A]' : 'text-[#6B8E23]'">
        {{ resultado }}
      </p>
    </section>
  </div>
</template>