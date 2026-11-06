// F09/D-15: consola admin contra notif-api real (roles 'admin').
// Endpoints verificados: GET /event-log, GET/POST/DELETE /dlq, GET /emails.
import { api } from '@/api/http'

function peticion(ruta, opciones = {}) {
  return api('notif', ruta, opciones)
}

export async function getEventos(params = {}) {
  const q = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '')
  ).toString()
  const { datos } = await peticion(`/api/v1/event-log${q ? `?${q}` : ''}`)
  return datos ?? []
}

export async function getDlq(limite = 50) {
  const { datos } = await peticion(`/api/v1/dlq?limite=${limite}`)
  return datos ?? []
}

export async function reintentarDlq(id) {
  const { datos } = await peticion(`/api/v1/dlq/${id}/reintentar`, { metodo: 'POST' })
  return datos ?? { id }
}

export async function descartarDlq(id) {
  await peticion(`/api/v1/dlq/${id}`, { metodo: 'DELETE' })
  return true
}

export async function getEmails(limite = 50) {
  const { datos } = await peticion(`/api/v1/emails?limite=${limite}`)
  return datos ?? []
}

export async function reintentarEmail(id) {
  const { datos } = await peticion(`/api/v1/emails/${id}/reintentar`, { metodo: 'POST' })
  return datos ?? { id, estado: 'enviado' }
}
