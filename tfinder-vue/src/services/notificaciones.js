import { notifApi } from '@/api/endpoints'

export async function getNotificaciones() {
  const { datos } = await notifApi.notificaciones()
  return datos ?? []
}

export async function marcarLeida(id) {
  const { datos } = await notifApi.marcarLeida(id)
  return datos
}

export async function marcarTodasLeidas() {
  const noLeidas = (await getNotificaciones()).filter((n) => !n.leida)
  await Promise.all(noLeidas.map((n) => notifApi.marcarLeida(n.id)))
  return getNotificaciones()
}

export async function getNoLeidas() {
  const { datos } = await notifApi.notificaciones(true)
  return (datos ?? []).length
}
