import { api } from '@/api/http'

export const authApi = {
  register: (b) => api('mesas', '/api/v1/auth/register', { metodo: 'POST', cuerpo: b }),
  login: (b) => api('mesas', '/api/v1/auth/login', { metodo: 'POST', cuerpo: b }),
  logout: () => api('mesas', '/api/v1/auth/logout', { metodo: 'POST' }),
  me: () => api('mesas', '/api/v1/auth/me')
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
  estado: (mmId) => api('mesas', `/api/v1/matchmaking/${mmId}/estado`)
}

export const notifApi = {
  notificaciones: () => api('notif', '/api/v1/notificaciones'),
  marcarLeida: (id) =>
    api('notif', `/api/v1/notificaciones/${id}/leida`, { metodo: 'PATCH' }),
  eventLog: () => api('notif', '/api/v1/event-log'),
  pdf: (docId) => api('notif', `/api/v1/pdf/${docId}`)
}