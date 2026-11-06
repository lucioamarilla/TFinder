<template>
  <div class="app-grid">
    <template v-if="cargando">
      <main><p class="label">Cargando…</p></main>
    </template>
    <template v-else-if="!mesa">
      <main>
        <article class="card" style="padding: var(--space-xl); text-align: center;">
          <h2>Mesa no encontrada</h2>
          <RouterLink class="btn btn--secondary" to="/mesas" style="margin-top: var(--space-md);">Volver a las mesas</RouterLink>
        </article>
      </main>
    </template>
    <template v-else-if="!esGM">
      <main>
        <article class="card" style="padding: var(--space-xl); text-align: center;">
          <h2>Esta mesa no es tuya</h2>
          <p style="font-size: var(--text-sm); color: var(--color-ink-2); margin-top: var(--space-sm);">Solo el GM propietario administra la mesa (VAL-17).</p>
          <RouterLink class="btn btn--secondary" to="/mesas" style="margin-top: var(--space-md);">Volver a las mesas</RouterLink>
        </article>
      </main>
    </template>
    <template v-else>
      <main style="display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-md);">
        <div style="display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: var(--space-sm);">
          <div>
            <h2>Panel de mesa</h2>
            <p class="label">{{ mesa.nombre }}, por {{ mesa.gm }}</p>
          </div>
          <div style="display: flex; gap: var(--space-2xs); align-items: center;">
            <span class="tag" :class="mesa.estado === 'cerrada' ? 'tag--ember' : 'tag--acid'">{{ mesa.estado === 'cerrada' ? 'Cerrada' : 'Abierta' }}</span>
            <button class="btn btn--secondary btn--sm" @click="toggleEstado">{{ mesa.estado === 'cerrada' ? 'Reabrir mesa' : 'Cerrar mesa' }}</button>
          </div>
        </div>

        <div class="grid-3">
          <div class="metrica"><p class="figure-lg ember" style="font-size: 40px;">{{ pendientes.length }}</p><p class="label">Solicitudes</p></div>
          <div class="metrica"><p class="figure-lg" style="font-size: 40px;">{{ ocupacion }}/{{ mesa.cupo }}</p><p class="label">Asientos</p></div>
          <div class="metrica"><p class="figure-lg acid" style="font-size: 40px;">{{ mesa.cupo - ocupacion }}</p><p class="label">Vacantes</p></div>
        </div>

        <div class="card" style="padding: var(--space-md);">
          <h3>Bandeja de solicitudes</h3>
          <p class="hint-error" v-if="errorBandeja" role="alert" data-test="error-gm-bandeja">{{ errorBandeja }}</p>
          <div v-if="pendientes.length === 0" style="font-size: var(--text-sm); color: var(--color-ink-2);">No queda nadie esperando: la bandeja está limpia.</div>
          <div v-for="s in pendientes" :key="s.id" class="solicitud">
            <div class="quien">
              <span class="av">{{ iniciales(s.nombre) }}</span>
              <div>
                <p style="font-weight: 700; font-size: var(--text-sm); margin: 0;">{{ s.nombre }}</p>
                <p style="font-size: var(--text-xs); color: var(--color-muted); margin: 0;">{{ s.nota || 'Sin nota' }}</p>
              </div>
            </div>
            <div style="display: flex; gap: var(--space-2xs);">
              <button class="btn btn--sm" @click="aceptar(s)">Aceptar</button>
              <button class="btn btn--danger btn--sm" @click="rechazar(s)">Rechazar</button>
            </div>
          </div>
        </div>

        <details class="card" style="padding: var(--space-md);" open data-test="panel-edicion">
          <h3>Editar mesa</h3>
          <div class="field">
            <label class="label" for="e-nombre">Nombre</label>
            <input class="input" id="e-nombre" v-model="edicion.nombre" />
          </div>
          <div class="field">
            <label class="label" for="e-horario">Horario</label>
            <input class="input" id="e-horario" v-model="edicion.horario" />
          </div>
          <div class="field">
            <label class="label" for="e-cupo">Cupo</label>
            <input class="input" id="e-cupo" data-test="input-cupo" v-model.number="edicion.cupo" type="number" min="1" />
          </div>
          <p class="hint-error" v-if="errorEdicion" role="alert" data-test="error-edicion">{{ errorEdicion }}</p>
          <button class="btn btn--sm" data-test="guardar-detalle" @click="guardar">Guardar cambios</button>
        </details>
      </main>

      <aside>
        <div class="well" style="padding: var(--space-md); margin-bottom: var(--space-md); display: grid; gap: var(--space-2xs);">
          <p class="label" style="margin-bottom: var(--space-2xs);">Acciones rápidas</p>
          <RouterLink class="accion-rapida" :to="`/mesas/${mesa.id}/sesion`">Modo sesión</RouterLink>
          <RouterLink class="accion-rapida" to="/wiki/nueva">Nueva página de wiki</RouterLink>
        </div>
      </aside>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { getMesa, actualizarMesa } from '@/services/mesas'
import { getMiembros, getSolicitudes, aceptarSolicitud, rechazarSolicitud } from '@/services/jugadores'
import { mesasApi } from '@/api/endpoints'
// sin demo
import { validarMesa, validarCupo } from '@/rules/mesas'

const route = useRoute()
const router = useRouter()
const { user } = useAuth()

const mesa = ref(null)
const cargando = ref(true)
const ocupacion = ref(0)
const pendientes = ref([])
const errorBandeja = ref(null)
const errorEdicion = ref(null)

const edicion = reactive({ nombre: '', horario: '', cupo: null })

const esGM = computed(() => !!mesa.value && !!user.value && mesa.value.gmId === Number(user.value?.id ?? user.value?.sub))

onMounted(async () => {
  // D-01: mesa define existencia; ocupación y bandeja fallan de forma aislada.
  try {
    mesa.value = await getMesa(route.params.id)
  } catch (e) {
    mesa.value = null
    cargando.value = false
    return
  }
  try {
    const miembros = await getMiembros(mesa.value.id)
    ocupacion.value = miembros?.miembros?.length ?? mesa.value.jugadores ?? 0
  } catch {
    ocupacion.value = mesa.value.jugadores ?? 0 // contingencia sin membresía
  }
  try {
    const sols = await getSolicitudes(mesa.value.id)
    pendientes.value = (sols ?? []).filter((s) => s.estado === 'pendiente')
  } catch (e) {
    pendientes.value = []
    errorBandeja.value = e?.message || 'No se pudo cargar la bandeja de solicitudes.'
  }
  edicion.nombre = mesa.value.nombre
  edicion.horario = mesa.value.horario
  edicion.cupo = mesa.value.plazas
  cargando.value = false
})

function iniciales(n) { return (n || '').trim().split(/\s+/).map((p) => p[0]).slice(0, 2).join('').toUpperCase() || 'AV' }

async function aceptar(s) {
  try {
    await aceptarSolicitud(mesa.value.id, s.id)
    pendientes.value = pendientes.value.filter((x) => x.id !== s.id)
    ocupacion.value += 1
    // ok
  } catch (e) {
    errorBandeja.value = e?.message || 'No se pudo aceptar.'
  }
}

async function rechazar(s) {
  try {
    await rechazarSolicitud(mesa.value.id, s.id)
    pendientes.value = pendientes.value.filter((x) => x.id !== s.id)
    // ok
  } catch (e) {
    errorBandeja.value = e?.message || 'No se pudo rechazar.'
  }
}

async function toggleEstado() {
  const nuevo = mesa.value.estado === 'cerrada' ? 'abierta' : 'cerrada'
  try {
    await actualizarMesa(mesa.value.id, { estado: nuevo })
    mesa.value.estado = nuevo
    // ok
  } catch (e) {
    // ok
  }
}

async function guardar() {
  errorEdicion.value = null
  const errores = validarMesa({ nombre: edicion.nombre, sistema: 'pf1e', estado: mesa.value.estado, cupo: edicion.cupo })
  if (errores.length) {
    errorEdicion.value = errores[0].mensaje
    // ok
    return
  }
  try {
    const actualizada = await actualizarMesa(mesa.value.id, { nombre: edicion.nombre, horario: edicion.horario, cupo: edicion.cupo })
    mesa.value.nombre = actualizada.nombre
    mesa.value.horario = actualizada.horario
    mesa.value.cupo = actualizada.plazas
    mesa.value.plazas = actualizada.plazas
    // ok
  } catch (e) {
    errorEdicion.value = e?.message || 'No se pudo actualizar.'
    // ok
  }
}

async function invitar() {
  // ok
}
</script>

<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: minmax(0, 1fr) 312px; gap: var(--space-lg); align-items: start; }
.metrica { background: var(--color-paper-3); border: var(--rule-hair) solid var(--color-rule); border-radius: var(--radius-card); padding: var(--space-md); text-align: center; }
.solicitud { display: flex; align-items: center; justify-content: space-between; gap: var(--space-md); padding-block: var(--space-sm); border-bottom: var(--rule-hair) solid var(--color-rule); flex-wrap: wrap; }
.solicitud:last-child { border-bottom: none; }
.solicitud .quien { display: flex; align-items: center; gap: var(--space-sm); min-width: 0; }
.solicitud .av { width: 36px; height: 36px; border-radius: var(--radius-card); background: var(--color-paper-3); border: var(--rule-hair) solid var(--color-rule); display: grid; place-items: center; font-size: var(--text-xs); font-weight: 700; color: var(--color-ink); flex: none; }
.accion-rapida { display: flex; align-items: center; gap: var(--space-2xs); width: 100%; min-height: 40px; padding: var(--space-2xs) var(--space-md); background: transparent; border: var(--rule-bar) solid var(--color-rule); border-radius: var(--radius-card); color: var(--color-ink); font: 700 var(--text-sm) var(--font-body); cursor: pointer; text-decoration: none; text-align: left; }
.accion-rapida:hover { border-color: var(--color-focus); color: var(--color-ink); }
@media (max-width: 75rem) { .app-grid { grid-template-columns: minmax(0, 1fr); } }
@media (max-width: 60rem) { .app-grid { padding-top: 120px; } }
</style>