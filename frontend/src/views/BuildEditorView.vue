<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast.js'
import { getBuild, actualizarBuild } from '@/services/builds.js'

const props = defineProps({ id: { type: String, required: true } })

const router = useRouter()
const toast = useToast()

const cargando = ref(true)
const error = ref(null)
const guardando = ref(false)

const nombre = ref('')
const nivel = ref(1)
const clase = ref('Guerrero (Fighter)')
const arquetipo = ref('')
const tipo = ref('personaje')
const detalle = ref('')
const esPersonaje = computed(() => tipo.value === 'personaje')

const base = [
  { etiqueta: 'FUE', valor: 10, fila: 0 },
  { etiqueta: 'DES', valor: 10, fila: 1 },
  { etiqueta: 'CON', valor: 10, fila: 2 },
  { etiqueta: 'INT', valor: 10, fila: 3 },
  { etiqueta: 'SAB', valor: 10, fila: 4 },
  { etiqueta: 'CAR', valor: 10, fila: 5 }
]
const rasgos = ref(base.map((r) => ({ ...r })))

const dotes = ref([])
const magia = ref([])

const busquedaDotes = ref('')
const busquedaMagia = ref('')

const COMPENDIO_DOTES = [
  { nombre: 'Ataque Poderoso', fuente: 'General' },
  { nombre: 'Esquiva', fuente: 'General' },
  { nombre: 'Soltura con un Arma', fuente: 'General' },
  { nombre: 'Combate con Dos Armas', fuente: 'General' },
  { nombre: 'Doble Tajo', fuente: 'General' },
  { nombre: 'Especialización en Armas', fuente: 'General' },
  { nombre: 'Arremetida Potente', fuente: 'Guerrero' },
  { nombre: 'Reflejos de Combate', fuente: 'General' },
  { nombre: 'Carga Alocada', fuente: 'General' },
  { nombre: 'Valentía', fuente: 'Guerrero' },
  { nombre: 'Esquiva Gigantes', fuente: 'General' },
  { nombre: 'Movilidad', fuente: 'General' },
  { nombre: 'Furtivo', fuente: 'General' },
  { nombre: 'Disparo a Bocajarro', fuente: 'General' }
]

const GRIMORIO = [
  { nombre: 'Varita de Curar Heridas Leves', fuente: 'Nivel 1 (28 cargas)' },
  { nombre: 'Aura de Valentía (Su)', fuente: 'Innato Guerrero' },
  { nombre: 'Aceite de Arma Mágica', fuente: '2 viales' },
  { nombre: 'Poción de Agrandar Persona', fuente: 'Nvl 1 Transmutación' },
  { nombre: 'Rayo de Debilitamiento', fuente: 'Nivel 1' },
  { nombre: 'Sanar Heridas Leves', fuente: 'Nivel 1' },
  { nombre: 'Fuego Fatuo', fuente: 'Nivel 1' }
]

const COSTO_POR_PUNTO = [0, 1, 1, 1, 2, 2, 3, 4]

function costoSobre10(valor) {
  let costo = 0
  for (let i = 11; i <= valor; i++) costo += COSTO_POR_PUNTO[i - 10]
  return costo
}

const puntosUsados = computed(() => rasgos.value.reduce((acc, r) => acc + costoSobre10(r.valor), 0))
const puntosRestantes = computed(() => Math.max(0, 20 - puntosUsados.value))

const sinCupo = computed(() => puntosRestantes.value === 0)

function mod(valor) {
  const m = Math.floor((valor - 10) / 2)
  return m >= 0 ? `+${m}` : `${m}`
}

function ajustar(fila, delta) {
  const r = rasgos.value.find((x) => x.fila === fila)
  const destino = r.valor + delta
  if (destino < 7 || destino > 20) return
  if (delta > 0 && sinCupo.value) {
    toast.info('No quedan puntos para este atributo (límite Buy 20).')
    return
  }
  r.valor = destino
}

const dotesFiltradas = computed(() => {
  const q = busquedaDotes.value.trim().toLowerCase()
  const presentes = new Set(dotes.value.map((d) => d.nombre))
  return COMPENDIO_DOTES.filter((d) => !presentes.has(d.nombre)).filter(
    (d) => !q || d.nombre.toLowerCase().includes(q) || d.fuente.toLowerCase().includes(q)
  )
})

const magiaFiltrada = computed(() => {
  const q = busquedaMagia.value.trim().toLowerCase()
  const presentes = new Set(magia.value.map((m) => m.nombre))
  return GRIMORIO.filter((m) => !presentes.has(m.nombre)).filter(
    (m) => !q || m.nombre.toLowerCase().includes(q) || m.fuente.toLowerCase().includes(q)
  )
})

function anadirDote({ nombre: n, fuente }) {
  if (dotes.value.length >= 5) {
    toast.info('Cupo de dotes completo (5/5).')
    return
  }
  dotes.value.push({ nombre: n, fuente })
}

function quitarDote(indice) {
  dotes.value.splice(indice, 1)
}

function anadirMagia({ nombre: n, fuente }) {
  magia.value.push({ nombre: n, fuente })
}

function quitarMagia(indice) {
  magia.value.splice(indice, 1)
}

const cupoDotes = computed(() => `${dotes.value.length}/5`)

async function cargar() {
  cargando.value = true
  error.value = null
  try {
    const b = await getBuild(props.id)
    tipo.value = b.tipo || 'personaje'
    nombre.value = b.nombre || b.display || ''
    nivel.value = b.nivel || 1
    detalle.value = b.detalle || b.ficha?.cuerpo || ''
    clase.value = b.clase ? (b.clase.includes('(') ? b.clase : `${b.clase} (${b.clase})`) : 'Guerrero (Fighter)'
    arquetipo.value = b.arquetipo || ''
    if (b.ficha?.rasgos) {
      rasgos.value = b.ficha.rasgos.map((r, i) => ({
        etiqueta: r.etiqueta,
        valor: Number(r.valor) || 10,
        fila: i
      }))
    }
    dotes.value = (b.ficha?.dotes || []).map((d) => ({ nombre: d.nombre, fuente: d.fuente }))
    magia.value = (b.ficha?.magia?.items || []).map((m) => ({ nombre: m.nombre, fuente: m.fuente }))
  } catch (e) {
    error.value = e.message || 'No pudimos cargar la ficha para editar.'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)

async function publicarFicha() {
  guardando.value = true
  try {
    const b = await getBuild(props.id)
    const clave = clase.value.replace(/\s*\(.*\)$/, '').trim()
    const nuevaFicha = {
      ...(b.ficha || {}),
      rasgos: rasgos.value.map((r) => ({
        etiqueta: r.etiqueta,
        valor: r.valor,
        mod: mod(r.valor),
        ancho: Math.min(100, Math.round(((r.valor - 7) / 13) * 100))
      })),
      dotes: dotes.value.map((d) => ({ nombre: d.nombre, fuente: d.fuente })),
      magia: {
        intro: 'Capacidades arcanas y objetos activables registrados en la hoja.',
        items: magia.value.map((m) => ({ nombre: m.nombre, fuente: m.fuente, destacado: false }))
      }
    }
    const cambios = {
      nombre: nombre.value.trim(),
      display: nombre.value.trim() || 'Personaje sin nombre',
      nivel: Number(nivel.value),
      clase: clave,
      arquetipo: arquetipo.value,
      privacidad: 'publico',
      ficha: nuevaFicha,
      resumenCambio: `${clave} Nv ${nivel.value}: actualización de atributos, dotes y conjuros.`
    }
    const actualizado = await actualizarBuild(props.id, cambios)
    toast.ok('Build publicado en tu Códice personal.')
    router.push(`/builds/${actualizado.id}`)
  } catch (e) {
    toast.error(e.message || 'No pudimos guardar los cambios.')
  } finally {
    guardando.value = false
  }
}

async function guardarBorrador() {
  try {
    const b = await getBuild(props.id)
    const clave = clase.value.replace(/\s*\(.*\)$/, '').trim()
    const actualizado = await actualizarBuild(props.id, {
      nombre: nombre.value.trim() || b.nombre,
      display: nombre.value.trim() || b.display,
      nivel: Number(nivel.value),
      clase: clave,
      arquetipo: arquetipo.value,
      privacidad: 'borrador',
      resumenCambio: 'Borrador autoguardado.'
    })
    toast.ok('Borrador autoguardado.')
    router.push(`/builds/${actualizado.id}`)
  } catch (e) {
    toast.error(e.message || 'No pudimos autoguardar el borrador.')
  }
}

async function guardarSimple() {
  guardando.value = true
  try {
    const actualizado = await actualizarBuild(props.id, {
      nombre: nombre.value.trim() || 'Sin nombre',
      display: nombre.value.trim() || 'Sin nombre',
      detalle: detalle.value,
      privacidad: 'borrador'
    })
    toast.ok('Cambios guardados.')
    router.push(`/builds/${actualizado.id}`)
  } catch (e) {
    toast.error(e.message || 'No pudimos guardar los cambios.')
  } finally {
    guardando.value = false
  }
}
</script>

<template>
  <main class="forja">
    <div v-if="cargando" class="cargando" role="status" aria-live="polite">
      <div class="sckels">
        <div class="linea linea--grande"></div>
        <div class="linea"></div>
      </div>
      <p class="label">Abriendo la mesa de forja...</p>
    </div>

    <div v-else-if="error" class="cargando" role="alert">
      <p class="label contra">No se pudo editar</p>
      <p class="label">{{ error }}</p>
      <RouterLink to="/builds" class="btn btn--secondary volver-error">← Volver a mis builds</RouterLink>
    </div>

    <template v-else-if="esPersonaje">
      <div class="miga">
        <div class="miga-ruta">
          <RouterLink to="/builds" class="text-link">INICIO</RouterLink>
          <span class="label">/</span>
          <RouterLink to="/builds" class="text-link">BUILDS</RouterLink>
          <span class="label">/</span>
          <span class="label miga-actual">NUEVA FICHA DE PERSONAJE</span>
        </div>
        <RouterLink to="/builds" class="text-link volver">← VOLVER A MIS BUILDS</RouterLink>
      </div>

      <form class="card hoja" @submit.prevent="publicarFicha">
        <header class="seccion seccion--cabecera">
          <div class="cabecera-fila">
            <h1 class="titulo">Crear Personaje</h1>
            <span class="label">Formulario Oficial PF1e SRD</span>
          </div>
          <p class="label intro">Forja tu héroe para Pathfinder Primera Edición según las reglas canónicas de Paizo OGL.</p>
        </header>

        <section data-purpose="character-identity" class="seccion">
          <div class="seccion-titulo">
            <h2 class="rotulo">✦ 1. Identidad y Avance</h2>
            <div class="punteado"></div>
          </div>
          <div class="card bloque-identidad">
            <div class="ident-campo">
              <label for="char-name" class="label etiqueta">Nombre del Personaje <span class="obligatorio">*</span></label>
              <input id="char-name" v-model="nombre" type="text" class="input" placeholder="ej. Valeros el Temerario" required />
              <p class="label nota">Título heroico y renombre en las tierras de Golarion.</p>
            </div>

            <div class="ident-campo ident-campo--borde">
              <div class="nivel-cabeza">
                <label for="char-level" class="label etiqueta">Nivel</label>
                <span class="num nivel-ghost">Nivel {{ nivel }}</span>
              </div>
              <div class="slider-bloque">
                <input id="char-level" v-model.number="nivel" class="slider" max="20" min="1" type="range" />
                <div class=".Customer" aria-hidden="true"></div>
                <div class="escalas num" aria-hidden="true"><span>1</span><span>5</span><span>10</span><span>15</span><span>20</span></div>
              </div>
              <p class="label nota">Progresión BAB &amp; Habilidades.</p>
            </div>

            <div class="ident-campo">
              <label for="char-class" class="label etiqueta">Clase de Personaje <span class="obligatorio">*</span></label>
              <div class="clases">
                <select id="char-class" v-model="clase" class="input">
                  <option>Guerrero (Fighter)</option>
                  <option>Paladín</option>
                  <option>Mago Arcanista</option>
                  <option>Pícaro</option>
                  <option>Clérigo</option>
                  <option>Alquimista</option>
                  <option>Bárbaro</option>
                  <option>Explorador</option>
                </select>
                <input v-model="arquetipo" type="text" class="input arquetipo" placeholder="Arquetipo (opcional)" />
              </div>
            </div>
          </div>
        </section>

        <section data-purpose="ability-scores" class="seccion">
          <div class="seccion-titulo">
            <h2 class="rotulo">✦ 2. Puntuaciones de Característica (Buy-Points OGL)</h2>
            <div class="puntos-info">
              <span class="tag" :class="sinCupo ? 'tag--ember' : 'tag--ink'">Puntos restantes: {{ puntosRestantes }}</span>
              <span class="label nota">Fantasy Buy: 20 pts</span>
            </div>
          </div>
          <div class="atributos">
            <div v-for="r in rasgos" :key="r.etiqueta" class="card atributo">
              <span class="label atributo-clave">{{ r.etiqueta }}</span>
              <span class="num atributo-valor">{{ r.valor }}</span>
              <span class="tag" :class="Number(mod(r.valor)) < 0 ? 'tag--ember' : 'tag--ink'">{{ mod(r.valor) }}</span>
              <div class="slider-atributo">
                <input class="slider" type="range" min="7" max="20" :value="r.valor" @input="r.valor = Number($event.target.value)" />
              </div>
              <div class="atributo-botones">
                <button type="button" class="btn-atributo" aria-label="Reducir" @click="ajustar(r.fila, -1)">-</button>
                <button type="button" class="btn-atributo" aria-label="Aumentar" @click="ajustar(r.fila, 1)">+</button>
              </div>
            </div>
          </div>
        </section>

        <section data-purpose="feats-selection" class="seccion">
          <div class="seccion-titulo">
            <div>
              <h2 class="rotulo">✦ 3. Dotes Seleccionadas ({{ cupoDotes }})</h2>
              <p class="label nota">Dotes de nivel y de clase de Guerrero.</p>
            </div>
            <span v-if="dotes.length >= 5" class="tag tag--ember">Cupo Completo</span>
          </div>
          <div class="busqueda-fila">
            <input v-model="busquedaDotes" type="text" class="input" placeholder="Buscar dotes en el Compendio OGL (ej. Ataque Poderoso, Esquiva...)" />
            <button type="button" class="btn btn--sm" @click="dotesFiltradas[0] && anadirDote(dotesFiltradas[0])">Añadir</button>
          </div>
          <div class="card grupo">
            <div class="chips">
              <div v-for="(d, i) in dotes" :key="d.nombre" class="chip-eleccion">
                <span class="chip-nombre">{{ d.nombre }}</span>
                <span class="tag tag--ink">{{ d.fuente }}</span>
                <button type="button" class="quitar" title="Eliminar" @click="quitarDote(i)">×</button>
              </div>
              <p v-if="dotes.length === 0" class="label vacio-chips">Ninguna dote seleccionada todavía.</p>
            </div>
            <div v-if="dotesFiltradas.length" class="sugerencias">
              <span class="label sugerencias-etiqueta">Sugerencias:</span>
              <button v-for="sug in dotesFiltradas.slice(0, 3)" :key="sug.nombre" type="button" class="btn btn--secondary btn--sm" @click="anadirDote(sug)">+ {{ sug.nombre }}</button>
            </div>
          </div>
        </section>

        <section data-purpose="spells-and-magic-abilities" class="seccion">
          <div class="seccion-titulo">
            <div>
              <h2 class="rotulo">✦ 4. Conjuros y Objetos Activables</h2>
              <p class="label nota">Capacidades de conjuración, varitas o dones sagrados.</p>
            </div>
            <span class="label">{{ magia.length }} {{ magia.length === 1 ? 'elemento asignado' : 'elementos asignados' }}</span>
          </div>
          <div class="busqueda-fila">
            <input v-model="busquedaMagia" type="text" class="input" placeholder="Buscar en el Grimorio Arcano/Divino..." />
          </div>
          <div class="card grupo">
            <div class="chips">
              <div v-for="(m2, i) in magia" :key="m2.nombre" class="chip-eleccion">
                <span class="chip-nombre">{{ m2.nombre }}</span>
                <span class="tag tag--ink">{{ m2.fuente }}</span>
                <button type="button" class="quitar" title="Eliminar" @click="quitarMagia(i)">×</button>
              </div>
              <p v-if="magia.length === 0" class="label vacio-chips">Sin capacidades mágicas registradas.</p>
            </div>
            <div v-if="magiaFiltrada.length" class="sugerencias">
              <span class="label sugerencias-etiqueta">Disponibles:</span>
              <button v-for="op in magiaFiltrada.slice(0, 3)" :key="op.nombre" type="button" class="btn btn--secondary btn--sm" @click="anadirMagia(op)">+ {{ op.nombre }}</button>
            </div>
          </div>
        </section>

        <div class="acciones">
          <button type="button" class="btn btn--secondary" :disabled="guardando" @click="router.push(`/builds/${id}`)">Cancelar</button>
          <button type="button" class="btn btn--secondary" :disabled="guardando" @click="guardarBorrador">Guardar Borrador</button>
          <button type="submit" class="btn" :disabled="guardando">
            {{ guardando ? 'Guardando…' : 'Publicar Ficha' }}
          </button>
        </div>
      </form>
    </template>

    <template v-else>
      <form class="card hoja" @submit.prevent="guardarSimple">
        <header class="seccion seccion--cabecera">
          <h1 class="titulo">Editar {{ tipo }}</h1>
          <p class="label intro">Editá el contenido y los detalles de esta creación.</p>
        </header>
        <div class="field">
          <label class="label" for="simple-nombre">Nombre</label>
          <input id="simple-nombre" v-model="nombre" type="text" class="input" />
        </div>
        <div class="field">
          <label class="label" for="simple-detalle">Descripción / cuerpo</label>
          <textarea id="simple-detalle" v-model="detalle" rows="6" class="input"></textarea>
        </div>
        <div class="acciones">
          <button type="button" class="btn btn--secondary" :disabled="guardando" @click="router.push(`/builds/${id}`)">Cancelar</button>
          <button type="submit" class="btn" :disabled="guardando">
            {{ guardando ? 'Guardando…' : 'Guardar' }}
          </button>
        </div>
      </form>
    </template>
  </main>
</template>

<style scoped>
.forja { width: 100%; max-width: 75rem; margin-inline: auto; padding: var(--space-lg) var(--gutter); display: grid; gap: var(--space-md); align-items: start; }
.contra { color: var(--color-error); }
.cargando { padding-block: var(--space-xl); text-align: center; display: grid; gap: var(--space-sm); justify-items: center; }
.sckels { width: 100%; max-width: 28rem; display: grid; gap: var(--space-2xs); }
.linea { height: 10px; border-radius: 999px; background: var(--color-paper-3); }
.linea--grande { width: 66%; height: 20px; }
.volver-error { justify-self: center; margin-top: var(--space-sm); }
.miga { display: flex; align-items: center; justify-content: space-between; gap: var(--space-2xs); padding-inline: var(--space-3xs); flex-wrap: wrap; }
.miga-ruta { display: inline-flex; align-items: center; gap: var(--space-2xs); font-size: var(--text-xs); color: var(--color-muted); letter-spacing: .06em; }
.miga-actual { color: var(--color-accent); font-weight: 700; }
.volver { font-weight: 700; font-size: var(--text-xs); letter-spacing: .06em; display: inline-flex; gap: var(--space-3xs); }
.hoja { padding: var(--space-lg); display: grid; gap: var(--space-lg); border: var(--rule-bar) solid var(--color-rule); }
.seccion { display: grid; gap: var(--space-sm); }
.seccion--cabecera { border-bottom: var(--rule-bar) solid var(--color-rule); padding-bottom: var(--space-sm); }
.cabecera-fila { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: var(--space-2xs); }
.titulo { margin: 0; font-size: var(--text-title); color: var(--color-ink); text-transform: uppercase; }
.intro { font-style: italic; color: var(--color-ink-2); }
.seccion-titulo { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: var(--space-2xs); border-bottom: var(--rule-hair) solid var(--color-rule); padding-bottom: var(--space-3xs); }
.rotulo { margin: 0; font-size: var(--text-sm); font-weight: 700; color: var(--color-ink); text-transform: uppercase; letter-spacing: .08em; }
.punteado { flex: 1; border-top: var(--rule-hair) dashed var(--color-rule); }
.bloque-identidad { display: grid; gap: var(--space-md); padding: var(--space-md); grid-template-columns: minmax(0, 1fr); }
@media (min-width: 60rem) { .bloque-identidad { grid-template-columns: 5fr 3fr 4fr; } }
.ident-campo { display: grid; gap: var(--space-3xs); align-content: space-between; }
.ident-campo--borde { border-block: var(--rule-hair) solid var(--color-rule); padding-block: var(--space-2xs); }
@media (min-width: 60rem) { .ident-campo--borde { border: 0; border-inline: var(--rule-hair) solid var(--color-rule); padding-inline: var(--space-md); } }
.etiqueta { text-transform: uppercase; letter-spacing: .06em; color: var(--color-accent-2); }
.obligatorio { color: var(--color-error); font-weight: 900; }
.nota { color: var(--color-ink-2); font-style: italic; margin: 0; }
.nivel-cabeza { display: flex; align-items: center; justify-content: space-between; gap: var(--space-2xs); }
.nivel-ghost { font-family: var(--font-display); font-size: var(--text-xl); color: var(--color-accent-2); font-weight: 900; }
.slider-bloque { display: grid; gap: 2px; padding-block: var(--space-2xs); }
.slider { width: 100%; accent-color: var(--color-accent-2); }
.escalas { display: flex; justify-content: space-between; color: var(--color-muted); font-size: 10px; font-weight: 700; padding-inline: var(--space-3xs); }
.clases { display: grid; gap: var(--space-2xs); }
.arquetipo { font-style: italic; font-size: var(--text-xs); }
.atributos { display: grid; gap: var(--space-2xs); grid-template-columns: repeat(2, minmax(0, 1fr)); }
@media (min-width: 40rem) { .atributos { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (min-width: 60rem) { .atributos { grid-template-columns: repeat(6, minmax(0, 1fr)); } }
.atributo { padding: var(--space-2xs); display: grid; gap: var(--space-3xs); justify-items: center; text-align: center; }
.atributo-clave { text-transform: uppercase; letter-spacing: .16em; font-weight: 900; color: var(--color-accent-2); }
.atributo-valor { font-family: var(--font-display); font-size: var(--text-xl); font-weight: 700; color: var(--color-ink); }
.slider-atributo { height: 7rem; display: grid; place-content: center; width: 100%; }
.atributo-botones { display: flex; align-items: center; justify-content: space-between; width: 100%; }
.btn-atributo { width: 24px; height: 24px; border: var(--rule-hair) solid var(--color-rule); background: var(--color-paper); color: var(--color-ink); font-weight: 700; cursor: pointer; display: grid; place-content: center; }
.btn-atributo:hover { background: var(--color-paper-3); }
.busqueda-fila { display: flex; flex-direction: column; gap: var(--space-2xs); }
@media (min-width: 40rem) { .busqueda-fila { flex-direction: row; align-items: center; } .busqueda-fila .input { flex: 1; } }
.grupo { padding: var(--space-sm) var(--space-md); display: grid; gap: var(--space-sm); align-content: start; }
.chips { display: flex; flex-wrap: wrap; gap: var(--space-2xs); align-items: center; }
.chip-eleccion { display: inline-flex; align-items: center; gap: var(--space-2xs); border: var(--rule-bar) solid var(--color-accent-2); background: var(--color-paper-3); padding: var(--space-3xs) var(--space-sm); }
.chip-nombre { font-weight: 700; font-size: var(--text-xs); color: var(--color-ink); }
.quitar { background: transparent; border: 0; color: var(--color-error); font-weight: 900; cursor: pointer; font-size: var(--text-sm); padding-inline: var(--space-3xs); }
.vacio-chips { margin: 0; font-style: italic; }
.sugerencias { display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-2xs); border-top: var(--rule-hair) dashed var(--color-rule); padding-top: var(--space-2xs); }
.sugerencias-etiqueta { text-transform: uppercase; color: var(--color-accent-2); font-weight: 700; }
.acciones { display: flex; flex-direction: column; justify-content: flex-end; gap: var(--space-2xs); border-top: var(--rule-hair) solid var(--color-rule); padding-top: var(--space-2xs); }
@media (min-width: 40rem) { .acciones { flex-direction: row; } }
.Customer { height: 4px; background: var(--color-paper-3); border-radius: 999px; }
</style>
