export const NAV = {
  guest: [
    { label: 'Explorar', to: '/mesas' },
    { label: 'Registrarse', to: '/registro', cta: true },
    { label: 'Iniciar sesión', to: '/login' }
  ],
  auth: [
    { label: 'Explorar', to: '/mesas' },
    { label: 'Mis Mesas', to: '/mis-mesas' },
    { label: 'Mi perfil', to: '/perfil' }
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
    { label: 'Mis Mesas', to: '/mis-mesas' },
    { label: 'Mi perfil', to: '/perfil' }
  ],
  admin: []
}