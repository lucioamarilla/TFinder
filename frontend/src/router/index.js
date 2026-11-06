import { createRouter, createWebHistory } from 'vue-router'
import { resolveGuard } from '@/router/guard'
import { currentRole } from '@/composables/useAuth'

const LandingView = () => import('@/views/LandingView.vue')
const CatalogoView = () => import('@/views/CatalogoView.vue')
const LoginView = () => import('@/views/LoginView.vue')
const RegistroView = () => import('@/views/RegistroView.vue')
const RecuperarView = () => import('@/views/RecuperarView.vue')
const FeedView = () => import('@/views/FeedView.vue')
const MesasListView = () => import('@/views/MesasListView.vue')
const MesaDetailJugadorView = () => import('@/views/MesaDetailJugadorView.vue')
const MesaDetailGmView = () => import('@/views/MesaDetailGmView.vue')
const MisMesasJugadorView = () => import('@/views/MisMesasJugadorView.vue')
const MisMesasGmView = () => import('@/views/MisMesasGmView.vue')
// Retirado: PanelGmView (solo demo)
const SolicitudesGmView = () => import('@/views/SolicitudesGmView.vue')
const CrearMesaView = () => import('@/views/CrearMesaView.vue')
const ModoSesionBitacoraView = () => import('@/views/ModoSesionBitacoraView.vue')
const WikiIndiceView = () => import('@/views/WikiIndiceView.vue')
const WikiLecturaView = () => import('@/views/WikiLecturaView.vue')
const WikiEditorView = () => import('@/views/WikiEditorView.vue')
const CalculadoraAplView = () => import('@/views/CalculadoraAplView.vue')
// Retirados: CompendioView, BestiarioView (sin backend)
const PerfilView = () => import('@/views/PerfilView.vue')
const NotificacionesView = () => import('@/views/NotificacionesView.vue')
const NotFoundView = () => import('@/views/NotFoundView.vue')
const IndiceView = () => import('@/views/IndiceView.vue')
const ComingSoonView = () => import('@/views/ComingSoonView.vue')

// Fase 11 · pantallas estructurales v5
// Retirado: BusquedaView (búsqueda solo local)
const MesaCalendarioView = () => import('@/views/MesaCalendarioView.vue')
const ModoSesionJugadorView = () => import('@/views/ModoSesionJugadorView.vue')

// Módulos revividos (iteración anterior, ahora con el estado demo de reglas)
const MesaFormularioView = () => import('@/views/MesaFormularioView.vue')
// const DashboardView = () => import('@/views/DashboardView.vue')  // simplificado: redirect a /mesas
// Retirado: MatchmakingView (candidatos mock)
const EncuentrosView = () => import('@/views/EncuentrosView.vue')
const TagsView = () => import('@/views/TagsView.vue')
const BuildsListView = () => import('@/views/BuildsListView.vue')
const BuildDetailView = () => import('@/views/BuildDetailView.vue')
const BuildWizardView = () => import('@/views/BuildWizardView.vue')
const BuildEditorView = () => import('@/views/BuildEditorView.vue')
const BuildHistorialView = () => import('@/views/BuildHistorialView.vue')
const GestionLayout = () => import('@/layouts/GestionLayout.vue')
const GestionView = () => import('@/views/gestion/GestionView.vue')
const GestionWikiView = () => import('@/views/gestion/WikiView.vue')
const GestionWikiEditorView = () => import('@/views/gestion/WikiEditorView.vue')
const GestionPaginaWikiView = () => import('@/views/gestion/PaginaWikiView.vue')
const GestionCalendarioView = () => import('@/views/gestion/CalendarioView.vue')
const GestionSesionesView = () => import('@/views/gestion/SesionesView.vue')
const GestionSesionQrView = () => import('@/views/gestion/SesionQrView.vue')
const GestionSesionBitacoraView = () => import('@/views/gestion/BitacoraView.vue')
const GestionDiarioEditorView = () => import('@/views/gestion/DiarioEditorView.vue')
const GestionJugadoresView = () => import('@/views/gestion/JugadoresView.vue')
const GestionBuildsView = () => import('@/views/gestion/BuildsView.vue')
const AdminLayout = () => import('@/layouts/AdminLayout.vue')
const AdminPanelView = () => import('@/views/admin/AdminPanelView.vue')
const AdminEventosView = () => import('@/views/admin/AdminEventosView.vue')
const AdminDlqView = () => import('@/views/admin/AdminDlqView.vue')
const AdminEmailsView = () => import('@/views/admin/AdminEmailsView.vue')
// F09/D-15: consola admin RE-implementada sobre notif-api (event-log, DLQ, emails)

export const routes = [
  { path: '/', name: 'landing', component: LandingView },
  { path: '/catalogo', name: 'catalogo', component: CatalogoView },
  { path: '/login', name: 'login', component: LoginView, meta: { roles: ['guest'], layout: 'guest' } },
  { path: '/registro', name: 'registro', component: RegistroView, meta: { roles: ['guest'], layout: 'guest' } },
  { path: '/recuperar', name: 'recuperar', component: RecuperarView, meta: { roles: ['guest'], layout: 'guest' } },
  { path: '/dashboard', redirect: '/mesas' },
  { path: '/builds/nuevo', redirect: '/builds/asistente' },
  // retirado: busqueda
  { path: '/feed', name: 'feed', component: FeedView },
  { path: '/mesas', name: 'mesas', component: MesasListView },
  { path: '/mesas/nueva', name: 'mesa-nueva', component: CrearMesaView, meta: { roles: ['auth'] } },
  { path: '/mesas/:id', name: 'mesa-detalle', component: MesaDetailJugadorView, props: true },
  { path: '/mesas/:id/gm', name: 'mesa-detalle-gm', component: MesaDetailGmView, props: true, meta: { roles: ['auth'] } },
  // Builds y campo encuentros (revividos): el asistente ya usa rutas enable
  { path: '/mesas/:id/sesion', name: 'mesa-sesion', component: ModoSesionBitacoraView, props: true, meta: { roles: ['auth'] } },
  { path: '/mesas/:id/editar', name: 'mesa-editar', component: MesaFormularioView, props: true, meta: { roles: ['auth'] } },
  { path: '/mesas/:id/sesion/jugador', name: 'mesa-sesion-jugador', component: ModoSesionJugadorView, props: true, meta: { roles: ['auth'] } },
  { path: '/mesas/:id/calendario', name: 'mesa-calendario', component: MesaCalendarioView, props: true, meta: { roles: ['auth'] } },

  // Gestión de campaña por tabs (revivida, ambiente GM)
  // Gestión de campaña por tabs (revivida, ambiente GM)
  {
    path: '/mesas/:id/gestion',
    component: GestionLayout,
    props: true,
    meta: { roles: ['auth'] },
    children: [
      { path: '', name: 'mesa-gestion', component: GestionView },
      { path: 'wiki', name: 'gestion-wiki', component: GestionWikiView },
      { path: 'wiki/nueva', name: 'gestion-wiki-nueva', component: GestionWikiEditorView },
      { path: 'wiki/:paginaId', name: 'gestion-wiki-pagina', component: GestionPaginaWikiView, props: true },
      { path: 'wiki/:paginaId/editar', name: 'gestion-wiki-editar', component: GestionWikiEditorView, props: true },
      { path: 'calendario', name: 'gestion-calendario', component: GestionCalendarioView },
      { path: 'sesiones', name: 'gestion-sesiones', component: GestionSesionesView },
      { path: 'sesiones/:sesionId/qr', name: 'gestion-sesion-qr', component: GestionSesionQrView, props: true },
      { path: 'sesiones/:sesionId/bitacora', name: 'gestion-sesion-bitacora', component: GestionSesionBitacoraView, props: true },
      { path: 'sesiones/:sesionId/diario', name: 'gestion-diario', component: GestionDiarioEditorView, props: true },
      { path: 'jugadores', name: 'gestion-jugadores', component: GestionJugadoresView },
      { path: 'builds', name: 'gestion-builds', component: GestionBuildsView }
    ]
  },

  { path: '/mis-mesas', name: 'mis-mesas', component: MisMesasJugadorView, meta: { roles: ['auth'] } },
  { path: '/mis-mesas-gm', name: 'mis-mesas-gm', component: MisMesasGmView, meta: { roles: ['auth'] } },
  // retirado: panel-gm
  { path: '/solicitudes-gm', name: 'solicitudes-gm', component: SolicitudesGmView, meta: { roles: ['auth'] } },
  { path: '/wiki', name: 'wiki', component: WikiIndiceView },
  { path: '/wiki/nueva', name: 'wiki-nueva', component: WikiEditorView, meta: { roles: ['auth'] } },
  { path: '/wiki/:id', name: 'wiki-lectura', component: WikiLecturaView, props: true },
  { path: '/wiki/:id/editar', name: 'wiki-editar', component: WikiEditorView, props: true, meta: { roles: ['auth'] } },
  { path: '/calculadora-apl', name: 'calculadora-apl', component: CalculadoraAplView },
  // retirados: compendio, bestiario
  { path: '/perfil', name: 'perfil', component: PerfilView, meta: { roles: ['auth'] } },
  { path: '/notificaciones', name: 'notificaciones', component: NotificacionesView, meta: { roles: ['auth'] } },
  { path: '/indice', name: 'indice', component: IndiceView },

  // Builds PF1e
  { path: '/builds', name: 'builds', component: BuildsListView },
  { path: '/builds/asistente', name: 'build-asistente', component: BuildWizardView, meta: { roles: ['auth'] } },
  { path: '/builds/:id', name: 'build-detalle', component: BuildDetailView, props: true },
  { path: '/builds/:id/editar', name: 'build-editor', component: BuildEditorView, props: true, meta: { roles: ['auth'] } },
  { path: '/builds/:id/historial', name: 'build-historial', component: BuildHistorialView, props: true },

  // Social y herramientas (matchmaking público, anotarse requiere sesión)
  // retirado: matchmaking
  { path: '/encuentros', name: 'encuentros', component: EncuentrosView },
  { path: '/tags', name: 'tags', component: TagsView },

  // Consola admin (F09/D-15): roles ['admin'] en cada nivel del merge.
  {
    path: '/admin',
    component: AdminLayout,
    meta: { roles: ['admin'] },
    children: [
      { path: '', name: 'admin-panel', component: AdminPanelView, meta: { roles: ['admin'] } },
      { path: 'eventos', name: 'admin-eventos', component: AdminEventosView, meta: { roles: ['admin'] } },
      { path: 'dlq', name: 'admin-dlq', component: AdminDlqView, meta: { roles: ['admin'] } },
      { path: 'emails', name: 'admin-emails', component: AdminEmailsView, meta: { roles: ['admin'] } }
    ]
  },
  { path: '/proximamente/:feature', name: 'proximamente', component: ComingSoonView, props: true },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, saved) {
    if (saved) return saved
    return { top: 0 }
  }
})

// Reusable también desde los tests (mismo guard, otro history).
export function instalarGuard(routerInstancia) {
  routerInstancia.beforeEach((to) => resolveGuard(to, currentRole()))
  return routerInstancia
}

instalarGuard(router)

export default router
