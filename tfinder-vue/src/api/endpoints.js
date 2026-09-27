import { api, apiBlob } from '@/api/http'

export const authApi = {
  register: (b) => api('mesas', '/api/v1/auth/register', { metodo: 'POST', cuerpo: b }),
  login: (b) => api('mesas', '/api/v1/auth/login', { metodo: 'POST', cuerpo: b }),
  logout: () => api('mesas', '/api/v1/auth/logout', { metodo: 'POST' }),
  me: () => api('mesas', '/api/v1/auth/me'),
  recuperar: (b) => api('notif', '/api/v1/auth/recuperar', { metodo: 'POST', cuerpo: b })
}

export const mesasApi = {
  listar: () => api('mesas', '/api/v1/mesas'),
  detalle: (id) => api('mesas', `/api/v1/mesas/${id}`),
  crear: (b) => api('mesas', '/api/v1/mesas', { metodo: 'POST', cuerpo: b }),
  actualizar: (id, b) => api('mesas', `/api/v1/mesas/${id}`, { metodo: 'PUT', cuerpo: b }),
  eliminar: (id) => api('mesas', `/api/v1/mesas/${id}`, { metodo: 'DELETE' }),
  solicitarUnion: (mesaId, cuerpo, key) =>
    api('mesas', `/api/v1/mesas/${mesaId}/solicitudes`, {
      metodo: 'POST',
      cuerpo: cuerpo ?? {},
      idempotenciaKey: key
    })
}

export const sesionesApi = {
  qr: (sesionId) => api('mesas', `/api/v1/sesiones/${sesionId}/qr`, { metodo: 'POST' }),
  validarQr: (sesionId, body) =>
    api('mesas', `/api/v1/sesiones/${sesionId}/qr/validar`, { metodo: 'POST', cuerpo: body })
}

export const matchmakingApi = {
  abrir: (mmId) => api('mesas', `/api/v1/matchmaking/${mmId}/abrir`, { metodo: 'POST' }),
  estado: (mmId) => api('mesas', `/api/v1/matchmaking/${mmId}/estado`),
  anotarse: (mesaId, cuerpo) =>
    api('mesas', `/api/v1/mesas/${mesaId}/solicitudes`, { metodo: 'POST', cuerpo })
}

function consulta(params) {
  const pares = Object.entries(params || {}).filter(([, v]) => v !== null && v !== undefined && v !== '')
  return pares.length ? `?${pares.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`).join('&')}` : ''
}

export const notifApi = {
  notificaciones: (soloNoLeidas = false) =>
    api('notif', `/api/v1/notificaciones${soloNoLeidas ? '?solo_no_leidas=true' : ''}`),
  marcarLeida: (id) =>
    api('notif', `/api/v1/notificaciones/${id}/leida`, { metodo: 'PATCH' }),
  eventLog: (filtro = {}) =>
    api('notif', `/api/v1/event-log${consulta({ correlation_id: filtro.correlationId, entidad_tipo: filtro.entidadTipo, entidad_id: filtro.entidadId })}`)
}

export const pdfApi = {
  solicitarBuild: (buildId) => api('builds', `/api/v1/builds/${buildId}/pdf`, { metodo: 'POST' }),
  estado: (docId) => api('notif', `/api/v1/pdf/${docId}/estado`),
  descargar: (docId) => apiBlob('notif', `/api/v1/pdf/${docId}`)
}

// /live y /ready son públicos en los 4 servicios. /ready responde 503 cuando
// alguna dependencia (pg/redis/rabbitmq) está caída, pero con el detalle de
// cuáles en el body: por eso es el único endpoint que usa aceptarEstados.
export const adminApi = {
  live: (servicio) => api(servicio, '/live'),
  ready: (servicio) => api(servicio, '/ready', { aceptarEstados: [503] }),
  dlq: (limite) => api('notif', `/api/v1/dlq${consulta({ limite })}`),
  reintentarDlq: (id) => api('notif', `/api/v1/dlq/${id}/reintentar`, { metodo: 'POST' }),
  descartarDlq: (id) => api('notif', `/api/v1/dlq/${id}`, { metodo: 'DELETE' })
}