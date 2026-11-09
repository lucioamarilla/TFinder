import { api } from '@/api/http'

export const authApi = {
  register: (b) => api('mesas', '/api/v1/auth/register', { metodo: 'POST', cuerpo: b }),
  verificarRegistro: (b) => api('mesas', '/api/v1/auth/register/verificar', { metodo: 'POST', cuerpo: b }),
  reenviarRegistro: (b) => api('mesas', '/api/v1/auth/register/reenviar', { metodo: 'POST', cuerpo: b }),
  recuperar: (b) => api('mesas', '/api/v1/auth/recuperar', { metodo: 'POST', cuerpo: b }),
  confirmarRecupero: (b) => api('mesas', '/api/v1/auth/recuperar/verificar', { metodo: 'POST', cuerpo: b }),
  login: (b) => api('mesas', '/api/v1/auth/login', { metodo: 'POST', cuerpo: b }),
  logout: () => api('mesas', '/api/v1/auth/logout', { metodo: 'POST' }),
  me: () => api('mesas', '/api/v1/auth/me')
}

export const mesasApi = {
  listarmias: () => api('mesas', '/api/v1/mesas/mias'),
  listar: (params = {}) => {
    const busqueda = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '')
    ).toString()
    return api('mesas', `/api/v1/mesas${busqueda ? `?${busqueda}` : ''}`)
  },
  detalle: (id) => api('mesas', `/api/v1/mesas/${id}`),
  crear: (b) => api('mesas', '/api/v1/mesas', { metodo: 'POST', cuerpo: b }),
  actualizar: (id, b) => api('mesas', `/api/v1/mesas/${id}`, { metodo: 'PUT', cuerpo: b }),
  eliminar: (id) => api('mesas', `/api/v1/mesas/${id}`, { metodo: 'DELETE' }),
  solicitarUnion: (mesaId, cuerpo, key) =>
    api('mesas', `/api/v1/mesas/${mesaId}/solicitudes`, {
      metodo: 'POST',
      cuerpo: cuerpo ?? {},
      idempotenciaKey: key
    }),
  listarSolicitudes: (mesaId, estado) =>
    api('mesas', `/api/v1/mesas/${mesaId}/solicitudes${estado ? `?estado=${estado}` : ''}`),
  responderSolicitud: (mesaId, solicitudId, accion) =>
    api('mesas', `/api/v1/mesas/${mesaId}/solicitudes/${solicitudId}/${accion}`, {
      metodo: 'POST'
    }),
  miembros: (mesaId) => api('mesas', `/api/v1/mesas/${mesaId}/miembros`),
  salir: (mesaId) => api('mesas', `/api/v1/mesas/${mesaId}/miembros/mi`, { metodo: 'DELETE' }),
  expulsar: (mesaId, usuarioId) =>
    api('mesas', `/api/v1/mesas/${mesaId}/miembros/${usuarioId}`, { metodo: 'DELETE' }),
  sesiones: (mesaId) => api('mesas', `/api/v1/mesas/${mesaId}/sesiones`)
}

export const fechasApi = {
  listar: (mesaId) => api('mesas', `/api/v1/mesas/${mesaId}/fechas`),
  proponer: (mesaId, fechaISO) =>
    api('mesas', `/api/v1/mesas/${mesaId}/fechas`, {
      metodo: 'POST',
      cuerpo: { propuesta: fechaISO }
    }),
  votar: (mesaId, fechaId, valor) =>
    api('mesas', `/api/v1/mesas/${mesaId}/fechas/${fechaId}/voto`, {
      metodo: 'POST',
      cuerpo: { valor }
    }),
  confirmar: (mesaId, fechaId) =>
    api('mesas', `/api/v1/mesas/${mesaId}/fechas/${fechaId}/confirmar`, { metodo: 'POST' }),
  descartar: (mesaId, fechaId) =>
    api('mesas', `/api/v1/mesas/${mesaId}/fechas/${fechaId}`, { metodo: 'DELETE' })
}

export const perfilApi = {
  ver: () => api('mesas', '/api/v1/auth/perfil'),
  editar: (b) => api('mesas', '/api/v1/auth/perfil', { metodo: 'PATCH', cuerpo: b })
}

export const sesionesApi = {
  marcarAsistencia: (sesionId) =>
    api('mesas', `/api/v1/sesiones/${sesionId}/asistencia`, { metodo: 'POST' })
}

export const matchmakingApi = {
  abrir: (mmId) => api('mesas', `/api/v1/matchmaking/${mmId}/abrir`, { metodo: 'POST' }),
  estado: (mmId) => api('mesas', `/api/v1/matchmaking/${mmId}/estado`),
  anotarse: (mesaId, cuerpo) =>
    api('mesas', `/api/v1/mesas/${mesaId}/solicitudes`, { metodo: 'POST', cuerpo })
}

