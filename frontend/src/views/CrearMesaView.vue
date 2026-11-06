<template>
  <div class="app-grid">
    <main>
      <form class="card form-grid" style="padding: var(--space-lg);" novalidate @submit.prevent="submit">
        <div>
          <h2>Publicá tu campaña</h2>
          <p class="lead">Lo que escribís a la izquierda se ve como la mesa real a la derecha.</p>
        </div>
        <div class="field">
          <label class="label" for="f-nombre">Nombre de la mesa</label>
          <input class="input" :class="{ 'is-error': errNombre }" id="f-nombre" v-model="nombre" placeholder="La Cripta de Vellmar" />
          <p class="hint-error" :hidden="!errNombre">El nombre necesita 4 o más caracteres.</p>
        </div>
        <div class="grid-2" style="gap: var(--space-md);">
          <div class="field">
            <label class="label" for="f-nivel">Nivel</label>
            <input class="input" :class="{ 'is-error': errNivel }" id="f-nivel" v-model.number="nivel" type="number" min="1" max="20" />
            <p class="hint-error" :hidden="!errNivel">El nivel inicial debe ser un entero positivo.</p>
          </div>
          <div class="field">
            <label class="label" for="f-cupos">Cupo</label>
            <input class="input" :class="{ 'is-error': errCupos }" id="f-cupos" v-model.number="cupos" type="number" min="1" />
            <p class="hint-error" :hidden="!errCupos">El cupo máximo debe ser un entero mayor a cero.</p>
          </div>
        </div>
        <div class="field">
          <label class="label" for="f-lugar">Ambientación</label>
          <textarea class="input" id="f-lugar" data-test="input-ambientacion" v-model="lugar" rows="2" placeholder="Ej: Ustalav, un condado de fantasmas al este de Golarion…"></textarea>
          <p class="label">Textira libre: región, ciudad o ambiente de tu campaña.</p>
        </div>
        <div class="field">
          <label class="label" for="f-horario">Horario</label>
          <input class="input" id="f-horario" v-model="horario" placeholder="Jueves 21:00" />
          <p class="label" :hidden="horario.trim() !== ''">Opcional: día y hora sugeridos.</p>
        </div>
        <div class="field">
          <label class="label" for="f-desc">Descripción</label>
          <textarea class="input" id="f-desc" v-model="desc" placeholder="Contá el tono, la campaña y qué esperás de las fichas…"></textarea>
        </div>
        <div style="display: flex; justify-content: flex-end; gap: var(--space-sm);">
          <RouterLink class="btn btn--secondary" to="/mis-mesas-gm">Cancelar</RouterLink>
          <button class="btn" type="submit" :disabled="ocupado">Publicar mesa</button>
        </div>
        <p class="hint-error" v-if="errorForma" role="alert" data-test="error-mesa">{{ errorForma }}</p>
      </form>
    </main>

    <aside>
      <p class="label" style="margin-bottom: var(--space-2xs);">Así la ve la gente</p>
      <article class="card mesa-card" style="padding: var(--space-md);">
        <div class="crt-cover"><span class="figure-lg acid" style="font-size: 40px;">{{ nivelClamped }}</span></div>
        <div style="display: flex; gap: var(--space-2xs); flex-wrap: wrap; margin-bottom: var(--space-2xs);">
          <span class="tag tag--ink">PF1e, nivel {{ nivelClamped }}</span>
          <span class="tag tag--acid">Abierta</span>
          <span class="tag tag--ink">{{ horario || 'Horario a definir' }}</span>
        </div>
        <h3>{{ nombre || 'Mesa sin nombre' }}</h3>
        <p style="font-size: var(--text-sm); color: var(--color-ink-2); margin-block: var(--space-2xs) var(--space-sm);">Dirigida por {{ user?.nombre || 'tu' }}, {{ lugar }}</p>
        <p style="font-size: var(--text-sm); color: var(--color-ink-2);">{{ desc || 'Todavía sin descripción.' }}</p>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-top: var(--space-md);">
          <span class="seats" :aria-label="'0 de ' + cuposClamped">
            <i class="off" v-for="i in cuposClamped" :key="i"></i>
          </span>
          <button class="btn btn--sm" type="button">Unirse</button>
        </div>
      </article>
    </aside>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { validarMesa } from '@/rules/mesas'
import { crearMesa as crearMesaApi } from '@/services/mesas'
// sin demo

const { user, isAuthenticated } = useAuth()
const router = useRouter()

const nombre = ref('')
const nivel = ref(4)
const cupos = ref(5)
const lugar = ref('Ustalav')
const horario = ref('')
const desc = ref('')

const ocupado = ref(false)
const touched = ref(false)
const errorForma = ref(null)

const nivelClamped = computed(() => Math.min(20, Math.max(1, +nivel.value || 1)))
const cuposClamped = computed(() => Math.max(1, +cupos.value || 1))
const errNombre = computed(() => touched.value && nombre.value.trim().length > 0 && nombre.value.trim().length < 4)
const errNivel = computed(() => touched.value && nivel.value !== '' && !(nivel.value >= 1 && nivel.value <= 20))
const errCupos = computed(() => touched.value && !(cupos.value > 0))

async function submit() {
  touched.value = true
  errorForma.value = null
  if (!isAuthenticated.value) { router.push({ path: '/login', query: { redirect: '/mesas/nueva' } }); return }

  // Reglas de negocio antes de publicar (VAL-06/07/08/09/13/14)
  const errores = validarMesa({ nombre: nombre.value, sistema: 'pf1e', estado: 'abierta', nivel: nivel.value === '' ? null : nivel.value, cupo: cupos.value === '' ? null : cupos.value })
  // El nombre vacío se informa con el mensaje de VAL-06
  if (nombre.value.trim() === '') errores.unshift({ codigo: '400', mensaje: 'El nombre de la mesa es obligatorio' })
  if (errores.length) {
    errorForma.value = errores[0].mensaje
    // ok
    return
  }
  if (nombre.value.trim().length > 0 && nombre.value.trim().length < 4) {
    errorForma.value = 'El nombre necesita 4 o más caracteres.'
    // ok
    return
  }

  try {
    await crearMesaApi({
      nombre: nombre.value.trim(),
      estado: 'abierta',
      nivel: nivelClamped.value,
      cupo: cuposClamped.value,
      horario: horario.value.trim(),
      // D-06: la ambientación libre del GM se persiste en el campo tono del
      // contrato (MesaCreate no tiene 'lugar' y es extra="forbid").
      tono: lugar.value.trim(),
      descripcion: desc.value.trim()
    })
    // ok
    router.push('/mis-mesas-gm')
  } catch (e) {
    errorForma.value = e?.message || 'No se pudo crear la mesa.'
    // ok
  }
}
</script>

<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: var(--space-lg); align-items: start; }
.form-grid { display: grid; gap: var(--space-md); }
.preview .crt-cover { height: 88px; }
.mesa-card .crt-cover { height: 88px; background: var(--color-paper-3); color: var(--color-ink); border-bottom: var(--rule-bar) solid var(--color-accent-2); display: grid; place-items: center; margin: calc(-1 * var(--space-md)) calc(-1 * var(--space-md)) var(--space-md); }
@media (max-width: 60rem) { .app-grid { grid-template-columns: minmax(0, 1fr); padding-top: 120px; } }
</style>