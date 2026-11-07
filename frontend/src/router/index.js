import { createRouter, createWebHistory } from 'vue-router'
import { resolveGuard } from '@/router/guard'
import { currentRole } from '@/composables/useAuth'

const LandingView = () => import('@/views/LandingView.vue')
const LoginView = () => import('@/views/LoginView.vue')
const RegistroView = () => import('@/views/RegistroView.vue')
const RecuperarView = () => import('@/views/RecuperarView.vue')
const MesasListView = () => import('@/views/MesasListView.vue')
const MesaDetailJugadorView = () => import('@/views/MesaDetailJugadorView.vue')
const MesaDetailGmView = () => import('@/views/MesaDetailGmView.vue')
const MisMesasJugadorView = () => import('@/views/MisMesasJugadorView.vue')
const SolicitudesGmView = () => import('@/views/SolicitudesGmView.vue')
const CrearMesaView = () => import('@/views/CrearMesaView.vue')
const ModoSesionBitacoraView = () => import('@/views/ModoSesionBitacoraView.vue')
const PerfilView = () => import('@/views/PerfilView.vue')
const NotFoundView = () => import('@/views/NotFoundView.vue')
const ComingSoonView = () => import('@/views/ComingSoonView.vue')
const MesaCalendarioView = () => import('@/views/MesaCalendarioView.vue')
const ModoSesionJugadorView = () => import('@/views/ModoSesionJugadorView.vue')
const MesaFormularioView = () => import('@/views/MesaFormularioView.vue')
const GestionLayout = () => import('@/layouts/GestionLayout.vue')
const GestionView = () => import('@/views/gestion/GestionView.vue')
const GestionCalendarioView = () => import('@/views/gestion/CalendarioView.vue')
const GestionSesionesView = () => import('@/views/gestion/SesionesView.vue')
const GestionSesionBitacoraView = () => import('@/views/gestion/BitacoraView.vue')
const GestionJugadoresView = () => import('@/views/gestion/JugadoresView.vue')

export const routes = [
  { path: '/', name: 'landing', component: LandingView },
  { path: '/login', name: 'login', component: LoginView, meta: { roles: ['guest'], layout: 'guest' } },
  { path: '/registro', name: 'registro', component: RegistroView, meta: { roles: ['guest'], layout: 'guest' } },
  { path: '/recuperar', name: 'recuperar', component: RecuperarView, meta: { roles: ['guest'], layout: 'guest' } },
  { path: '/dashboard', redirect: '/mesas' },
  { path: '/mesas', name: 'mesas', component: MesasListView },
  { path: '/mesas/nueva', name: 'mesa-nueva', component: CrearMesaView, meta: { roles: ['auth'] } },
  { path: '/mesas/:id', name: 'mesa-detalle', component: MesaDetailJugadorView, props: true },
  { path: '/mesas/:id/gm', name: 'mesa-detalle-gm', redirect: (to) => `/mesas/${to.params.id}/gestion`, meta: { roles: ['auth'] } },
  { path: '/mesas/:id/sesion', name: 'mesa-sesion', component: ModoSesionBitacoraView, props: true, meta: { roles: ['auth'] } },
  { path: '/mesas/:id/editar', name: 'mesa-editar', component: MesaFormularioView, props: true, meta: { roles: ['auth'] } },
  { path: '/mesas/:id/sesion/jugador', name: 'mesa-sesion-jugador', component: ModoSesionJugadorView, props: true, meta: { roles: ['auth'] } },
  { path: '/mesas/:id/calendario', name: 'mesa-calendario', component: MesaCalendarioView, props: true, meta: { roles: ['auth'] } },

  {
    path: '/mesas/:id/gestion',
    component: GestionLayout,
    props: true,
    meta: { roles: ['auth'] },
    children: [
      { path: '', name: 'mesa-gestion', component: GestionView },
      { path: 'calendario', name: 'gestion-calendario', component: GestionCalendarioView },
      { path: 'sesiones', name: 'gestion-sesiones', component: GestionSesionesView },
      { path: 'sesiones/:sesionId/bitacora', name: 'gestion-sesion-bitacora', component: GestionSesionBitacoraView, props: true },
      { path: 'jugadores', name: 'gestion-jugadores', component: GestionJugadoresView }
    ]
  },

  { path: '/mis-mesas', name: 'mis-mesas', component: MisMesasJugadorView, meta: { roles: ['auth'] } },
  { path: '/solicitudes-gm', name: 'solicitudes-gm', component: SolicitudesGmView, meta: { roles: ['auth'] } },
  { path: '/perfil', name: 'perfil', component: PerfilView, meta: { roles: ['auth'] } },

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

export function instalarGuard(routerInstancia) {
  routerInstancia.beforeEach((to) => resolveGuard(to, currentRole()))
  return routerInstancia
}

instalarGuard(router)

export default router