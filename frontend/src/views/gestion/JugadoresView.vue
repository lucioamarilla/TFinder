<script setup>
import { ref, computed, inject, onMounted, watch } from 'vue'
import { useToast } from '@/composables/useToast.js'
import ModalExpulsar from '@/components/modals/ModalExpulsar.vue'
import { getMiembros, getSolicitudes, aceptarSolicitud, rechazarSolicitud, expulsarMiembro, contarJugadores } from '@/services/jugadores.js'

const props = defineProps({ mesaId: { type: String, required: true } })

const toast = useToast()
const gestion = inject('mesaGestion')

const miembros = ref([])
const solicitudes = ref([])
const capacidad = ref(5)
const expulsarAbierto = ref(false)
const candidatoExpulsar = ref(null)
const procesando = ref(false)

const nombreMesa = computed(() => gestion?.mesa.value?.nombre || 'la mesa')
// El master figura en la tabla pero no ocupa plaza: el conteo solo suma
// jugadores (rol 'Jugador'), igual que mesa.jugadores del buscador de mesas.
const cantidadJugadores = computed(() => contarJugadores(miembros.value))
const jugadorModal = computed(() => {
  if (!candidatoExpulsar.value) return { nombre: '', rol: '', chip: '' }
  const m = candidatoExpulsar.value
  return { nombre: m.nombre, rol: m.rol, chip: `${m.personaje} · ${m.clase} Nvl ${m.nivel}` }
})

async function cargar() {
  const mesa = gestion?.mesa.value ?? null
  const [equipo, pendientes] = await Promise.all([getMiembros(props.mesaId, mesa), getSolicitudes(props.mesaId)])
  miembros.value = equipo.miembros
  capacidad.value = equipo.capacidad ?? mesa?.plazas ?? capacidad.value
  solicitudes.value = pendientes
}

onMounted(cargar)
watch(() => props.mesaId, cargar)

async function aceptar(solicitud) {
  await aceptarSolicitud(props.mesaId, solicitud.id)
  toast.ok('Solicitud aceptada · nuevo héroe en la mesa.')
  await cargar()
}

async function rechazar(solicitud) {
  await rechazarSolicitud(props.mesaId, solicitud.id)
  toast.info('Solicitud rechazada · se notificó al aventurero.')
  await cargar()
}

function abrirExpulsar(miembro) {
  candidatoExpulsar.value = miembro
  expulsarAbierto.value = true
}

async function confirmarExpulsion() {
  procesando.value = true
  try {
    const expulsado = await expulsarMiembro(props.mesaId, candidatoExpulsar.value.id)
    toast.ok(`${expulsado.nombre} fue expulsado de ${nombreMesa.value}.`)
    await cargar()
  } catch (e) {
    toast.error(e.message || 'No pudimos expulsar al miembro.')
  } finally {
    procesando.value = false
    expulsarAbierto.value = false
  }
}
</script>

<template>
      <div class="jugadores">
      <div class="cabecera-fila">
        <h2 class="titulo-seccion">Jugadores &amp; Solicitudes</h2>
        <span class="tag tag--acid num">{{ cantidadJugadores }}/{{ capacidad }}</span>
      </div>

      <!-- Solicitudes pendientes -->
      <section v-if="solicitudes.length" aria-labelledby="heading-solicitudes">
        <div class="subtitulo-fila">
          <h3 id="heading-solicitudes" class="rotulo">Solicitudes Pendientes de Ingreso ({{ solicitudes.length }})</h3>
        </div>

        <div class="tarjetas-solicitud">
          <article v-for="solicitud in solicitudes" :key="solicitud.id" class="card pedido">
            <div class="pedido-cabeza">
              <div class="crt avatar">{{ solicitud.avatar }}</div>
              <div class="min-w">
                <h4 class="pedido-nombre">{{ solicitud.nombre }}</h4>
                <p class="label pedido-meta">{{ solicitud.personaje }} · {{ solicitud.clase }} Nvl {{ solicitud.nivel }}</p>
                <p class="label pedido-nota">{{ solicitud.nota }}</p>
              </div>
            </div>
            <div class="pedido-pie">
              <span class="label pedido-fecha">{{ solicitud.fecha }}</span>
              <div class="pedido-botones">
                <button
                  type="button"
                  class="btn btn--danger btn--sm"
                  title="Rechazar solicitud"
                  @click="rechazar(solicitud)"
                >
                  Rechazar
                </button>
                <button
                  type="button"
                  class="btn btn--sm"
                  title="Aceptar e incorporar a la campaña"
                  @click="aceptar(solicitud)"
                >
                  Aceptar
                </button>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- Miembros -->
      <section aria-labelledby="heading-miembros">
        <h3 id="heading-miembros" class="subtitulo">Mesa de Aventureros ({{ cantidadJugadores }} de {{ capacidad }} plazas)</h3>

        <div class="datos">
          <table class="tf-table">
            <thead>
              <tr>
                <th>Miembro</th>
                <th>Personaje activo</th>
                <th>Estado</th>
                <th>Ingreso</th>
                <th class="centrado">Acción</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="miembro in miembros" :key="miembro.id">
                <td data-label="Miembro">
                  <div class="miembro-ident">
                    <div class="crt avatar--chico">{{ miembro.avatar }}</div>
                    <div>
                      <div class="nombre">{{ miembro.nombre }}</div>
                      <div class="label">{{ miembro.handle || miembro.rol }}</div>
                    </div>
                  </div>
                </td>
                <td data-label="Personaje activo">
                  <template v-if="miembro.rol === 'Master'">
                    <div class="valor">Sin personaje</div>
                    <div class="label">Dirige la mesa</div>
                  </template>
                  <template v-else>
                    <div class="valor">{{ miembro.personaje }}</div>
                    <div class="label">{{ miembro.clase }} Nvl {{ miembro.nivel }}</div>
                  </template>
                </td>
                <td data-label="Estado">
                  <span v-if="miembro.rol === 'Master'" class="tag tag--ink">Master</span>
                  <span v-else class="tag tag--acid">{{ miembro.estado }}</span>
                </td>
                <td class="label" data-label="Ingreso">{{ miembro.rol === 'Master' ? 'Dirige la mesa' : miembro.fecha }}</td>
                <td class="centrado" data-label="Acción">
                  <button
                    v-if="miembro.rol !== 'Master'"
                    type="button"
                    class="btn btn--danger btn--sm"
                    @click="abrirExpulsar(miembro)"
                  >
                    Expulsar
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>

    <ModalExpulsar
      :open="expulsarAbierto"
      :jugador="jugadorModal"
      :mesa-nombre="nombreMesa"
      @close="expulsarAbierto = false"
      @accepted="confirmarExpulsion"
    />
</template>

<style scoped>
.jugadores { display: grid; gap: var(--space-lg); }
.cabecera-fila { display: flex; align-items: center; justify-content: space-between; gap: var(--space-sm); flex-wrap: wrap; border-bottom: var(--rule-bar) solid var(--color-rule); padding-bottom: var(--space-sm); }
.titulo-seccion { margin: 0; font-size: var(--text-title); color: var(--color-ink); }
.subtitulo { margin: 0 0 var(--space-sm); font-size: var(--text-md); color: var(--color-ink); }
.subtitulo-fila { display: flex; align-items: center; gap: var(--space-2xs); margin-bottom: var(--space-sm); }
.rotulo { margin: 0; font-size: var(--text-sm); color: var(--color-accent-2); }
.tarjetas-solicitud { display: grid; gap: var(--space-sm); grid-template-columns: repeat(1, minmax(0, 1fr)); }
@media (min-width: 60rem) { .tarjetas-solicitud { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.pedido { padding: var(--space-sm) var(--space-md); display: flex; flex-direction: column; justify-content: space-between; gap: var(--space-sm); }
.pedido-cabeza { display: flex; align-items: flex-start; gap: var(--space-sm); }
.min-w { min-width: 0; display: grid; gap: 2px; }
.pedido-nombre { margin: 0; font-weight: 700; color: var(--color-ink); }
.pedido-meta { margin: 0; }
.pedido-nota { margin: 0; font-style: italic; }
.pedido-pie { display: flex; align-items: center; justify-content: space-between; gap: var(--space-2xs); flex-wrap: wrap; }
.pedido-botones { display: flex; align-items: center; gap: var(--space-2xs); }
.datos { border: var(--rule-hair) solid var(--color-rule); overflow-x: auto; }
/* móvil: la tabla de miembros colapsa a una tarjeta por miembro (el mismo
   lenguaje de las tarjetas de solicitud); la etiqueta de cada dato viaja
   inline sobre el valor via attr(data-label) */
@media (max-width: 40rem) {
  .datos { border: 0; overflow: visible; background: transparent; }
  .tf-table { display: block; }
  .tf-table thead { display: none; }
  .tf-table tbody { display: grid; gap: var(--space-sm); }
  .tf-table tbody tr { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: var(--space-2xs) var(--space-sm); border: var(--rule-hair) solid var(--color-rule); border-top: var(--rule-bar) solid var(--color-rule); border-radius: var(--radius-card); background: var(--color-paper-2); padding: var(--space-sm); }
  .tf-table td { border-top: 0; padding: 0; }
  .tf-table td::before { content: attr(data-label); display: block; font-size: var(--text-xs); font-weight: 700; color: var(--color-muted); }
  .tf-table td:first-child { grid-column: 1 / -1; }
  .tf-table td:first-child::before { content: none; }
  .tf-table td:nth-child(2) { grid-column: 1; }
  .tf-table td:nth-child(3) { grid-column: 2; justify-self: end; }
  .tf-table td:nth-child(4) { grid-column: 1; }
  .tf-table td:nth-child(5) { grid-column: 2; justify-self: end; }
  .tf-table td:nth-child(5)::before { content: none; }
}
.centrado { text-align: center; }
.miembro-ident { display: flex; align-items: center; gap: var(--space-2xs); }
.nombre { font-weight: 700; color: var(--color-ink); }
.valor { font-weight: 700; font-size: var(--text-sm); color: var(--color-ink); }
.bloque-orden { display: grid; gap: var(--space-2xs); }
</style>
