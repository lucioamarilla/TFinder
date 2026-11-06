// Votaciones de fechas (fechas-api).
import { useAuth } from '@/composables/useAuth'

function dividirLista(valor) {
  if (Array.isArray(valor)) return valor
  if (typeof valor === 'string' && valor.trim()) return valor.split(',').map((s) => s.trim())
  return []
}

// D-14: el voto propio. Primero el campo real del backend (mi_voto: 'a_favor'
// | 'en_contra'); si el despliegue aún no lo manda, se infiere comparando el
// nombre del usuario con la lista de firmas (el backend devuelve nombres, no
// ids) y queda null si no hay pista.
function miVotoDe(p, favor, contra) {
  if (p.mi_voto === 'a_favor') return 'favor'
  if (p.mi_voto === 'en_contra') return 'contra'
  const { user } = useAuth()
  const yo = String(user.value?.nombre ?? user.value?.email ?? '').trim().toLowerCase()
  if (yo) {
    if (favor.some((n) => n.trim().toLowerCase() === yo)) return 'favor'
    if (contra.some((n) => n.trim().toLowerCase() === yo)) return 'contra'
  }
  return null
}

function normalizarApi(p) {
  const favor = dividirLista(p.a_favor_nombres)
  const contra = dividirLista(p.en_contra_nombres)
  return {
    id: p.id,
    sesionNumero: 'próxima',
    titulo: 'Sesión propuesta',
    resumen:
      p.estado === 'confirmada'
        ? 'Fecha confirmada por la dirección.'
        : p.estado === 'descartada'
          ? 'Propuesta descartada.'
          : 'Convocatoria abierta a votos de los miembros.',
    fecha: p.propuesta,
    tipo: p.estado === 'confirmada' ? 'FECHA CONFIRMADA' : 'PROPUESTA OFICIAL GM',
    favor,
    contra,
    miVoto: miVotoDe(p, favor, contra),
    confirmada: p.estado === 'confirmada'
  }
}

export async function getVotaciones(mesaId) {
  const { fechasApi } = await import('@/api/endpoints')
  const { datos } = await fechasApi.listar(mesaId)
  return (datos ?? []).map(normalizarApi)
}

export async function votar(mesaId, votacionId, direccion) {
  const { fechasApi } = await import('@/api/endpoints')
  const valor = direccion === 'contra' ? 'en_contra' : 'a_favor'
  await fechasApi.votar(mesaId, votacionId, valor)
  return (await getVotaciones(mesaId)).find((v) => v.id === votacionId) ?? { id: votacionId }
}

// D-05: la fecha es real (YYYY-MM-DD de un input date) y la hora un input
// time ('HH:mm'); nunca un label humano. El backend acepta ISO con hora.
export async function proponerFecha(mesaId, { fecha, sesionNumero, titulo, hora } = {}) {
  const { fechasApi } = await import('@/api/endpoints')
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(fecha))) {
    const err = new Error('Elegí una fecha con el selector de día.')
    err.codigo = '400'
    throw err
  }
  const hhmm = String(hora ?? '').trim()
  const horaISO = /^\d{2}:\d{2}$/.test(hhmm) ? `${hhmm}:00` : '20:00:00'
  const iso = `${fecha}T${horaISO}`
  const { datos } = await fechasApi.proponer(mesaId, iso)
  return normalizarApi(datos)
}

export async function confirmarFecha(mesaId, votacionId) {
  const { fechasApi } = await import('@/api/endpoints')
  await fechasApi.confirmar(mesaId, votacionId)
  return { id: votacionId }
}
