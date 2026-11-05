<template>
  <div class="app-grid">
    <main>
      <article v-if="!puedeEditar" class="card" style="padding: var(--space-xl); text-align: center;">
        <h2>Solo el GM propietario edita la wiki</h2>
        <p style="font-size: var(--text-sm); color: var(--color-ink-2); margin-top: var(--space-sm);">Históricamente la wiki de campaña es mantenida por su director (RN-05/RN-18).</p>
        <RouterLink class="btn btn--secondary" to="/wiki" style="margin-top: var(--space-md);">Volver al índice</RouterLink>
      </article>

      <form v-else class="card form-grid" novalidate @submit.prevent="publicar">
        <div style="display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: var(--space-sm);">
          <div>
            <h2>Editor de wiki</h2>
            <p class="label">{{ existente ? 'Editando una página existente' : 'Se publica en la wiki de la mesa elegida' }}</p>
          </div>
          <RouterLink class="btn btn--secondary" to="/wiki">Cancelar</RouterLink>
        </div>
        <div class="grid-2" style="gap: var(--space-md);">
          <div class="field">
            <label class="label" for="w-titulo">Título</label>
            <input class="input" :class="{ 'is-error': errTitulo }" id="w-titulo" v-model="titulo" placeholder="El Sello de Vellmar" />
            <p class="hint-error" :hidden="!errTitulo">El título de la página es obligatorio</p>
          </div>
          <div class="field">
            <label class="label" for="w-tipo">Tipo</label>
            <select class="input" id="w-tipo" v-model="tipo">
              <option>NPC</option><option>Lugar</option><option>Criatura</option><option>Sesión</option><option>Nota</option>
            </select>
          </div>
        </div>
        <div class="grid-2" style="gap: var(--space-md);">
          <div class="field">
            <label class="label" for="w-mesa">Mesa</label>
            <select class="input" id="w-mesa" v-model="mesaId">
              <option v-for="m in misMesas" :key="m.id" :value="m.id">{{ m.nombre }}</option>
            </select>
          </div>
          <div class="field">
            <label class="label" for="w-visibilidad">Visibilidad</label>
            <select class="input" id="w-visibilidad" v-model="visibilidad">
              <option value="privada">Privada · solo GM</option>
              <option value="jugadores">Jugadores de la mesa</option>
              <option value="publica">Pública</option>
            </select>
          </div>
        </div>
        <div class="field">
          <label class="label" for="w-cuerpo">Contenido</label>
          <textarea class="input" id="w-cuerpo" v-model="cuerpo" rows="12" placeholder="Escribí la página. Separá párrafos con una línea vacía…"></textarea>
          <p class="hint-error" :hidden="!errCuerpo">La página necesita contenido.</p>
        </div>
        <p class="hint-error" v-if="errorForma" role="alert" data-test="error-wiki">{{ errorForma }}</p>
        <div style="display: flex; justify-content: flex-end; gap: var(--space-sm);">
          <button class="btn" type="submit" :disabled="ocupado">{{ existente ? 'Guardar cambios' : 'Publicar' }}</button>
        </div>
      </form>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { getMisMesas } from '@/services/mesas'
import { wikiApi } from '@/api/endpoints'
// sin demo

const TIPO_OK = new Set(['NPC', 'Lugar', 'Criatura', 'Nota', 'Sesión'])

const { user, isAuthenticated } = useAuth()
const route = useRoute()
const router = useRouter()

const titulo = ref('')
const tipo = ref('NPC')
const cuerpo = ref('')
const visibilidad = ref('jugadores')
const mesaId = ref('')
const existente = ref(null)
const touched = ref(false)
const ocupado = ref(false)
const errorForma = ref(null)
const misMesas = ref([])

const puedeEditar = computed(() => {
  if (!isAuthenticated.value) return false
  if (existente.value) return true
  return misMesas.value.length > 0
})

onMounted(async () => {
  try {
    const todas = await getMisMesas()
    misMesas.value = todas.filter((m) => m.miRol === 'master')
    mesaId.value = misMesas.value[0]?.id || ''
  } catch (e) {
    misMesas.value = []
  }
  const id = route.params.id
  if (id && id !== 'nueva') {
    try {
      const { datos } = await wikiApi.detallar(id)
      existente.value = datos
      titulo.value = datos.titulo || ''
      tipo.value = TIPO_OK.has(datos.tipo) ? datos.tipo : 'NPC'
      visibilidad.value = datos.visibilidad || 'jugadores'
      mesaId.value = datos.mesaId ?? datos.mesa_id ?? mesaId.value
      const contenido = datos.contenido || []
      cuerpo.value = contenido.map((b) => (typeof b === 'string' ? b : b?.texto)).filter(Boolean).join('\n\n')
    } catch (e) {
      existente.value = null
    }
  }
})

const errTitulo = computed(() => touched.value && titulo.value.trim() === '')
const errCuerpo = computed(() => touched.value && cuerpo.value.trim().length === 0)

function validar() {
  touched.value = true
  errorForma.value = null
  if (titulo.value.trim() === '') {
    errorForma.value = 'El título de la página es obligatorio'
    return false
  }
  if (cuerpo.value.trim() === '') {
    errorForma.value = 'La página necesita contenido.'
    return false
  }
  return true
}

async function publicar() {
  if (!validar()) return
  ocupado.value = true
  try {
    const payload = {
      titulo: titulo.value.trim(),
      tipo: tipo.value,
      visibilidad: visibilidad.value,
      contenido: [{ kind: 'parrafo', texto: cuerpo.value.trim() }]
    }
    let pagina
    if (existente.value) {
      const { datos } = await wikiApi.actualizar(existente.value.id, payload)
      pagina = datos
      // ok
    } else {
      const { datos } = await wikiApi.crear(mesaId.value, payload)
      pagina = datos
      // ok
    }
    router.push('/wiki/' + (pagina?.id ?? ''))
  } catch (e) {
    errorForma.value = e?.message || 'No se pudo guardar la página.'
    // ok
  } finally {
    ocupado.value = false
  }
}
</script>

<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-lg); align-items: start; }
.form-grid { display: grid; gap: var(--space-md); padding: var(--space-lg); }
@media (max-width: 60rem) { .app-grid { padding-top: 120px; } }
</style>