// Votaciones de fechas (fechas-api).
import { useAuth } from '@/composables/useAuth'

function dividirLista(valor) {
  if (Array.isArray(valor)) return valor
  if (typeof valor === 'string' && valor.trim()) return valor.split(',').map((s) => s.trim())
  return []
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
    miVoto: null,
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

export async function proponerFecha(mesaId, { fecha, sesionNumero, titulo, hora }) {
  const { fechasApi } = await import('@/api/endpoints')
  const iso = hora ? `${fecha}T${hora}` : `${fecha}T20:00:00`
  const { datos } = await fechasApi.proponer(mesaId, iso)
  return normalizarApi(datos)
}

export async function confirmarFecha(mesaId, votacionId) {
  const { fechasApi } = await import('@/api/endpoints')
  await fechasApi.confirmar(mesaId, votacionId)
  return { id: votacionId }
}