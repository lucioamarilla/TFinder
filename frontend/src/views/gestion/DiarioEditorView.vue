<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast.js'
import { getSesion, getSesiones, guardarDiario } from '@/services/sesiones.js'
import { getMiembros } from '@/services/jugadores.js'

const props = defineProps({ mesaId: { type: String, required: true }, sesionId: { type: String, required: true } })

const router = useRouter()
const toast = useToast()

const sesion = ref(null)
const falta = ref(false)
const miembros = ref([])
const presentes = ref({})
const tituloCapitulo = ref('')
const recompensas = ref('')
const contenido = ref('')
const guardando = ref(false)

const rutaBase = computed(() => `/mesas/${props.mesaId}/gestion/sesiones`)
// D-04: SesionOut no trae numero; el ordinal se deriva al leer la lista.
const sesionesOrden = ref([])

async function cargar() {
  try {
    const [lista, detalle, jugadores] = await Promise.all([
      getSesiones(props.mesaId),
      getSesion(props.mesaId, props.sesionId),
      getMiembros(props.mesaId)
    ])
    sesionesOrden.value = lista
    sesion.value = detalle
    miembros.value = (jugadores.miembros ?? []).filter((m) => m.rol === 'Jugador' || m.rol === 'Master')
    presentes.value = miembros.value.reduce((acc, m) => ({ ...acc, [m.id]: true }), {})
    tituloCapitulo.value = `Sesión ${ordinalDe(detalle)}`
    recompensas.value = ''
    contenido.value = ''
  } catch {
    falta.value = true
  }
}

function ordinalDe(s) {
  const idx = sesionesOrden.value.findIndex((x) => String(x.id) === String(s.id))
  return `#${idx + 1}`
}

onMounted(cargar)
watch(() => props.sesionId, cargar)

function cancelar() {
  router.push(rutaBase.value)
}

async function guardar() {
  if (!contenido.value.trim()) {
    toast.error('El resumen del diario no puede quedar en blanco.')
    return
  }
  guardando.value = true
  try {
    await guardarDiario(props.mesaId, props.sesionId, { titulo: tituloCapitulo.value, cuerpo: contenido.value.trim() })
    toast.ok(`Diario de la sesión ${ordinalDe(sesion.value)} registrado en el archivo de campaña.`)
    router.push(rutaBase.value)
  } catch (e) {
    toast.error(e.message || 'No pudimos guardar el diario.')
  } finally {
    guardando.value = false
  }
}
</script>

<template>
      <div v-if="falta" class="falta">
      No encontramos esa sesión en el archivo de la campaña.
      <RouterLink :to="rutaBase" class="text-link">← Volver al historial</RouterLink>
    </div>

    <div v-else-if="sesion" class="diario">
      <div class="volver-fila">
        <RouterLink :to="rutaBase" class="text-link volver">← Volver al historial de sesiones</RouterLink>
        <p class="label">
          Sesión {{ ordinalDe(sesion) }} · {{ sesion.fecha ? sesion.fecha.slice(0, 10) : '' }}
        </p>
      </div>

      <h2 class="crt titulo">✒ {{ tituloCapitulo }}</h2>

      <div class="grupo-campos">
        <label class="field">
          <span class="label">Título del Capítulo</span>
          <input v-model="tituloCapitulo" type="text" class="input" />
        </label>
        <label class="field">
          <span class="label">XP / Tesoro (opcional)</span>
          <input v-model="recompensas" type="text" placeholder="Ej. +1.800 PX • 650 po repartidas" class="input" />
        </label>
      </div>

      <label class="field">
        <span class="label">Resumen de la Sesión <span class="obligatorio">*</span></span>
        <textarea
          v-model="contenido"
          rows="12"
          placeholder="Narra lo ocurrido: decisiones, combates, descubrimientos y ganchos pendientes…"
          class="input area"
        ></textarea>
        <span class="label nota">Autoguardado local activo · los cambios se conservan en el grimorio de la mesa.</span>
      </label>

      <section v-if="miembros.length" class="card presentes">
        <h3 class="label rotulo">Personajes presentados en la mesa</h3>
        <div class="lista">
          <label v-for="m in miembros" :key="m.id" class="presente">
            <input v-model="presentes[m.id]" type="checkbox" />
            <span class="cuando">{{ m.nombre }}</span>
            <span class="label">({{ m.rol }})</span>
          </label>
        </div>
      </section>

      <div class="fila-envio">
        <button type="button" class="btn btn--secondary" @click="cancelar">
          Cancelar
        </button>
        <button type="button" :disabled="guardando" class="btn" @click="guardar">
          {{ guardando ? 'Guardando…' : 'Guardar diario' }}
        </button>
      </div>
    </div>
</template>

<style scoped>
.diario { display: grid; gap: var(--space-md); }
.falta { text-align: center; padding-block: var(--space-xl); display: grid; gap: var(--space-sm); justify-items: center; color: var(--color-ink-2); }
.volver-fila { display: grid; gap: var(--space-3xs); }
.volver { font-weight: 700; font-size: var(--text-sm); }
.titulo { padding-bottom: var(--space-sm); border-bottom: var(--rule-bar) solid var(--color-rule); margin: 0; font-size: var(--text-title); color: var(--color-ink); }
.grupo-campos { display: grid; gap: var(--space-sm); }
.field { display: grid; gap: var(--space-3xs); }
.obligatorio { color: var(--color-error); }
.area { min-height: 16rem; resize: vertical; line-height: 1.6; }
.rotulo { margin: 0 0 var(--space-2xs); }
.presentes { padding: var(--space-sm) var(--space-md); }
.lista { display: grid; grid-template-columns: repeat(1, minmax(0, 1fr)); gap: var(--space-2xs); }
@media (min-width: 40rem) { .lista { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.presente { display: flex; align-items: center; gap: var(--space-2xs); cursor: pointer; color: var(--color-ink); }
.cuando { font-weight: 700; }
.nota { color: var(--color-ink-2); }
.fila-envio { display: flex; gap: var(--space-2xs); justify-content: flex-end; }
@media (max-width: 60rem) { .diario { padding-top: 0; } .grupo-campos { grid-template-columns: minmax(0, 1fr); } }
</style>
