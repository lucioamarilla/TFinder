export const BASE = {
  mesas: import.meta.env.VITE_MESAS_API ?? 'http://localhost:8001',
  builds: import.meta.env.VITE_BUILDS_API ?? 'http://localhost:8002',
  feed: import.meta.env.VITE_FEED_API ?? 'http://localhost:8003',
  notif: import.meta.env.VITE_NOTIF_API ?? 'http://localhost:8004'
}

export function apiUrl(servicio, ruta) {
  return `${BASE[servicio] ?? BASE.mesas}${ruta}`
}
