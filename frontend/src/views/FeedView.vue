<template>
  <div class="app-grid">
    <aside class="sidebar">
      <div class="well">
        <p class="label" style="margin-bottom: var(--space-2xs);">Comunidades</p>
        <p v-if="comunidades.length === 0 && !cargandoComunidades" class="side-item side-soft">
          Todavía no hay comunidades activas. Creá la primera publicando en el feed.
        </p>
        <button
          v-for="c in comunidades"
          :key="c.id"
          type="button"
          class="side-item side-link"
          :aria-pressed="comunidadActiva === c.id"
          @click="elegir(c.id)"
        >
          <span class="num">{{ c.cantidad }}</span>
          {{ c.id }}
        </button>
        <button
          v-if="comunidadActiva"
          type="button"
          class="side-item side-link"
          @click="elegir(null)"
        >
          ← Volver al feed general
        </button>
      </div>
    </aside>

    <main>
      <div class="feed-tabs" role="tablist" aria-label="Filtros del feed">
        <button v-for="f in filtros" :key="f.key" role="tab" :aria-selected="tabActiva === f.key" @click="elegirTab(f.key)">{{ f.label }}</button>
        <span class="spacer"></span>
        <RouterLink class="text-link" to="/mesas">Explorar mesas</RouterLink>
      </div>

      <template v-if="isAuthenticated">
      <form class="card composer" @submit.prevent="publicar">
        <div class="field">
          <label class="label" for="np-titulo">Nueva publicación {{ comunidadActiva ? `en ${comunidadActiva}` : '' }}</label>
          <input class="input" id="np-titulo" v-model="titulo" placeholder="¿De qué querés hablar?" />
        </div>
        <div class="field">
          <textarea class="input" id="np-cuerpo" v-model="cuerpo" placeholder="Contá la jugada, la duda o la crónica…"></textarea>
        </div>
        <div class="field" v-if="!comunidadActiva">
          <label class="label" for="np-comunidad">Comunidad (opcional, se publica como t/…)</label>
          <input class="input" id="np-comunidad" v-model="comunidadNueva" placeholder="VellmarCronistas" />
        </div>
        <p class="hint-error" v-if="errorPublicar" role="alert" data-test="error-publicar">{{ errorPublicar }}</p>
        <div style="display: flex; justify-content: flex-end;">
          <button class="btn" type="submit">Publicar</button>
        </div>
      </form>
    </template>
    <template v-else>
      <div class="card" style="padding: var(--space-md); text-align: center;">
        <p>Iniciá sesión para publicar en el feed.</p>
        <RouterLink class="btn" to="/login">Iniciar sesión</RouterLink>
      </div>
    </template>

      <div v-if="cargando" class="card" style="padding: var(--space-xl); text-align: center;" role="status">
        Cargando el feed…
      </div>
      <div v-else-if="errorCarga" class="card" style="padding: var(--space-xl); text-align: center;" role="alert">
        <p>No se pudo cargar el feed. Intentá de nuevo en un momento.</p>
        <button class="btn" style="margin-top: var(--space-sm);" @click="cargar">Reintentar</button>
      </div>
      <div v-else-if="postsFiltrados.length === 0" class="card" style="padding: var(--space-xl); text-align: center;">
        <p v-if="comunidadActiva">
          Nadie posteo todavía en {{ comunidadActiva }}. Habría que revivirlo con tu primera publicación.
        </p>
        <p v-else>Nadie posteo todavía. Publicá el primer mensaje de la jornada.</p>
      </div>

      <article v-for="p in postsFiltrados" :key="String(p.id)" class="card post">
        <div class="post-card">
          <div class="votecell vote">
            <button @click="votar(p, 'up')" :aria-pressed="p.miVoto === 'up'" aria-label="Votar a favor">▲</button>
            <span class="count">{{ p.votos }}</span>
            <button @click="votar(p, 'down')" :aria-pressed="p.miVoto === 'down'" aria-label="Votar en contra">▼</button>
          </div>
          <div class="body">
            <p class="label">
              Publicado por {{ p.autorNombre || p.autor }}<span v-if="p.comunidad"> en {{ p.comunidad }}</span>, hace {{ relativo(p) }}
            </p>
            <p class="post-title" style="margin-block: var(--space-2xs);">{{ p.titulo }}</p>
            <p style="font-size: var(--text-sm); color: var(--color-ink-2);">{{ p.cuerpo }}</p>
            <div class="acciones" v-if="p.totalComentarios > 0">
              <button class="thread-toggle" @click="toggleComentarios(p)">{{ p.totalComentarios }} {{ p.totalComentarios === 1 ? 'comentario' : 'comentarios' }}</button>
            </div>
            <div class="thread" v-if="p.totalComentarios > 0 && !ocultas[String(p.id)]">
              <div v-for="(c, i) in comentariosDe(p)" :key="i" class="reply">
                <span class="num" style="color: var(--color-accent-2);">{{ c.iniciales }}</span>
                <div>
                  <p style="font-size: var(--text-sm); margin: 0;"><strong>{{ c.autor }}</strong></p>
                  <p style="font-size: var(--text-sm); color: var(--color-ink-2); margin: 0;">{{ c.texto }}</p>
                </div>
              </div>
            </div>
            <div class="acciones">
              <button class="thread-link" type="button" @click="compartir(p)">Compartir</button>
            </div>
          </div>
        </div>
      </article>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'

// F1: el feed deja de leer el simulador directo y pasa por la capa de servicios
// (dual-mode: demo en pruebas, backends reales en modo api).
import {
  crearPost,
  getComunidades,
  getFeedPosts,
  votarPost
} from '@/services/feed'
import { useToast } from '@/composables/useToast'

const filtros = [
  { key: 'todas', label: 'Todas' },
  { key: 'comunidades', label: 'Comunidades' },
  { key: 'mesas', label: 'Mis mesas' }
]

const titulo = ref('')
const cuerpo = ref('')
const comunidadNueva = ref('')
const errorPublicar = ref(null)
const { isAuthenticated } = useAuth()

const comunidades = ref([])
const tabActiva = ref('todas')
const comunidadActiva = ref(null)
const cargandoComunidades = ref(true)
const cargando = ref(true)
const errorCarga = ref(null)
const ocultas = ref({})

function elegir(id) {
  const previo = comunidadActiva.value
  if (id === 'comunidades-tab') return
  comunidadActiva.value = id ? (comunidadActiva.value === id ? null : id) : id
  if (comunidadActiva.value) tabActiva.value = 'comunidades'
  else tabActiva.value = previo ? 'comunidades' : 'todas'
  cargar()
}

function elegirTab(key) {
  tabActiva.value = key
  if (key !== 'comunidades') comunidadActiva.value = null
  cargar()
}

const postsFiltrados = ref([])

async function cargar() {
  cargando.value = true
  errorCarga.value = null
  try {
    if (comunidadActiva.value && tabActiva.value === 'comunidades') {
      postsFiltrados.value = await getFeedPosts({ orden: 'recientes', comunidad: String(comunidadActiva.value).slice(2) })
    } else if (tabActiva.value === 'comunidades') {
      const todas = await getFeedPosts({ orden: 'hot' })
      postsFiltrados.value = todas.filter((p) => !p.soloMesa && !p.mesaId)
    } else if (tabActiva.value === 'mesas') {
      postsFiltrados.value = await getFeedPosts({ orden: 'recientes', soloMesas: true })
    } else {
      postsFiltrados.value = await getFeedPosts({ orden: 'hot' })
    }
    postsFiltrados.value = postsFiltrados.value
  } catch (e) {
    errorCarga.value = e?.mensaje || e?.message || 'Falló la carga'
  } finally {
    cargando.value = false
  }
}

async function cargarComunidades() {
  cargandoComunidades.value = true
  try {
    comunidades.value = await getComunidades()
  } catch {
    comunidades.value = []
  } finally {
    cargandoComunidades.value = false
  }
}

function relativo(p) {
  const horas = Number(p.horas ?? 0)
  if (horas <= 0) return 'un rato'
  if (horas < 24) return `${horas} h`
  return `${Math.round(horas / 24)} d`
}

async function votar(p, dir) {
  try {
    const actualizado = await votarPost(p.id, dir)
    const idx = postsFiltrados.value.findIndex((x) => String(x.id) === String(p.id))
    if (idx >= 0) postsFiltrados.value[idx] = { ...postsFiltrados.value[idx], ...actualizado }
  } catch (e) {
    useToast().toast(e.mensaje || e.message || 'No se pudo votar.', 'error')
  }
}

function comentariosDe(p) {
  return Array.isArray(p.comentarios) ? p.comentarios : []
}

function toggleComentarios(p) {
  ocultas.value = { ...ocultas.value, [String(p.id)]: !ocultas.value[String(p.id)] }
}

async function compartir(p) {
  try {
    const enlace = `${location.origin}/feed#${p.id}`
    if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(enlace)
    useToast().toast('Enlace copiado.', 'success')
  } catch {
    useToast().toast('No se pudo copiar el enlace.', 'error')
  }
}

async function publicar() {
  errorPublicar.value = null
  const t = titulo.value.trim()
  const c = cuerpo.value.trim()
  if (!t || !c) {
    errorPublicar.value = 'El contenido de la publicación no puede estar vacío.'
    return
  }
  if (t.length > 200) {
    errorPublicar.value = 'El título no puede superar los 200 caracteres.'
    return
  }
  if (c.length > 5000) {
    errorPublicar.value = 'El cuerpo no puede superar los 5000 caracteres.'
    return
  }
  const comunidad = comunidadActiva.value || (comunidadNueva.value.trim() ? `t/${comunidadNueva.value.trim()}` : null)
  try {
    await crearPost({
      titulo: titulo.value,
      cuerpo: cuerpo.value,
      comunidad: comunidad ? String(comunidad).replace(/^t\//, '') : undefined
    })
    titulo.value = ''
    cuerpo.value = ''
    if (comunidadActiva.value) {
      await Promise.all([cargar(), cargarComunidades()])
    } else {
      await cargar()
    }
    useToast().toast(comunidad ? `Publicado en ${comunidad}.` : 'Publicado en el feed general.', 'success')
  } catch (e) {
    errorPublicar.value = e.mensaje || e.message || 'No se pudo publicar.'
  }
}

onMounted(async () => {
  await Promise.all([cargar(), cargarComunidades()])
})

</script>

<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: 240px minmax(0, 1fr); gap: var(--space-lg); align-items: start; }
.sidebar .well { padding: var(--space-md); margin-bottom: var(--space-md); }
.sidebar .side-item { display: flex; align-items: center; gap: var(--space-2xs); padding: var(--space-2xs) var(--space-sm); border-radius: var(--radius-card); font-size: var(--text-sm); font-weight: 700; color: var(--color-ink-2); text-decoration: none; }
.side-item.side-link { background: none; border: 0; width: 100%; text-align: left; cursor: pointer; }
.side-item.side-link:hover { background: var(--color-paper-3); }
.side-item.side-link[aria-pressed="true"] { background: var(--color-accent); color: var(--color-accent-ink); }
.side-item.side-soft { color: var(--color-muted); font-weight: 400; }
.feed-tabs { display: flex; gap: var(--space-2xs); align-items: center; margin-bottom: var(--space-md); flex-wrap: wrap; }
.feed-tabs button { min-height: 36px; background: none; border: var(--rule-bar) solid transparent; border-radius: var(--radius-card); padding: var(--space-2xs) var(--space-md); font: 700 var(--text-sm) var(--font-body); color: var(--color-muted); cursor: pointer; }
.feed-tabs button[aria-selected="true"] { color: var(--color-ink); border-color: var(--color-rule); background: var(--color-paper-2); }
.feed-tabs .spacer { flex: 1; }
.composer { padding: var(--space-md); margin-bottom: var(--space-md); display: grid; gap: var(--space-sm); }
.post { margin-bottom: var(--space-md); }
.post .acciones { display: flex; gap: var(--space-md); font-size: var(--text-sm); color: var(--color-muted); margin-top: var(--space-sm); }
.thread-toggle, .thread-link { background: none; border: 0; cursor: pointer; color: var(--color-muted); font-size: var(--text-sm); padding: 0; }
.thread-toggle:hover, .thread-link:hover { color: var(--color-ink); }
.thread { display: grid; gap: var(--space-sm); margin-top: var(--space-sm); }
.thread .reply { display: grid; grid-template-columns: 40px minmax(0, 1fr); gap: var(--space-sm); }
@media (max-width: 60rem) { .app-grid { grid-template-columns: minmax(0, 1fr); padding-top: 120px; } .sidebar { display: none; } }
</style>
