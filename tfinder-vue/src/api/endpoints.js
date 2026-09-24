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
  solicitarUnion: (mesaId, cuerpo, key) =>
    api('mesas', `/api/v1/mesas/${mesaId}/solicitudes`, { metodo: 'POST', cuerpo, idempotenciaKey: key })
}

export const notifApi = {
  notificaciones: () => api('notif', '/api/v1/notificaciones'),
  marcarLeida: (id) => api('notif', `/api/v1/notificaciones/${id}/leida`, { metodo: 'PATCH' }),
  eventLog: () => api('notif', '/api/v1/event-log')
}
