export const FEATURES = {
  dashboard: { label: 'Dashboard', available: true },
  perfil: { label: 'Perfil extendido', available: true },
  crearMesa: { label: 'Crear mesa', available: true },
  editarMesa: { label: 'Editar mesa', available: true },
  misMesas: { label: 'Mis campañas', available: true },
  gestionMesa: { label: 'Gestión de campaña', available: true },
  wiki: { label: 'Wiki de campaña', available: true },
  calendario: { label: 'Calendario y votación', available: true },
  sesiones: { label: 'Sesiones y diario', available: true },
  qr: { label: 'Asistencia por QR', available: true },
  jugadores: { label: 'Gestión de jugadores', available: true },
  builds: { label: 'Builds', available: true },
  feed: { label: 'Feed Social', available: true },
  directorio: { label: 'Directorio de aventureros', available: true },
  notificaciones: { label: 'Notificaciones', available: true },
  matchmaking: { label: 'Matchmaking', available: true },
  encuentros: { label: 'Encuentros', available: true },
  tags: { label: 'Tags', available: true },
  recuperacion: { label: 'Recuperación de contraseña', available: true },
  admin: { label: 'Administración', available: true }
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
