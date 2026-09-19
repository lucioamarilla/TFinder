import { createRouter, createWebHistory } from 'vue-router'
import { currentRole } from '@/composables/useAuth'
import { resolveGuard } from '@/router/guard'

const NotFoundView = () => import('@/views/NotFoundView.vue')
const LandingView = () => import('@/views/LandingView.vue')
const MesasListView = () => import('@/views/MesasListView.vue')
const MesaDetailView = () => import('@/views/MesaDetailView.vue')
const LoginView = () => import('@/views/LoginView.vue')
const RegistroView = () => import('@/views/RegistroView.vue')
const RecuperarView = () => import('@/views/RecuperarView.vue')
const DashboardView = () => import('@/views/DashboardView.vue')
const MisMesasView = () => import('@/views/MisMesasView.vue')
const MesaFormularioView = () => import('@/views/MesaFormularioView.vue')
const GestionView = () => import('@/views/gestion/GestionView.vue')
const WikiView = () => import('@/views/gestion/WikiView.vue')
const PaginaWikiView = () => import('@/views/gestion/PaginaWikiView.vue')
const WikiEditorView = () => import('@/views/gestion/WikiEditorView.vue')
const CalendarioView = () => import('@/views/gestion/CalendarioView.vue')
const SesionesView = () => import('@/views/gestion/SesionesView.vue')
const DiarioEditorView = () => import('@/views/gestion/DiarioEditorView.vue')
const JugadoresView = () => import('@/views/gestion/JugadoresView.vue')
const BuildsView = () => import('@/views/gestion/BuildsView.vue')
const BuildsListView = () => import('@/views/BuildsListView.vue')
const BuildDetailView = () => import('@/views/BuildDetailView.vue')
const BuildEditorView = () => import('@/views/BuildEditorView.vue')
const BuildWizardView = () => import('@/views/BuildWizardView.vue')
const BuildHistorialView = () => import('@/views/BuildHistorialView.vue')
const EncuentrosView = () => import('@/views/EncuentrosView.vue')
const TagsView = () => import('@/views/TagsView.vue')
const FeedView = () => import('@/views/FeedView.vue')
const FeedNewView = () => import('@/views/FeedNewView.vue')
const PerfilView = () => import('@/views/PerfilView.vue')
const UsuarioDetailView = () => import('@/views/UsuarioDetailView.vue')
const NotificacionesView = () => import('@/views/NotificacionesView.vue')
const MatchmakingView = () => import('@/views/MatchmakingView.vue')
const AdminModeracionView = () => import('@/views/admin/AdminModeracionView.vue')
const AdminUsuariosView = () => import('@/views/admin/AdminUsuariosView.vue')
const AdminEstadisticasView = () => import('@/views/admin/AdminEstadisticasView.vue')
const AdminPlataformaView = () => import('@/views/admin/AdminPlataformaView.vue')
const AdminTrazabilidadView = () => import('@/views/admin/AdminTrazabilidadView.vue')
const AdminObservabilidadView = () => import('@/views/admin/AdminObservabilidadView.vue')
const AdminDlqView = () => import('@/views/admin/AdminDlqView.vue')
const AdminResilienciaView = () => import('@/views/admin/AdminResilienciaView.vue')
const AdminComparadorView = () => import('@/views/admin/AdminComparadorView.vue')
const AdminPrometheusView = () => import('@/views/admin/AdminPrometheusView.vue')

const routes = [
  {
    path: '/',
    name: 'landing',
    component: LandingView,
    meta: { roles: ['guest', 'auth', 'admin'] }
  },
  { path: '/mesas', name: 'mesas', component: MesasListView, meta: { roles: ['guest', 'auth', 'admin'] } },
  { path: '/mesas/:id', name: 'mesa-detalle', component: MesaDetailView, props: true, meta: { roles: ['guest', 'auth', 'admin'] } },
  { path: '/registro', name: 'registro', component: RegistroView, meta: { roles: ['guest'] } },
  { path: '/login', name: 'login', component: LoginView, meta: { roles: ['guest'] } },
  { path: '/recuperar', name: 'recuperar', component: RecuperarView, meta: { roles: ['guest'] } },

  { path: '/dashboard', name: 'dashboard', component: DashboardView, meta: { roles: ['auth', 'admin'] } },
  { path: '/mis-mesas', name: 'mis-mesas', component: MisMesasView, meta: { roles: ['auth', 'admin'] } },
  { path: '/mesas/nueva', name: 'mesa-nueva', component: MesaFormularioView, meta: { roles: ['auth', 'admin'] } },
  { path: '/mesas/:id/editar', name: 'mesa-editar', component: MesaFormularioView, props: true, meta: { roles: ['auth', 'admin'] } },
  { path: '/mesas/:id/gestion', name: 'mesa-gestion', component: GestionView, props: (r) => ({ mesaId: r.params.id }), meta: { roles: ['auth', 'admin'] } },
  { path: '/mesas/:id/wiki', name: 'mesa-wiki', component: WikiView, props: (r) => ({ mesaId: r.params.id }), meta: { roles: ['auth', 'admin'] } },
  { path: '/mesas/:id/wiki/nueva', name: 'mesa-wiki-nueva', component: WikiEditorView, props: (r) => ({ mesaId: r.params.id, paginaId: 'nueva' }), meta: { roles: ['auth', 'admin'] } },
  { path: '/mesas/:id/wiki/:paginaId/editar', name: 'mesa-wiki-editar', component: WikiEditorView, props: (r) => ({ mesaId: r.params.id, paginaId: r.params.paginaId }), meta: { roles: ['auth', 'admin'] } },
  { path: '/mesas/:id/wiki/:paginaId', name: 'mesa-wiki-pagina', component: PaginaWikiView, props: (r) => ({ mesaId: r.params.id, paginaId: r.params.paginaId }), meta: { roles: ['auth', 'admin'] } },
  { path: '/mesas/:id/calendario', name: 'mesa-calendario', component: CalendarioView, props: (r) => ({ mesaId: r.params.id }), meta: { roles: ['auth', 'admin'] } },
  { path: '/mesas/:id/sesiones', name: 'mesa-sesiones', component: SesionesView, props: (r) => ({ mesaId: r.params.id }), meta: { roles: ['auth', 'admin'] } },
  { path: '/mesas/:id/sesiones/:sesionId/diario', name: 'mesa-diario-editar', component: DiarioEditorView, props: (r) => ({ mesaId: r.params.id, sesionId: r.params.sesionId }), meta: { roles: ['auth', 'admin'] } },
  { path: '/mesas/:id/jugadores', name: 'mesa-jugadores', component: JugadoresView, props: (r) => ({ mesaId: r.params.id }), meta: { roles: ['auth', 'admin'] } },
  { path: '/mesas/:id/builds', name: 'mesa-builds', component: BuildsView, props: (r) => ({ mesaId: r.params.id }), meta: { roles: ['auth', 'admin'] } },

  { path: '/builds', name: 'builds', component: BuildsListView, meta: { roles: ['auth', 'admin'] } },
  { path: '/builds/nuevo', name: 'build-nuevo', component: BuildWizardView, meta: { roles: ['auth', 'admin'] } },
  { path: '/builds/:id', name: 'build-detalle', component: BuildDetailView, props: true, meta: { roles: ['auth', 'admin'] } },
  { path: '/builds/:id/editar', name: 'build-editar', component: BuildEditorView, props: true, meta: { roles: ['auth', 'admin'] } },
  { path: '/builds/:id/historial', name: 'build-historial', component: BuildHistorialView, props: true, meta: { roles: ['auth', 'admin'] } },
  { path: '/feed', name: 'feed', component: FeedView, meta: { roles: ['auth', 'admin'] } },
  { path: '/feed/nuevo', name: 'feed-nuevo', component: FeedNewView, meta: { roles: ['auth', 'admin'] } },
  { path: '/perfil', name: 'perfil', component: PerfilView, meta: { roles: ['auth', 'admin'] } },
  { path: '/usuarios/:id', name: 'usuario-detalle', component: UsuarioDetailView, props: true, meta: { roles: ['auth', 'admin'] } },
  { path: '/notificaciones', name: 'notificaciones', component: NotificacionesView, meta: { roles: ['auth', 'admin'] } },
  { path: '/matchmaking', name: 'matchmaking', component: MatchmakingView, meta: { roles: ['auth', 'admin'] } },
  { path: '/encuentros', name: 'encuentros', component: EncuentrosView, meta: { roles: ['auth', 'admin'] } },
  { path: '/tags', name: 'tags', component: TagsView, meta: { roles: ['auth', 'admin'] } },

  { path: '/admin/moderacion', name: 'admin-moderacion', component: AdminModeracionView, meta: { roles: ['admin'] } },
  { path: '/admin/usuarios', name: 'admin-usuarios', component: AdminUsuariosView, meta: { roles: ['admin'] } },
  { path: '/admin/estadisticas', name: 'admin-estadisticas', component: AdminEstadisticasView, meta: { roles: ['admin'] } },
  { path: '/admin/plataforma', name: 'admin-plataforma', component: AdminPlataformaView, meta: { roles: ['admin'] } },
  { path: '/admin/trazabilidad', name: 'admin-trazabilidad', component: AdminTrazabilidadView, meta: { roles: ['admin'] } },
  { path: '/admin/observabilidad', name: 'admin-observabilidad', component: AdminObservabilidadView, meta: { roles: ['admin'] } },
  { path: '/admin/dlq', name: 'admin-dlq', component: AdminDlqView, meta: { roles: ['admin'] } },
  { path: '/admin/resiliencia', name: 'admin-resiliencia', component: AdminResilienciaView, meta: { roles: ['admin'] } },
  { path: '/admin/comparador', name: 'admin-comparador', component: AdminComparadorView, meta: { roles: ['admin'] } },
  { path: '/admin/prometheus', name: 'admin-prometheus', component: AdminPrometheusView, meta: { roles: ['admin'] } },

  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView, meta: { roles: ['guest', 'auth', 'admin'] } }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, saved) {
    if (saved) return saved
    return { top: 0 }
  }
})

router.beforeEach((to) => resolveGuard(to, currentRole()))

export default router