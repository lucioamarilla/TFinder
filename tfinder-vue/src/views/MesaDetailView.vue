<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getMesa } from '@/services/mesas'
import { useAuth } from '@/composables/useAuth'
import { useSolicitud } from '@/composables/useSolicitud'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const router = useRouter()
const { isAuthenticated, user } = useAuth()
const toast = useToast()

const mesa = ref(null)
const isLoading = ref(true)
const error = ref(null)
const tabActiva = ref('resumen')

const mesaId = computed(() => Number(route.params.id))
const solicitud = useSolicitud(mesaId.value)

const requisitosLista = computed(() =>
  (mesa.value?.requisitos ?? '').split('·').map((r) => r.trim()).filter(Boolean)
)

const vacantes = computed(() =>
  mesa.value ? Math.max(mesa.value.plazas - mesa.value.jugadores, 0) : 0
)

const hayVacantes = computed(() => Boolean(mesa.value?.vacante) && vacantes.value > 0)

const ultimaVacante = computed(() =>
  Boolean(mesa.value) && mesa.value.jugadores === mesa.value.plazas - 1 && mesa.value.plazas > 1
)

const etiquetaBotón = computed(() => ({
  inactivo: 'Quiero unirme',
  enviando: 'Enviando solicitud…',
  solicitada: 'Solicitud enviada',
  agotada: 'Sin vacantes',
  error: 'Reintentar'
}[solicitud.estado.value]))

async function cargar() {
  isLoading.value = true
  error.value = null
  try {
    mesa.value = await getMesa(route.params.id)
    tabActiva.value = 'resumen'
  } catch (err) {
    mesa.value = null
    error.value = err instanceof Error ? err.message : 'No pudimos cargar los detalles de la mesa.'
  } finally {
    isLoading.value = false
  }
}

async function unirse() {
  if (!mesa.value) return
  if (!isAuthenticated.value || !user.value) {
    router.push({ path: '/login', query: { redirect: route.fullPath } })
    return
  }
  if (solicitud.estado.value === 'enviando' || solicitud.estado.value === 'solicitada') return
  if (!hayVacantes.value && solicitud.estado.value !== 'error') {
    toast.info('La crónica no tiene vacantes disponibles por ahora.')
    return
  }
  await solicitud.unirse(user.value.email)
  if (solicitud.estado.value === 'solicitada') {
    toast.ok(`Solicitud enviada a "${mesa.value.nombre}".`)
  } else if (solicitud.estado.value === 'agotada') {
    toast.error(solicitud.mensaje.value)
  } else if (solicitud.estado.value === 'error') {
    toast.error(solicitud.mensaje.value)
  }
}

watch(() => route.params.id, () => {
  solicitud.estado.value = 'inactivo'
  solicitud.mensaje.value = ''
  cargar()
})
onMounted(cargar)
</script>

<template>
  <div>
    <div class="max-w-7xl w-full mx-auto px-6 pt-5 pb-2">
      <RouterLink
        class="inline-flex items-center gap-2 text-sm font-stat tracking-wider uppercase text-[#8B5A2B] hover:text-[#8B1A1A] transition-colors font-bold"
        :to="'/mesas'"
      >
        <span class="text-xs">◀</span> Volver al listado de mesas
      </RouterLink>
    </div>

    <div v-if="isLoading" class="max-w-7xl w-full mx-auto px-6 py-10" role="status" aria-live="polite">
      <div class="vellum-panel rounded-sm border border-[#C2A980] overflow-hidden shadow-2xl animate-pulse">
        <div class="bg-[#FDF8EE] border-b-2 border-[#8B5A2B] p-6 lg:px-8">
          <div class="w-2/3 h-8 bg-[#C2A980]/40 rounded mb-3"></div>
          <div class="w-1/3 h-4 bg-[#C2A980]/25 rounded"></div>
        </div>
        <div class="p-6 lg:p-8 space-y-4">
          <div class="w-full h-24 bg-[#E8DCC8]/50 rounded"></div>
          <div class="w-full h-32 bg-[#E8DCC8]/40 rounded"></div>
        </div>
      </div>
    </div>

    <div v-else-if="error" class="max-w-3xl mx-auto px-6 py-16">
      <div class="card-parchment p-10 text-center rounded-[2px]" role="alert">
        <div class="text-4xl mb-3 select-none" aria-hidden="true">🗝️</div>
        <h1 class="font-mason font-bold text-2xl text-[#8B5A2B]">Crónica no hallada</h1>
        <p class="font-narrative text-[#5A4A3A] mt-2">{{ error }}</p>
        <div class="flex items-center justify-center gap-3 mt-5">
          <button type="button" class="btn-gold px-6 py-2.5 font-stat font-bold uppercase tracking-wider text-sm rounded-[2px]" @click="cargar">
            ↻ Reintentar
          </button>
          <RouterLink class="btn-copper-outline inline-block px-6 py-2.5 font-stat font-bold uppercase tracking-wider text-sm rounded-[2px]" to="/mesas">
            ← Volver a explorar mesas
          </RouterLink>
        </div>
      </div>
    </div>

    <main v-else-if="mesa" class="max-w-7xl w-full mx-auto px-6 pb-12 flex-1 flex flex-col">
      <div class="vellum-panel rounded-sm border border-[#C2A980] overflow-hidden flex flex-col flex-1 shadow-2xl">
        <!-- CABECERA -->
        <div class="bg-[#FDF8EE] border-b-2 border-[#8B5A2B] p-6 lg:px-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div class="flex flex-col gap-2">
            <div class="flex items-center flex-wrap gap-3">
              <h1 class="font-mason text-3xl lg:text-[34px] leading-tight text-[#8B5A2B] tracking-wide font-bold">
                {{ mesa.nombre }}
              </h1>
              <div class="flex items-center gap-2">
                <span class="font-tarzana text-[0.8rem] font-bold bg-[#1A1A1A] text-[#FDF8EE] px-2.5 py-0.5 rounded tracking-wider uppercase">
                  {{ mesa.sistema }}
                </span>
                <span
                  class="font-tarzana text-[0.8rem] font-bold px-2.5 py-0.5 rounded tracking-wider uppercase flex items-center gap-1.5 shadow-sm"
                  :class="mesa.estado === 'Abierta' ? 'bg-[#6B8E23] text-[#FDF8EE]' : 'bg-[#8B1A1A] text-[#FDF8EE]'"
                >
                  <span class="w-1.5 h-1.5 rounded-full bg-[#FDF8EE] animate-pulse"></span>
                  {{ mesa.estadoCategoria }}
                </span>
              </div>
            </div>
            <div class="text-sm font-minion text-[#5C3A1A] italic flex items-center flex-wrap gap-2">
              <span>{{ mesa.tono }}</span>
              <span class="text-[#8B5A2B]">♦</span>
              <span>{{ mesa.frecuencia }}</span>
            </div>
          </div>

          <div class="flex items-center flex-col gap-2">
            <div
              v-if="solicitud.estado.value === 'agotada'"
              class="font-tarzana text-[0.8rem] font-bold px-3 py-1.5 rounded uppercase tracking-wider bg-[#8B1A1A]/10 text-[#8B1A1A] border border-[#8B1A1A]/50 max-w-[220px] text-center"
              role="alert"
            >
              {{ solicitud.mensaje.value }}
            </div>
            <button
              type="button"
              :disabled="isLoading || solicitud.estado.value === 'enviando' || solicitud.estado.value === 'solicitada'"
              :aria-busy="solicitud.estado.value === 'enviando'"
              :title="isAuthenticated ? 'Solicitar plaza en esta crónica' : 'Debes registrarte o iniciar sesión para solicitar plaza en esta crónica'"
              class="font-tarzana text-[0.9rem] font-semibold px-5 py-2.5 rounded-sm uppercase tracking-wider shadow-inner flex items-center gap-2 transition-colors"
              :class="isAuthenticated
                ? (solicitud.estado.value === 'agotada' ? 'text-[#8B7D6B] bg-[#E8DCC8] border border-[#8B7D6B] cursor-not-allowed' : (hayVacantes ? 'btn-gold text-[#1A1A1A]' : 'text-[#8B7D6B] bg-[#E8DCC8] border border-[#8B7D6B] cursor-not-allowed'))
                : 'text-[#8B7D6B] bg-[#E8DCC8] border border-[#8B7D6B] cursor-pointer hover:text-[#8B5A2B] hover:bg-[#E5D5BC]'"
              @click="unirse"
            >
              <svg v-if="!isAuthenticated" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354c-1.813 1.25-3.5 2-4.5 2S5.313 6.354 4.5 6.604V18c.813-.25 2-.604 3.5-.854 1.5-.25 2.5.062 3.5.854m0-9v9m0-9c-1.313-.75-3-1.5-4.5-1.5S5.313 5.104 4.5 5.354V17c.813-.25 2-.604 3.5-.854 1.5-.25 2.5.062 3.5.854"/>
              </svg>
              {{ isAuthenticated ? etiquetaBotón : 'Inicia sesión para unirte' }}
            </button>
          </div>
        </div>

        <!-- CUERPO DOS COLUMNAS -->
        <div class="flex-1 flex flex-col lg:flex-row">
          <!-- Izquierda 70% -->
          <div class="lg:w-[70%] p-6 lg:p-8 flex flex-col gap-6">
            <div class="border-b border-[#C2A980] flex gap-1" role="tablist" aria-label="Secciones de la mesa">
              <button
                type="button"
                role="tab"
                :aria-selected="tabActiva === 'resumen'"
                class="tab-item font-mason text-[1rem] font-semibold px-6 py-2.5 rounded-t-sm tracking-wide flex items-center gap-2"
                :class="tabActiva === 'resumen' ? 'active' : ''"
                @click="tabActiva = 'resumen'"
              >
                Resumen de la Crónica
              </button>
              <button
                type="button"
                role="tab"
                :aria-selected="tabActiva === 'miembros'"
                class="tab-item font-mason text-[1rem] font-semibold px-6 py-2.5 rounded-t-sm tracking-wide flex items-center gap-2"
                :class="tabActiva === 'miembros' ? 'active' : ''"
                @click="tabActiva = 'miembros'"
              >
                Miembros de la Partida
                <span class="font-tarzana text-xs bg-[#8B5A2B]/15 px-2 py-0.5 rounded-full text-[#8B5A2B] font-bold">{{ mesa.jugadores }}/{{ mesa.plazas }}</span>
              </button>
            </div>

            <div v-show="tabActiva === 'resumen'" class="space-y-6">
              <!-- Ficha técnica / stat block -->
              <div class="border border-[#8B5A2B]/40 bg-[#F4EAD6]/70 p-4 rounded-sm shadow-sm">
                <div class="flex items-center justify-between pb-2 border-b border-[#8B1A1A] gap-3">
                  <span class="font-tarzana font-bold text-xs uppercase tracking-widest text-[#8B1A1A]">
                    PARÁMETROS DE RECLUTAMIENTO Y SISTEMA
                  </span>
                  <span class="font-mason text-xs text-[#8B5A2B] text-right">{{ mesa.proximaSesion }}</span>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 pt-3 font-tarzana text-[0.9rem] text-[#1A1A1A]">
                  <div class="flex flex-col">
                    <span class="stat-label text-xs">Game Master</span>
                    <span class="font-minion italic text-[1.05rem] font-semibold">{{ mesa.gm }}</span>
                  </div>
                  <div class="flex flex-col">
                    <span class="stat-label text-xs">Tono de Campaña</span>
                    <span class="font-tarzana font-medium text-[0.95rem]">{{ mesa.tono }}</span>
                  </div>
                  <div class="flex flex-col">
                    <span class="stat-label text-xs">Horario de Juego</span>
                    <span class="font-tarzana font-medium text-[0.95rem]">{{ mesa.frecuencia }}</span>
                  </div>
                  <div class="flex flex-col">
                    <span class="stat-label text-xs">Nivel Inicial</span>
                    <span class="font-mason font-bold text-[1.1rem] text-[#8B5A2B]">{{ mesa.rangoNivel }}</span>
                  </div>
                </div>

                <div class="mt-3 pt-3 border-t border-[#C2A980]/70 grid grid-cols-2 md:grid-cols-4 gap-4 font-tarzana text-[0.85rem] text-[#5C3A1A]">
                  <div><span class="font-bold text-[#8B5A2B]">Plataforma VTT:</span> {{ mesa.modalidad }} · {{ mesa.ubicacion }}</div>
                  <div><span class="font-bold text-[#8B5A2B]">Reglas adicionales:</span> {{ mesa.etiquetas.slice(0, 2).join(' · ') }}</div>
                  <div><span class="font-bold text-[#8B5A2B]">Vacantes restantes:</span> {{ vacantes }} de {{ mesa.plazas }} puestos</div>
                  <div><span class="font-bold text-[#8B5A2B]">Frecuencia:</span> {{ mesa.frecuencia }}</div>
                </div>
              </div>

              <div class="space-y-4">
                <div class="flex items-center gap-3">
                  <h2 class="font-mason text-xl font-bold text-[#8B5A2B] tracking-wide">Sinopsis del Grimorio</h2>
                  <div class="flex-1 garnet-divider"></div>
                </div>
                <p class="font-minion text-[1rem] leading-[1.6] text-[#1A1A1A]">{{ mesa.descripcion }}</p>
                <p class="font-minion text-[1rem] leading-[1.6] text-[#1A1A1A]">{{ mesa.lore }}</p>

                <div class="p-4 bg-[#E8DCC8]/60 border-l-4 border-[#8B1A1A] rounded-r-sm italic font-minion text-[#1A1A1A] leading-relaxed text-[0.98rem]">
                  "El cronista de esta mesa recomienda lectura previa del trasfondo y una ficha coherente con el tono de la crónica antes de la sesión cero."
                  <div class="text-right not-italic font-tarzana text-xs text-[#8B5A2B] font-bold mt-1.5 uppercase tracking-wider">— {{ mesa.gm }}</div>
                </div>

                <h3 class="font-mason text-lg font-bold text-[#8B5A2B] pt-2">Pautas para la Creación de Héroes</h3>
                <ul class="font-minion text-[1rem] leading-[1.6] text-[#1A1A1A] space-y-2 list-none pl-1">
                  <li v-for="(r, i) in requisitosLista" :key="i" class="flex items-start gap-2">
                    <span class="text-[#8B1A1A] font-bold mt-0.5">♦</span>
                    <span>{{ r }}</span>
                  </li>
                </ul>
              </div>
            </div>

            <div v-show="tabActiva === 'miembros'" class="pt-2 border-t border-[#C2A980]">
              <div class="flex items-center justify-between mb-4">
                <div class="flex items-center gap-3">
                  <h3 class="font-mason text-lg font-bold text-[#8B5A2B] tracking-wide">Expedicionarios Confirmados</h3>
                  <span class="font-tarzana text-xs uppercase tracking-wider bg-[#8B5A2B]/10 text-[#8B5A2B] px-2 py-0.5 font-bold rounded">
                    {{ mesa.jugadores }} de {{ mesa.plazas }} Plazas
                  </span>
                </div>
                <span class="font-tarzana text-xs text-[#8B7D6B]">{{ vacantes }} {{ vacantes === 1 ? 'vacante disponible' : 'vacantes disponibles' }}</span>
              </div>

              <div class="px-6 py-8 text-center bg-[#F4EAD6]/50 rounded-sm border border-[#C2A980]/80">
                <div class="w-12 h-12 rounded-full bg-[#8B5A2B]/15 border border-[#8B5A2B]/40 flex items-center justify-center text-[#8B5A2B] mx-auto mb-3">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                </div>
                <p class="font-narrative text-[#5A4A3A]">
                  El detalle del grupo de expedicionarios está disponible para quienes integran la mesa.
                  {{ isAuthenticated ? 'Solicitá tu plaza para formar parte de la crónica.' : 'Iniciá sesión para solicitar tu plaza.' }}
                </p>
              </div>
            </div>
          </div>

          <!-- Derecha 30% -->
          <aside class="lg:w-[30%] vellum-sidebar border-t lg:border-t-0 lg:border-l border-[#B8A68B] p-6 lg:p-6 flex flex-col gap-5">
            <span class="font-tarzana font-bold text-sm uppercase tracking-widest text-[#5C3A1A] border-b border-[#C2A980] pb-2">
              Ficha Rápida de la Mesa
            </span>

            <div>
              <span class="stat-label text-xs block mb-1">Progreso de Ocupación</span>
              <div class="flex items-end justify-between font-stat text-sm font-bold text-[#8B5A2B]">
                <span>{{ mesa.jugadores }} / {{ mesa.plazas }} jugadores</span>
                <span>{{ vacantes }} vacante{{ vacantes === 1 ? '' : 's' }}</span>
              </div>
              <div class="mt-1.5 h-2.5 bg-[#C2A980]/40 border border-[#C2A980] rounded overflow-hidden">
                <div class="h-full bg-gradient-to-r from-[#B8860B] to-[#D4AF37]" :style="{ width: `${Math.round((mesa.jugadores / mesa.plazas) * 100)}%` }"></div>
              </div>
              <div
                v-if="ultimaVacante"
                class="mt-2 font-tarzana text-[0.75rem] font-bold uppercase tracking-wider px-2 py-1 rounded border bg-[#8B1A1A]/10 text-[#8B1A1A] border-[#8B1A1A]/50"
                role="alert"
              >
                ⚠ Última vacante — 1 puesto en disputa
              </div>
            </div>

            <dl class="space-y-3 font-tarzana text-[0.9rem] text-[#1A1A1A]">
              <div>
                <dt class="stat-label text-xs">Sistema</dt>
                <dd class="mt-0.5"><span class="bg-[#1A1A1A] text-[#FDF8EE] font-bold text-xs px-2 py-0.5 rounded tracking-wider uppercase">{{ mesa.sistema }}</span></dd>
              </div>
              <div>
                <dt class="stat-label text-xs">Modalidad</dt>
                <dd class="mt-0.5 font-semibold">{{ mesa.modalidad }}</dd>
              </div>
              <div>
                <dt class="stat-label text-xs">Ubicación / VTT</dt>
                <dd class="mt-0.5">{{ mesa.ubicacion }}</dd>
              </div>
              <div>
                <dt class="stat-label text-xs">Rango de Nivel</dt>
                <dd class="mt-0.5">{{ mesa.rangoNivel }}</dd>
              </div>
              <div>
                <dt class="stat-label text-xs">Próxima Sesión</dt>
                <dd class="mt-0.5 font-semibold text-[#8B5A2B]">{{ mesa.proximaSesion }}</dd>
              </div>
            </dl>

            <div>
              <span class="stat-label text-xs block mb-2">Etiquetas</span>
              <div class="flex flex-wrap gap-1.5">
                <span v-for="et in mesa.etiquetas" :key="et" class="px-2 py-0.5 rounded bg-[#8B5A2B]/10 border border-[#8B5A2B]/30 font-stat text-xs font-bold text-[#5C3A1A]">
                  {{ et }}
                </span>
              </div>
            </div>

            <div class="mt-auto border-t border-[#C2A980] pt-4">
              <p class="font-narrative italic text-sm text-[#5C3A1A] leading-relaxed">
                "{{ mesa.lore }}" — <span class="not-italic font-semibold">{{ mesa.gm }}</span>
              </p>
            </div>
          </aside>
        </div>
      </div>
    </main>
  </div>
</template>