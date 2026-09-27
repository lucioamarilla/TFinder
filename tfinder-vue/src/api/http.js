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

function idAleatorio() {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`
}

function tokenActual() {
  return currentAccessToken()
}

function leerEncabezados(respuesta) {
  const encabezados = {}
  if (respuesta.headers?.forEach) {
    respuesta.headers.forEach((v, k) => { encabezados[k.toLowerCase()] = v })
  } else {
    for (const [k, v] of Object.entries(respuesta.headers || {})) {
      encabezados[(k || '').toLowerCase()] = v
    }
  }
  return encabezados
}

function errorDe(respuesta, datos) {
  return datos?.error ?? { codigo: respuesta.status, mensaje: `HTTP ${respuesta.status}` }
}

const OPCIONES_POR_DEFECTO = { metodo: 'GET', cuerpo: null, idempotenciaKey: null, timeoutMs: TIMEOUT_MS, aceptarEstados: null }

async function enviar(servicio, ruta, opciones) {
  const { metodo, cuerpo, idempotenciaKey, timeoutMs } = { ...OPCIONES_POR_DEFECTO, ...opciones }
  const nombreServicio = SERVICIOS_NOMBRES[servicio] ?? servicio
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
    const esTimeout = e.name === 'AbortError'
    throw new ApiError(
      'timeout',
      esTimeout
        ? `El servicio ${nombreServicio} no respondió en ${timeoutMs} ms.`
        : `No se pudo conectar con el servicio ${nombreServicio}. Revisá que esté levantado.`
    )
  } finally {
    clearTimeout(timer)
  }

  if (respuesta.status === 401) {
    clearSession()
    window.location.assign(`/login?redirect=${encodeURIComponent(window.location.pathname + window.location.search)}`)
    throw new ApiError('unauthorized', 'Sesión expirada o inválida.')
  }

  return { respuesta, solicitado }
}

export async function api(servicio, ruta, opciones = {}) {
  const { aceptarEstados } = { ...OPCIONES_POR_DEFECTO, ...opciones }
  const { respuesta, solicitado } = await enviar(servicio, ruta, opciones)

  let datos = null
  try {
    datos = await respuesta.json()
  } catch {
    /* 204 o sin cuerpo */
  }

  // Un 503 puede venir con el body que el cliente necesita leer (ej. /ready
  // responde degradado con el detalle de dependencias). Por defecto no cambia
  // nada: sin la opción, cualquier no-2xx sigue lanzando ApiError.
  const aceptado = respuesta.ok || (Array.isArray(aceptarEstados) && aceptarEstados.includes(respuesta.status))

  if (!aceptado) {
    const err = errorDe(respuesta, datos)
    throw new ApiError(err.codigo, err.mensaje, err.detalles ?? null)
  }

  return { status: respuesta.status, datos, idempotenciaKey: solicitado, encabezados: leerEncabezados(respuesta) }
}

export async function apiBlob(servicio, ruta, opciones = {}) {
  const { respuesta, solicitado } = await enviar(servicio, ruta, opciones)

  if (!respuesta.ok) {
    let datos = null
    try {
      datos = await respuesta.json()
    } catch {
      /* cuerpo no-JSON */
    }
    const err = errorDe(respuesta, datos)
    throw new ApiError(err.codigo, err.mensaje, err.detalles ?? null)
  }

  return { status: respuesta.status, blob: await respuesta.blob(), idempotenciaKey: solicitado, encabezados: leerEncabezados(respuesta) }
}