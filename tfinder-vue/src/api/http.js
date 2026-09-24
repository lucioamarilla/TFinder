import { apiUrl } from '@/config/api'
import { currentAccessToken, clearSession } from '@/composables/useAuth'

const TIMEOUT_MS = 8000
const SERVICIOS_NOMBRES = { mesas: 'mesas-api (8001)', builds: 'builds-api (8002)', feed: 'feed-api (8003)', notif: 'notif-api (8004)' }

export class ApiError extends Error {
  constructor(codigo, mensaje, detalles = null) {
    super(mensaje)
    this.name = 'ApiError'
    this.codigo = codigo
    this.mensaje = mensaje
    this.detalles = detalles
  }
}

function tokenActual() {
  return currentAccessToken()
}

export async function api(servicio, ruta, { metodo = 'GET', cuerpo = null, idempotenciaKey = null, timeoutMs = TIMEOUT_MS } = {}) {
  const controlador = new AbortController()
  const timer = setTimeout(() => controlador.abort(), timeoutMs)
  const solicitado = idempotenciaKey || idAleatorio()

  const cabeceras = {
    'Content-Type': 'application/json',
    'X-Correlation-Id': idAleatorio()
  }
  const token = tokenActual()
  if (token) cabeceras.Authorization = `Bearer ${token}`
  if (cuerpo != null) cabeceras['Idempotency-Key'] = solicitado

  let respuesta
  try {
    respuesta = await fetch(apiUrl(servicio, ruta), {
      method: metodo,
      headers: cabeceras,
      body: cuerpo != null ? JSON.stringify(cuerpo) : undefined,
      signal: controlador.signal
    })
  } catch (e) {
    clearTimeout(timer)
    const esTimeout = e.name === 'AbortError'
    throw new ApiError(
      'timeout',
      esTimeout
        ? `El servicio ${nombreServicio} no respondió en ${timeoutMs} ms.`
        : `No se pudo conectar con el servicio ${nombreServicio}. Revisá que esté levantado.`
    )
  }
  clearTimeout(timer)

  if (respuesta.status === 401) {
    clearSession()
    window.location.assign(`/login?redirect=${encodeURIComponent(window.location.pathname + window.location.search)}`)
    throw new ApiError('unauthorized', 'Sesión expirada o inválida.')
  }

  let datos = null
  try {
    datos = await respuesta.json()
  } catch {
    /* 204 o sin cuerpo */
  }

  if (!respuesta.ok) {
    const err = datos?.error ?? { codigo: respuesta.status, mensaje: `HTTP ${respuesta.status}` }
    throw new ApiError(err.codigo, err.mensaje, err.detalles ?? null)
  }

    const encabezados = {}
  if (respuesta.headers?.forEach) {
    respuesta.headers.forEach((v, k) => { encabezados[k.toLowerCase()] = v })
  } else {
    for (const [k, v] of Object.entries(respuesta.headers || {})) {
      encabezados[(k || '').toLowerCase()] = v
    }
  }

  return { status: respuesta.status, datos, idempotenciaKey: solicitado, encabezados }
}
