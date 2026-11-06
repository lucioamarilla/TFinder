// Navegación por rol — solo rutas que existen en el router real.
// Las features cerradas apuntan a /proximamente/<feature> (ruta definida).
import { comingSoonPath, isFeatureEnabled } from '@/config/features'

const item = (label, to, feature) => (feature && !isFeatureEnabled(feature) ? { label, to: comingSoonPath(feature), feature } : { label, to, feature })

export const NAV = {
  guest: [
    { label: '✦ Explorar', to: '/mesas' },
    { label: 'Registrarse', to: '/registro', cta: true },
    { label: 'Iniciar sesión', to: '/login' }
  ],
  auth: [
    { label: 'Explorar', to: '/mesas' },
    item('Mis Mesas', '/mis-mesas', 'misMesas'),
    item('Builds', '/builds', 'builds'),
    item('Feed Social', '/feed', 'feed'),
    { label: 'Notificaciones', to: '/notificaciones' }
  ],
  admin: []
}

export const FOOTER_NAV = {
  guest: [
    { label: 'Inicio', to: '/' },
    { label: 'Explorar Mesas', to: '/mesas' },
    { label: 'Registro', to: '/registro' }
  ],
  auth: [
    item('Mis Mesas', '/mis-mesas', 'misMesas'),
    item('Builds', '/builds', 'builds')
  ],
  admin: []
}
