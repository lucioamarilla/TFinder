export const BASE = {
  mesas: import.meta.env.VITE_MESAS_API ?? 'http://localhost:8001'
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