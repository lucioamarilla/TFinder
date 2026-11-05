<template>
  <div class="wrap" style="padding-top: 120px;">
    <header class="mb-8">
      <div class="flex items-center gap-2 mb-2">
        <div class="w-8 h-8 rounded-sm bg-tf-primary/15 border border-tf-primary/40 flex items-center justify-center"><span class="material-symbols-outlined text-tf-primary" style="font-size:16px">casino</span></div>
        <span class="font-logo text-[13px] text-tf-primary tracking-wide">TFINDER</span>
        <span class="tag tag--gold" style="color: var(--color-gold);">PF1E</span>
      </div>
      <h1 class="text-[32px] font-bold tracking-[-0.01em] mb-1" style="font-family: var(--font-display); text-transform: uppercase;">Índice de pantallas — Celeste Frío</h1>
      <p class="text-[14px] text-tf-muted">Galería navegable del rediseño migrado a Vue.</p>
    </header>

    <div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: var(--space-md);">
      <RouterLink v-for="s in pantallas" :key="s.to" :to="s.to" class="card p-4" style="text-decoration: none; color: inherit; display: block;">
        <p class="font-data text-[11px] text-tf-muted mb-1">{{ s.n }}</p>
        <p class="text-[14px] font-semibold text-tf-ink">{{ s.titulo }}</p>
        <p class="text-[12px] text-tf-muted">{{ s.desc }}</p>
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
const pantallas = [
  { n: '01', to: '/', titulo: 'Landing Arcade', desc: 'Marketing · hero · mesas activas' },
  { n: '02', to: '/login', titulo: 'Login', desc: '2 columnas · auth' },
  { n: '03', to: '/registro', titulo: 'Registro', desc: '2 columnas · auth' },
  { n: '04', to: '/recuperar', titulo: 'Recuperar contraseña', desc: '2 columnas · auth' },
  { n: '05', to: '/feed', titulo: 'Home Feed', desc: '3 columnas · posts' },
  { n: '06', to: '/mesas', titulo: 'Explorar mesas', desc: 'Grid de MesaCard · filtros' },
  { n: '07', to: '/mesas/vellmar', titulo: 'Detalle de mesa (jugador)', desc: 'Hero · tabs · miembros' },
  { n: '08', to: '/mesas/vellmar/gm', titulo: 'Detalle de mesa (GM)', desc: 'Editable · acciones rápidas' },
  { n: '09', to: '/mis-mesas', titulo: 'Mis mesas (jugador)', desc: 'Lista MesaRow' },
  { n: '10', to: '/mis-mesas-gm', titulo: 'Mis mesas (GM)', desc: 'Grid · nueva mesa' },
  { n: '11', to: '/panel-gm', titulo: 'Panel GM', desc: 'Dashboard · métricas · sesiones' },
  { n: '12', to: '/solicitudes-gm', titulo: 'Solicitudes (GM)', desc: 'Bandeja · aceptar/rechazar' },
  { n: '13', to: '/mesas/nueva', titulo: 'Crear mesa', desc: 'Formulario · publicar' },
  { n: '14', to: '/mesas/vellmar/sesion', titulo: 'Modo sesión (GM)', desc: 'Iniciativa · notas · botín' },
  { n: '15', to: '/wiki', titulo: 'Wiki índice', desc: 'Lista de páginas por tipo' },
  { n: '16', to: '/wiki/sello', titulo: 'Wiki lectura', desc: 'Lore · statblock · propiedades' },
  { n: '17', to: '/wiki/nueva', titulo: 'Wiki editor', desc: 'Título · tipo · contenido' },
  { n: '18', to: '/calculadora-apl', titulo: 'Calculadora APL', desc: 'APL · BudgetBar · tabla XP' },
  { n: '19', to: '/compendio', titulo: 'Compendio', desc: 'Tabla · hechizos/objetos/dotes' },
  { n: '20', to: '/bestiario', titulo: 'Bestiario', desc: 'StatBlock · criaturas' },
  { n: '21', to: '/ficha', titulo: 'Ficha de personaje', desc: 'Atributos · equipo · dotes' },
  { n: '22', to: '/perfil', titulo: 'Perfil', desc: 'Avatar · mesas' },
  { n: '23', to: '/notificaciones', titulo: 'Notificaciones', desc: 'Lista · nuevo/leído' },
  { n: '24', to: '/no-existe', titulo: '404', desc: 'Página no encontrada' },
  { n: 'CAT', to: '/catalogo', titulo: 'Catálogo Arcade', desc: 'Identidad visual + set completo' }
]
</script>