import { apiUrl } from '@/config/api'
import { currentAccessToken, clearSession } from '@/composables/useAuth'

export class ApiError extends Error {
  constructor(codigo, mensaje, detalles) {
    super(mensaje)
    this.codigo = codigo
    this.detalles = detalles
  }
}

function idAleatorio() {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`
}

export async function api(
  servicio,
  ruta,
  { metodo = 'GET', cuerpo, idempotenciaKey, timeoutMs = 8000 } = {}
) {
  const controlador = new AbortController()
  const timer = setTimeout(() => controlador.abort(), timeoutMs)
  const solicitado = idempotenciaKey || idAleatorio()

  const cabeceras = {
    'Content-Type': 'application/json',
    'X-Correlation-Id': idAleatorio()
  }
  const token = currentAccessToken()
  if (token) cabeceras.Authorization = `Bearer ${token}`
  if (cuerpo != null) cabeceras['Idempotency-Key'] = solicitado

  try {
    const resp = await fetch(apiUrl(servicio, ruta), {
      method: metodo,
      headers: cabeceras,
      body: cuerpo != null ? JSON.stringify(cuerpo) : undefined,
      signal: controlador.signal
    })
    if (resp.status === 401) {
      clearSession()
      window.location.assign(
        `/login?redirect=${encodeURIComponent(location.pathname)}`
      )
      throw new ApiError(401, 'Sesión expirada')
    }
    let datos = null
    try {
      datos = await resp.json()
    } catch {
      /* 204 o cuerpo vacío */
    }
    if (!resp.ok) {
      const err = datos?.error ?? {
        codigo: resp.status,
        mensaje: `HTTP ${resp.status}`
      }
      throw new ApiError(err.codigo, err.mensaje, datos)
    }
    return { status: resp.status, datos, idempotenciaKey: solicitado }
  } finally {
    clearTimeout(timer)
  }
}