import moderacionData from '@/data/admin/moderacion.json'
import usuariosData from '@/data/admin/usuarios.json'
import estadisticasData from '@/data/admin/estadisticas.json'
import plataformaData from '@/data/admin/plataforma.json'
import trazabilidadData from '@/data/admin/trazabilidad.json'
import comparadorData from '@/data/admin/comparador.json'
import prometheusData from '@/data/admin/prometheus.json'
import { adminApi } from '@/api/endpoints'

const LATENCIA_SIMULADA_MS = 350
const latencia = (ms = LATENCIA_SIMULADA_MS) => new Promise((resolve) => setTimeout(resolve, ms))

const clon = (v) => JSON.parse(JSON.stringify(v))

const casos = moderacionData.casos.map((c) => ({ ...c }))
const cuentas = usuariosData.usuarios.map((u) => ({ ...u }))
const ajustes = resilienciaData.ajustes.map((a) => ({ ...a }))
let breakerEstado = resilienciaData.breakerEstado

/* ── 7.1 Moderación ── */
export async function getModeracion() {
  await latencia()
  return {
    stats: clon(moderacionData.stats),
    pestanas: clon(moderacionData.pestanas),
    casos: clon(casos)
  }
}

export async function ocultarCaso(id) {
  await latencia()
  const caso = casos.find((c) => c.id === id)
  if (!caso) throw new Error('No encontramos ese caso en el Tribunal de Vigilancia.')
  caso.estado = 'oculto'
  return { ...caso }
}

export async function restaurarCaso(id) {
  await latencia()
  const caso = casos.find((c) => c.id === id)
  if (!caso) throw new Error('No encontramos ese caso en el Tribunal de Vigilancia.')
  caso.estado = 'pendiente'
  return { ...caso }
}

export async function eliminarCaso(id) {
  await latencia()
  const i = casos.findIndex((c) => c.id === id)
  if (i < 0) throw new Error('Ese contenido ya había sido purgado.')
  const [eliminado] = casos.splice(i, 1)
  return { id: eliminado.id }
}

/* ── 7.2 Usuarios ── */
export async function getAdminUsuarios(filtros = {}) {
  await latencia()
  const termino = (filtros.busqueda || '').trim().toLowerCase()
  const lista = cuentas.filter((u) => {
    const porEstado = !filtros.estado || filtros.estado === 'todos' || u.estado === filtros.estado
    const porTexto =
      !termino ||
      `${u.nombre} ${u.handle} ${u.email} ${u.rol}`.toLowerCase().includes(termino)
    return porEstado && porTexto
  })
  return {
    stats: clon(usuariosData.stats),
    usuarios: clon(lista),
    total: cuentas.length
  }
}

export async function suspenderUsuario(id) {
  await latencia()
  const cuenta = cuentas.find((u) => u.id === id)
  if (!cuenta) throw new Error('No encontramos esa cuenta en el padrón del gremio.')
  cuenta.estado = 'suspendido'
  return { ...cuenta }
}

export async function activarUsuario(id) {
  await latencia()
  const cuenta = cuentas.find((u) => u.id === id)
  if (!cuenta) throw new Error('No encontramos esa cuenta en el padrón del gremio.')
  cuenta.estado = 'activo'
  return { ...cuenta }
}

/* ── 7.3 Estadísticas y logs ── */
export async function getEstadisticas() {
  await latencia(450)
  return clon(estadisticasData)
}

/* ── 7.4 Plataforma ── */
export async function getPlataforma() {
  await latencia()
  return clon(plataformaData)
}

/* ── 7.5 Trazabilidad ── */
export async function getTrazabilidad() {
  await latencia(450)
  return clon(trazabilidadData)
}

/* ── 7.6 Observabilidad ── */
const SERVICIOS = ['mesas', 'builds', 'feed', 'notif']

export async function getObservabilidad() {
  const servicios = []
  const alertas = []
  for (const nombre of SERVICIOS) {
    let estado = 'sin_datos'
    let dependencias = null
    let detalle = 'sin datos'
    try {
      const live = await adminApi.live(nombre)
      if (live.datos?.estado === 'vivo') {
        try {
          const rd = await adminApi.ready(nombre)
          dependencias = rd.datos?.dependencias ?? null
          estado = rd.datos?.estado ?? 'degradado'
          detalle = estado === 'listo' ? 'Listo' : 'Degradado'
        } catch {
          estado = 'degradado'
          detalle = 'Dependencias no responden'
        }
      } else {
        detalle = 'Servicio apagado'
      }
    } catch {
      estado = 'sin_datos'
      detalle = 'Sin datos del operador'
      alertas.push(`Sin datos del operador: ${nombre}`)
    }
    if (estado === 'degradado') {
      alertas.push(`${nombre} degradado: ${JSON.stringify(dependencias ?? {})}`)
    }
    servicios.push({
      id: nombre,
      nombre: nombre.toUpperCase(),
      estado,
      detalle,
      dependencias,
      tono: estado === 'listo' ? 'verde' : estado === 'degradado' ? 'ocre' : 'gris',
      salud: estado === 'listo' ? 100 : estado === 'degradado' ? 60 : 0,
      latencia: detalle,
      uptime: ''
    })
  }

  let logs = []
  try {
    const { datos } = await adminApi.eventLog()
    logs = datos.slice(0, 20).map((e, i) => ({
      id: i,
      timestamp: formatearHora(e.ocurridoEn),
      nivel: 'INFO',
      servicio: 'notif',
      mensaje: `evento ${e.accion} · ${e.entidadTipo ?? ''}`,
      correlationId: e.correlationId || '-'
    })).filter((l) => l.correlationId !== '-')
  } catch {
    // notif-api caído: logs sin datos, no rompe el panel
  }

  return { servicios, alertas, logs }
}

function formatearHora(iso) {
  if (!iso) return '-'
  try {
    return new Date(iso).toLocaleTimeString('es-CO', { hour12: false })
  } catch {
    return '-'
  }
}

/* ── 7.7 DLQ ── */
export async function getDlq() {
  const { datos } = await adminApi.dlq()
  return {
    mensajes: datos.map((m) => ({
      id: m.id,
      nombre: (m.payload?.tipo ?? m.cola) || 'evento',
      cola: m.cola,
      reintentos: typeof m.payload?._intentos === 'number' ? m.payload._intentos : 3,
      fecha: m.fecha,
      error: m.error,
      payload: JSON.stringify(m.payload, null, 2),
      correlationId: m.payload?.correlation_id ?? '-'
    }))
  }
}

export async function reintentarMensaje(id) {
  const { datos } = await adminApi.reintentarDlq(id)
  return { id: datos.id, nombre: 'reintentado' }
}

export async function descartarMensaje(id) {
  await adminApi.descartarDlq(id)
  return { id }
}

export async function drenarCola() {
  const { datos } = await adminApi.dlq()
  let total = 0
  for (const m of datos) {
    await adminApi.descartarDlq(m.id)
    total += 1
  }
  return { total }
}

/* ── 7.8 Resiliencia ── */
export async function getResiliencia() {
  const broker = { redis: false, rabbitmq: false, postgres: false }
  let estadoBroker = 'sin_datos'
  try {
    const rd = await adminApi.ready('mesas')
    Object.assign(broker, rd.datos?.dependencias ?? {})
    estadoBroker = rd.datos?.estado ?? 'degradado'
  } catch {
    estadoBroker = 'sin_datos'
  }
  let dlqTotal = 0
  try {
    const { datos } = await adminApi.dlq()
    dlqTotal = datos.length
  } catch {
    dlqTotal = 0
  }
  breakerEstado = estadoBroker === 'listo' ? 'CERRADO' : 'ABIERTO'
  const ajusteBroker = ajustes.find((a) => a.id === 'cb-umbral')
  if (ajusteBroker) {
    ajusteBroker.badge = {
      texto: breakerEstado,
      tono: breakerEstado === 'CERRADO' ? 'verde' : 'rojo'
    }
  }
  return {
    breakerEstado,
    estadoBroker,
    broker,
    dlqTotal,
    ajustes: clon(ajustes)
  }
}

export async function guardarResiliencia(limites) {
  await latencia(450)
  Object.entries(limites).forEach(([id, valor]) => {
    const ajuste = ajustes.find((a) => a.id === id)
    if (!ajuste) throw new Error(`No existe el parámetro de resiliencia «${id}».`)
    const numero = Number(valor)
    if (Number.isNaN(numero) || numero < ajuste.min || numero > ajuste.max) {
      throw new Error(`El valor de «${ajuste.label}» debe estar entre ${ajuste.min} y ${ajuste.max}.`)
    }
    ajuste.valor = numero
  })
  return { breakerEstado, ajustes: clon(ajustes) }
}

export async function simularCaida() {
  return getResiliencia()
}

/* ── 7.9 Comparador ── */
export async function getComparador() {
  await latencia()
  return clon(comparadorData)
}

/* ── 7.10 Prometheus ── */
export async function consultarMetrica(query) {
  await latencia(450)
  if (!query || !query.trim()) throw new Error('La consulta PromQL no puede estar vacía.')
  return { resultado: prometheusData.resultado }
}

export async function getPrometheus() {
  await latencia()
  return clon(prometheusData)
}
