<script setup>
import { ref, computed, inject, onMounted, watch } from 'vue'
import { useToast } from '@/composables/useToast.js'
import ModalExpulsar from '@/components/modals/ModalExpulsar.vue'
import { getMiembros, getSolicitudes, aceptarSolicitud, rechazarSolicitud, expulsarMiembro } from '@/services/jugadores.js'

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
        <h2 class="titulo-seccion">✦ Jugadores &amp; Solicitudes</h2>
        <span class="tag tag--acid num">{{ miembros.length }}/{{ capacidad }}</span>
      </div>

      <!-- Solicitudes pendientes -->
      <section v-if="solicitudes.length" aria-labelledby="heading-solicitudes">
        <div class="subtitulo-fila">
          <span class="num">◆</span>
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
        <h3 id="heading-miembros" class="subtitulo">Mesa de Aventureros ({{ miembros.length }} de {{ capacidad }} plazas)</h3>

        <div class="datos">
          <table class="tf-table">
            <thead>
              <tr>
                <th>MIEMBRO</th>
                <th>PERSONAJE ACTIVO</th>
                <th>ESTADO</th>
                <th>INGRESO</th>
                <th class="centrado">ACCIÓN</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="miembro in miembros" :key="miembro.id">
                <td>
                  <div class="miembro-ident">
                    <div class="crt avatar--chico">{{ miembro.avatar }}</div>
                    <div>
                      <div class="nombre">{{ miembro.nombre }}</div>
                      <div class="label">{{ miembro.handle || miembro.rol }}</div>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="valor">{{ miembro.personaje }}</div>
                  <div class="label">{{ miembro.clase }} Nvl {{ miembro.nivel }}</div>
                </td>
                <td>
                  <span class="tag tag--acid">{{ miembro.estado.toUpperCase() }}</span>
                </td>
                <td class="label">{{ miembro.fecha }}</td>
                <td class="centrado">
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
.rotulo { margin: 0; font-size: var(--text-sm); color: var(--color-accent-2); text-transform: uppercase; letter-spacing: .06em; }
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
.centrado { text-align: center; }
.miembro-ident { display: flex; align-items: center; gap: var(--space-2xs); }
.nombre { font-weight: 700; color: var(--color-ink); }
.valor { font-weight: 700; font-size: var(--text-sm); color: var(--color-ink); }
.bloque-orden { display: grid; gap: var(--space-2xs); }
</style>
