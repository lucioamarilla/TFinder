import moderacionData from '@/data/admin/moderacion.json'
import usuariosData from '@/data/admin/usuarios.json'
import estadisticasData from '@/data/admin/estadisticas.json'
import plataformaData from '@/data/admin/plataforma.json'
import trazabilidadData from '@/data/admin/trazabilidad.json'
import observabilidadData from '@/data/admin/observabilidad.json'
import dlqData from '@/data/admin/dlq.json'
import resilienciaData from '@/data/admin/resiliencia.json'
import comparadorData from '@/data/admin/comparador.json'
import prometheusData from '@/data/admin/prometheus.json'

const LATENCIA_SIMULADA_MS = 350
const latencia = (ms = LATENCIA_SIMULADA_MS) => new Promise((resolve) => setTimeout(resolve, ms))

const clon = (v) => JSON.parse(JSON.stringify(v))

const casos = moderacionData.casos.map((c) => ({ ...c }))
const cuentas = usuariosData.usuarios.map((u) => ({ ...u }))
const mensajesDlq = dlqData.mensajes.map((m) => ({ ...m }))
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
export async function getObservabilidad() {
  await latencia(450)
  return clon(observabilidadData)
}

/* ── 7.7 DLQ ── */
export async function getDlq() {
  await latencia()
  return { mensajes: clon(mensajesDlq) }
}

export async function reintentarMensaje(id) {
  await latencia(400)
  const i = mensajesDlq.findIndex((m) => m.id === id)
  if (i < 0) throw new Error('Ese mensaje ya salió de la cola de fallidos.')
  const [m] = mensajesDlq.splice(i, 1)
  return { id: m.id, nombre: m.nombre }
}

export async function descartarMensaje(id) {
  await latencia()
  const i = mensajesDlq.findIndex((m) => m.id === id)
  if (i < 0) throw new Error('Ese mensaje ya salió de la cola de fallidos.')
  const [m] = mensajesDlq.splice(i, 1)
  return { id: m.id, nombre: m.nombre }
}

export async function drenarCola() {
  await latencia(450)
  const total = mensajesDlq.length
  mensajesDlq.splice(0, mensajesDlq.length)
  return { total }
}

/* ── 7.8 Resiliencia ── */
export async function getResiliencia() {
  await latencia()
  return { breakerEstado, ajustes: clon(ajustes) }
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
  await latencia(400)
  breakerEstado = 'ABIERTO'
  const cb = ajustes.find((a) => a.id === 'cb-umbral')
  if (cb) cb.badge = { texto: 'ABIERTO', tono: 'rojo' }
  return { breakerEstado, ajustes: clon(ajustes) }
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
