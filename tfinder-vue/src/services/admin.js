import { adminApi, notifApi } from '@/api/endpoints'
import { formatearFecha } from '@/services/notificaciones'
import moderacionData from '@/data/admin/moderacion.json'
import usuariosData from '@/data/admin/usuarios.json'
import estadisticasData from '@/data/admin/estadisticas.json'
import plataformaData from '@/data/admin/plataforma.json'
import trazabilidadData from '@/data/admin/trazabilidad.json'
import resilienciaData from '@/data/admin/resiliencia.json'
import comparadorData from '@/data/admin/comparador.json'
import prometheusData from '@/data/admin/prometheus.json'

const LATENCIA_SIMULADA_MS = 350
const latencia = (ms = LATENCIA_SIMULADA_MS) => new Promise((resolve) => setTimeout(resolve, ms))

const clon = (v) => JSON.parse(JSON.stringify(v))

const casos = moderacionData.casos.map((c) => ({ ...c }))
const cuentas = usuariosData.usuarios.map((u) => ({ ...u }))
const ajustes = resilienciaData.ajustes.map((a) => ({ ...a }))

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

/* ── 7.6 Observabilidad (real: /live y /ready de los 4 servicios) ── */
const SERVICIOS = [
  { id: 'mesas', nombre: 'mesas-api' },
  { id: 'builds', nombre: 'builds-api' },
  { id: 'feed', nombre: 'feed-api' },
  { id: 'notif', nombre: 'notif-api' }
]

const DEPENDENCIAS = [
  { clave: 'postgres', nombre: 'PostgreSQL' },
  { clave: 'redis', nombre: 'Redis' },
  { clave: 'rabbitmq', nombre: 'RabbitMQ' }
]

function tonoDe(live, estadoReady) {
  if (!live) return 'gris'
  return estadoReady === 'listo' ? 'verde' : estadoReady === 'degradado' ? 'ocre' : 'gris'
}

function dependenciasDe(mapa) {
  return DEPENDENCIAS.map((d) => ({ ...d, ok: Boolean(mapa?.[d.clave]) }))
}

export async function estadoDe(servicioId) {
  const meta = SERVICIOS.find((s) => s.id === servicioId) ?? { id: servicioId, nombre: servicioId }
  const canal = { id: meta.id, nombre: meta.nombre, live: false, ready: 'sin_datos', dependencias: [], detalle: null }

  try {
    const { datos } = await adminApi.live(meta.id)
    canal.live = datos?.estado === 'vivo'
  } catch (e) {
    canal.detalle = e.mensaje || e.message
  }

  try {
    // /ready responde 503 con el detalle de dependencias cuando algo está caído;
    // adminApi.ready lo acepta para que ese body sea legible.
    const { datos } = await adminApi.ready(meta.id)
    canal.ready = datos?.estado ?? 'sin_datos'
    canal.dependencias = dependenciasDe(datos?.dependencias)
  } catch (e) {
    canal.detalle = e.mensaje || e.message
  }

  canal.tono = tonoDe(canal.live, canal.ready)
  return canal
}

export async function getCanalesReales() {
  return Promise.all(SERVICIOS.map((s) => estadoDe(s.id)))
}

export async function getEventosRecorridos(filtro = {}) {
  const { datos } = await notifApi.eventLog(filtro)
  return (datos ?? []).map((e) => ({
    id: e.id,
    ocurridoEn: formatearFecha(e.ocurridoEn) ?? '—',
    entidad: e.entidadId ? `${e.entidadTipo} #${e.entidadId}` : (e.entidadTipo ?? '—'),
    accion: e.accion ?? '—',
    correlationId: e.correlationId ?? null,
    metadata: e.metadata ?? null
  }))
}

/* ── 7.7 DLQ (real: GET /dlq, POST /dlq/{id}/reintentar, DELETE /dlq/{id}) ── */
function normalizarMensaje(m) {
  let payload = m.payload
  if (typeof payload === 'string') {
    try {
      payload = JSON.parse(payload)
    } catch {
      /* el backend puede mandar un payload que no es JSON */
    }
  }
  return {
    id: m.id,
    cola: m.cola ?? '—',
    tipo: payload?.tipo ?? m.cola ?? 'desconocido',
    error: m.error ?? '',
    fecha: formatearFecha(m.fecha) ?? '—',
    payload
  }
}

export async function getDlq() {
  const { datos } = await adminApi.dlq()
  return { mensajes: (datos ?? []).map(normalizarMensaje) }
}

export async function reintentarMensaje(id) {
  const { datos } = await adminApi.reintentarDlq(id)
  return { id: datos?.id ?? id, cola: datos?.cola ?? null }
}

export async function descartarMensaje(id) {
  await adminApi.descartarDlq(id)
  return { id }
}

export async function drenarCola({ alProgresar } = {}) {
  const { mensajes } = await getDlq()
  const total = mensajes.length
  let hechos = 0
  for (const mensaje of mensajes) {
    await adminApi.descartarDlq(mensaje.id)
    hechos += 1
    alProgresar?.({ hechos, total, id: mensaje.id })
  }
  return { total, hechos }
}

/* ── 7.8 Resiliencia (derivada del estado real, no simulada) ── */
export async function getResiliencia() {
  const [mesas, { mensajes }] = await Promise.all([estadoDe('mesas'), getDlq()])
  return {
    breakerEstado: mesas.tono === 'verde' ? 'CERRADO' : 'ABIERTO',
    alcanzable: mesas.live,
    servicio: mesas.nombre,
    ready: mesas.ready,
    detalle: mesas.detalle,
    dependencias: mesas.dependencias,
    dlqEnCola: mensajes.length,
    ajustes: clon(ajustes)
  }
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
