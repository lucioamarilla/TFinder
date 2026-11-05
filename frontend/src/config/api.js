export const BASE = {
  mesas: import.meta.env.VITE_MESAS_API ?? 'http://localhost:8001',
  builds: import.meta.env.VITE_BUILDS_API ?? 'http://localhost:8002',
  feed: import.meta.env.VITE_FEED_API ?? 'http://localhost:8003',
  notif: import.meta.env.VITE_NOTIF_API ?? 'http://localhost:8004'
}

export function apiUrl(servicio, ruta) {
  const base = BASE[servicio]
  if (!base) {
    throw new Error(
      `Servicio desconocido: "${servicio}". Servicios registrados: ${Object.keys(BASE).join(', ')}`,
    )
  }
  return `${base}${ruta}`
}