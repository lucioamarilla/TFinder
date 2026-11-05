import { api } from '@/api/http'

export const authApi = {
  register: (b) => api('mesas', '/api/v1/auth/register', { metodo: 'POST', cuerpo: b }),
  login: (b) => api('mesas', '/api/v1/auth/login', { metodo: 'POST', cuerpo: b }),
  logout: () => api('mesas', '/api/v1/auth/logout', { metodo: 'POST' }),
  me: () => api('mesas', '/api/v1/auth/me'),
  recuperar: (b) => api('notif', '/api/v1/auth/recuperar', { metodo: 'POST', cuerpo: b })
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

export const feedApi = {
  listar: (params = {}) => {
    const busqueda = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '')
    ).toString()
    return api('feed', `/api/v1/feed${busqueda ? `?${busqueda}` : ''}`)
  },
  comunidades: () => api('feed', '/api/v1/feed/comunidades'),
  crear: (b) => api('feed', '/api/v1/feed', { metodo: 'POST', cuerpo: b }),
  like: (postId) => api('feed', `/api/v1/feed/${postId}/like`, { metodo: 'POST' }),
  seguir: (usuarioId) =>
    api('feed', `/api/v1/usuarios/${usuarioId}/seguir`, { metodo: 'POST' })
}

export const wikiApi = {
  listar: (mesaId) => api('feed', `/api/v1/wiki${mesaId ? `?mesa_id=${mesaId}` : ''}`),
  detallar: (id) => api('feed', `/api/v1/wiki/${id}`),
  crear: (mesaId, b) => api('feed', `/api/v1/mesas/${mesaId}/wiki`, { metodo: 'POST', cuerpo: b }),
  actualizar: (id, b) => api('feed', `/api/v1/wiki/${id}`, { metodo: 'PUT', cuerpo: b }),
  eliminar: (id) => api('feed', `/api/v1/wiki/${id}`, { metodo: 'DELETE' }),
  crearContribucion: (mesaId, paginaId, b) => api('feed', `/api/v1/mesas/${mesaId}/wiki/${paginaId}/contribuciones`, { metodo: 'POST', cuerpo: b }),
  listarContribuciones: (mesaId, estado) => api('feed', `/api/v1/mesas/${mesaId}/wiki/contribuciones${estado ? `?estado=${estado}` : ''}`),
  aprobarContribucion: (mesaId, id) => api('feed', `/api/v1/mesas/${mesaId}/wiki/contribuciones/${id}/aprobar`, { metodo: 'POST' }),
  rechazarContribucion: (mesaId, id) => api('feed', `/api/v1/mesas/${mesaId}/wiki/contribuciones/${id}/rechazar`, { metodo: 'POST' }),
}

export const buildsApi = {
  listar: (params = {}) => {
    const busqueda = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '')
    ).toString()
    return api('builds', `/api/v1/builds${busqueda ? `?${busqueda}` : ''}`)
  },
  detallar: (id) => api('builds', `/api/v1/builds/${id}`),
  crear: (b) => api('builds', '/api/v1/builds', { metodo: 'POST', cuerpo: b }),
  actualizar: (id, b) => api('builds', `/api/v1/builds/${id}`, { metodo: 'PUT', cuerpo: b }),
  eliminar: (id) => api('builds', `/api/v1/builds/${id}`, { metodo: 'DELETE' }),
  publicar: (id) => api('builds', `/api/v1/builds/${id}/publicar`, { metodo: 'POST' }),
  vincular: (id, mesaId) => api('builds', `/api/v1/builds/${id}/vincular/${mesaId}`, { metodo: 'POST' }),
  desvincular: (id) => api('builds', `/api/v1/builds/${id}/vincular`, { metodo: 'DELETE' }),
  restaurar: (id, indice) => api('builds', `/api/v1/builds/${id}/restaurar/${indice}`, { metodo: 'POST' }),
  asignarTags: (id, nombres) => api('builds', `/api/v1/builds/${id}/tags`, { metodo: 'POST', cuerpo: { nombres } })
}

export const uploadsApi = {
  subir: (archivo) => {
    const fd = new FormData()
    fd.append('upload', archivo)
    return api('feed', '/api/v1/uploads', { metodo: 'POST', cuerpo: null, idempotenciaKey: null }).then(() => fd)
  },
  subirManual: (formData) => api('feed', '/api/v1/uploads', { metodo: 'POST', cuerpo: formData })
}

export const perfilApi = {
  ver: () => api('mesas', '/api/v1/auth/perfil'),
  editar: (b) => api('mesas', '/api/v1/auth/perfil', { metodo: 'PATCH', cuerpo: b })
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

export const notifApi = {
  notificaciones: (soloNoLeidas = false) =>
    api('notif', `/api/v1/notificaciones${soloNoLeidas ? '?solo_no_leidas=true' : ''}`),
  marcarLeida: (id) =>
    api('notif', `/api/v1/notificaciones/${id}/leida`, { metodo: 'PATCH' }),
  leerTodas: () => api('notif', '/api/v1/notificaciones/leer-todas', { metodo: 'PATCH' }),
  eventLog: () => api('notif', '/api/v1/event-log'),
  pdf: (docId) => api('notif', `/api/v1/pdf/${docId}`)
}