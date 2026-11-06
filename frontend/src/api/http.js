import { apiUrl } from '@/config/api'
import { currentAccessToken, clearSession, renovarSesion } from '@/composables/useAuth'

// F2 (2.1 renovación): una llamada que reciba 401 renovándose una vez corra
// recursión única con la MISMA Idempotency-Key. El flag por-invocación
// (sinRenovacion) evita bucles; el de módulo serializa renovaciones paralelas.
let renovandoEnCurso = false

const TIMEOUT_MS = 8000
const MAX_INTENTOS = 3
const BACKOFF_BASE_MS = 200

// Circuit breaker simple por servicio (cerrado/abierto/semiabierto).
const circuitos = {}
function circuito(servicio) {
  if (!circuitos[servicio]) {
    circuitos[servicio] = { estado: 'cerrado', fallos: 0, abiertoDesde: 0, umbral: 5, recuperacion: 30000 }
  }
  return circuitos[servicio]
}
function puedePasar(cb) {
  if (cb.estado === 'cerrado') return true
  if (cb.estado === 'abierto' && Date.now() - cb.abiertoDesde >= cb.recuperacion) {
    cb.estado = 'semiabierto'
    return true
  }
  return cb.estado === 'semiabierto'
}
function registrarExito(cb) {
  cb.fallos = 0
  cb.estado = 'cerrado'
}
function registrarFallo(cb) {
  cb.fallos += 1
  if (cb.fallos >= cb.umbral) {
    cb.estado = 'abierto'
    cb.abiertoDesde = Date.now()
  }
}
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

export async function api(servicio, ruta, opciones = {}) {
  const { sinRenovacion = false, ...resto } = opciones
  const inicial = await apiInterna(servicio, ruta, resto)
  if (inicial?.status === 401 && !sinRenovacion) {
    // La lógica de renovación vive DENTRO de apiInterna: si dejó la marca
    // 'renovado', la respuesta fue consumida y reintentada en el mismo lugar.
    if (inicial.renuevo) {
      // apiInterna ya reintentó y devolvió la respuesta final.
      return inicial
    }
  }
  return inicial
}

async function apiInterna(
  servicio,
  ruta,
  { metodo = 'GET', cuerpo = null, idempotenciaKey = null, timeoutMs = TIMEOUT_MS, sinRenovacion = false } = {}
) {
  const nombreServicio = SERVICIOS_NOMBRES[servicio] ?? servicio
  const cb = circuito(servicio)
  let respuesta = null
  let ultimoError = null
  // La Idempotency-Key es ÚNICA por petición lógica: los reintentos reenvían la
  // misma clave (para eso existe). Se genera una sola vez acá.
  const solicitado = idempotenciaKey || idAleatorio()

  // Cada reintento vive y muere con su propio AbortController: un timeout del
  // intento 1 no puede abortar los fetch de los intentos siguientes.
  let ultimoToken = null
  for (let intento = 0; intento < MAX_INTENTOS; intento++) {
    if (!puedePasar(cb)) {
      throw new ApiError('circuit_open', `El servicio ${nombreServicio} está temporalmente no disponible.`)
    }
    const controlador = new AbortController()
    const timer = setTimeout(() => controlador.abort(), timeoutMs)
    const cabeceras = {
      'Content-Type': 'application/json',
      'X-Correlation-Id': idAleatorio()
    }
    const token = tokenActual()
    ultimoToken = token
    if (token) cabeceras.Authorization = `Bearer ${token}`
    if (cuerpo != null) cabeceras['Idempotency-Key'] = solicitado

    try {
      respuesta = await fetch(apiUrl(servicio, ruta), {
        method: metodo,
        headers: cabeceras,
        body: cuerpo != null ? JSON.stringify(cuerpo) : undefined,
        signal: controlador.signal
      })
      if (respuesta.status === 429) {
        // RNF-22: el backend firma Retry-After. Reintentar una vez tras esperar
        // (tope 5s) para no bloquear la UI; si persiste, propagar el error con
        // un mensaje claro en vez de "Mesa no encontrada"/"vacío".
        const espera = Math.min(5000, (Number(respuesta.headers?.get?.('Retry-After') || respuesta.headers?.['retry-after'] || 1) || 1) * 1000)
        ultimoError = new ApiError(429, 'Demasiadas peticiones: esperá un momento y reintentá.')
        if (intento < MAX_INTENTOS - 1) {
          await new Promise((r) => setTimeout(r, espera))
          continue
        }
        registrarFallo(cb)
        clearTimeout(timer)
        break
      }
      if (respuesta.status >= 500) {
        registrarFallo(cb)
        ultimoError = new ApiError(respuesta.status, `HTTP ${respuesta.status}`)
        await new Promise((r) => setTimeout(r, BACKOFF_BASE_MS * (2 ** intento)))
        continue
      }
      registrarExito(cb)
      clearTimeout(timer)
      break
    } catch (e) {
      clearTimeout(timer)
      registrarFallo(cb)
      ultimoError = new ApiError('timeout', e.name === 'AbortError'
        ? `El servicio ${nombreServicio} no respondió en ${timeoutMs} ms.`
        : `No se pudo conectar con el servicio ${nombreServicio}. Revisá que esté levantado.`)
      await new Promise((r) => setTimeout(r, BACKOFF_BASE_MS * (2 ** intento)))
    }
  }
  if (!respuesta) {
    throw ultimoError || new ApiError('timeout', `El servicio ${nombreServicio} no respondió.`)
  }

  if (respuesta.status === 401) {
    const esEndpointPublico =
      ruta.startsWith('/api/v1/auth/login') || ruta.startsWith('/api/v1/auth/register') ||
      ruta.startsWith('/api/v1/auth/refresh')
    if (ultimoToken && !esEndpointPublico && !sinRenovacion && !renovandoEnCurso) {
      const marca = { renovado: false }
      renovandoEnCurso = true
      const renovada = await renovarSesion()
      renovandoEnCurso = false
      if (renovada) {
        // Recursión única con la MISMA Idempotency-Key y el token nuevo.
        return { ...(await apiInterna(servicio, ruta, { metodo, cuerpo, idempotenciaKey: solicitado, timeoutMs, sinRenovacion: true })), renuevo: true, _marca: marca }
      }
    }
    if (ultimoToken && !esEndpointPublico) {
      clearSession()
      const destino = `/login?redirect=${encodeURIComponent(window.location.pathname + window.location.search)}&sesion=expirada`
      window.location.assign(destino)
      // La navegación se encarga de sacar al usuario; no propagamos el error
      // para que la vista no muestre un toast duplicado mientras se descarga.
      await new Promise(() => {})
    }
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