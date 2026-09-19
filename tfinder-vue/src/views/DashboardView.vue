<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMembresias } from '@/services/membresias'
import { getActividad } from '@/services/actividad'
import { getEventosProximos } from '@/services/eventos'
import { getFeedPosts } from '@/services/feed'
import { useNotifications } from '@/composables/useNotifications'

const router = useRouter()
const { unreadCount, loadCount } = useNotifications()

const membresias = ref([])
const actividad = ref([])
const eventos = ref([])
const posts = ref([])
const isLoading = ref(true)
const error = ref(null)

async function load() {
  isLoading.value = true
  error.value = null
  try {
    const [m, a, e, p] = await Promise.all([
      getMembresias(),
      getActividad(),
      getEventosProximos(),
      getFeedPosts()
    ])
    membresias.value = m
    actividad.value = a
    eventos.value = e
    posts.value = p
    loadCount()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Ocurrió un error inesperado.'
  } finally {
    isLoading.value = false
  }
}

const activas = computed(() => membresias.value.filter((m) => m.estado !== 'Cerrada').length)
const sesionesProximas = computed(() => eventos.value.filter((e) => e.tipo.startsWith('Sesión')).length)

const colorEstado = (estado) => {
  if (estado === 'Abierta') return 'bg-[#6B8E23] text-[#FDF8EE]'
  if (estado === 'Cerrada') return 'bg-[#8B1A1A] text-[#FDF8EE]'
  return 'bg-[#8B7D6B] text-[#FDF8EE]'
}

const destinoMesa = (m) => (m.rol === 'gm' ? `/mesas/${m.id}/gestion` : `/mesas/${m.id}`)

const iconoActividad = (tipo) => {
  const svgs = {
    diario: `<path d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" stroke-linecap="round" stroke-linejoin="round"></path>`,
    espadas: `<path d="M3.75 13.5l10.5-10.5m0 0L17.25 6m-3-3l3 3M6.75 16.5l-3 3m0 0l3-3m-3 3h3m7.5-10.5l6 6m0 0l-3 3m3-3l-3-3" stroke-linecap="round" stroke-linejoin="round"></path>`,
    foro: `<path d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.502 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" stroke-linecap="round" stroke-linejoin="round"></path>`,
    estrella: `<path d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" stroke-linecap="round" stroke-linejoin="round"></path>`,
    reloj: `<path d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"></path>`
  }
  return svgs[tipo] ?? svgs.reloj
}

onMounted(() => load())
</script>

<template>
  <main class="flex-grow max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8" aria-label="Dashboard personal">
    <div class="bg-[#FDF8EE]/95 border-2 border-[#C2A980] shadow-2xl rounded-sm flex flex-col lg:flex-row overflow-hidden">
      <div v-if="isLoading" class="w-full p-12 flex flex-col items-center gap-4" role="status" aria-live="polite">
        <div class="animate-pulse space-y-3 w-full max-w-md">
          <div class="h-4 bg-[#C2A980]/40 rounded w-2/3"></div>
          <div class="h-2.5 bg-[#C2A980]/25 rounded w-full"></div>
          <div class="h-2.5 bg-[#C2A980]/25 rounded w-full"></div>
          <div class="h-2.5 bg-[#C2A980]/25 rounded w-1/2"></div>
        </div>
        <p class="font-tarzana text-xs uppercase tracking-widest text-[#8B7D6B]">Abriendo el Códex...</p>
      </div>

      <div v-else-if="error" class="w-full p-12 text-center" role="alert">
        <p class="font-tarzana uppercase tracking-widest text-xs text-[#8B1A1A] font-bold mb-1">Error al cargar el dashboard</p>
        <p class="font-minion text-[#5A4A3A]">{{ error }}</p>
        <button type="button" class="btn-gold mt-4 px-6 py-2 font-tarzana font-bold uppercase tracking-wider text-sm" @click="load">Reintentar</button>
      </div>

      <template v-else>
        <!-- COLUMNA IZQUIERDA (70%) -->
        <section class="w-full lg:w-[70%] p-6 sm:p-8 flex flex-col space-y-8">
          <!-- Stat Summary -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3" aria-label="Resumen rápido">
            <div class="bg-[#1A1A1A] border border-[#B8860B] rounded-sm px-4 py-3 text-center">
              <p class="font-tarzana text-[0.68rem] uppercase tracking-widest text-[#B8860B]">Campañas activas</p>
              <p class="font-mason text-2xl font-bold text-[#D4AF37] mt-1">{{ activas }}</p>
            </div>
            <div class="bg-[#1A1A1A] border border-[#B8860B] rounded-sm px-4 py-3 text-center">
              <p class="font-tarzana text-[0.68rem] uppercase tracking-widest text-[#B8860B]">Sesiones próximas</p>
              <p class="font-mason text-2xl font-bold text-[#D4AF37] mt-1">{{ sesionesProximas }}</p>
            </div>
            <div class="bg-[#1A1A1A] border border-[#B8860B] rounded-sm px-4 py-3 text-center">
              <p class="font-tarzana text-[0.68rem] uppercase tracking-widest text-[#B8860B]">Notificaciones</p>
              <p class="font-mason text-2xl font-bold text-[#D4AF37] mt-1">{{ unreadCount }}</p>
            </div>
          </div>

          <!-- Mis Mesas -->
          <article aria-label="Mis mesas">
            <div class="flex items-center justify-between pb-2 border-b border-[#C2A980] mb-4">
              <h2 class="font-mason text-xl font-bold text-[#8B5A2B] tracking-wide flex items-center gap-2">
                <span class="text-[#8B5A2B] text-xs">◆</span> Mis Mesas
              </h2>
              <span class="font-tarzana text-xs text-[#8B7D6B] uppercase tracking-wider">
                {{ membresias.length }} {{ membresias.length === 1 ? 'Campaña activa' : 'Campañas activas' }}
              </span>
            </div>

            <div class="space-y-2.5">
              <RouterLink
                v-for="m in membresias"
                :key="m.mesaId"
                :to="destinoMesa(m)"
                class="h-auto sm:h-[72px] bg-[#FDF8EE] border border-[#C2A980] border-l-4 border-l-[#D4AF37] shadow-sm px-4 py-3 rounded-r-sm flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-stone-50 transition-colors"
              >
                <div class="space-y-1 min-w-0">
                  <div class="flex flex-wrap items-center gap-2">
                    <h3 class="font-mason text-base font-bold text-[#8B5A2B] hover:underline truncate">{{ m.nombre }}</h3>
                    <span class="font-tarzana text-[0.7rem] bg-[#1A1A1A] text-[#FDF8EE] px-2 py-0.5 rounded leading-none">{{ m.sistema }}</span>
                    <span class="font-tarzana text-[0.7rem] px-2 py-0.5 rounded leading-none" :class="colorEstado(m.estado)">{{ m.estado }}</span>
                  </div>
                  <p class="font-minion italic text-[0.85rem] text-[#1A1A1A] truncate">
                    Rol:
                    <span class="font-semibold not-italic">{{ m.rol === 'gm' ? 'Director de Juego (GM)' : `Jugador (${m.personaje})` }}</span>
                  </p>
                </div>
                <span class="inline-flex items-center font-minion font-bold text-sm text-[#8B5A2B] hover:text-[#5c3b1c] self-end sm:self-center shrink-0">
                  Entrar <span class="ml-1 text-base leading-none">→</span>
                </span>
              </RouterLink>
            </div>
          </article>

          <!-- Actividad Reciente -->
          <article aria-label="Actividad reciente">
            <div class="flex items-center justify-between pb-2 border-b border-[#C2A980] mb-3">
              <h2 class="font-mason text-xl font-bold text-[#8B5A2B] tracking-wide flex items-center gap-2">
                <span class="text-[#8B5A2B] text-xs">◆</span> Actividad Reciente
              </h2>
              <span class="font-tarzana text-xs text-[#8B7D6B] uppercase tracking-wider">Actualizaciones de Campaña</span>
            </div>

            <div class="bg-[#FDF8EE] border border-[#C2A980] p-4 sm:p-5 rounded shadow-sm relative divide-y divide-[#B8A68B]/40">
              <div v-for="item in actividad" :key="item.id" class="py-3 flex items-start space-x-3.5 first:pt-1">
                <div class="p-1.5 bg-[#E8DCC8] rounded text-[#8B5A2B] shrink-0 border border-[#B8A68B]/40 mt-0.5">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true" v-html="iconoActividad(item.icono)"></svg>
                </div>
                <div class="flex-grow flex flex-col sm:flex-row sm:items-baseline sm:justify-between gap-1 min-w-0">
                  <p class="font-minion text-[0.95rem] text-[#1A1A1A] leading-snug">
                    <span v-if="item.fuerte" class="font-bold text-[#8B5A2B]">{{ item.fuerte }}</span>
                    {{ item.cuerpo }}
                    <span v-if="item.citado" class="italic text-stone-700">"{{ item.citado }}"</span>
                  </p>
                  <span class="font-tarzana text-[0.72rem] text-[#8B7D6B] shrink-0 whitespace-nowrap">{{ item.tiempo }}</span>
                </div>
              </div>
            </div>
          </article>

          <!-- Próximos Eventos -->
          <article aria-label="Próximos eventos">
            <div class="flex items-center justify-between pb-2 border-b border-[#C2A980] mb-3">
              <h2 class="font-mason text-xl font-bold text-[#8B5A2B] tracking-wide flex items-center gap-2">
                <span class="text-[#8B5A2B] text-xs">◆</span> Próximos Eventos
              </h2>
              <span class="font-tarzana text-xs text-[#8B7D6B] uppercase tracking-wider">Convocatorias y votaciones</span>
            </div>

            <div class="space-y-2.5">
              <div v-for="ev in eventos" :key="ev.id" class="bg-[#FDF8EE]/80 border border-[#C2A980] rounded-sm px-4 py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div class="flex items-center gap-3 min-w-0">
                  <span
                    class="font-tarzana text-[0.7rem] uppercase tracking-wide font-bold px-2 py-1 rounded shrink-0 text-[#FDF8EE]"
                    :class="ev.tipo.startsWith('Sesión') ? 'bg-[#6B8E23]' : 'bg-[#8B1A1A]'"
                  >
                    {{ ev.tipo }}
                  </span>
                  <div class="min-w-0">
                    <p class="font-mason font-bold text-[#8B5A2B]">{{ ev.titulo }}</p>
                    <p class="font-tarzana text-xs text-[#8B7D6B] truncate">{{ ev.mesaNombre }} · {{ ev.nota }}</p>
                  </div>
                </div>
                <RouterLink :to="`/mesas/${ev.mesaId}`" class="font-tarzana text-xs font-bold uppercase tracking-wider text-[#8B5A2B] hover:underline shrink-0">
                  Ver mesa →
                </RouterLink>
              </div>
            </div>
          </article>
        </section>

        <!-- COLUMNA DERECHA (30%) -->
        <aside class="w-full lg:w-[30%] bg-[#E8DCC8]/80 border-t lg:border-t-0 lg:border-l border-[#B8A68B] p-6 sm:p-7 flex flex-col justify-between" aria-label="Feed rápido">
          <div class="space-y-6">
            <div class="flex items-center space-x-2 pb-2 border-b border-[#B8A68B]">
              <span class="text-[#D4AF37] text-xs">❖</span>
              <h2 class="font-mason text-base font-bold text-[#8B5A2B] tracking-wide uppercase">Feed Rápido</h2>
            </div>

            <div class="space-y-5">
              <div v-for="post in posts" :key="post.id" class="space-y-2">
                <div class="flex items-center justify-between">
                  <div class="flex items-center space-x-2">
                    <div
                      class="w-6 h-6 rounded-full border border-[#8B5A2B] flex items-center justify-center text-[10px] font-mason font-bold"
                      :style="{ backgroundColor: post.avatarBg, color: post.avatarText }"
                    >
                      {{ post.iniciales }}
                    </div>
                    <span class="font-minion font-bold text-[0.9rem] text-[#1A1A1A]">{{ post.autor }}</span>
                  </div>
                  <span class="font-tarzana text-[0.7rem] text-[#8B7D6B]">{{ post.tiempo }}</span>
                </div>
                <p class="font-minion text-[0.82rem] text-[#1A1A1A] leading-snug line-clamp-2 italic">"{{ post.resumen }}"</p>
                <RouterLink to="/feed" class="inline-block font-minion font-semibold text-[0.78rem] text-[#8B5A2B] hover:underline">
                  Leer más en Feed →
                </RouterLink>
              </div>
            </div>

            <div class="mt-6 pt-5 border-t border-[#B8A68B] space-y-3">
              <span class="font-tarzana text-[0.75rem] text-[#8B7D6B] uppercase tracking-widest block font-semibold">Grimorio de Personajes</span>
              <div class="p-3 bg-[#FDF8EE]/80 border border-[#C2A980] rounded text-center">
                <p class="font-minion text-xs text-stone-700 mb-2">
                  Exporta y sincroniza tus fichas bajo licencia OGL v1.0a Paizo con un clic.
                </p>
                <RouterLink
                  to="/builds/nuevo"
                  class="block w-full py-1.5 px-3 bg-gradient-to-b from-[#8B5A2B] to-[#6d441e] hover:from-[#9c6632] hover:to-[#7d4e23] text-[#FDF8EE] font-minion text-xs font-semibold rounded border border-[#5a3818] shadow-sm transition-colors"
                >
                  Crear Ficha / Build OGL
                </RouterLink>
              </div>
            </div>

            <div class="mt-6 pt-5 border-t border-[#B8A68B] space-y-3">
              <span class="font-tarzana text-[0.75rem] text-[#8B7D6B] uppercase tracking-widest block font-semibold">Matchmaking</span>
              <div class="p-3 bg-[#FDF8EE]/80 border border-[#C2A980] rounded text-center">
                <p class="font-minion text-xs text-stone-700 mb-2">
                  Encontrá compañeros de aventura según estilo de juego, disponibilidad y tono de crónica.
                </p>
                <RouterLink
                  to="/matchmaking"
                  class="block w-full py-1.5 px-3 bg-gradient-to-b from-[#D4AF37] to-[#B8860B] hover:from-[#e0bd48] hover:to-[#c99208] text-[#1A1A1A] font-minion text-xs font-bold rounded border border-[#8a6a10] shadow-sm transition-colors"
                >
                  Buscar Aventureros Afines
                </RouterLink>
              </div>
            </div>
          </div>

          <div class="mt-8 pt-4 border-t border-[#B8A68B]/60 text-center">
            <p class="font-mason text-[0.68rem] text-stone-600 tracking-wider uppercase">Sistema D20 • Pathfinder RPG 1e</p>
          </div>
        </aside>
      </template>
    </div>

    <!-- FAB: Crear nueva mesa -->
    <button
      type="button"
      aria-label="Crear nueva mesa"
      class="fixed bottom-8 right-8 z-50 group w-14 h-14 rounded-full bg-gradient-to-b from-[#D4AF37] to-[#B8860B] border-2 border-[#FFE885] shadow-[0_4px_16px_rgba(0,0,0,0.4),inset_0_1px_1px_rgba(255,255,255,0.6)] flex items-center justify-center text-[#1A1A1A] hover:scale-105 transition-all cursor-pointer"
      title="Crear nueva mesa"
      @click="router.push('/mesas/nueva')"
    >
      <span class="font-mason font-extrabold text-3xl leading-none select-none pb-0.5 group-hover:rotate-90 transition-transform duration-200">+</span>
    </button>
  </main>
</template>