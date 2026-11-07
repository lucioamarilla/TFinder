<template>
  <div class="app-grid">
    <template v-if="cargando">
      <main><p class="label">Cargando mesa…</p></main>
    </template>
    <template v-else-if="!mesa">
      <main>
        <article class="card" style="padding: var(--space-xl); text-align: center;">
          <h2>Mesa no encontrada</h2>
          <p style="font-size: var(--text-sm); color: var(--color-ink-2); margin-top: var(--space-sm);">La mesa que buscás no existe o fue eliminada por su directora.</p>
          <RouterLink class="btn btn--secondary" to="/mesas" style="margin-top: var(--space-md);">Ver las mesas abiertas</RouterLink>
        </article>
      </main>
    </template>
    <template v-else>
      <main>
        <article class="card">
          <div class="cover crt"><span class="figure-lg acid" style="font-size: 40px;">{{ mesa.nivel }}</span></div>
          <div style="padding: var(--space-md);">
            <div style="display: flex; gap: var(--space-2xs); flex-wrap: wrap; margin-bottom: var(--space-2xs);">
              <span class="tag tag--ink">PF1e, nivel {{ mesa.nivel }}</span>
              <span class="tag" :class="esMesaCerrada(mesa) ? 'tag--ember' : 'tag--acid'">{{ esMesaCerrada(mesa) ? 'Cerrada' : (mesaCompleta(mesa) ? 'Completa' : 'Abierta') }}</span>
              <span v-if="pendiente" class="tag tag--ink">Solicitud enviada</span>
              <span v-if="yaMiembro" class="tag tag--acid">Ya eres miembro</span>
              <span class="tag tag--ink">{{ mesa.horario }}</span>
            </div>
            <h2>{{ mesa.nombre }}</h2>
            <p class="lead" style="font-size: var(--text-md);">Dirigida por {{ mesa.gm }}, {{ mesa.ubicacion }}.</p>
            <p style="font-size: var(--text-sm); color: var(--color-ink-2); margin-top: var(--space-sm);">{{ mesa.descripcion }}</p>
            <div style="display: flex; align-items: center; gap: var(--space-md); margin-top: var(--space-md); flex-wrap: wrap;">
              <span class="seats" :aria-label="ocupacionDe(mesa) + ' de ' + ((cupoDe(mesa)) ?? '∞') + ' asientos'">
                <i v-for="i in ocupacionDe(mesa)" :key="'on' + i"></i>
                <i v-for="i in Math.max(0, ((cupoDe(mesa)) ?? 0) - ocupacionDe(mesa))" :key="'off' + i" class="off"></i>
              </span>
              <span class="num" style="font-size: var(--text-sm);">{{ ocupacionDe(mesa) }}/{{ (cupoDe(mesa)) ?? '∞' }}</span>
              <button v-if="!esMaster && !yaMiembro" class="btn" :disabled="!puedoPedir" @click="unirse">Solicitar unión</button>
              <RouterLink class="btn btn--secondary" :to="`/mesas/${id}/calendario`">Calendario y votación</RouterLink>
              <RouterLink class="btn btn--secondary" :to="`/mesas/${id}/sesion/jugador`">Bitácora de sesiones</RouterLink>

            </div>
            <p v-if="mensaje" class="label" style="margin-top: var(--space-sm);">{{ mensaje }}</p>
          </div>
        </article>

        <div class="tabs" role="tablist" style="margin-top: var(--space-lg);">
          <button v-for="t in tabs" :key="t.key" role="tab" :aria-selected="tab === t.key" @click="tab = t.key">{{ t.label }}</button>
        </div>

        <div v-if="tab === 'personajes'" class="panel card">
          <h3>Personajes de la mesa</h3>
          <div v-if="miembros.length === 0" class="label">Sin miembros aún.</div>
          <div v-for="m in miembros" :key="m.id" class="miembro">
            <span class="av">{{ iniciales(m.nombre || m.email) }}</span>
            <span><strong>{{ m.nombre || m.email }}</strong> · {{ m.rol === 'master' || m.rol === 'Master' ? 'Master' : 'Jugador' }}</span>
          </div>
        </div>
      </main>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { getMesa, esMesaAbierta, esMesaCerrada, cupoDe, ocupacionDe } from '@/services/mesas'
import { getMiembros } from '@/services/jugadores'
import { mesasApi } from '@/api/endpoints'

const route = useRoute()
const router = useRouter()
const { user, isAuthenticated } = useAuth()

const id = route.params.id
const mesa = ref(null)
const cargando = ref(true)
const mensaje = ref('')
const miembros = ref([])
const tab = ref('resumen')
const tabs = [{ key: 'resumen', label: 'Resumen' }, { key: 'personajes', label: 'Personajes' }]

function iniciales(n) { return (n || '').trim().split(/\s+/).map((p) => p[0]).slice(0, 2).join('').toUpperCase() || 'AV' }
// D-09/D-10: helpers únicos de estado y cupo (/services/mesas).
function mesaCompleta(m) { return cupoDe(m) != null && ocupacionDe(m) >= cupoDe(m) }

const pendiente = ref(false)
const yaMiembro = ref(false)

const esMaster = computed(() => !!mesa.value && !!user.value && Number(mesa.value.gmId) === Number(user.value?.id ?? user.value?.sub))
const puedoPedir = computed(() => isAuthenticated.value && mesa.value && !esMaster.value && !yaMiembro.value && esMesaAbierta(mesa.value) && !mesaCompleta(mesa.value))

onMounted(async () => {
  // D-01: la mesa define la existencia; los datos protegidos (miembros) no
  // pueden anularla. Un invitado o no-miembro ve la ficha con la pestaña vacía.
  try {
    mesa.value = await getMesa(id)
  } catch (e) {
    mesa.value = null
    cargando.value = false
    return
  }
  try {
    const data = await getMiembros(mesa.value.id)
    miembros.value = data?.miembros ?? []
    // detectar membresía actual
    if (isAuthenticated.value) {
      yaMiembro.value = miembros.value.some((m) => String(m.id) === String(user.value?.id ?? user.value?.sub) || m.email === user.value?.email)
    }
  } catch {
    // 403 (no-miembro) o 401 (invitado): pestaña Personajes vacía, sin error.
    miembros.value = []
  } finally {
    cargando.value = false
  }
})

async function unirse() {
  if (!isAuthenticated.value) { router.push({ path: '/login', query: { redirect: `/mesas/${id}` } }); return }
  try {
    await mesasApi.solicitarUnion(id, {})
    pendiente.value = true
    mensaje.value = 'Solicitud enviada'
  } catch (e) {
    mensaje.value = e?.message || 'No se pudo enviar la solicitud.'
  }
}
</script>

<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-md); align-items: start; }
.cover { aspect-ratio: 16/9; background: var(--color-paper-3); border: var(--rule-hair) solid var(--color-rule); display: grid; place-items: center; margin-bottom: var(--space-2xs); }
.miembro { display: flex; align-items: center; gap: var(--space-sm); padding: var(--space-2xs) 0; }
.av { width: 34px; height: 34px; display: grid; place-items: center; background: var(--color-paper-3); border: var(--rule-hair) solid var(--color-rule); font-weight: 700; font-size: var(--text-xs); }
.tabs { display: flex; gap: var(--space-2xs); margin-bottom: var(--space-md); }
.tabs button { padding: var(--space-2xs) var(--space-md); border: var(--rule-hair) solid var(--color-rule); background: transparent; cursor: pointer; }
.panel { padding: var(--space-md); }
.seats { display: inline-flex; gap: 3px; }
.seats i { width: 10px; height: 10px; background: var(--color-accent-2); display: block; }
.seats i.off { background: var(--color-paper-3); border: var(--rule-hair) solid var(--color-rule); }
@media (max-width: 60rem) { .app-grid { padding-top: 120px; } }
</style>