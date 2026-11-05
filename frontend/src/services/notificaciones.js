// Notificaciones reales (notif-api).
import { notifApi } from '@/api/endpoints'

function normalizarApiSur(n) {
  return {
    id: n.id,
    texto: n.mensaje || n.detalle || 'Novedad de TFinder',
    link: (n.enlace && n.enlace.to) || '/feed',
    tiempo: n.fecha || '',
    leida: !!n.leida,
    para: n.usuarioId ? String(n.usuarioId) : null
  }
}

export async function getNotificaciones() {
  const { datos } = await notifApi.notificaciones()
  return (datos ?? []).map(normalizarApiSur)
}

export async function marcarLeida(id) {
  const { datos } = await notifApi.marcarLeida(id)
  return normalizarApiSur(datos ?? { id, leida: true })
}

export async function marcarTodasLeidas() {
  await notifApi.leerTodas()
  return getNotificaciones()
}

export async function getNoLeidas() {
  const lista = await getNotificaciones()
  return lista.filter((n) => !n.leida).length
}