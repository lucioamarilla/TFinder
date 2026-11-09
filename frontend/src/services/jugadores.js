// Jugadores de mesa y solicitudes (mesas-api).
import { useAuth } from '@/composables/useAuth'

function emailSesion() {
  const { user } = useAuth()
  return user.value?.email || null
}

function solicitudApiNormalizada(s) {
  const nombre = s.nombre || s.email || `Usuario ${s.usuario_id}`
  return {
    id: s.id,
    nombre,
    avatar: nombre.slice(0, 2).toUpperCase(),
    personaje: '—',
    clase: '—',
    nivel: '—',
    nota: '',
    estado: s.estado,
    email: s.email
  }
}

// El master NO se cuenta como jugador: es miembro de la mesa con rol de
// direccion, pero no ocupa una de las plazas de la mesa de aventureros.
// Los exploradores de mesa usan mesa.jugadores (COUNT rol='jugador'), asi
// que aqui conteamos lo mismo para evitar el 1 vs 0 entre vistas.
// '!== Master' (y no '=== Jugador') para que un miembro sin rol cuente como
// jugador; un master nunca se cuenta doble.
export function contarJugadores(miembros) {
  return (miembros ?? []).filter((m) => m.rol !== 'Master').length
}

export async function getMiembros(mesaId, mesa = null) {
  const { mesasApi } = await import('@/api/endpoints')
  const { datos } = await mesasApi.miembros(mesaId)
  return {
    miembros: (datos?.miembros ?? []).map((m) => ({
      id: String(m.id),
      email: m.email,
      nombre: m.nombre,
      avatar: (m.nombre || '').slice(0, 2).toUpperCase(),
      personaje: '—',
      clase: '—',
      nivel: '—',
      estado: 'Activo',
      // D-11: rol real del backend ('master' | 'jugador'), sin hardcodeo.
      rol: m.rol === 'master' ? 'Master' : 'Jugador',
      buildVinculado: false,
      fecha: 'Activa en la mesa'
    })),
    solicitudes: [],
    // D-11: capacidad derivada de la mesa (jugadores_max) cuando el caller
    // la provee; null no corrompe la UI (los shells recurren a mesa.plazas).
    capacidad: mesa?.plazas ?? null
  }
}

export async function getSolicitudes(mesaId) {
  const { mesasApi } = await import('@/api/endpoints')
  const { datos } = await mesasApi.listarSolicitudes(mesaId, 'pendiente')
  return (datos ?? []).map(solicitudApiNormalizada)
}

export async function aceptarSolicitud(mesaId, solicitudId) {
  const { mesasApi } = await import('@/api/endpoints')
  await mesasApi.responderSolicitud(mesaId, solicitudId, 'aceptar')
  return { ok: true }
}

export async function rechazarSolicitud(mesaId, solicitudId) {
  const { mesasApi } = await import('@/api/endpoints')
  await mesasApi.responderSolicitud(mesaId, solicitudId, 'rechazar')
  return true
}

export async function expulsarMiembro(mesaId, miembroId) {
  const { mesasApi } = await import('@/api/endpoints')
  await mesasApi.expulsar(mesaId, miembroId)
  return { id: String(miembroId) }
}