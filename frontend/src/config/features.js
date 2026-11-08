export const FEATURES = {
  perfil: { label: 'Perfil', available: true },
  crearMesa: { label: 'Crear mesa', available: true },
  editarMesa: { label: 'Editar mesa', available: true },
  misMesas: { label: 'Mis campañas', available: true },
  gestionMesa: { label: 'Gestión de campaña', available: true },
  calendario: { label: 'Calendario y votación', available: true },
  sesiones: { label: 'Sesiones', available: true },
  jugadores: { label: 'Gestión de jugadores', available: true },
  matchmaking: { label: 'Matchmaking', available: true }
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