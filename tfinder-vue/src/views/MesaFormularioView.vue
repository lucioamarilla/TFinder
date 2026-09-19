<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMesa, crearMesa, actualizarMesa } from '@/services/mesas'
import { useToast } from '@/composables/useToast'
import ModalDatePicker from '@/components/modals/ModalDatePicker.vue'

const props = defineProps({
  id: { type: String, default: null }
})

const router = useRouter()
const toast = useToast()

const esEdicion = computed(() => Boolean(props.id))

const nombre = ref('')
const descripcion = ref('')
const tono = ref('')
const frecuencia = ref('')
const nivelInicial = ref(1)
const jugadoresMax = ref(6)
const estado = ref('Abierta')
const proximaSesion = ref('')

const isLoading = ref(Boolean(props.id))
const error = ref(null)
const errorForm = ref('')
const fechaAbierta = ref(false)

function proximosSabados(n = 4) {
  const hoy = new Date()
  const sabado = new Date(hoy)
  sabado.setDate(hoy.getDate() + ((6 - hoy.getDay() + 7) % 7))
  const res = []
  for (let i = 0; i < n; i++) {
    const f = new Date(sabado)
    f.setDate(sabado.getDate() + i * 7)
    const diaMes = f.toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
    res.push({ value: f.toISOString().slice(0, 10), label: `Sábado ${diaMes}`, detalle: '18:00 - 22:00 (GMT+1)' })
  }
  return res
}

function aplicarFecha(iso) {
  if (!iso) return
  const f = new Date(`${iso}T00:00:00`)
  const diaMes = f.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' })
  proximaSesion.value = `${diaMes.charAt(0).toUpperCase()}${diaMes.slice(1)} · 18:00 · Sesión inaugural`
  fechaAbierta.value = false
}

async function load() {
  if (!props.id) return
  isLoading.value = true
  error.value = null
  try {
    const mesa = await getMesa(props.id)
    nombre.value = mesa.nombre
    descripcion.value = mesa.descripcion
    tono.value = mesa.tono
    frecuencia.value = mesa.frecuencia
    const match = /(\d+)/.exec(mesa.rangoNivel ?? mesa.nivel ?? '')
    nivelInicial.value = match ? Number(match[1]) : 1
    jugadoresMax.value = Number(mesa.plazas ?? 6)
    estado.value = mesa.estado === 'Cerrada' ? 'Cerrada' : 'Abierta'
    proximaSesion.value = typeof mesa.proximaSesion === 'string' ? mesa.proximaSesion : (mesa.proximaSesion?.label ?? '')
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Ocurrió un error inesperado.'
  } finally {
    isLoading.value = false
  }
}

async function enviar() {
  errorForm.value = ''
  if (!nombre.value.trim()) {
    errorForm.value = 'El nombre de la mesa es obligatorio para convocar a los aventureros.'
    return
  }

  try {
    if (esEdicion.value) {
      await actualizarMesa(props.id, {
        nombre: nombre.value.trim(),
        descripcion: descripcion.value,
        tono: tono.value,
        frecuencia: frecuencia.value,
        nivel: String(nivelInicial.value),
        rangoNivel: `Nivel ${nivelInicial.value}`,
        plazas: Number(jugadoresMax.value),
        estado: estado.value,
        proximaSesion: proximaSesion.value
      })
      toast.ok('Campaña actualizada · cambios registrados en el grimorio.')
      router.push(`/mesas/${props.id}/gestion`)
    } else {
      await crearMesa({
        nombre: nombre.value.trim(),
        sistema: 'PF1e',
        estado: estado.value,
        estadoCategoria: estado.value === 'Abierta' ? 'En Reclutamiento' : 'Privada',
        tono: tono.value,
        rangoNivel: `Nivel ${nivelInicial.value}`,
        nivel: String(nivelInicial.value),
        frecuencia: frecuencia.value,
        modalidad: 'Online',
        ubicacion: 'Discord · VTT',
        descripcion: descripcion.value,
        lore: descripcion.value,
        plazas: Number(jugadoresMax.value),
        vacante: true,
        destacada: false,
        proximaSesion: proximaSesion.value
      })
      toast.ok('Campaña guardada · la taberna espera por sus héroes.')
      router.push('/mis-mesas')
    }
  } catch (err) {
    toast.error(err instanceof Error ? err.message : 'No se pudo guardar la campaña.')
  }
}

function cancelar() {
  router.push('/mis-mesas')
}

onMounted(load)
</script>

<template>
  <main class="flex-grow flex items-center justify-center py-10 px-4">
    <div class="w-full max-w-[800px] bg-[#FDF8EE] border border-[#B8A68B] rounded-sm shadow-xl p-10 relative">
      <div class="absolute top-2 left-2 w-6 h-6 border-l-2 border-t-2 border-[#D4AF37]" aria-hidden="true"></div>
      <div class="absolute top-2 right-2 w-6 h-6 border-r-2 border-t-2 border-[#D4AF37]" aria-hidden="true"></div>
      <div class="absolute bottom-2 left-2 w-6 h-6 border-l-2 border-b-2 border-[#D4AF37]" aria-hidden="true"></div>
      <div class="absolute bottom-2 right-2 w-6 h-6 border-r-2 border-b-2 border-[#D4AF37]" aria-hidden="true"></div>

      <div class="mb-4">
        <div class="flex items-center justify-between border-b border-[#C2A980]/60 pb-3 mb-2">
          <div class="flex items-center space-x-2 text-xs font-tarzana tracking-wider uppercase text-[#8B7D6B]">
            <RouterLink to="/mis-mesas" class="hover:text-[#8B5A2B] transition">Mis Mesas</RouterLink>
            <span>/</span>
            <span class="text-[#8B5A2B] font-bold">{{ esEdicion ? 'Editar Campaña' : 'Nueva Campaña' }}</span>
          </div>
          <RouterLink to="/mis-mesas" class="inline-flex items-center text-xs font-tarzana uppercase tracking-wider text-[#8B5A2B] hover:text-[#5C3A1B] transition font-semibold">
            <span class="mr-1.5">←</span> Volver a Mis Campañas
          </RouterLink>
        </div>
      </div>

      <div v-if="isLoading" class="py-16 flex flex-col items-center gap-4" role="status" aria-live="polite">
        <div class="animate-pulse space-y-3 w-full max-w-md">
          <div class="h-4 bg-[#C2A980]/40 rounded w-2/3"></div>
          <div class="h-2.5 bg-[#C2A980]/25 rounded w-full"></div>
          <div class="h-2.5 bg-[#C2A980]/25 rounded w-1/2"></div>
        </div>
        <p class="font-tarzana text-xs uppercase tracking-widest text-[#8B7D6B]">Cargando el rollo de campaña...</p>
      </div>

      <div v-else-if="error" class="py-16 text-center" role="alert">
        <p class="font-tarzana uppercase tracking-widest text-xs text-[#8B1A1A] font-bold mb-1">Error al cargar la campaña</p>
        <p class="font-minion text-[#5A4A3A]">{{ error }}</p>
        <button type="button" class="btn-gold mt-4 px-6 py-2 font-tarzana font-bold uppercase tracking-wider text-sm" @click="load">Reintentar</button>
      </div>

      <template v-else>
        <div class="text-center mb-8">
          <div class="text-[#8B5A2B] text-xs font-tarzana uppercase tracking-widest mb-1 flex items-center justify-center gap-1.5">
            <span>❖</span> GESTIÓN DE CRÓNICA &amp; MESA DE JUEGO <span>❖</span>
          </div>
          <h1 class="text-[1.8rem] leading-tight font-mason font-bold text-[#8B5A2B] tracking-wide">
            {{ esEdicion ? 'Editar Campaña' : 'Nueva Campaña' }}
          </h1>
          <div class="mt-2 max-w-sm mx-auto text-[#8B7D6B] text-[10px] select-none">◆ ✦ ◆</div>
          <p class="text-sm font-minion italic text-[#555] mt-1.5">
            Define los estatutos y parámetros para convocar a los aventureros en Golarion
          </p>
        </div>

        <form class="space-y-6" novalidate @submit.prevent="enviar">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-5">
            <div class="flex flex-col">
              <label class="text-[0.9rem] font-minion font-medium text-[#1A1A1A] mb-1 flex items-center justify-between">
                <span>Nombre de la Mesa <span class="text-[#8B1A1A] font-bold">*</span></span>
                <span class="text-[11px] font-tarzana text-[#8B7D6B]">Requerido</span>
              </label>
              <input
                v-model="nombre"
                type="text"
                placeholder="Ej: La Corona de Carroña - Cap. II"
                class="h-[40px] px-3 bg-transparent border-0 border-b border-[#8B7D6B] text-[#1A1A1A] font-minion text-base placeholder-[#8B7D6B]/70 focus:outline-none focus:border-[#D4AF37] focus:ring-0 transition-colors"
              />
            </div>

            <div class="flex flex-col">
              <label class="text-[0.9rem] font-minion font-medium text-[#1A1A1A] mb-1 flex items-center justify-between">
                <span>Sistema de Reglas</span>
                <span class="text-[11px] font-tarzana text-[#8B7D6B]">Fijo por plataforma</span>
              </label>
              <div class="relative">
                <select disabled class="h-[40px] w-full px-3 bg-[#E8DCC8] border border-[#C2A980]/80 rounded-sm text-[#8B7D6B] font-minion text-base cursor-not-allowed appearance-none select-none opacity-90 shadow-inner font-semibold">
                  <option selected>PF1e (Pathfinder 1ª Edición OGL v1.0a)</option>
                </select>
                <div class="absolute inset-y-0 right-3 flex items-center pointer-events-none text-[#8B7D6B]">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                    <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"></path>
                  </svg>
                </div>
              </div>
            </div>

            <div class="flex flex-col md:col-span-2">
              <label class="text-[0.9rem] font-minion font-medium text-[#1A1A1A] mb-1 flex items-center justify-between">
                <span>Descripción y Sinopsis de la Crónica</span>
                <span class="text-[11px] font-tarzana text-[#8B7D6B]">Visible para aspirantes</span>
              </label>
              <textarea
                v-model="descripcion"
                rows="4"
                placeholder="Escribe la sinopsis del Adventure Path o tu campaña personalizada, advertencias de contenido y ambientación..."
                class="min-h-[120px] p-3 bg-[#FAF4E8]/80 border border-[#8B7D6B] rounded-sm text-[#1A1A1A] font-minion text-base leading-relaxed placeholder-[#8B7D6B]/70 focus:outline-none focus:border-[#8B5A2B] focus:ring-1 focus:ring-[#8B5A2B] transition-all resize-y"
              ></textarea>
            </div>

            <div class="flex flex-col">
              <label class="text-[0.9rem] font-minion font-medium text-[#1A1A1A] mb-1">Tono de la Crónica</label>
              <input
                v-model="tono"
                type="text"
                placeholder="Ej: Terror gótico, investigación, misterio oscuro"
                class="h-[40px] px-3 bg-[#FAF4E8]/60 border-0 border-b border-[#8B7D6B] text-[#1A1A1A] font-minion text-base placeholder-[#8B7D6B]/70 focus:outline-none focus:border-[#D4AF37] focus:ring-0 transition-colors"
              />
            </div>

            <div class="flex flex-col">
              <label class="text-[0.9rem] font-minion font-medium text-[#1A1A1A] mb-1">Frecuencia y Horario</label>
              <input
                v-model="frecuencia"
                type="text"
                placeholder="Ej: Semanal • Sábados 18:00 - 22:00 (GMT+1)"
                class="h-[40px] px-3 bg-[#FAF4E8]/60 border-0 border-b border-[#8B7D6B] text-[#1A1A1A] font-minion text-base placeholder-[#8B7D6B]/70 focus:outline-none focus:border-[#D4AF37] focus:ring-0 transition-colors"
              />
            </div>

            <div class="flex flex-col">
              <label class="text-[0.9rem] font-minion font-medium text-[#1A1A1A] mb-1 flex items-center justify-between">
                <span>Nivel Inicial</span>
                <span class="text-[11px] font-tarzana text-[#8B7D6B]">Mínimo nivel 1</span>
              </label>
              <div class="relative">
                <input
                  v-model.number="nivelInicial"
                  type="number"
                  min="1"
                  max="20"
                  class="h-[40px] w-full px-3 pl-8 bg-[#FAF4E8]/60 border-0 border-b border-[#8B7D6B] text-[#1A1A1A] font-minion text-base placeholder-[#8B7D6B]/70 focus:outline-none focus:border-[#D4AF37] focus:ring-0 transition-colors"
                />
                <span class="absolute inset-y-0 left-2 flex items-center text-xs font-tarzana font-bold text-[#8B5A2B]">Nv</span>
              </div>
            </div>

            <div class="flex flex-col">
              <label class="text-[0.9rem] font-minion font-medium text-[#1A1A1A] mb-1 flex items-center justify-between">
                <span>Jugadores Máximos</span>
                <span class="text-[11px] font-tarzana text-[#8B7D6B]">Quórum de aventureros</span>
              </label>
              <div class="relative">
                <input
                  v-model.number="jugadoresMax"
                  type="number"
                  min="1"
                  max="10"
                  class="h-[40px] w-full px-3 pl-8 bg-[#FAF4E8]/60 border-0 border-b border-[#8B7D6B] text-[#1A1A1A] font-minion text-base placeholder-[#8B7D6B]/70 focus:outline-none focus:border-[#D4AF37] focus:ring-0 transition-colors"
                />
                <span class="absolute inset-y-0 left-2 flex items-center text-xs text-[#8B5A2B]" aria-hidden="true">👥</span>
              </div>
            </div>

            <div class="flex flex-col">
              <label class="text-[0.9rem] font-minion font-medium text-[#1A1A1A] mb-1 flex items-center justify-between">
                <span>Próxima Sesión</span>
                <span class="text-[11px] font-tarzana text-[#8B7D6B]">Elegir en el calendario</span>
              </label>
              <button
                type="button"
                class="h-[40px] w-full px-3 bg-[#FAF4E8]/60 border-0 border-b border-[#8B7D6B] text-left text-[#1A1A1A] font-minion text-base focus:outline-none focus:border-[#D4AF37] transition-colors flex items-center justify-between gap-2"
                @click="fechaAbierta = true"
              >
                <span :class="proximaSesion ? '' : 'text-[#8B7D6B]/70'">{{ proximaSesion || 'Seleccionar fecha de convocatoria…' }}</span>
                <svg class="w-4 h-4 shrink-0 text-[#8B5A2B]" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
              </button>
            </div>

            <div class="flex flex-col md:col-span-2 pt-1">
              <label class="text-[0.9rem] font-minion font-medium text-[#1A1A1A] mb-1.5 flex items-center justify-between">
                <span>Estado de Convocatoria de la Mesa</span>
                <span class="text-[11px] font-tarzana text-[#8B7D6B]">Visibilidad en el explorador</span>
              </label>
              <div class="flex flex-wrap items-center gap-4 p-3 bg-[#FAF4E8] border border-[#C2A980]/80 rounded-sm">
                <label class="inline-flex items-center cursor-pointer">
                  <input v-model="estado" type="radio" name="estado_mesa" value="Abierta" class="sr-only peer" />
                  <div
                    class="px-4 py-1.5 text-xs font-tarzana font-bold uppercase tracking-wider rounded-sm border border-transparent peer-checked:bg-[#6B8E23] peer-checked:text-[#FDF8EE] peer-checked:shadow-sm text-[#555] hover:text-[#1A1A1A] flex items-center space-x-1.5 transition"
                  >
                    <span class="inline-block w-2 h-2 rounded-full bg-[#A4D058]"></span>
                    <span>Abierta (Acepta postulaciones)</span>
                  </div>
                </label>
                <label class="inline-flex items-center cursor-pointer">
                  <input v-model="estado" type="radio" name="estado_mesa" value="Cerrada" class="sr-only peer" />
                  <div
                    class="px-4 py-1.5 text-xs font-tarzana font-bold uppercase tracking-wider rounded-sm border border-transparent peer-checked:bg-[#8B1A1A] peer-checked:text-[#FDF8EE] peer-checked:shadow-sm text-[#555] hover:text-[#1A1A1A] flex items-center space-x-1.5 transition"
                  >
                    <span class="inline-block w-2 h-2 rounded-full bg-[#D66D6D]"></span>
                    <span>Cerrada (Cupos completos / Privada)</span>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <p v-if="errorForm" class="text-xs text-[#8B1A1A] font-minion italic" role="alert">{{ errorForm }}</p>

          <div class="pt-2 border-t border-[#C2A980]/60 flex items-start space-x-3 text-xs text-[#665544] font-minion italic">
            <span class="text-[#8B5A2B] text-sm">✦</span>
            <span>Al guardar la campaña se generará el grimorio maestro de gestión del GM, la sección de Wiki con glosarios de Golarion y el registro de sesiones compatible con el sistema d20 OGL v1.0a.</span>
          </div>

          <div class="pt-4 flex items-center justify-end space-x-4">
            <button
              type="button"
              class="px-6 py-2.5 rounded-sm font-tarzana font-bold text-[0.95rem] tracking-wider uppercase border border-[#8B5A2B]/40 text-[#8B5A2B] hover:bg-[#8B5A2B]/10 transition-colors"
              @click="cancelar"
            >
              Cancelar
            </button>
            <button
              type="submit"
              class="btn-gold-emboss px-8 py-2.5 rounded-sm font-tarzana font-bold text-[0.95rem] tracking-wider uppercase text-[#1A1A1A] flex items-center space-x-2"
            >
              <span>Guardar Campaña</span>
              <span class="text-xs">✦</span>
            </button>
          </div>
        </form>
      </template>
    </div>

    <ModalDatePicker
      :open="fechaAbierta"
      :candidatos="proximosSabados()"
      chip="Próximas convocatorias sabatinas"
      @close="fechaAbierta = false"
      @accepted="aplicarFecha"
    />
  </main>
</template>