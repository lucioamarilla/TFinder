export const NAV = {
  guest: [
    { label: '✦ Explorar', to: '/mesas' },
    { label: 'Registrarse', to: '/registro', cta: true },
    { label: 'Iniciar sesión', to: '/login' }
  ],
  auth: [
    { label: 'Dashboard', to: '/dashboard' },
    { label: 'Explorar', to: '/mesas' },
    { label: 'Mis Mesas', to: '/mis-mesas' },
    { label: 'Builds', to: '/builds' },
    { label: 'Feed Social', to: '/feed' }
  ],
  admin: [
    { label: 'Moderación', to: '/admin/moderacion' },
    { label: 'Usuarios', to: '/admin/usuarios' },
    { label: 'Estadísticas & Logs', to: '/admin/estadisticas' }
  ]
}

export const FOOTER_NAV = {
  guest: [
    { label: 'Inicio', to: '/' },
    { label: 'Explorar Mesas', to: '/mesas' },
    { label: 'Registro', to: '/registro' }
  ],
  auth: [
    { label: 'Dashboard', to: '/dashboard' },
    { label: 'Mis Mesas', to: '/mis-mesas' },
    { label: 'Builds', to: '/builds' }
  ],
  admin: [
    { label: 'Moderación', to: '/admin/moderacion' },
    { label: 'Usuarios', to: '/admin/usuarios' },
    { label: 'Estadísticas & Logs', to: '/admin/estadisticas' }
  ]
}