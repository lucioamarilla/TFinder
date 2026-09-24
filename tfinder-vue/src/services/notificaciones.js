import { notifApi } from '@/api/endpoints'

function mapearEnlace(enlace) {
  if (!enlace) return null
  if (typeof enlace === 'string') return { label: 'Ver', to: enlace }
  const par = Object.entries(enlace)[0]
  if (!par) return null
  return { label: par[1] || 'Ver', to: par[0] }
}

function mapear(n) {
  return {
    id: n.id,
    grupo: n.grupo,
    icono: n.icono,
    leida: Boolean(n.leida),
    autor: n.autor,
    mensaje: n.mensaje,
    entidad: n.entidad,
    detalle: n.detalle,
    enlace: mapearEnlace(n.enlace),
    fecha: formatearFecha(n.creado_en)
  }
}

function formatearFecha(iso) {
  if (!iso) return 'recientemente'
  try {
    return new Intl.DateTimeFormat('es-CO', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(iso))
  } catch {
    return 'recientemente'
  }
}

export async function getNotificaciones() {
  const { datos } = await notifApi.notificaciones()
  return datos.map(mapear)
}

export async function marcarLeida(id) {
  const { datos } = await notifApi.marcarLeida(id)
  return mapear(datos)
}

export async function marcarTodasLeidas() {
  const { datos } = await notifApi.notificaciones()
  await Promise.all(datos.filter((n) => !n.leida).map((n) => notifApi.marcarLeida(n.id)))
  return getNotificaciones()
}

export async function getNoLeidas() {
  const { datos } = await notifApi.notificaciones()
  return datos.filter((n) => !n.leida).length
}