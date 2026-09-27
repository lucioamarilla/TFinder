import { notifApi } from '@/api/endpoints'

export function formatearFecha(valor) {
  if (!valor) return null
  const fecha = new Date(valor)
  if (Number.isNaN(fecha.getTime())) return String(valor)
  return fecha.toLocaleString('es-CO', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function normalizarEnlace(enlace) {
  if (!enlace || typeof enlace !== 'object' || !enlace.to) return null
  return { label: enlace.label || 'Ver detalle', to: enlace.to }
}

export function normalizarNotificacion(n) {
  return {
    ...n,
    grupo: n.grupo ?? 'mesas',
    icono: n.icono ?? 'solicitud',
    autor: n.autor ?? null,
    leida: Boolean(n.leida),
    fecha: formatearFecha(n.creado_en ?? n.fecha),
    enlace: normalizarEnlace(n.enlace)
  }
}

export async function getNotificaciones() {
  const { datos } = await notifApi.notificaciones()
  return (datos ?? []).map(normalizarNotificacion)
}

export async function marcarLeida(id) {
  const { datos } = await notifApi.marcarLeida(id)
  return datos ? normalizarNotificacion(datos) : datos
}

export async function marcarTodasLeidas() {
  const pendientes = (await getNotificaciones()).filter((n) => !n.leida)
  await Promise.all(pendientes.map((n) => notifApi.marcarLeida(n.id)))
  return true
}
