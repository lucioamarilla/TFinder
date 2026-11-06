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
    item('Dashboard', '/dashboard', 'dashboard'),
    { label: 'Explorar', to: '/mesas' },
    item('Mis Mesas', '/mis-mesas', 'misMesas'),
    item('Builds', '/builds', 'builds'),
    item('Feed Social', '/feed', 'feed'),
    item('Encuentros', '/encuentros', 'encuentros'),
    item('Tags', '/tags', 'tags'),
    { label: 'Notificaciones', to: '/notificaciones' }
  ],
  admin: [
    // Ciclo 14 (F09): se re-agregan junto con las rutas /admin reales.
  ]
}

export const FOOTER_NAV = {
  guest: [
    { label: 'Inicio', to: '/' },
    { label: 'Explorar Mesas', to: '/mesas' },
    { label: 'Registro', to: '/registro' }
  ],
  auth: [
    item('Dashboard', '/dashboard', 'dashboard'),
    item('Mis Mesas', '/mis-mesas', 'misMesas'),
    item('Builds', '/builds', 'builds'),
    item('Encuentros', '/encuentros', 'encuentros')
  ],
  admin: [
    // Ciclo 14 (F09): se re-agregan junto con las rutas /admin reales.
  ]
}
