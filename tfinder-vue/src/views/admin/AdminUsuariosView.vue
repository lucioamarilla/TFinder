<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAdminUsuarios, suspenderUsuario, activarUsuario } from '@/services/admin.js'
import { useToast } from '@/composables/useToast'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'

const toast = useToast()

const stats = ref([])
const usuarios = ref([])
const busqueda = ref('')
const filtro = ref('todos')
const cargando = ref(true)
const fallo = ref(null)
const enAccion = ref(null)

const filtros = computed(() => [
  { id: 'todos', label: 'Todos', conteo: stats.value.find((s) => s.label === 'Total Cuentas')?.valor ?? 0 },
  { id: 'activo', label: 'Activos', conteo: stats.value.find((s) => s.label === 'Activos')?.valor ?? 0 },
  { id: 'suspendido', label: 'Suspendidos', conteo: stats.value.find((s) => s.label === 'Suspendidos')?.valor ?? 0 }
])

const visibles = computed(() => {
  const termino = busqueda.value.trim().toLowerCase()
  return usuarios.value.filter((u) => {
    const porEstado = filtro.value === 'todos' || u.estado === filtro.value
    const porTexto = !termino || `${u.nombre} ${u.handle} ${u.email} ${u.rol}`.toLowerCase().includes(termino)
    return porEstado && porTexto
  })
})

const tonoStat = {
  tinta: 'text-[#1A1A1A]',
  verde: 'text-[#6B8E23]',
  rojo: 'text-[#8B1A1A]'
}

async function cargar() {
  cargando.value = true
  fallo.value = null
  try {
    const data = await getAdminUsuarios()
    stats.value = data.stats
    usuarios.value = data.usuarios
  } catch (e) {
    fallo.value = e.message || 'El padrón del gremio no respondió.'
  } finally {
    cargando.value = false
  }
}

function reemplazar(actualizada) {
  const i = usuarios.value.findIndex((u) => u.id === actualizada.id)
  if (i >= 0) usuarios.value.splice(i, 1, actualizada)
}

async function alternar(usuario) {
  enAccion.value = usuario.id
  try {
    if (usuario.estado === 'activo') {
      reemplazar(await suspenderUsuario(usuario.id))
      toast.ok('Usuario suspendido temporalmente.')
    } else {
      reemplazar(await activarUsuario(usuario.id))
      toast.ok('Usuario reactivado.')
    }
  } catch (e) {
    toast.error(e.message)
  } finally {
    enAccion.value = null
  }
}

onMounted(cargar)
</script>

<template>
  <main class="flex-grow max-w-7xl w-full mx-auto px-6 py-10">
    <nav class="flex items-center justify-between gap-2 text-[11px] font-tarzana font-semibold tracking-wider uppercase mb-4" aria-label="Migas de pan">
      <div class="flex items-center gap-2 text-[#8B7D6B]">
        <RouterLink to="/dashboard" class="hover:text-[#8B5A2B]">Inicio</RouterLink>
        <span>/</span>
        <span>Administración</span>
        <span>/</span>
        <span class="text-[#D4AF37]">Panel de Usuarios</span>
      </div>
      <div class="hidden sm:flex items-center gap-3 text-[10px]">
        <span class="inline-flex items-center gap-1.5 text-[#6B8E23] font-bold">
          <span class="w-1.5 h-1.5 rounded-full bg-[#6B8E23]" aria-hidden="true"></span>
          Padrón del gremio: 1,482 aventureros
        </span>
        <span class="text-[#8B7D6B]">Registro de edición OGL v1.0a</span>
      </div>
    </nav>

    <header class="mb-6">
      <h1 class="font-mason text-3xl font-bold text-[#8B5A2B] tracking-wide">✦ Usuarios ✦</h1>
      <p class="font-minion italic text-[#8B7D6B] mt-1">
        Registro de aventureros, directores de juego y guardianes juramentados de Golarion.
      </p>
    </header>

    <LoadingState v-if="cargando" message="Consultando el padrón del gremio…" />

    <ErrorState v-else-if="fallo" title="El padrón está sellado" :message="fallo" @retry="cargar" />

    <template v-else>
      <div class="grid sm:grid-cols-3 gap-4 mb-6">
        <div v-for="stat in stats" :key="stat.label" class="bg-[#FDF8EE]/90 border border-[#C2A980] rounded-sm px-4 py-3 text-center">
          <p class="font-tarzana text-[0.68rem] uppercase tracking-widest text-[#8B7D6B]">{{ stat.label }}</p>
          <p class="font-mason text-2xl font-bold mt-1" :class="tonoStat[stat.tono]">
            {{ stat.valor.toLocaleString('es-AR') }}
          </p>
        </div>
      </div>

      <div class="bg-[#FDF8EE]/90 border border-[#C2A980] rounded-sm p-4 mb-4 flex flex-col lg:flex-row lg:items-center gap-3">
        <div class="relative flex-grow">
          <label for="admin-busqueda" class="sr-only">Buscar aventurero</label>
          <svg class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#8B7D6B]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" stroke-linecap="round" />
          </svg>
          <input
            id="admin-busqueda"
            v-model="busqueda"
            type="text"
            placeholder="Buscar por nombre, pseudónimo o correo de aventurero..."
            class="w-full py-2 pl-9 pr-3 rounded-sm bg-[#F8F2E4] border border-[#C2A980] font-minion text-sm text-[#1A1A1A] focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/60"
          />
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <span class="font-tarzana text-xs uppercase tracking-wider text-[#8B7D6B]">Filtrar:</span>
          <button
            v-for="opcion in filtros"
            :key="opcion.id"
            type="button"
            class="min-h-[44px] px-3 py-1.5 rounded-sm border font-tarzana text-xs font-semibold transition-colors"
            :class="filtro === opcion.id
              ? 'bg-[#EAD9B8] border-[#8B5A2B] text-[#8B5A2B]'
              : 'bg-[#FDF8EE] border-[#C2A980] text-[#8B7D6B] hover:border-[#8B5A2B] hover:text-[#8B5A2B]'"
            @click="filtro = opcion.id"
          >
            {{ opcion.label }} ({{ opcion.conteo.toLocaleString('es-AR') }})
          </button>
        </div>
      </div>

      <div class="bg-[#FDF8EE]/95 border-2 border-[#C2A980] shadow-xl rounded-sm overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full font-minion text-sm">
            <thead class="bg-[#F4EAD6]">
              <tr class="text-left font-tarzana uppercase tracking-wider text-xs text-[#1A1A1A] border-b border-[#C2A980]">
                <th scope="col" class="px-4 py-3 w-[30%]">Nombre</th>
                <th scope="col" class="px-4 py-3 w-[28%]">Email</th>
                <th scope="col" class="px-4 py-3 w-[18%]">Fecha</th>
                <th scope="col" class="px-4 py-3 w-[12%]">Estado</th>
                <th scope="col" class="px-4 py-3 w-[12%] text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="usuario in visibles"
                :key="usuario.id"
                class="border-b border-[#C2A980]/60 last:border-0 odd:bg-[#F4EAD6]/40"
              >
                <td class="px-4 py-3">
                  <div class="flex items-center gap-3">
                    <span
                      class="w-10 h-10 rounded-full border flex items-center justify-center font-mason font-bold shrink-0"
                      :class="usuario.estado === 'suspendido'
                        ? 'bg-[#F2E3E3] border-[#D9A5A5] text-[#8B1A1A]'
                        : 'bg-[#EDE1CB] border-[#C2A980] text-[#8B5A2B]'"
                    >{{ usuario.iniciales }}</span>
                    <div class="min-w-0">
                      <p class="font-tarzana font-bold text-[#1A1A1A] truncate">{{ usuario.nombre }}</p>
                      <p class="font-tarzana text-[11px] text-[#8B7D6B] truncate">{{ usuario.handle }} • {{ usuario.rol }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3 text-[#3A2E1F] break-all">{{ usuario.email }}</td>
                <td class="px-4 py-3 font-tarzana text-xs text-[#5C5346] whitespace-nowrap">{{ usuario.fecha }}</td>
                <td class="px-4 py-3">
                  <span
                    class="inline-flex items-center gap-1.5 font-tarzana text-[11px] font-bold uppercase px-2.5 py-1 rounded-full border"
                    :class="usuario.estado === 'activo'
                      ? 'text-[#6B8E23] border-[#6B8E23] bg-[#6B8E23]/10'
                      : 'text-[#8B1A1A] border-[#8B1A1A] bg-[#8B1A1A]/10'"
                  >
                    <span class="w-1.5 h-1.5 rounded-full" :class="usuario.estado === 'activo' ? 'bg-[#6B8E23]' : 'bg-[#8B1A1A]'" aria-hidden="true"></span>
                    {{ usuario.estado === 'activo' ? 'Activo' : 'Suspendido' }}
                  </span>
                </td>
                <td class="px-4 py-3 text-right">
                  <button
                    type="button"
                    class="min-h-[44px] px-3 py-1.5 rounded-sm border font-tarzana text-[11px] font-bold uppercase transition-colors disabled:opacity-60"
                    :class="usuario.estado === 'activo'
                      ? 'border-[#8B1A1A] text-[#8B1A1A] hover:bg-[#8B1A1A] hover:text-[#FDF8EE]'
                      : 'border-[#6B8E23] text-[#6B8E23] hover:bg-[#6B8E23] hover:text-[#FDF8EE]'"
                    :disabled="enAccion === usuario.id"
                    :title="usuario.estado === 'activo' ? 'Suspender acceso de cuenta' : 'Restaurar y habilitar cuenta'"
                    @click="alternar(usuario)"
                  >
                    {{ usuario.estado === 'activo' ? 'Suspender' : 'Activar' }}
                  </button>
                </td>
              </tr>
              <tr v-if="visibles.length === 0">
                <td colspan="5" class="px-4 py-10 text-center">
                  <p class="font-mason text-lg text-[#8B5A2B] font-bold">Ningún aventurero coincide</p>
                  <p class="font-minion text-sm text-[#8B7D6B] italic mt-1">Ajustá la búsqueda o el filtro del padrón.</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="bg-[#F4EAD6] border-t border-[#C2A980] px-4 py-3 flex flex-col sm:flex-row items-center justify-between gap-3">
          <span class="font-tarzana text-xs text-[#8B7D6B]">Mostrando 1 - {{ visibles.length }} de {{ usuarios.length }} aventureros cargados</span>
          <div class="flex items-center gap-1 font-tarzana text-xs">
            <button type="button" class="min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2 py-1 rounded-sm border border-[#C2A980] text-[#8B7D6B] opacity-50 cursor-not-allowed" disabled>« Anterior</button>
            <button type="button" class="min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2.5 py-1 rounded-sm bg-[#8B5A2B] text-[#FDF8EE] font-bold" @click="toast.info('Ya estás en la primera página del padrón.')">1</button>
            <button type="button" class="min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2.5 py-1 rounded-sm border border-[#C2A980] hover:border-[#8B5A2B] text-[#8B5A2B]" @click="toast.info('Página 2 del padrón (simulada).')">2</button>
            <button type="button" class="min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2.5 py-1 rounded-sm border border-[#C2A980] hover:border-[#8B5A2B] text-[#8B5A2B]" @click="toast.info('Página 3 del padrón (simulada).')">3</button>
            <span class="px-1 text-[#8B7D6B]">…</span>
            <button type="button" class="min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2.5 py-1 rounded-sm border border-[#C2A980] hover:border-[#8B5A2B] text-[#8B5A2B]" @click="toast.info('Última página del padrón (simulada).')">247</button>
            <button type="button" class="min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2 py-1 rounded-sm border border-[#C2A980] hover:border-[#8B5A2B] text-[#8B5A2B]" @click="toast.info('Página siguiente del padrón (simulada).')">Siguiente »</button>
          </div>
        </div>
      </div>

      <div class="mt-6 bg-[#FDF8EE]/80 border border-[#C2A980] rounded-sm p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <p class="font-minion text-sm text-[#5C5346]">
          <span class="text-[#8B5A2B] text-lg mr-1" aria-hidden="true">⚖</span>
          <b class="font-mason text-[#8B5A2B]">Códice del Alguacil:</b>
          La suspensión temporal o indefinida de una cuenta restringe la creación de mesas, publicación de crónicas y
          postulación de builds, preservando las licencias OGL v1.0a archivadas.
        </p>
        <RouterLink to="/admin/trazabilidad" class="shrink-0 font-tarzana text-xs font-bold uppercase tracking-wider text-[#8B5A2B] hover:underline">
          Ver registro de auditoría →
        </RouterLink>
      </div>
    </template>
  </main>
</template>
