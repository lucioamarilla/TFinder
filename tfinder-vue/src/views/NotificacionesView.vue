<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getNotificaciones, marcarLeida, marcarTodasLeidas } from '@/services/notificaciones.js'
import { useNotifications } from '@/composables/useNotifications'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const toast = useToast()
const { unreadCount, loadCount } = useNotifications()

const FILTROS = [
  { id: 'todas', label: 'Todas' },
  { id: 'mesas', label: 'Mesas & Solicitudes' },
  { id: 'social', label: 'Social & Builds' },
  { id: 'sesiones', label: 'Sesiones & Decretos' }
]

const ICONOS = {
  solicitud: '🛡️',
  comentario: '💬',
  convocatoria: '🗳️',
  favorito: '❤️',
  diario: '📖',
  aceptacion: '📜'
}

const filtro = ref('todas')
const lista = ref([])
const cargando = ref(true)
const fallo = ref(null)
const procesando = ref(false)

const filtradas = computed(() =>
  filtro.value === 'todas' ? lista.value : lista.value.filter((n) => n.grupo === filtro.value)
)

function contar(id) {
  return id === 'todas' ? lista.value.length : lista.value.filter((n) => n.grupo === id).length
}

async function cargar() {
  cargando.value = true
  fallo.value = null
  try {
    lista.value = await getNotificaciones()
  } catch (e) {
    fallo.value = e.message || 'No pudimos abrir el centro de avisos.'
  } finally {
    cargando.value = false
  }
}

function reemplazar(actualizada) {
  const i = lista.value.findIndex((n) => n.id === actualizada.id)
  if (i >= 0) lista.value.splice(i, 1, actualizada)
}

async function abrir(notificacion) {
  if (!notificacion.leida) {
    try {
      reemplazar(await marcarLeida(notificacion.id))
      await loadCount()
    } catch (e) {
      toast.error(e.message)
    }
  }
  if (notificacion.enlace) router.push(notificacion.enlace.to)
}

async function marcarTodas() {
  if (unreadCount.value === 0) {
    toast.info('No quedan avisos sin leer.')
    return
  }
  procesando.value = true
  try {
    lista.value = await marcarTodasLeidas()
    await loadCount()
    toast.ok('Todos los avisos del cónclave fueron marcados como leídos.')
  } catch (e) {
    toast.error(e.message)
  } finally {
    procesando.value = false
  }
}

onMounted(cargar)
</script>

<template>
  <main class="flex-grow w-full max-w-4xl mx-auto px-4 py-8">
    <nav class="flex items-center justify-between gap-2 text-[11px] font-tarzana font-semibold tracking-wider uppercase mb-4">
      <div class="flex items-center gap-2 text-[#8B7D6B]">
        <RouterLink to="/dashboard" class="hover:text-[#8B5A2B]">Inicio</RouterLink>
        <span>/</span>
        <span>Centro de Avisos</span>
        <span>/</span>
        <span class="text-[#D4AF37]">Notificaciones del Cónclave</span>
      </div>
      <span class="hidden sm:block text-[10px] text-[#8B7D6B]">Avisos Canónicos Paizo OGL v1.0a</span>
    </nav>

    <header class="mb-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 class="font-mason text-2xl md:text-3xl font-bold text-[#8B5A2B] tracking-wide flex items-center gap-2">
            <span class="text-[#D4AF37]">✦</span> Notificaciones
          </h1>
          <p class="font-minion text-[#6B5B4B] mt-1">
            Avisos de partidas, menciones de pergaminos y decretos del gremio aventurero.
          </p>
        </div>
        <button
          type="button"
          class="self-start sm:self-auto px-4 py-2 border border-[#8B5A2B] text-[#8B5A2B] hover:bg-[#8B5A2B] hover:text-[#FDF8EE] rounded text-xs font-tarzana font-bold transition-all flex items-center gap-1.5 whitespace-nowrap"
          :disabled="procesando"
          @click="marcarTodas"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          {{ procesando ? 'Marcando…' : 'Marcar todas como leídas' }}
        </button>
      </div>

      <div class="flex flex-wrap gap-2 mt-4" role="tablist">
        <button
          v-for="opcion in FILTROS"
          :key="opcion.id"
          type="button"
          role="tab"
          :aria-selected="filtro === opcion.id"
          class="px-3 py-1.5 rounded-full border text-xs font-tarzana font-semibold transition-colors"
          :class="filtro === opcion.id
            ? 'bg-[#EAD9B8] border-[#8B5A2B] text-[#8B5A2B] shadow-sm'
            : 'bg-[#FDF8EE] border-[#C2A980] text-[#8B7D6B] hover:border-[#8B5A2B] hover:text-[#8B5A2B]'"
          @click="filtro = opcion.id"
        >
          {{ opcion.label }} ({{ contar(opcion.id) }})
        </button>
      </div>
    </header>

    <div v-if="cargando" class="space-y-3" role="status" aria-live="polite">
      <div v-for="n in 4" :key="n" class="card-parchment p-4 rounded-sm animate-pulse flex gap-3">
        <div class="w-8 h-8 rounded-full bg-[#C2A980]/40 flex-shrink-0"></div>
        <div class="flex-grow space-y-2">
          <div class="h-3 bg-[#C2A980]/40 rounded w-3/4"></div>
          <div class="h-3 bg-[#C2A980]/25 rounded w-1/2"></div>
        </div>
      </div>
    </div>

    <div v-else-if="fallo" class="parchment-sheet border border-[#C2A980] rounded-sm py-16 text-center" role="alert">
      <p class="font-tarzana uppercase tracking-widest text-xs text-[#8B1A1A] font-bold mb-1">El centro de avisos está cerrado</p>
      <p class="font-minion text-[#5A4A3A]">{{ fallo }}</p>
      <button type="button" class="btn-gold mt-4 px-6 py-2 font-tarzana font-bold uppercase tracking-wider text-sm" @click="cargar">Reintentar</button>
    </div>

    <div v-else-if="filtradas.length === 0" class="parchment-sheet border border-[#C2A980] rounded-sm py-16 text-center">
      <p class="font-mason text-xl text-[#8B5A2B] font-bold">No hay avisos en este filtro</p>
      <p class="font-minion text-sm text-[#6B5B4B] italic mt-1">Cuando el cónclave tenga noticias, aparecerán aquí.</p>
    </div>

    <ul v-else class="space-y-3">
      <li
        v-for="notificacion in filtradas"
        :key="notificacion.id"
        class="rounded-sm border border-[#E5D7C0] transition-colors"
        :class="notificacion.leida
          ? 'bg-[#F4EAD6]/80 opacity-90'
          : 'bg-[#FDF8EE] border-l-4 border-l-[#D4AF37]'"
      >
        <div class="flex items-start gap-3 p-4">
          <span class="w-8 h-8 rounded-full bg-[#EFE3CF] border border-[#C2A980] flex items-center justify-center text-base flex-shrink-0">
            {{ ICONOS[notificacion.icono] || '✦' }}
          </span>
          <div class="flex-grow min-w-0">
            <p class="font-minion text-[15px] text-[#332517] leading-relaxed">
              <b v-if="notificacion.autor">{{ notificacion.autor }}</b>
              {{ notificacion.mensaje }}
              <i v-if="notificacion.entidad" class="font-semibold text-[#8B5A2B]">{{ notificacion.entidad }}</i>
              <template v-if="notificacion.detalle">{{ notificacion.detalle }}</template>
            </p>
            <button
              v-if="notificacion.enlace"
              type="button"
              class="font-tarzana text-xs font-bold text-[#8B5A2B] hover:underline mt-1.5 inline-flex items-center gap-1"
              @click="abrir(notificacion)"
            >
              {{ notificacion.enlace.label }} →
            </button>
          </div>
          <div class="flex flex-col items-end gap-2 flex-shrink-0">
            <span class="font-tarzana text-[10px] text-[#8B7D6B] whitespace-nowrap">{{ notificacion.fecha }}</span>
            <span
              v-if="!notificacion.leida"
              class="w-2 h-2 rounded-full bg-[#D4AF37] ring-2 ring-[#D4AF37]/30"
              aria-label="Sin leer"
            ></span>
            <span v-else class="w-2 h-2" aria-hidden="true"></span>
          </div>
        </div>
      </li>
    </ul>

    <div v-if="!cargando && !fallo" class="mt-6 pt-4 border-t border-[#C2A980] flex flex-col sm:flex-row items-center justify-between gap-3 font-tarzana text-xs text-[#8B7D6B]">
      <span>Mostrando {{ filtradas.length }} avisos de los últimos 30 días de viaje</span>
      <button
        type="button"
        class="px-4 py-2 border border-[#C2A980] hover:border-[#8B5A2B] hover:text-[#8B5A2B] rounded transition-colors font-semibold"
        @click="toast.info('No hay pergaminos más antiguos en el archivo.')"
      >
        ❖ Cargar Notificaciones Anteriores
      </button>
    </div>
  </main>
</template>
