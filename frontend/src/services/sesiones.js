// Sesiones, bitácora y diario (mesas-api / feed-api).
import { api } from '@/api/http'

export async function getSesiones(mesaId) {
  const { mesasApi } = await import('@/api/endpoints')
  const { datos } = await mesasApi.sesiones(mesaId)
  return (datos ?? []).map((s) => ({
    id: s.id,
    mesaId: s.mesa_id,
    estado: s.estado,
    fecha: s.fecha,
    confirmadaAt: s.confirmada_at,
    diario: null
  }))
}

export async function getSesion(mesaId, sesionId) {
  const lista = await getSesiones(mesaId)
  const sesion = lista.find((s) => String(s.id) === String(sesionId))
  if (!sesion) {
    throw new Error(`No encontramos la sesión «${sesionId}» en el archivo de campaña.`)
  }
  return { ...sesion }
}

export async function registrarDiario(mesaId, sesionId) {
  return getSesion(mesaId, sesionId)
}

export async function getAnotaciones(mesaId, sesionId) {
  const { datos } = await api(
    'mesas',
    `/api/v1/mesas/${mesaId}/sesiones/${sesionId}/anotaciones`
  )
  return (datos ?? [])
    .map((a) => ({
      id: a.id,
      sesionId: a.sesion_id,
      texto: a.texto,
      autor: a.autor_nombre,
      autorId: a.autor_id,
      creadoEn: a.creado_en
    }))
    .sort((x, y) => String(x.creadoEn).localeCompare(String(y.creadoEn)))
}

export async function registrarAnotacion(mesaId, sesionId, texto, usuario = {}) {
  const limpio = (texto || '').trim()
  if (!limpio) {
    const e = new Error('El texto de la anotación no puede estar vacío.')
    e.codigo = '400'
    throw e
  }
  const { datos } = await api(
    'mesas',
    `/api/v1/mesas/${mesaId}/sesiones/${sesionId}/anotaciones`,
    { metodo: 'POST', cuerpo: { texto: limpio } }
  )
  return datos
}