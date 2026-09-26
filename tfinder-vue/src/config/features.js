export const FEATURES = {
  dashboard: { label: 'Dashboard', available: false },
  perfil: { label: 'Perfil extendido', available: false },
  crearMesa: { label: 'Crear mesa', available: true },
  editarMesa: { label: 'Editar mesa', available: true },
  misMesas: { label: 'Mis campañas', available: false },
  gestionMesa: { label: 'Gestión de campaña', available: false },
  wiki: { label: 'Wiki de campaña', available: false },
  calendario: { label: 'Calendario y votación', available: false },
  sesiones: { label: 'Sesiones y diario', available: false },
  qr: { label: 'Asistencia por QR', available: true },
  jugadores: { label: 'Gestión de jugadores', available: false },
  builds: { label: 'Builds', available: false },
  feed: { label: 'Feed Social', available: false },
  directorio: { label: 'Directorio de aventureros', available: false },
  notificaciones: { label: 'Notificaciones', available: true },
  matchmaking: { label: 'Matchmaking', available: true },
  encuentros: { label: 'Encuentros', available: true },
  tags: { label: 'Tags', available: false },
  recuperacion: { label: 'Recuperación de contraseña', available: true },
  admin: { label: 'Administración', available: false }
}

export function isFeatureEnabled(feature) {
  return FEATURES[feature]?.available === true
}

export function featureLabel(feature) {
  return FEATURES[feature]?.label ?? 'Esta función'
}

export function comingSoonPath(feature) {
  return `/proximamente/${FEATURES[feature] ? feature : 'no-disponible'}`
}
