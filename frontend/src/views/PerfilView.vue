<template>
  <div class="app-grid">
    <aside class="sidebar">
      <div class="well">
        <p class="label" style="margin-bottom: var(--space-2xs);">Tu cuenta</p>
        <RouterLink class="side-item" to="/mesas">Mis mesas</RouterLink>
        <RouterLink class="side-item" to="/builds">Mis builds</RouterLink>
        <RouterLink class="side-item" to="/notificaciones">Notificaciones</RouterLink>
      </div>
    </aside>

    <main>
      <article class="card" style="padding: var(--space-lg);">
        <div style="display: flex; align-items: center; gap: var(--space-md); flex-wrap: wrap;">
          <img
            :src="avatarUrl || '/assets/logo-tfinder.png'"
            alt="Avatar del usuario"
            width="96"
            height="96"
            style="border: var(--rule-bar) solid var(--color-rule); object-fit: cover;"
          />
          <div>
            <h2 style="margin: 0;">{{ nombre || 'Aventurero' }}</h2>
            <p class="label" style="margin-top: var(--space-3xs);">{{ email }}</p>
            <p class="label" style="margin-top: var(--space-3xs);">Rol de plataforma: {{ rol }}</p>
          </div>
        </div>

        <div class="field" style="margin-top: var(--space-md);">
          <label class="label" for="pv-nombre">Nombre visible</label>
          <input id="pv-nombre" class="input" v-model="nombre" type="text" />
        </div>
        <div class="field" style="margin-top: var(--space-sm);">
          <label class="label" for="pv-bio">Descripción</label>
          <textarea id="pv-bio" class="input" v-model="bio" rows="3" placeholder="Contá quién sos y qué jugás…"></textarea>
        </div>
        <div class="field" style="margin-top: var(--space-sm);">
          <label class="label" for="pv-avatar">Imagen de perfil</label>
          <input id="pv-avatar" type="file" accept="image/png,image/jpeg,image/webp" @change="onArchivo" />
          <p v-if="subiendo" class="label" style="margin-top: var(--space-3xs);">Subiendo…</p>
          <p v-if="error" class="hint-error" role="alert">{{ error }}</p>
        </div>
        <div style="display: flex; gap: var(--space-sm); margin-top: var(--space-md);">
          <button class="btn" :disabled="guardando" @click="guardar">Guardar perfil</button>
          <button class="btn btn--secondary" @click="cargar">Revertir</button>
        </div>
      </article>

      <article class="card" style="padding: var(--space-lg); margin-top: var(--space-md);">
        <h3 style="margin: 0 0 var(--space-2xs);">Actividad</h3>
        <p style="font-size: var(--text-sm); color: var(--color-ink-2);">
          Tus personajes se administran en <RouterLink class="text-link" to="/builds">Builds</RouterLink>.
          La ficha de personaje global fue retirada: cada personaje vive con su build.
        </p>
        <div v-if="misMesas.length > 0" data-test="perfil-mesas" style="margin-top: var(--space-md); display: grid; gap: var(--space-2xs);">
          <RouterLink v-for="m in misMesas" :key="m.id" class="side-item" :to="`/mesas/${m.id}`">
            {{ m.nombre }} · {{ m.miRol === 'master' ? 'Master' : 'Jugador' }}
          </RouterLink>
        </div>
        <p v-else class="label" style="margin-top: var(--space-2xs);">Aún no participás de ninguna mesa.</p>
      </article>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { verPerfil, editarPerfil } from '@/services/perfil'
import { subirImagen } from '@/services/uploads'
import { getMisMesas } from '@/services/mesas'
import { useToast } from '@/composables/useToast'

const email = ref('')
const nombre = ref('')
const bio = ref('')
const avatarUrl = ref(null)
const rol = ref('usuario')
const misMesas = ref([])
const subiendo = ref(false)
const guardando = ref(false)
const error = ref(null)
const { toast } = useToast()

async function cargar() {
  error.value = null
  try {
    const p = await verPerfil()
    email.value = p.email
    nombre.value = p.nombre
    bio.value = p.bio
    avatarUrl.value = p.avatarUrl
    rol.value = p.rol
    misMesas.value = await getMisMesas()
  } catch (e) {
    error.value = e.mensaje || e.message || 'No se pudo cargar el perfil.'
  }
}

async function onArchivo(event) {
  const archivo = event?.target?.files?.[0]
  if (!archivo) return
  subiendo.value = true
  error.value = null
  try {
    const subida = await subirImagen(archivo)
    avatarUrl.value = subida.url
    toast('Imagen subida. Guardá para aplicarla.', 'success')
  } catch (e) {
    error.value = e.mensaje || e.message || 'La imagen no pudo subirse.'
  } finally {
    subiendo.value = false
  }
}

async function guardar() {
  guardando.value = true
  error.value = null
  try {
    const p = await editarPerfil({ nombre: nombre.value, bio: bio.value, avatarUrl: avatarUrl.value })
    nombre.value = p.nombre
    bio.value = p.bio
    avatarUrl.value = p.avatarUrl
    toast('Perfil actualizado.', 'success')
  } catch (e) {
    error.value = e.mensaje || e.message || 'No se pudo actualizar el perfil.'
  } finally {
    guardando.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: 240px minmax(0, 1fr); gap: var(--space-lg); align-items: start; }
.sidebar .well { padding: var(--space-md); margin-bottom: var(--space-md); }
.sidebar .side-item { display: block; padding: var(--space-2xs) var(--space-sm); border-radius: var(--radius-card); font-size: var(--text-sm); font-weight: 700; color: var(--color-ink-2); text-decoration: none; }
.sidebar .side-item:hover { background: var(--color-paper-3); }
@media (max-width: 60rem) { .app-grid { grid-template-columns: minmax(0, 1fr); padding-top: 120px; } .sidebar { display: none; } }
</style>
