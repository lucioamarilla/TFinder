<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { sesionesApi } from '@/api/endpoints'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import Aviso from '@/components/Aviso.vue'

const props = defineProps({
  mesaId: { type: String, required: true },
  sesionId: { type: String, required: true }
})

const { user } = useAuth()
const toast = useToast()

const esGM = computed(() => ['gm', 'director'].includes(user.value?.rol))

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
  <div class="qrv">
    <header class="qrv-cabecera">
      <button
        type="button"
        class="text-link back"
        @click="$router.push(`/mesas/${mesaId}/gestion/sesiones`)"
      >
        ← Volver a sesiones
      </button>
      <span class="tag tag--ink">Sesión · QR de asistencia</span>
    </header>

    <section class="card principal">
      <h1 class="titulo">Pase de Asistencia</h1>
      <p class="label">
        QR single-use validado por el director de juego (TTL de 600 s en Redis).
      </p>

      <Aviso v-if="error" tipo="error" banner>
        {{ error }}
      </Aviso>

      <div v-if="cargando" class="label central">Generando el sello del gremio…</div>

      <template v-else-if="qr">
        <div class="cola">
          <img
            :src="`data:image/png;base64,${qr.png}`"
            alt="QR de asistencia"
            class="imagen"
          />
          <p class="label" role="timer" aria-live="polite">
            <span :class="segundosRestantes > 60 ? 'ok' : 'contra'">
              Vence en {{ segundosRestantes }} s
            </span>
          </p>
          <button
            type="button"
            class="btn btn--secondary btn--sm"
            :disabled="segundosRestantes > 0"
            @click="generar"
          >
            Generar otro QR
          </button>

          <details class="datos">
            <summary class="text-link">Datos del QR (para el GM)</summary>
            <code class="codigo">{{ qr.data }}</code>
          </details>
        </div>
      </template>
    </section>

    <section v-if="esGM" class="card principal">
      <h2 class="sub">Panel del Director de Juego · Validar asistencia</h2>
      <div class="validador">
        <input
          v-model="qrDataPegado"
          type="text"
          placeholder="Pegá el qr_data escaneado del jugador"
          class="input"
          :disabled="validando"
        />
        <button
          type="button"
          class="btn btn--sm"
          :disabled="validando || !qrDataPegado.trim()"
          @click="validar"
        >
          {{ validando ? 'Validando…' : 'Validar asistencia' }}
        </button>
      </div>
      <p v-if="resultado" class="label" :class="usado && resultado !== 'Asistencia registrada' ? 'contra' : 'ok'">
        {{ resultado }}
      </p>
    </section>
  </div>
</template>

<style scoped>
.qrv { max-width: 42rem; margin-inline: auto; padding: 112px var(--gutter) var(--space-lg); display: grid; gap: var(--space-md); }
.qrv-cabecera { display: flex; align-items: center; justify-content: space-between; gap: var(--space-md); margin-bottom: var(--space-2xs); }
.back { font-weight: 700; font-size: var(--text-sm); }
.principal { padding: var(--space-md); display: grid; gap: var(--space-sm); }
.titulo { margin: 0; font-size: var(--text-title); color: var(--color-ink); }
.sub { margin: 0; font-size: var(--text-title); color: var(--color-ink); }
.central { text-align: center; padding-block: var(--space-lg); }
.cola { display: flex; flex-direction: column; align-items: center; gap: var(--space-sm); }
.imagen { width: 14rem; height: 14rem; border: var(--rule-bar) solid var(--color-rule); background: var(--color-qr-paper); padding: var(--space-2xs); }
.datos { width: 100%; margin-top: var(--space-2xs); }
.codigo { display: block; margin-top: var(--space-2xs); padding: var(--space-sm); background: var(--color-ink); color: var(--color-accent-2); font-family: var(--font-outlier); font-size: var(--text-xs); overflow-wrap: anywhere; border-radius: var(--radius-card); }
.ok { color: var(--color-accent-2); font-weight: 700; }
.contra { color: var(--color-error); font-weight: 700; }
.validador { display: flex; flex-direction: column; gap: var(--space-2xs); }
@media (min-width: 40rem) { .validador { flex-direction: row; } .validador .input { flex: 1; } }
@media (max-width: 60rem) { .qrv { padding-top: 120px; } }
</style>
