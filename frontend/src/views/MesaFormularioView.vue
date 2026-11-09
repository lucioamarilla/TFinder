<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMesa, crearMesa, actualizarMesa } from '@/services/mesas'
import { componerHorario, descomponerHorario } from '@/rules/fechas'
import { useToast } from '@/composables/useToast'
import ModalDatePicker from '@/components/modals/ModalDatePicker.vue'
import Aviso from '@/components/Aviso.vue'

const props = defineProps({
  id: { type: String, default: null }
})

const router = useRouter()
const toast = useToast()

const esEdicion = computed(() => Boolean(props.id))

const nombre = ref('')
const descripcion = ref('')
const tono = ref('')
// D-11: la frecuencia/horario se edita con pickers día/hora. `frecuenciaPrevio`
// conserva el texto legal del contrato; si el GM no toca los pickers, ese texto
// viaja tal cual (los horarios heredados nunca cambian a la mandadera).
const frecDia = ref('')
const frecHora = ref('')
const frecuenciaPrevio = ref('')
const frecuenciaTocada = ref(false)
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
    res.push({ value: f.toISOString().slice(0, 10), label: `Sábado ${diaMes}`, detalle: 'Horario a definir' })
  }
  return res
}

function aplicarFecha(iso) {
  if (!iso) return
  const f = new Date(`${iso}T00:00:00`)
  const diaMes = f.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' })
  proximaSesion.value = `${diaMes.charAt(0).toUpperCase()}${diaMes.slice(1)} · Sesión inaugural`
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
    // D-08: usar el horario real del contrato; el normalizador deriva
    // 'frecuencia' con el literal "A coordinar" y no debe contaminarlo.
    const desarmado = descomponerHorario(mesa.horario ?? '')
    frecDia.value = desarmado.dia
    frecHora.value = desarmado.hora
    frecuenciaPrevio.value = mesa.horario ?? ''
    frecuenciaTocada.value = false
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

  // D-11: componer el horario del contrato desde los pickers día/hora;
  // si el usuario no tocó los pickers, el valor previo viaja tal cual.
  const frecuencia = frecuenciaTocada.value
    ? componerHorario(frecDia.value, frecHora.value)
    : frecuenciaPrevio.value

  try {
    if (esEdicion.value) {
      await actualizarMesa(props.id, {
        nombre: nombre.value.trim(),
        descripcion: descripcion.value,
        tono: tono.value,
        frecuencia,
        nivel: Number(nivelInicial.value),
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
        nivel: Number(nivelInicial.value),
        frecuencia,
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
  <main class="formulario-shell">
    <div class="card panel">
      <div class="miga">
        <div class="miga-ruta">
          <RouterLink to="/mis-mesas" class="text-link">Mis Mesas</RouterLink>
          <span>/</span>
          <span class="label">{{ esEdicion ? 'Editar Campaña' : 'Nueva Campaña' }}</span>
        </div>
        <RouterLink to="/mis-mesas" class="text-link volver">
          <span class="flecha">←</span> Volver a Mis Campañas
        </RouterLink>
      </div>

      <div v-if="isLoading" class="cargando" role="status" aria-live="polite">
        <div class="sckels" aria-hidden="true">
          <div class="skel skel--grande"></div>
          <div class="skel"></div>
          <div class="skel skel--mitad"></div>
        </div>
        <p class="label">Cargando el rollo de campaña</p>
      </div>

      <div v-else-if="error" class="cargando" role="alert">
        <p class="label contra">Error al cargar la campaña</p>
        <p class="label">{{ error }}</p>
        <button type="button" class="btn reintentar" @click="load">Reintentar</button>
      </div>

      <template v-else>
        <div class="cabecera">
          <div class="etiqueta-chequeo">Gestión de crónica y mesa de juego</div>
          <h1 class="titulo">{{ esEdicion ? 'Editar Campaña' : 'Nueva Campaña' }}</h1>
          <p class="label sub-cabecera">Define los estatutos y parámetros para convocar a los aventureros en Golarion</p>
        </div>

        <form class="cuerpo" novalidate @submit.prevent="enviar">
          <div class="grilla">
            <label class="field">
              <span class="etiqueta"><span>Nombre de la Mesa <span class="obligatorio">*</span></span><span class="detalle">Requerido</span></span>
              <input v-model="nombre" type="text" placeholder="Ej: La Corona de Carroña - Cap. II" class="input" />
            </label>

            <label class="field">
              <span class="etiqueta"><span>Sistema de Reglas</span><span class="detalle">Fijo por plataforma</span></span>
              <select disabled class="input fijo">
                <option selected>PF1e (Pathfinder 1ª Edición OGL v1.0a)</option>
              </select>
            </label>

            <label class="field span2">
              <span class="etiqueta"><span>Descripción y Sinopsis de la Crónica</span><span class="detalle">Visible para aspirantes</span></span>
              <textarea v-model="descripcion" rows="4" placeholder="Escribe la sinopsis del Adventure Path o tu campaña personalizada, advertencias de contenido y ambientación..." class="input area area--chica"></textarea>
            </label>

            <label class="field">
              <span class="etiqueta"><span>Tono de la Crónica</span></span>
              <input v-model="tono" type="text" placeholder="Ej: Terror gótico, investigación, misterio oscuro" class="input" />
            </label>

            <div class="field">
              <span class="etiqueta"><span>Frecuencia y Horario</span><span class="detalle">Opcional: día y hora sugeridos</span></span>
              <div class="par-dia-hora">
                <label>
                  <span class="sub-etiqueta">Día</span>
                  <input v-model="frecDia" @input="frecuenciaTocada = true" type="date" class="input" />
                </label>
                <label>
                  <span class="sub-etiqueta">Hora</span>
                  <input v-model="frecHora" @input="frecuenciaTocada = true" type="time" class="input" />
                </label>
              </div>
            </div>

            <label class="field">
              <span class="etiqueta"><span>Nivel Inicial</span><span class="detalle">Mínimo nivel 1</span></span>
              <input v-model.number="nivelInicial" type="number" min="1" max="20" class="input" />
            </label>

            <label class="field">
              <span class="etiqueta"><span>Jugadores Máximos</span><span class="detalle">Quórum de aventureros</span></span>
              <input v-model.number="jugadoresMax" type="number" min="1" max="10" class="input" />
            </label>

            <label class="field">
              <span class="etiqueta"><span>Próxima Sesión</span><span class="detalle">Elegir en el calendario</span></span>
              <button type="button" class="input selector-fecha" @click="fechaAbierta = true">
                <span :class="proximaSesion ? '' : 'apagado'">{{ proximaSesion || 'Seleccionar fecha de convocatoria…' }}</span>
                <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
              </button>
            </label>

            <div class="field span2">
              <span class="etiqueta"><span>Estado de Convocatoria de la Mesa</span><span class="detalle">Visibilidad en el explorador</span></span>
              <div class="estados">
                <label class="estado-opcion">
                  <input v-model="estado" type="radio" name="estado_mesa" value="Abierta" class="sr" />
                  <span class="tag tag--acid op-tag">Abierta (Acepta postulaciones)</span>
                </label>
                <label class="estado-opcion">
                  <input v-model="estado" type="radio" name="estado_mesa" value="Cerrada" class="sr" />
                  <span class="tag tag--ember op-tag">Cerrada (Cupos completos / Privada)</span>
                </label>
              </div>
            </div>
          </div>

          <Aviso v-if="errorForm" tipo="error">{{ errorForm }}</Aviso>

          <div class="nota">
            <span>Al guardar la campaña se generará el grimorio maestro de gestión del GM, la sección de Wiki con glosarios de Golarion y el registro de sesiones compatible con el sistema d20 OGL v1.0a.</span>
          </div>

          <div class="acciones">
            <button type="button" class="btn btn--secondary" @click="cancelar">
              Cancelar
            </button>
            <button type="submit" class="btn">
              Guardar Campaña
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

<style scoped>
.formulario-shell { display: flex; align-items: center; justify-content: center; padding: var(--space-lg) var(--gutter); min-height: 100%; }
.panel { width: 100%; max-width: 50rem; padding: var(--space-lg); position: relative; display: grid; gap: var(--space-md); }
.miga { display: flex; align-items: center; justify-content: space-between; gap: var(--space-sm); border-bottom: var(--rule-hair) solid var(--color-rule); padding-bottom: var(--space-2xs); flex-wrap: wrap; }
.miga-ruta { display: inline-flex; align-items: center; gap: var(--space-2xs); font-size: var(--text-xs); color: var(--color-muted); }
.volver { font-size: var(--text-xs); font-weight: 700; }
.flecha { margin-right: var(--space-3xs); }
.contra { color: var(--color-error); }
.cargando { padding-block: var(--space-lg); text-align: center; display: grid; gap: var(--space-sm); justify-items: center; }
.sckels { width: 100%; max-width: 28rem; display: grid; gap: var(--space-2xs); }
.sckels .skel { height: 10px; }
.sckels .skel--grande { width: 66%; height: 16px; }
.sckels .skel--mitad { width: 50%; }
.reintentar { justify-self: center; }
.cabecera { text-align: center; display: grid; gap: var(--space-3xs); justify-items: center; }
.etiqueta-chequeo { color: var(--color-accent-2); font-size: var(--text-xs); }
.titulo { margin: 0; font-size: var(--text-display-s); color: var(--color-ink); }
.sub-cabecera { margin: 0; color: var(--color-ink-2); font-style: italic; }
.cuerpo { display: grid; gap: var(--space-md); }
.grilla { display: grid; gap: var(--space-md); grid-template-columns: minmax(0, 1fr); }
@media (min-width: 40rem) { .grilla { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.field { display: grid; gap: var(--space-3xs); min-width: 0; }
.span2 { grid-column: 1 / -1; }
.etiqueta { display: flex; align-items: baseline; justify-content: space-between; gap: var(--space-2xs); font-size: var(--text-sm); color: var(--color-ink); }
.detalle { font-size: var(--text-xs); color: var(--color-muted); }
.obligatorio { color: var(--color-error); font-weight: 900; }
.input { width: 100%; }
.fijo { cursor: not-allowed; color: var(--color-muted); background: var(--color-paper-3); }
.area { min-height: 7rem; resize: vertical; line-height: 1.6; }
.area--chica { min-height: 7.5rem; }
.selector-fecha { display: flex; align-items: center; justify-content: space-between; gap: var(--space-2xs); text-align: left; cursor: pointer; }
.apagado { color: var(--color-muted); }
.par-dia-hora { display: grid; gap: var(--space-3xs); }
.par-dia-hora label { display: grid; gap: var(--space-3xs); min-width: 0; }
.sub-etiqueta { font-size: var(--text-xs); color: var(--color-muted); }
.estados { display: flex; flex-wrap: wrap; gap: var(--space-sm); align-items: center; padding: var(--space-2xs) var(--space-sm); border: var(--rule-hair) solid var(--color-rule); }
.estado-opcion { display: inline-flex; align-items: center; cursor: pointer; }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
.op-tag { cursor: pointer; }
.estados .sr:not(:checked) + .op-tag { opacity: .55; }
.nota { display: flex; gap: var(--space-2xs); align-items: flex-start; font-size: var(--text-xs); color: var(--color-ink-2); border-top: var(--rule-hair) solid var(--color-rule); padding-top: var(--space-sm); font-style: italic; }
.acciones { display: flex; justify-content: flex-end; gap: var(--space-md); flex-wrap: wrap; }
</style>
