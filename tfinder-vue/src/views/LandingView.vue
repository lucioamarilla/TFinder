<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMesas } from '@/composables/useMesas'

const router = useRouter()
const { mesas, isLoading, error, retry } = useMesas()
const busqueda = ref('')

const herramientas = [
  {
    icono: 'description',
    titulo: 'Hoja de Personaje Interactiva',
    texto: 'Cálculo inmediato de salvaciones, BMC/DMC, penalizaciones por armadura y dotes encadenadas de PF1e.',
    pie: 'Reglas OGL'
  },
  {
    icono: 'menu_book',
    titulo: 'Diario de Campaña & Wiki',
    texto: 'Registra bitácoras de cada sesión, PNJ conocidos, tesoro acumulado e inventario colectivo del grupo.',
    pie: 'Crónicas Vivas'
  },
  {
    icono: 'calendar_month',
    titulo: 'Calendario y Votación',
    texto: 'Sincroniza horarios entre continentes mediante encuestas rápidas de disponibilidad y recordatorios.',
    pie: 'Sin Cancelaciones'
  },
  {
    icono: 'library_books',
    titulo: 'Dotes & Conjuros Indexados',
    texto: 'Biblioteca veloz para consultar tiempos de lanzamiento, componentes, resistencias a conjuros y requisitos.',
    pie: 'Consulta Inmediata'
  }
]

const pasos = [
  { numero: '01', titulo: 'Crea tu Cuenta', texto: 'Accede de forma totalmente gratuita y personaliza tu perfil de jugador o Master en minutos.', pie: 'Paso Inmediato' },
  { numero: '02', titulo: 'Diseña tu Personaje', texto: 'Constructor de builds con reglas oficiales, arquetipos, cálculo de atributos y equipo inicial.', pie: 'Gestor de Héroes' },
  { numero: '03', titulo: 'Únete a una Mesa', texto: 'Filtra por Adventure Paths oficiales, campañas caseras, horario semanal y nivel requerido.', pie: 'Encuentra tu Grupo' },
  { numero: '04', titulo: 'Vive la Crónica', texto: 'Juega tus sesiones y atesora el progreso de la partida en el diario histórico compartido.', pie: 'Inicia la Leyenda' }
]

const testimonios = [
  {
    inicial: 'M', fondo: 'bg-[#8B5A2B]', color: 'text-white',
    cita: '«Conseguir un grupo constante para la Senda de las Runas era casi imposible hasta que usamos las convocatorias de TFinder. La ficha interactiva ahorra horas de cálculo.»',
    nombre: 'Marcos E.', rol: 'Director de Juego • 6 años en PF1e'
  },
  {
    inicial: 'S', fondo: 'bg-[#1A1A1A]', color: 'text-[#D4AF37]',
    cita: '«La wiki integrada para registrar el diario de la campaña nos ha salvado la vida. Tras un año de partida en Ustalav, nadie olvida una sola pista ni aliada.»',
    nombre: 'Sara G.', rol: 'Paladín de Iomedae • Nivel 11'
  },
  {
    inicial: 'D', fondo: 'bg-[#556B2F]', color: 'text-white',
    cita: '«Poder reclutar reemplazos para bajas inesperadas con el filtro de nivel y horario exacto mantiene la mesa activa cada fin de semana sin interrupciones.»',
    nombre: 'Diego R.', rol: 'Master de Calaveras y Grilletes'
  }
]

const capacidades = [
  { icono: 'shield', titulo: 'Bestiario & Hojas PF1e', texto: 'Plantillas oficiales completas para PNJ y monstruos con desglose de CA de toque, desprevenido, RD y resistencias energéticas listas para el combate.' },
  { icono: 'auto_stories', titulo: 'Wiki de Campaña & Lore Compartido', texto: 'Crea entradas de conocimiento secreto para el Master o públicas para los aventureros. Adjunta retratos, mapas de mazmorras y pistas cruciales.' },
  { icono: 'wb_sunny', titulo: 'Calendario Solar de Absalom', texto: 'Registra el paso del tiempo en el cómputo de Golarion (Meses de Abadius, Pharast, Neth) y programa sesiones regulares sincronizadas con husos horarios reales.' },
  { icono: 'forum', titulo: 'Feed Social & Reputación', texto: 'Comunidad respetuosa respaldada por un sistema de karma, recomendaciones entre jugadores de rol y foros de debate táctico sobre arquetipos y reglas.' }
]

const guias = [
  { etiqueta: 'Iniciación Rápida', titulo: '¿Nuevo en Pathfinder 1e?', texto: 'Guía esencial sobre la creación de atributos, bonos de ataque base, tiradas de salvación y cómo funciona la economía de acciones en combate táctico.' },
  { etiqueta: 'Búsqueda Efectiva', titulo: 'Cómo Encontrar tu Primera Mesa', texto: 'Consejos para postular con una propuesta de personaje coherente, entender el contrato social de la mesa y acordar horarios con Directores de Juego.' },
  { etiqueta: 'Para Directores', titulo: 'Guía para Nuevos Game Masters', texto: 'Herramientas para calcular el Nivel de Desafío (CR), gestionar las sesiones cero y administrar el diario de campaña compartido sin esfuerzo.' }
]

function buscar(e) {
  e.preventDefault()
  router.push({ path: '/mesas', query: busqueda.value ? { q: busqueda.value } : {} })
}

onMounted(() => retry())

function estadoClase(mesa) {
  return mesa.estado === 'Abierta' ? 'text-[#556B2F]' : 'text-[#8B1A1A]'
}
</script>

<template>
  <div>
    <div class="parchment-vignette" aria-hidden="true"></div>
    <main class="relative z-10">
      <!-- HERO -->
      <section class="max-w-7xl mx-auto px-6 pt-12 pb-14 lg:pt-16 lg:pb-20">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          <div class="lg:col-span-7 flex flex-col items-start text-left">
            <div class="inline-flex items-center gap-2 px-3 py-1 bg-[#8B5A2B]/10 border border-[#8B5A2B]/30 rounded-full mb-4">
              <span class="text-[#8B1A1A] text-xs">❖</span>
              <span class="font-stat uppercase text-xs tracking-wider font-bold text-[#8B5A2B]">La plataforma definitiva de rol táctico</span>
            </div>
            <h1 class="font-mason text-[40px] sm:text-[50px] lg:text-[58px] leading-[1.12] font-bold hero-h1-relief tracking-wide max-w-2xl mb-5">
              Encuentra tu próxima aventura en Golarion
            </h1>
            <p class="font-narrative italic text-[20px] text-[#2B1D11] leading-relaxed max-w-xl mb-6">
              Conéctate con directores de juego y jugadores apasionados. Juega Pathfinder Primera Edición con herramientas creadas a medida para la gloria de tus campañas.
            </p>
            <ul class="space-y-2.5 mb-8 text-[#1A1A1A] font-narrative text-[17px]">
              <li class="flex items-center gap-3">
                <span class="text-[#8B5A2B] font-bold text-sm">✦</span>
                <span><strong>Fichas fieles a las reglas de PF1e</strong> con cálculo automático y dotes oficiales.</span>
              </li>
              <li class="flex items-center gap-3">
                <span class="text-[#8B5A2B] font-bold text-sm">✦</span>
                <span><strong>Gestión completa de campañas</strong>: crónicas de sesiones, diario de grupo y votación.</span>
              </li>
              <li class="flex items-center gap-3">
                <span class="text-[#8B5A2B] font-bold text-sm">✦</span>
                <span><strong>Comunidad abierta de Directores y Jugadores</strong>: sin descargas obligatorias ni costes.</span>
              </li>
            </ul>
            <div class="flex flex-wrap items-center gap-4 w-full sm:w-auto mb-6">
              <RouterLink class="btn-gold-relief px-8 py-3.5 rounded-[2px] font-stat font-bold text-[17px] text-[#1A1A1A] tracking-wider uppercase inline-flex items-center gap-2" to="/registro">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M20 21a8 8 0 0 0-16 0"/></svg>
                Únete gratis
              </RouterLink>
              <RouterLink class="btn-copper-outline px-7 py-3 rounded-[2px] font-stat font-bold text-[17px] tracking-wider uppercase inline-flex items-center gap-2" to="/mesas">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                Explorar Mesas
              </RouterLink>
            </div>
            <form class="w-full max-w-lg mt-2" @submit="buscar" role="search">
              <div class="relative flex items-center">
                <svg class="absolute left-3.5 text-[#8B5A2B] pointer-events-none text-xl" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input
                  v-model="busqueda"
                  class="parchment-input w-full pl-11 pr-4 py-2.5 font-narrative text-[15px] rounded-[2px] shadow-inner placeholder:text-[#8B7D6B] placeholder:italic"
                  placeholder="Buscar mesas por senda, GM o estilo (ej. Ustalav, Runelords)..."
                  type="text"
                />
              </div>
            </form>
          </div>

          <div class="lg:col-span-5 relative">
            <div class="card-vellum rounded-[3px] p-5 shadow-2xl border-2 border-[#8B5A2B] overflow-hidden">
              <div class="rune-spine"></div>
              <div class="rune-pattern"></div>
              <div class="pl-4 pb-3 border-b border-[#C2A980] flex items-center justify-between">
                <div>
                  <span class="font-stat uppercase text-[11px] text-[#8B7D6B] tracking-wider block font-semibold">Mesa Activa • Sesión 14</span>
                  <h4 class="font-mason font-bold text-[#8B5A2B] text-lg leading-tight">Cripta de los Lamentos</h4>
                </div>
                <span class="bg-[#8B1A1A] text-[#FDF8EE] font-stat font-bold text-xs px-2 py-0.5 rounded tracking-wide">EN COMBATE</span>
              </div>
              <div class="mt-3 relative h-44 rounded border border-[#C2A980] bg-[#eedec0] battlemap-grid overflow-hidden flex items-center justify-center">
                <div class="absolute inset-0 bg-gradient-to-t from-[#e0ca9c]/50 to-transparent pointer-events-none"></div>
                <div class="absolute top-8 left-12 flex flex-col items-center">
                  <div class="w-9 h-9 rounded-full bg-[#1A1A1A] border-2 border-[#D4AF37] flex items-center justify-center text-xs font-stat font-bold text-[#D4AF37] shadow-md">VAL</div>
                  <span class="font-stat text-[10px] text-[#1A1A1A] font-semibold mt-0.5">Valeros (G1)</span>
                </div>
                <div class="absolute bottom-6 right-16 flex flex-col items-center">
                  <div class="w-10 h-10 rounded-full bg-[#8B1A1A] border-2 border-[#D4AF37] flex items-center justify-center text-xs font-stat font-bold text-white shadow-md ring-2 ring-[#8B1A1A]/40">LICH</div>
                  <span class="font-stat text-[10px] text-[#8B1A1A] font-bold mt-0.5">Nigromante (CR 7)</span>
                </div>
                <div class="absolute top-14 right-28 flex flex-col items-center">
                  <div class="w-8 h-8 rounded-full bg-[#556B2F] border border-[#FDF8EE] flex items-center justify-center text-xs font-stat font-bold text-white shadow">EZR</div>
                  <span class="font-stat text-[10px] text-[#1A1A1A] font-medium mt-0.5">Ezren (Mago 7)</span>
                </div>
                <div class="absolute bottom-2 left-3 bg-[#1A1A1A]/85 text-[#FDF8EE] px-2 py-1 rounded text-[11px] font-stat tracking-wider flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-[#D4AF37] animate-pulse"></span>
                  Iniciativa: Turno 3 • Ronda 2
                </div>
              </div>
              <div class="mt-3 pl-4 pt-2 text-xs font-narrative">
                <div class="flex justify-between items-center text-[#8B5A2B] font-bold border-b border-[#C2A980]/50 pb-1">
                  <span class="font-stat text-sm uppercase">Valeros, Guerrero Humano Lvl 7</span>
                  <span class="font-stat text-[#1A1A1A]">PV: 68/74 • CA: 22</span>
                </div>
                <p class="text-[#5A4A3A] italic mt-1 line-clamp-1">
                  Ataque: Espada larga +1 (+13/+8 cuerpo a cuerpo, 1d8+7/19-20)
                </p>
                <div class="flex gap-2 mt-2 font-stat text-[11px]">
                  <span class="bg-[#1A1A1A]/10 text-[#1A1A1A] px-2 py-0.5 rounded">Fort +8</span>
                  <span class="bg-[#1A1A1A]/10 text-[#1A1A1A] px-2 py-0.5 rounded">Ref +5</span>
                  <span class="bg-[#1A1A1A]/10 text-[#1A1A1A] px-2 py-0.5 rounded">Vol +3</span>
                  <span class="ml-auto text-[#8B5A2B] font-bold">BMA: +7/+2</span>
                </div>
              </div>
            </div>
            <div class="absolute -bottom-3 -right-3 w-16 h-16 border-r-2 border-b-2 border-[#8B5A2B] opacity-60 pointer-events-none"></div>
            <div class="absolute -top-3 -left-3 w-16 h-16 border-l-2 border-t-2 border-[#8B5A2B] opacity-60 pointer-events-none"></div>
          </div>
        </div>
      </section>

      <!-- BANNER COMPATIBILIDAD -->
      <section class="border-y border-[#8B5A2B]/30 bg-[#1A1A1A]/90 py-3.5 text-center text-[#F4E8D1] shadow-md">
        <div class="max-w-6xl mx-auto px-4 flex flex-wrap items-center justify-center gap-y-2 gap-x-6 text-xs md:text-sm font-stat tracking-widest uppercase">
          <span class="text-[#D4AF37] flex items-center gap-1.5">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            Diseñado con devoción para Pathfinder Rol OGL v1.0a
          </span>
          <span class="text-[#8B7D6B] hidden md:inline">•</span>
          <span class="text-[#F4E8D1]/80">D&D 3.5 Compatible</span>
          <span class="text-[#8B7D6B] hidden md:inline">•</span>
          <span class="text-[#F4E8D1]/80">Códice de Dotes y Conjuros</span>
          <span class="text-[#8B7D6B] hidden md:inline">•</span>
          <span class="text-[#D4AF37]">Bestiario y Encuentros Tácticos</span>
        </div>
      </section>

      <!-- HERRAMIENTAS LISTAS PARA JUGAR -->
      <section class="max-w-6xl mx-auto px-6 py-16">
        <div class="text-center max-w-3xl mx-auto mb-12">
          <div class="text-[#8B5A2B] font-bold text-xs uppercase font-stat tracking-widest mb-1">Mesa Virtual &amp; Grimorio Integrado</div>
          <h2 class="font-mason text-3xl md:text-4xl font-bold text-[#8B5A2B] tracking-wide">Comienza con Campañas Listas para Jugar</h2>
          <p class="font-narrative text-lg text-[#5A4A3A] mt-2 italic">
            Todo lo que un Director de Juego y un grupo de aventureros necesitan reunido en un tomo digital sin fricciones.
          </p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="h in herramientas" :key="h.icono" class="card-vellum p-5 rounded-[2px] flex flex-col justify-between">
            <div class="rune-spine"></div>
            <div class="pl-3">
              <div class="w-10 h-10 rounded-full bg-[#8B5A2B]/15 border border-[#8B5A2B]/40 flex items-center justify-center text-[#8B5A2B] mb-3">
                <svg v-if="h.icono === 'description'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                <svg v-else-if="h.icono === 'menu_book'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
                <svg v-else-if="h.icono === 'calendar_month'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
              </div>
              <h3 class="font-mason font-bold text-lg text-[#8B5A2B] mb-1">{{ h.titulo }}</h3>
              <p class="font-narrative text-sm text-[#1A1A1A] leading-relaxed">{{ h.texto }}</p>
            </div>
            <div class="pl-3 pt-3 mt-3 border-t border-[#C2A980]/50 flex items-center justify-between">
              <span class="font-stat text-xs uppercase font-bold text-[#8B5A2B]">{{ h.pie }}</span>
              <svg class="text-[#8B5A2B] text-base" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="12 7 12 12 15 14"/><circle cx="12" cy="12" r="10"/></svg>
            </div>
          </div>
        </div>
      </section>

      <!-- 4 PASOS -->
      <section class="bg-[#1A1A1A]/95 border-y-2 border-[#D4AF37] py-16 text-[#FDF8EE] relative">
        <div class="max-w-6xl mx-auto px-6">
          <div class="text-center max-w-2xl mx-auto mb-12">
            <span class="font-stat text-xs tracking-widest text-[#D4AF37] uppercase font-bold">Guía en Cuatro Pasos</span>
            <h2 class="font-mason text-3xl md:text-4xl text-[#D4AF37] font-bold mt-1">Tu Senda del Aventurero</h2>
            <p class="font-narrative italic text-base text-[#F4E8D1]/80 mt-1">Desde la creación de tu cuenta hasta el lanzamiento de los primeros dados en el tablero.</p>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6 relative">
            <div v-for="p in pasos" :key="p.numero" class="bg-[#262626] border border-[#8B5A2B]/60 p-6 rounded-[2px] relative flex flex-col">
              <span class="font-logo text-4xl text-[#D4AF37]/40 font-bold mb-2">{{ p.numero }}</span>
              <h3 class="font-mason text-lg font-bold text-[#FDF8EE] mb-2">{{ p.titulo }}</h3>
              <p class="font-narrative text-sm text-[#F4E8D1]/75 leading-relaxed flex-grow">{{ p.texto }}</p>
              <div class="mt-4 pt-3 border-t border-[#8B5A2B]/40 text-xs font-stat text-[#D4AF37] uppercase tracking-wider">{{ p.pie }}</div>
            </div>
          </div>
          <div class="mt-10 text-center">
            <RouterLink class="btn-gold-relief inline-block px-10 py-3 rounded-[2px] font-stat font-bold text-[16px] text-[#1A1A1A] tracking-wider uppercase" to="/registro">Comenzar mi Aventura Ahora</RouterLink>
          </div>
        </div>
      </section>

      <!-- TESTIMONIOS -->
      <section class="max-w-6xl mx-auto px-6 py-16">
        <div class="text-center max-w-2xl mx-auto mb-12">
          <span class="text-[#8B5A2B] font-bold text-xs uppercase font-stat tracking-widest">Ecos de las Tabernas</span>
          <h2 class="font-mason text-3xl md:text-4xl text-[#8B5A2B] font-bold mt-1">Testimonios de la Hermandad</h2>
          <p class="font-narrative italic text-lg text-[#5A4A3A]">Lo que dicen los Directores de Juego y aventureros veteranos de nuestra comunidad.</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div v-for="t in testimonios" :key="t.nombre" class="card-vellum p-6 rounded-[2px] flex flex-col justify-between pl-7">
            <div class="rune-spine"></div>
            <div>
              <div class="flex items-center space-x-1 text-[#D4AF37] mb-3">
                <span v-for="n in 5" :key="n">★</span>
              </div>
              <p class="font-narrative italic text-base text-[#1A1A1A] leading-relaxed mb-4">{{ t.cita }}</p>
            </div>
            <div class="pt-3 border-t border-[#C2A980]/60 flex items-center gap-3">
              <div class="w-10 h-10 rounded-full border border-[#D4AF37] flex items-center justify-center font-mason font-bold text-sm" :class="[t.fondo, t.color]">{{ t.inicial }}</div>
              <div>
                <h4 class="font-mason font-bold text-[#8B5A2B] text-sm leading-tight">{{ t.nombre }}</h4>
                <span class="font-stat text-xs text-[#8B7D6B] uppercase">{{ t.rol }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- PERSONALIZA TU CAMPAÑA -->
      <section class="max-w-6xl mx-auto px-6 py-12">
        <div class="text-center max-w-2xl mx-auto mb-12">
          <span class="font-stat text-xs tracking-widest text-[#8B5A2B] uppercase font-bold">Códice de Capacidades</span>
          <h2 class="font-mason text-3xl md:text-4xl text-[#8B5A2B] font-bold mt-1">Personaliza tu Campaña</h2>
          <p class="font-narrative italic text-base text-[#5A4A3A]">Arquitectura forjada para respetar cada pormenor táctico y narrativo de la Primera Edición.</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-for="c in capacidades" :key="c.icono" class="card-vellum p-6 rounded-[2px] flex items-start gap-4 pl-7">
            <div class="rune-spine"></div>
            <div class="w-12 h-12 shrink-0 rounded bg-[#8B5A2B]/10 border border-[#8B5A2B]/40 flex items-center justify-center text-[#8B5A2B]">
              <svg v-if="c.icono === 'shield'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              <svg v-else-if="c.icono === 'auto_stories'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 6.253v13m0 0C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5s3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18s-3.332.477-4.5 1.253"/></svg>
              <svg v-else-if="c.icono === 'wb_sunny'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>
              <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            </div>
            <div>
              <h3 class="font-mason font-bold text-xl text-[#8B5A2B] mb-1">{{ c.titulo }}</h3>
              <p class="font-narrative text-sm text-[#1A1A1A] leading-relaxed">{{ c.texto }}</p>
            </div>
          </div>
        </div>
      </section>

      <div class="bestiary-divider" aria-hidden="true"></div>

      <!-- MESAS DESTACADAS (reactivas, desde servicio) -->
      <section class="max-w-6xl mx-auto px-6 py-10 mb-10" id="explorar">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-8 border-b border-[#8B5A2B]/40 pb-3 gap-2">
          <h2 class="font-mason font-bold text-[1.6rem] text-[#8B5A2B] flex items-center gap-2">
            <span class="text-[#D4AF37]">§</span> Mesas destacadas en búsqueda de héroes
          </h2>
          <span class="font-stat text-xs tracking-wider text-[#8B7D6B] uppercase font-bold">Bestiario de Partidas Activas</span>
        </div>

        <div v-if="isLoading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 justify-items-center" role="status" aria-live="polite">
          <div v-for="n in 6" :key="n" class="card-vellum w-full max-w-[340px] min-h-[270px] p-5 rounded-[2px] animate-pulse">
            <div class="w-3/4 h-4 bg-[#C2A980]/40 rounded mb-3"></div>
            <div class="w-full h-2 bg-[#C2A980]/25 rounded mb-2"></div>
            <div class="w-full h-2 bg-[#C2A980]/25 rounded mb-2"></div>
            <div class="w-2/3 h-2 bg-[#C2A980]/25 rounded"></div>
          </div>
        </div>

        <div v-else-if="error" class="card-parchment p-8 text-center max-w-xl mx-auto" role="alert">
          <p class="font-stat uppercase tracking-widest text-xs text-[#8B1A1A] font-bold mb-1">Error</p>
          <p class="font-narrative">{{ error }}</p>
          <button type="button" class="btn-gold mt-4 px-6 py-2 font-stat font-bold uppercase tracking-wider text-sm" @click="retry">Reintentar</button>
        </div>

        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 justify-items-center">
          <article v-for="mesa in mesas.filter((m) => m.destacada).slice(0, 6)" :key="mesa.id" class="card-vellum w-full max-w-[340px] min-h-[270px] p-5 flex flex-col justify-between rounded-[2px] pl-6 overflow-hidden">
            <div class="rune-spine"></div>
            <div class="rune-pattern"></div>
            <div>
              <div class="flex items-start justify-between gap-2 mb-2">
                <h3 class="font-mason font-bold text-[1.05rem] text-[#8B5A2B] leading-tight">{{ mesa.nombre }}</h3>
                <span class="font-stat text-[0.7rem] bg-[#1A1A1A] text-[#FDF8EE] px-1.5 py-0.5 rounded-[1px] uppercase tracking-wider font-bold">{{ mesa.sistema }}</span>
              </div>
              <div class="h-[1px] bg-[#8B1A1A]/30 w-full mb-3"></div>
              <p class="font-narrative italic text-[0.85rem] text-[#1A1A1A] leading-relaxed">
                Dirigida por <span class="font-semibold text-[#8B5A2B] not-italic">{{ mesa.gm }}</span>
              </p>
              <p class="font-narrative text-[0.85rem] text-[#1A1A1A]/85 mt-2 line-clamp-3">{{ mesa.lore }}</p>
            </div>
            <div class="pt-3 border-t border-[#C2A980]/60 flex items-center justify-between">
              <span class="font-narrative text-[0.78rem] font-semibold flex items-center gap-1" :class="estadoClase(mesa)">
                ● {{ mesa.estadoCategoria }}
              </span>
              <span class="font-stat font-bold text-[0.82rem] text-[#8B7D6B] bg-[#1A1A1A]/5 px-2 py-0.5 rounded border border-[#8B7D6B]/30">{{ mesa.ocurrenciasPlazas }} Plazas</span>
            </div>
          </article>
        </div>
      </section>

      <!-- COMUNIDAD Y RECURSOS -->
      <section class="max-w-6xl mx-auto px-6 py-12 mb-12">
        <div class="text-center max-w-2xl mx-auto mb-10">
          <span class="text-[#8B5A2B] font-bold text-xs uppercase font-stat tracking-widest">Guías del Códice</span>
          <h2 class="font-mason text-3xl text-[#8B5A2B] font-bold mt-1">Comunidad &amp; Recursos de Inicio</h2>
          <p class="font-narrative italic text-base text-[#5A4A3A]">Material de iniciación pensado tanto para aprendices como para maestros de juego veteranos.</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div v-for="g in guias" :key="g.titulo" class="card-vellum p-5 rounded-[2px]">
            <div class="rune-spine"></div>
            <div class="pl-4">
              <span class="text-xs font-stat font-bold uppercase text-[#8B5A2B] tracking-wider">{{ g.etiqueta }}</span>
              <h3 class="font-mason font-bold text-lg text-[#1A1A1A] mt-1 mb-2">{{ g.titulo }}</h3>
              <p class="font-narrative text-sm text-[#5A4A3A] leading-relaxed">{{ g.texto }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA FINAL -->
      <section class="border-t-2 border-[#D4AF37] bg-gradient-to-b from-[#1A1A1A] to-[#121212] py-16 text-center text-[#FDF8EE] relative overflow-hidden">
        <div class="max-w-3xl mx-auto px-6 relative z-10">
          <div class="text-[#D4AF37] text-xl mb-2 select-none">✤ ❖ ✤</div>
          <h2 class="font-mason text-3xl sm:text-4xl lg:text-5xl font-bold text-[#FDF8EE] tracking-wide mb-4">¿Listo para iniciar tu propia epopeya?</h2>
          <p class="font-narrative italic text-lg sm:text-xl text-[#F4E8D1]/85 max-w-2xl mx-auto mb-8 leading-relaxed">
            Cientos de aventureros ya se reúnen en TFinder para forjar leyendas en Golarion. Únete hoy a la comunidad y abre tu propio tomo.
          </p>
          <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
            <RouterLink class="btn-gold-relief w-full sm:w-auto px-10 py-4 rounded-[2px] font-stat font-bold text-[18px] text-[#1A1A1A] tracking-wider uppercase inline-flex items-center justify-center gap-2" to="/registro">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="7" r="4"/><path d="M2 21v-2a4 4 0 0 1 4-4h6a4 4 0 0 1 4 4v2"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/></svg>
              Crear Cuenta Gratuita
            </RouterLink>
            <RouterLink class="btn-copper-outline w-full sm:w-auto px-8 py-3.5 rounded-[2px] font-stat font-bold text-[18px] tracking-wider uppercase inline-flex items-center justify-center gap-2" to="/mesas">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              Explorar Mesas
            </RouterLink>
          </div>
          <p class="font-stat text-xs uppercase tracking-widest text-[#8B7D6B] mt-6">Sin pagos ocultos • Acceso instantáneo en tu navegador web</p>
        </div>
      </section>
    </main>
  </div>
</template>