export const NAV = {
  guest: [
    { label: '✦ Explorar', to: '/mesas' },
    { label: 'Registrarse', to: '/registro', cta: true },
    { label: 'Iniciar sesión', to: '/login' }
  ],
  auth: [
    { label: 'Dashboard', to: '/dashboard', feature: 'dashboard' },
    { label: 'Explorar', to: '/mesas' },
    { label: 'Mis Mesas', to: '/mis-mesas', feature: 'misMesas' },
    { label: 'Builds', to: '/builds', feature: 'builds' },
    { label: 'Feed Social', to: '/feed', feature: 'feed' },
    { label: 'Encuentros', to: '/encuentros', feature: 'encuentros' }
  ],
  admin: [
    { label: 'Moderación', to: '/admin/moderacion', feature: 'admin' },
    { label: 'Usuarios', to: '/admin/usuarios', feature: 'admin' },
    { label: 'Estadísticas & Logs', to: '/admin/estadisticas', feature: 'admin' }
  ]
}

export const FOOTER_NAV = {
  guest: [
    { label: 'Inicio', to: '/' },
    { label: 'Explorar Mesas', to: '/mesas' },
    { label: 'Registro', to: '/registro' }
  ],
  auth: [
    { label: 'Dashboard', to: '/dashboard', feature: 'dashboard' },
    { label: 'Mis Mesas', to: '/mis-mesas', feature: 'misMesas' },
    { label: 'Builds', to: '/builds', feature: 'builds' },
    { label: 'Encuentros', to: '/encuentros', feature: 'encuentros' }
  ],
  admin: [
    { label: 'Moderación', to: '/admin/moderacion', feature: 'admin' },
    { label: 'Usuarios', to: '/admin/usuarios', feature: 'admin' },
    { label: 'Estadísticas & Logs', to: '/admin/estadisticas', feature: 'admin' }
  ]
}