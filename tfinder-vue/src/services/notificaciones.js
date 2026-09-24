import notificacionesData from '@/data/notificaciones.json'

const LATENCIA_SIMULADA_MS = 250

const latencia = () => new Promise((resolve) => setTimeout(resolve, LATENCIA_SIMULADA_MS))

const catalogo = notificacionesData.notificaciones.map((n) => ({
  ...n,
  enlace: n.enlace ? { ...n.enlace } : null
}))

function clonar(notificacion) {
  return { ...notificacion, enlace: notificacion.enlace ? { ...notificacion.enlace } : null }
}

export async function getNotificaciones() {
  await latencia()
  return catalogo.map(clonar)
}

export async function marcarLeida(id) {
  await latencia(150)
  const notificacion = catalogo.find((n) => n.id === id)
  if (!notificacion) throw new Error('No encontramos ese aviso del cónclave.')
  notificacion.leida = true
  return clonar(notificacion)
}

export async function marcarTodasLeidas() {
  await latencia(280)
  catalogo.forEach((n) => {
    n.leida = true
  })
  return catalogo.map(clonar)
}

export async function getNoLeidas() {
  await latencia(120)
  return catalogo.filter((n) => !n.leida).length
}
